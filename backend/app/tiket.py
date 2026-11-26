"""Tiket tugas bertanda tangan (3.6).

Setiap tugas diwakili satu tiket: jenis, tier, benih publik, modifier,
waktu terbit, waktu kedaluwarsa, dan tanda tangan HMAC dengan garam
rahasia server. Data tugas dibuat dari benih yang dicampur garam,
sehingga membaca kode di repositori publik tidak cukup untuk
menghitung jawaban.

- Garam hanya ada di variabel lingkungan ``OFFICE_QUEST_GARAM``
  (dashboard hosting). Repo hanya memuat contoh nama variabel
  (``backend/.env.example``) tanpa nilai.
- Tiket berlaku sampai 02.00 WIB hari berikutnya, supaya pemain yang
  bermain larut tidak terpotong.
- Mode paritas berakhir di langkah ini: seed produksi selalu
  diturunkan dari garam.

Kode galat (dipakai endpoint di 3.7): tiket tidak sah -> 403,
tiket kedaluwarsa -> 410.
"""

import base64
import binascii
import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from app.generator import buat_data_tugas

NAMA_VAR_GARAM = "OFFICE_QUEST_GARAM"
WIB = ZoneInfo("Asia/Jakarta")
JAM_KEDALUWARSA = time(2, 0)  # 02.00 WIB hari berikutnya

JENIS_TUGAS = ("rekap_penjualan", "absensi", "penilaian_magang")


class GalatGaram(Exception):
    """Garam rahasia belum diatur."""


class GalatTiket(Exception):
    """Tiket tidak bisa dipakai; ``kode`` untuk mesin (dan HTTP 3.7)."""

    def __init__(self, kode, pesan):
        super().__init__(pesan)
        self.kode = kode
        self.pesan = pesan


def buat_garam():
    """Buat garam acak baru (64 karakter hex). Simpan di dashboard
    hosting, jangan di repo."""
    return secrets.token_hex(32)


def garam_dari_lingkungan():
    """Baca garam dari variabel lingkungan. Gagal keras bila belum
    diatur — jangan pernah diam-diam memakai garam bawaan/publik."""
    garam = os.environ.get(NAMA_VAR_GARAM)
    if not garam:
        raise GalatGaram(
            f"Variabel lingkungan {NAMA_VAR_GARAM} belum diatur. "
            "Isi di dashboard hosting backend (bukan di repo)."
        )
    return garam


def _kanonis(obj):
    """JSON kanonis: kunci terurut, tanpa spasi (seperti aoa_ke_json)."""
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _tanda(muatan, garam):
    return hmac.new(
        garam.encode("utf-8"),
        _kanonis(muatan).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _ke_teks_iso(dt):
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _dari_teks_iso(teks):
    return datetime.strptime(teks, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def kedaluwarsa_berikutnya(sekarang):
    """02.00 WIB pada tanggal WIB besok (dari waktu terbit)."""
    tanggal_wib = sekarang.astimezone(WIB).date() + timedelta(days=1)
    return datetime.combine(tanggal_wib, JAM_KEDALUWARSA, tzinfo=WIB)


def benih_harian(id_pemain, tanggal):
    """Benih publik tugas harian: pemain yang sama di hari yang sama
    selalu mendapat benih yang sama, di hari berbeda benih berbeda.
    ``tanggal`` berupa 'YYYY-MM-DD' (tanggal WIB)."""
    return f"harian-{tanggal}-{id_pemain}"


def turunkan_seed(benih_publik, garam):
    """Turunkan seed produksi dari benih publik + garam rahasia.
    Garam berbeda -> seed berbeda -> data tugas berbeda."""
    return hmac.new(
        garam.encode("utf-8"),
        str(benih_publik).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def terbitkan_tiket(jenis, garam, tier=1, benih_publik=None, modifier=None, sekarang=None):
    """Terbitkan tiket tugas. ``benih_publik`` bila kosong dibuat dari
    jenis + waktu terbit (unik per tiket)."""
    if jenis not in JENIS_TUGAS:
        raise GalatTiket("tiket_tidak_sah", f"Jenis tugas tidak dikenal: {jenis}.")
    if not isinstance(tier, int) or isinstance(tier, bool) or tier < 1:
        raise GalatTiket("tiket_tidak_sah", "Tier harus bilangan bulat >= 1.")
    if modifier is not None and not isinstance(modifier, str):
        raise GalatTiket("tiket_tidak_sah", "Modifier harus teks.")
    sekarang = sekarang or datetime.now(timezone.utc)
    muatan = {
        "jenis": jenis,
        "tier": tier,
        "benih": benih_publik or f"{jenis}-{_ke_teks_iso(sekarang)}",
        "modifier": modifier,
        "diterbitkan": _ke_teks_iso(sekarang),
        "kedaluwarsa": _ke_teks_iso(kedaluwarsa_berikutnya(sekarang)),
    }
    amplop = {"muatan": muatan, "tanda": _tanda(muatan, garam)}
    return base64.urlsafe_b64encode(_kanonis(amplop).encode("utf-8")).decode("ascii").rstrip("=")


def periksa_tiket(teks_tiket, garam, sekarang=None):
    """Periksa tiket; kembalikan muatannya. Gagal -> GalatTiket:
    'tiket_rusak' (bukan tiket), 'tiket_tidak_sah' (tanda tidak cocok,
    HTTP 403), 'tiket_kedaluwarsa' (HTTP 410)."""
    sekarang = sekarang or datetime.now(timezone.utc)
    try:
        mentah = base64.urlsafe_b64decode(teks_tiket + "=" * (-len(teks_tiket) % 4))
        amplop = json.loads(mentah.decode("utf-8"))
        muatan = amplop["muatan"]
        tanda = amplop["tanda"]
        if not isinstance(muatan, dict) or not isinstance(tanda, str):
            raise ValueError("amplop tidak lengkap")
        for kunci in ("jenis", "tier", "benih", "modifier", "diterbitkan", "kedaluwarsa"):
            if kunci not in muatan:
                raise ValueError(f"muatan tanpa {kunci}")
    except (ValueError, KeyError, TypeError, binascii.Error, UnicodeDecodeError):
        raise GalatTiket("tiket_rusak", "Tiket tidak bisa dibaca.") from None
    if muatan["jenis"] not in JENIS_TUGAS:
        raise GalatTiket("tiket_tidak_sah", "Jenis tugas pada tiket tidak dikenal.")
    if not hmac.compare_digest(_tanda(muatan, garam), tanda):
        raise GalatTiket("tiket_tidak_sah", "Tanda tangan tiket tidak cocok.")
    if _dari_teks_iso(muatan["kedaluwarsa"]) <= sekarang:
        raise GalatTiket("tiket_kedaluwarsa", "Tiket sudah kedaluwarsa.")
    return muatan


def data_untuk_tiket(muatan, garam):
    """Data tugas (AOA) untuk satu tiket yang sudah diperiksa:
    seed produksi = benih publik tiket + garam."""
    return buat_data_tugas(muatan["jenis"], turunkan_seed(muatan["benih"], garam))
