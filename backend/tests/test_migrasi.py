"""Tes migrasi progres lokal ke akun (Fase 5.4)."""

import sqlite3

import pytest
from fastapi.testclient import TestClient

from app.akun import hitung_level
from app.main import buat_app


@pytest.fixture
def jalur_db(tmp_path, monkeypatch):
    jalur = tmp_path / "uji.db"
    monkeypatch.setenv("OFFICE_QUEST_DB", str(jalur))
    return jalur


@pytest.fixture
def klien(jalur_db):
    with TestClient(buat_app(garam="garam-uji")) as c:
        yield c


def _daftar(klien, nama="wibi", sandi="rahasia123"):
    return klien.post("/akun/daftar", json={"nama_akun": nama, "kata_sandi": sandi})


def _kepala(token):
    return {"Authorization": f"Bearer {token}"} if token else {}


def _migrasi(klien, token, xp=0, koin=0, chat=None):
    return klien.post(
        "/akun/migrasi",
        json={"xp": xp, "koin": koin, "chat": chat if chat is not None else []},
        headers=_kepala(token),
    )


def _chat_contoh():
    return [
        {
            "karakter": "bima",
            "pengirim": "bima",
            "isi": "Selamat pagi, ada tugas baru.",
            "dibuat_pada": "2026-11-28T08:00:00+07:00",
            "dibaca": True,
        },
        {
            "karakter": "rina",
            "pengirim": "rina",
            "isi": "Semangat ya!",
            "dibuat_pada": "2026-11-28T08:05:00+07:00",
            "dibaca": False,
        },
    ]


def _progres(jalur_db, akun_id):
    conn = sqlite3.connect(str(jalur_db))
    conn.row_factory = sqlite3.Row
    baris = conn.execute(
        "SELECT * FROM progres WHERE akun_id = ?", (akun_id,)
    ).fetchone()
    pesan = conn.execute(
        "SELECT * FROM pesan_chat WHERE akun_id = ? ORDER BY id", (akun_id,)
    ).fetchall()
    conn.close()
    return baris, pesan


def test_hitung_level():
    assert hitung_level(0) == 1
    assert hitung_level(249) == 1
    assert hitung_level(250) == 2
    assert hitung_level(999) == 4
    assert hitung_level(1000) == 4
    assert hitung_level(10_000_000) == 4


def test_migrasi_berhasil_akun_baru(klien, jalur_db):
    isi = _daftar(klien).json()
    jawaban = _migrasi(klien, isi["token"], xp=800, koin=5000, chat=_chat_contoh())
    assert jawaban.status_code == 200
    assert jawaban.json() == {
        "status": "ok",
        "progres": {"xp": 800, "koin": 5000, "level": 4, "pesan_chat": 2},
    }
    baris, pesan = _progres(jalur_db, isi["id"])
    assert (baris["xp"], baris["koin"], baris["level"]) == (800, 5000, 4)
    assert len(pesan) == 2
    assert pesan[0]["karakter"] == "bima"
    assert pesan[0]["pengirim"] == "bima"
    assert pesan[0]["isi"] == "Selamat pagi, ada tugas baru."
    assert pesan[0]["dibaca"] == 1
    assert pesan[1]["karakter"] == "rina"
    assert pesan[1]["isi"] == "Semangat ya!"
    assert pesan[1]["dibaca"] == 0


@pytest.mark.parametrize("xp,level", [(0, 1), (250, 2), (1000, 4)])
def test_migrasi_level(klien, jalur_db, xp, level):
    isi = _daftar(klien).json()
    jawaban = _migrasi(klien, isi["token"], xp=xp)
    assert jawaban.status_code == 200
    assert jawaban.json()["progres"]["level"] == level
    baris, _pesan = _progres(jalur_db, isi["id"])
    assert baris["level"] == level


def test_migrasi_kedua_ditolak_409(klien, jalur_db):
    isi = _daftar(klien).json()
    assert _migrasi(klien, isi["token"], xp=100, koin=200).status_code == 200
    jawaban = _migrasi(klien, isi["token"], xp=500, koin=900, chat=_chat_contoh())
    assert jawaban.status_code == 409
    assert jawaban.json()["detail"]["kode"] == "sudah_punya_progres"
    baris, pesan = _progres(jalur_db, isi["id"])
    assert (baris["xp"], baris["koin"], baris["level"]) == (100, 200, 1)
    assert len(pesan) == 0


def test_migrasi_tanpa_token_dan_token_palsu(klien, jalur_db):
    isi = _daftar(klien).json()
    jawaban = _migrasi(klien, None, xp=100)
    assert jawaban.status_code == 401
    assert jawaban.json()["detail"]["kode"] == "belum_masuk"
    jawaban = _migrasi(klien, "token-asal", xp=100)
    assert jawaban.status_code == 401
    assert jawaban.json()["detail"]["kode"] == "belum_masuk"
    baris, pesan = _progres(jalur_db, isi["id"])
    assert (baris["xp"], baris["koin"], baris["level"]) == (0, 0, 1)
    assert len(pesan) == 0


def test_migrasi_tidak_valid(klien, jalur_db):
    isi = _daftar(klien).json()
    token = isi["token"]

    def tolak(jawaban):
        assert jawaban.status_code == 400
        assert jawaban.json()["detail"]["kode"] == "migrasi_tidak_valid"

    # XP negatif, koin negatif, dan XP di atas batas ditolak layanan.
    tolak(_migrasi(klien, token, xp=-1))
    tolak(_migrasi(klien, token, koin=-5))
    tolak(_migrasi(klien, token, xp=10_000_001))
    # Butir chat tanpa isi ditolak layanan.
    tolak(
        _migrasi(
            klien,
            token,
            chat=[
                {
                    "karakter": "bima",
                    "pengirim": "bima",
                    "dibuat_pada": "2026-11-28T08:00:00+07:00",
                }
            ],
        )
    )
    # Isi lebih dari 2000 karakter ditolak layanan.
    tolak(_migrasi(klien, token, chat=[{**_chat_contoh()[0], "isi": "x" * 2001}]))
    # Chat 501 butir ditolak layanan.
    tolak(_migrasi(klien, token, chat=[_chat_contoh()[0]] * 501))
    # dibuat_pada bukan tanggal ISO ditolak layanan.
    tolak(
        _migrasi(
            klien,
            token,
            chat=[{**_chat_contoh()[0], "dibuat_pada": "kemarin"}],
        )
    )
    # Tipe salah dicegat Pydantic -> 422 bawaan FastAPI (kontrak
    # membolehkan 422 untuk tipe salah); DB tetap tidak tersentuh.
    jawaban = klien.post(
        "/akun/migrasi",
        json={"xp": 0, "koin": "seratus", "chat": []},
        headers=_kepala(token),
    )
    assert jawaban.status_code == 422
    jawaban = klien.post(
        "/akun/migrasi",
        json={"xp": 0, "koin": 0, "chat": "bukan-list"},
        headers=_kepala(token),
    )
    assert jawaban.status_code == 422
    # Progres DB tetap baru.
    baris, pesan = _progres(jalur_db, isi["id"])
    assert (baris["xp"], baris["koin"], baris["level"]) == (0, 0, 1)
    assert len(pesan) == 0


def test_migrasi_chat_kosong(klien, jalur_db):
    isi = _daftar(klien).json()
    jawaban = _migrasi(klien, isi["token"], xp=300, koin=100, chat=[])
    assert jawaban.status_code == 200
    assert jawaban.json()["progres"] == {
        "xp": 300,
        "koin": 100,
        "level": 2,
        "pesan_chat": 0,
    }
    baris, pesan = _progres(jalur_db, isi["id"])
    assert (baris["xp"], baris["koin"], baris["level"]) == (300, 100, 2)
    assert len(pesan) == 0
