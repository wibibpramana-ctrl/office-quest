"""Layanan akun Office Quest (Fase 5.2).

- Kata sandi: hash argon2id (argon2-cffi), tidak pernah teks biasa.
- Sesi: token acak 32 byte; yang disimpan hanya hash SHA-256 + kedaluwarsa
  (30 hari, diputuskan Wibi 27 Nov 2026).
- Semua fungsi menerima koneksi SQLite; HTTPException dilempar di main.py.
- Pesan galat masuk sengaja sama untuk nama tak dikenal dan kata sandi
  salah (tidak membocorkan akun mana yang ada).
"""

import hashlib
import json
import re
import secrets
import sqlite3
from datetime import datetime, timedelta

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.tiket import WIB

MASA_SESI_HARI = 30

_penghash = PasswordHasher()


class GalatAkun(Exception):
    def __init__(self, kode, pesan, status=400):
        super().__init__(pesan)
        self.kode = kode
        self.pesan = pesan
        self.status = status


_NAMA_AKUN = re.compile(r"^[A-Za-z][A-Za-z0-9_]{2,29}$")
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def hash_kata_sandi(kata_sandi):
    return _penghash.hash(kata_sandi)


def periksa_kata_sandi(hash_tersimpan, kata_sandi):
    try:
        return _penghash.verify(hash_tersimpan, kata_sandi)
    except VerifyMismatchError:
        return False
    except Exception:
        return False


def validasi_nama_akun(nama):
    if not isinstance(nama, str) or not _NAMA_AKUN.match(nama):
        raise GalatAkun(
            "nama_tidak_valid",
            "Nama akun 3–30 karakter, diawali huruf, hanya huruf, angka, dan garis bawah.",
            400,
        )


def validasi_kata_sandi(kata_sandi):
    if not isinstance(kata_sandi, str) or not 8 <= len(kata_sandi) <= 128:
        raise GalatAkun("kata_sandi_tidak_valid", "Kata sandi 8–128 karakter.", 400)


def validasi_email(email):
    if email is None:
        return None
    email = email.strip()
    if email == "":
        return None
    if not _EMAIL.match(email):
        raise GalatAkun("email_tidak_valid", "Alamat email tidak valid.", 400)
    return email


def validasi_nama_panggilan(nama):
    if nama is None:
        return None
    nama = nama.strip()
    if nama == "":
        return None
    if len(nama) > 30 or any(ord(c) < 32 for c in nama):
        raise GalatAkun(
            "nama_panggilan_tidak_valid", "Nama panggilan maksimal 30 karakter.", 400
        )
    return nama


def _sekarang():
    return datetime.now(WIB)


def _iso(dt):
    return dt.isoformat()


def _hash_token(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def cari_akun_nama(conn, nama_akun):
    return conn.execute(
        "SELECT * FROM akun WHERE nama_akun = ?", (nama_akun,)
    ).fetchone()


def cari_akun_id(conn, akun_id):
    return conn.execute("SELECT * FROM akun WHERE id = ?", (akun_id,)).fetchone()


def buat_akun(conn, nama_akun, nama_panggilan, email, kata_sandi):
    """Buat akun + baris progres awal (level 1, 0 XP, energi penuh)."""
    validasi_nama_akun(nama_akun)
    validasi_kata_sandi(kata_sandi)
    nama_panggilan = validasi_nama_panggilan(nama_panggilan)
    email = validasi_email(email)
    sekarang = _iso(_sekarang())
    try:
        cur = conn.execute(
            "INSERT INTO akun (nama_akun, nama_panggilan, email, hash_kata_sandi, dibuat_pada)"
            " VALUES (?, ?, ?, ?, ?)",
            (nama_akun, nama_panggilan, email, hash_kata_sandi(kata_sandi), sekarang),
        )
        akun_id = cur.lastrowid
        conn.execute(
            "INSERT INTO progres (akun_id, xp, koin, level, energi, energi_dihitung_pada,"
            " streak_absen, terakhir_absen, diperbarui_pada)"
            " VALUES (?, 0, 0, 1, 100, ?, 0, NULL, ?)",
            (akun_id, sekarang, sekarang),
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.rollback()
        pesan = str(e)
        if "akun.email" in pesan:
            raise GalatAkun("email_sudah_dipakai", "Email sudah dipakai.", 409) from None
        raise GalatAkun("nama_sudah_dipakai", "Nama akun sudah dipakai.", 409) from None
    return akun_id


def periksa_masuk(conn, nama_akun, kata_sandi):
    """Kembalikan baris akun bila kredensial benar; bila tidak, 401."""
    akun = cari_akun_nama(conn, nama_akun)
    if akun is None or not periksa_kata_sandi(akun["hash_kata_sandi"], kata_sandi):
        raise GalatAkun("kredensial_salah", "Nama akun atau kata sandi salah.", 401)
    return akun


def buat_sesi(conn, akun_id, perangkat=None):
    """Buat sesi baru, kembalikan token mentahnya (hanya sekali ini)."""
    token = secrets.token_urlsafe(32)
    sekarang = _sekarang()
    kedaluwarsa = sekarang + timedelta(days=MASA_SESI_HARI)
    conn.execute(
        "INSERT INTO sesi (akun_id, token_hash, dibuat_pada, kedaluwarsa_pada, perangkat)"
        " VALUES (?, ?, ?, ?, ?)",
        (akun_id, _hash_token(token), _iso(sekarang), _iso(kedaluwarsa), perangkat),
    )
    conn.execute(
        "UPDATE akun SET terakhir_masuk = ? WHERE id = ?", (_iso(sekarang), akun_id)
    )
    conn.commit()
    return token


def akun_dari_token(conn, token):
    """Kembalikan (baris akun, baris sesi) untuk token; 401 bila tidak sah."""
    if not token:
        raise GalatAkun("belum_masuk", "Masuk dulu untuk memakai endpoint ini.", 401)
    baris = conn.execute(
        "SELECT * FROM sesi WHERE token_hash = ?", (_hash_token(token),)
    ).fetchone()
    if baris is None:
        raise GalatAkun("belum_masuk", "Sesi tidak dikenal, masuk lagi.", 401)
    if _sekarang() > datetime.fromisoformat(baris["kedaluwarsa_pada"]):
        raise GalatAkun("sesi_kedaluwarsa", "Sesi sudah kedaluwarsa, masuk lagi.", 401)
    akun = cari_akun_id(conn, baris["akun_id"])
    if akun is None:
        raise GalatAkun("belum_masuk", "Akun tidak ditemukan.", 401)
    return akun, baris


def hapus_sesi(conn, token):
    conn.execute("DELETE FROM sesi WHERE token_hash = ?", (_hash_token(token),))
    conn.commit()


def hapus_sesi_lain(conn, akun_id, token_saat_ini):
    """Keluar dari semua perangkat lain (dipakai saat ganti kata sandi)."""
    conn.execute(
        "DELETE FROM sesi WHERE akun_id = ? AND token_hash != ?",
        (akun_id, _hash_token(token_saat_ini)),
    )
    conn.commit()


def ganti_kata_sandi(conn, akun_id, hash_baru):
    conn.execute(
        "UPDATE akun SET hash_kata_sandi = ? WHERE id = ?", (hash_baru, akun_id)
    )
    conn.commit()


def info_akun_publik(baris):
    """Isi /akun/saya — tanpa hash kata sandi, tanpa apa pun yang rahasia."""
    return {
        "id": baris["id"],
        "nama_akun": baris["nama_akun"],
        "nama_panggilan": baris["nama_panggilan"],
        "email": baris["email"],
        "dibuat_pada": baris["dibuat_pada"],
    }


# --- Migrasi progres lokal ke akun (Fase 5.4) ---


def hitung_level(xp):
    """Level dari XP — sama dengan hitungLevel di frontend (model lama:
    250 XP/level, maks 4). Model ekonomi baru (Fase 6) akan menggantikannya."""
    n = xp if isinstance(xp, int) and not isinstance(xp, bool) and xp > 0 else 0
    return min(n // 250 + 1, 4)


def _validasi_nilai_migrasi(nama, nilai, kode="migrasi_tidak_valid", label="migrasi"):
    if (
        isinstance(nilai, bool)
        or not isinstance(nilai, int)
        or not 0 <= nilai <= 10_000_000
    ):
        raise GalatAkun(
            kode,
            f"{nama} {label} harus bilangan bulat 0–10.000.000.",
            400,
        )


def _validasi_nilai_progres(nama, nilai):
    _validasi_nilai_migrasi(nama, nilai, "progres_tidak_valid", "progres")


def _validasi_butir_chat(butir, kode="migrasi_tidak_valid"):
    """Kembalikan butir chat yang sudah dinormalisasi (dibaca -> 0/1)."""
    if not isinstance(butir, dict):
        raise GalatAkun(
            kode, "Tiap pesan chat harus berupa objek.", 400
        )
    for nama in ("karakter", "pengirim"):
        nilai = butir.get(nama)
        if (
            not isinstance(nilai, str)
            or not 1 <= len(nilai) <= 30
            or any(ord(c) < 32 for c in nilai)
        ):
            raise GalatAkun(
                kode,
                f"{nama} pesan chat 1–30 karakter tanpa karakter kontrol.",
                400,
            )
    isi = butir.get("isi")
    if not isinstance(isi, str) or not 1 <= len(isi) <= 2000:
        raise GalatAkun(
            kode, "Isi pesan chat 1–2000 karakter.", 400
        )
    dibuat_pada = butir.get("dibuat_pada")
    if not isinstance(dibuat_pada, str):
        raise GalatAkun(
            kode,
            "dibuat_pada pesan chat harus tanggal ISO.",
            400,
        )
    try:
        datetime.fromisoformat(dibuat_pada)
    except ValueError:
        raise GalatAkun(
            kode,
            "dibuat_pada pesan chat harus tanggal ISO.",
            400,
        ) from None
    dibaca = butir.get("dibaca", True)
    if not isinstance(dibaca, bool):
        raise GalatAkun(
            kode,
            "dibaca pesan chat harus benar atau salah.",
            400,
        )
    return {
        "karakter": butir["karakter"],
        "pengirim": butir["pengirim"],
        "isi": isi,
        "dibuat_pada": dibuat_pada,
        "dibaca": 1 if dibaca else 0,
    }


def _validasi_butir_chat_progres(butir):
    return _validasi_butir_chat(butir, "progres_tidak_valid")


def migrasi_progres(conn, akun_id, xp, koin, chat):
    """Pindahkan progres lokal (simpanan lama / Tamu) ke akun — sekali saja.

    Hanya bila akun belum punya progres (xp=0, koin=0, level=1). Semua
    tulis dilakukan dalam satu transaksi: progres + pesan_chat. Status
    tugas lama sengaja tidak ikut (diputuskan Wibi 28 Nov 2026).
    """
    _validasi_nilai_migrasi("XP", xp)
    _validasi_nilai_migrasi("Koin", koin)
    if not isinstance(chat, list) or len(chat) > 500:
        raise GalatAkun(
            "migrasi_tidak_valid", "Chat migrasi maksimal 500 butir.", 400
        )
    butir_chat = [_validasi_butir_chat(b) for b in chat]
    baris = conn.execute(
        "SELECT xp, koin, level FROM progres WHERE akun_id = ?", (akun_id,)
    ).fetchone()
    if baris is None:
        lama = (0, 0, 1)
    else:
        lama = (baris["xp"], baris["koin"], baris["level"])
    if lama[0] > 0 or lama[1] > 0 or lama[2] > 1:
        raise GalatAkun(
            "sudah_punya_progres", "Akun ini sudah punya progres.", 409
        )
    sekarang = _iso(_sekarang())
    level = hitung_level(xp)
    try:
        if baris is None:
            conn.execute(
                "INSERT INTO progres (akun_id, xp, koin, level, energi,"
                " energi_dihitung_pada, streak_absen, terakhir_absen, diperbarui_pada)"
                " VALUES (?, ?, ?, ?, 100, ?, 0, NULL, ?)",
                (akun_id, xp, koin, level, sekarang, sekarang),
            )
        else:
            conn.execute(
                "UPDATE progres SET xp = ?, koin = ?, level = ?,"
                " diperbarui_pada = ? WHERE akun_id = ?",
                (xp, koin, level, sekarang, akun_id),
            )
        conn.execute("DELETE FROM pesan_chat WHERE akun_id = ?", (akun_id,))
        for b in butir_chat:
            conn.execute(
                "INSERT INTO pesan_chat (akun_id, karakter, pengirim, isi,"
                " dibuat_pada, dibaca) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    akun_id,
                    b["karakter"],
                    b["pengirim"],
                    b["isi"],
                    b["dibuat_pada"],
                    b["dibaca"],
                ),
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return {"xp": xp, "koin": koin, "level": level, "pesan_chat": len(butir_chat)}


# --- Progres tersimpan di server (Fase 5.5) ---


SLOT_TERPASANG = {"kepala", "wajah", "baju", "celana", "sepatu", "meja"}


def _validasi_hint_progres(hint):
    """Jatah hint: {tugas: {karakter: 0..3}} — bentuk yang sama dengan
    simpanan lokal frontend."""
    if not isinstance(hint, dict) or len(hint) > 32:
        raise GalatAkun(
            "progres_tidak_valid",
            "Hint progres harus objek maksimal 32 tugas.",
            400,
        )
    hasil = {}
    for tugas, per_karakter in hint.items():
        if not isinstance(tugas, str) or not 1 <= len(tugas) <= 64:
            raise GalatAkun(
                "progres_tidak_valid",
                "Id tugas hint 1–64 karakter.",
                400,
            )
        if not isinstance(per_karakter, dict) or len(per_karakter) > 10:
            raise GalatAkun(
                "progres_tidak_valid",
                "Hint tiap tugas maksimal 10 karakter.",
                400,
            )
        entri = {}
        for karakter, jumlah in per_karakter.items():
            if not isinstance(karakter, str) or not 1 <= len(karakter) <= 30:
                raise GalatAkun(
                    "progres_tidak_valid",
                    "Id karakter hint 1–30 karakter.",
                    400,
                )
            if (
                isinstance(jumlah, bool)
                or not isinstance(jumlah, int)
                or not 0 <= jumlah <= 3
            ):
                raise GalatAkun(
                    "progres_tidak_valid",
                    "Jatah hint tiap karakter 0–3.",
                    400,
                )
            entri[karakter] = jumlah
        hasil[tugas] = entri
    return hasil


def _validasi_id_item(nama, nilai):
    if (
        not isinstance(nilai, str)
        or not 1 <= len(nilai) <= 64
        or any(ord(c) < 32 for c in nilai)
    ):
        raise GalatAkun(
            "progres_tidak_valid",
            f"{nama} 1–64 karakter tanpa karakter kontrol.",
            400,
        )


def _validasi_inventori(inventori):
    if not isinstance(inventori, list) or len(inventori) > 200:
        raise GalatAkun(
            "progres_tidak_valid", "Inventori maksimal 200 item.", 400
        )
    hasil = []
    for item in inventori:
        _validasi_id_item("Id item inventori", item)
        if item not in hasil:
            hasil.append(item)
    return hasil


def _validasi_terpasang(terpasang):
    if not isinstance(terpasang, dict) or len(terpasang) > 6:
        raise GalatAkun(
            "progres_tidak_valid",
            "Terpasang harus objek maksimal 6 slot.",
            400,
        )
    hasil = {}
    for slot, item in terpasang.items():
        if slot not in SLOT_TERPASANG:
            raise GalatAkun(
                "progres_tidak_valid",
                f"Slot terpasang tidak dikenal: {slot}.",
                400,
            )
        if item is not None:
            _validasi_id_item("Id item terpasang", item)
        hasil[slot] = item
    return hasil


def _baca_preferensi(conn, akun_id):
    """preferensi_json pengaturan sebagai dict (rusak/kosong -> {})."""
    baris = conn.execute(
        "SELECT preferensi_json FROM pengaturan WHERE akun_id = ?", (akun_id,)
    ).fetchone()
    if baris is None or not baris["preferensi_json"]:
        return {}
    try:
        data = json.loads(baris["preferensi_json"])
    except (ValueError, TypeError):
        return {}
    return data if isinstance(data, dict) else {}


def baca_progres(conn, akun_id):
    """Baca seluruh progres akun untuk dimuat frontend (5.5)."""
    baris = conn.execute(
        "SELECT xp, koin, level, energi, diperbarui_pada FROM progres"
        " WHERE akun_id = ?",
        (akun_id,),
    ).fetchone()
    if baris is None:
        return {
            "xp": 0,
            "koin": 0,
            "level": 1,
            "energi": 100,
            "diperbarui_pada": None,
            "chat": [],
            "hint": {},
            "inventori": [],
            "terpasang": {},
        }
    chat = [
        {
            "karakter": r["karakter"],
            "pengirim": r["pengirim"],
            "isi": r["isi"],
            "dibuat_pada": r["dibuat_pada"],
            "dibaca": bool(r["dibaca"]),
        }
        for r in conn.execute(
            "SELECT karakter, pengirim, isi, dibuat_pada, dibaca"
            " FROM pesan_chat WHERE akun_id = ? ORDER BY id",
            (akun_id,),
        )
    ]
    inventori = [
        r["item_id"]
        for r in conn.execute(
            "SELECT item_id FROM inventori WHERE akun_id = ?"
            " ORDER BY rowid",
            (akun_id,),
        )
    ]
    terpasang = {
        r["slot"]: r["item_id"]
        for r in conn.execute(
            "SELECT slot, item_id FROM terpasang WHERE akun_id = ?",
            (akun_id,),
        )
        if r["item_id"] is not None
    }
    hint = _baca_preferensi(conn, akun_id).get("hint", {})
    return {
        "xp": baris["xp"],
        "koin": baris["koin"],
        "level": baris["level"],
        "energi": baris["energi"],
        "diperbarui_pada": baris["diperbarui_pada"],
        "chat": chat,
        "hint": hint if isinstance(hint, dict) else {},
        "inventori": inventori,
        "terpasang": terpasang,
    }


def simpan_progres(conn, akun_id, xp, koin, chat, hint, inventori, terpasang):
    """Simpan seluruh progres akun — tulis-terakhir-menang (5.5).

    Satu transaksi: progres + pesan_chat + hint (pengaturan) +
    inventori + terpasang. Status tugas lama sengaja tidak ikut
    (diputuskan Wibi 28 Nov 2026; diganti tugas harian di Fase 7).
    Terpasang tidak dicek ke inventori di sini — daftar kepemilikan
    belum dilacak frontend (semua item Toko dimiliki bawaan);
    dicek saat pembelian ada (Fase 8).
    """
    _validasi_nilai_progres("XP", xp)
    _validasi_nilai_progres("Koin", koin)
    if not isinstance(chat, list) or len(chat) > 500:
        raise GalatAkun(
            "progres_tidak_valid", "Chat progres maksimal 500 butir.", 400
        )
    butir_chat = [_validasi_butir_chat_progres(b) for b in chat]
    hint_bersih = _validasi_hint_progres(hint)
    inventori_bersih = _validasi_inventori(inventori)
    terpasang_bersih = _validasi_terpasang(terpasang)
    sekarang = _iso(_sekarang())
    level = hitung_level(xp)
    try:
        baris = conn.execute(
            "SELECT akun_id FROM progres WHERE akun_id = ?", (akun_id,)
        ).fetchone()
        if baris is None:
            conn.execute(
                "INSERT INTO progres (akun_id, xp, koin, level, energi,"
                " energi_dihitung_pada, streak_absen, terakhir_absen,"
                " diperbarui_pada)"
                " VALUES (?, ?, ?, ?, 100, ?, 0, NULL, ?)",
                (akun_id, xp, koin, level, sekarang, sekarang),
            )
        else:
            conn.execute(
                "UPDATE progres SET xp = ?, koin = ?, level = ?,"
                " diperbarui_pada = ? WHERE akun_id = ?",
                (xp, koin, level, sekarang, akun_id),
            )
        conn.execute("DELETE FROM pesan_chat WHERE akun_id = ?", (akun_id,))
        for b in butir_chat:
            conn.execute(
                "INSERT INTO pesan_chat (akun_id, karakter, pengirim, isi,"
                " dibuat_pada, dibaca) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    akun_id,
                    b["karakter"],
                    b["pengirim"],
                    b["isi"],
                    b["dibuat_pada"],
                    b["dibaca"],
                ),
            )
        preferensi = _baca_preferensi(conn, akun_id)
        preferensi["hint"] = hint_bersih
        ada_pengaturan = conn.execute(
            "SELECT akun_id FROM pengaturan WHERE akun_id = ?", (akun_id,)
        ).fetchone()
        if ada_pengaturan is None:
            conn.execute(
                "INSERT INTO pengaturan (akun_id, tema, preferensi_json)"
                " VALUES (?, NULL, ?)",
                (akun_id, json.dumps(preferensi, ensure_ascii=False)),
            )
        else:
            conn.execute(
                "UPDATE pengaturan SET preferensi_json = ? WHERE akun_id = ?",
                (json.dumps(preferensi, ensure_ascii=False), akun_id),
            )
        conn.execute("DELETE FROM inventori WHERE akun_id = ?", (akun_id,))
        for item in inventori_bersih:
            conn.execute(
                "INSERT INTO inventori (akun_id, item_id, diperoleh_pada,"
                " sumber) VALUES (?, ?, ?, 'toko')",
                (akun_id, item, sekarang),
            )
        conn.execute("DELETE FROM terpasang WHERE akun_id = ?", (akun_id,))
        for slot, item in terpasang_bersih.items():
            if item is None:
                continue
            conn.execute(
                "INSERT INTO terpasang (akun_id, slot, item_id)"
                " VALUES (?, ?, ?)",
                (akun_id, slot, item),
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return baca_progres(conn, akun_id)
