"""Layanan akun Office Quest (Fase 5.2).

- Kata sandi: hash argon2id (argon2-cffi), tidak pernah teks biasa.
- Sesi: token acak 32 byte; yang disimpan hanya hash SHA-256 + kedaluwarsa
  (30 hari, diputuskan Wibi 27 Nov 2026).
- Semua fungsi menerima koneksi SQLite; HTTPException dilempar di main.py.
- Pesan galat masuk sengaja sama untuk nama tak dikenal dan kata sandi
  salah (tidak membocorkan akun mana yang ada).
"""

import hashlib
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
