"""Tes progres tersimpan di server (Fase 5.5)."""

import sqlite3

import pytest
from fastapi.testclient import TestClient

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


def _simpan(klien, token, badan=None):
    dasar = {
        "xp": 0,
        "koin": 0,
        "chat": [],
        "hint": {},
        "inventori": [],
        "terpasang": {},
    }
    if badan:
        dasar.update(badan)
    return klien.post("/akun/progres", json=dasar, headers=_kepala(token))


def _baca(klien, token):
    return klien.get("/akun/progres", headers=_kepala(token))


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


def _progres_lengkap():
    return {
        "xp": 800,
        "koin": 1500,
        "chat": _chat_contoh(),
        "hint": {"rekap_penjualan": {"rina": 2}},
        "inventori": ["topi_jerami", "set_meja_1"],
        "terpasang": {"kepala": "topi_jerami", "meja": "set_meja_1"},
    }


def _baris(jalur_db, tabel, akun_id=1):
    conn = sqlite3.connect(jalur_db)
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute(
            f"SELECT * FROM {tabel} WHERE akun_id = ?", (akun_id,)
        ).fetchall()
    finally:
        conn.close()


def test_baca_progres_akun_baru(klien):
    token = _daftar(klien).json()["token"]
    jawaban = _baca(klien, token)
    assert jawaban.status_code == 200
    progres = jawaban.json()["progres"]
    assert progres["xp"] == 0
    assert progres["koin"] == 0
    assert progres["level"] == 1
    assert progres["energi"] == 100
    assert isinstance(progres["diperbarui_pada"], str)
    assert progres["chat"] == []
    assert progres["hint"] == {}
    assert progres["inventori"] == []
    assert progres["terpasang"] == {}


def test_simpan_dan_baca_bulat(klien, jalur_db):
    token = _daftar(klien).json()["token"]
    jawaban = _simpan(klien, token, _progres_lengkap())
    assert jawaban.status_code == 200
    progres = jawaban.json()["progres"]
    assert progres["xp"] == 800
    assert progres["koin"] == 1500
    assert progres["level"] == 4
    assert progres["energi"] == 100
    assert len(progres["chat"]) == 2
    assert progres["chat"][0]["isi"] == "Selamat pagi, ada tugas baru."
    assert progres["chat"][0]["dibaca"] is True
    assert progres["chat"][1]["dibaca"] is False
    assert progres["hint"] == {"rekap_penjualan": {"rina": 2}}
    assert progres["inventori"] == ["topi_jerami", "set_meja_1"]
    assert progres["terpasang"] == {"kepala": "topi_jerami", "meja": "set_meja_1"}
    # Beda dengan migrasi: baca ulang mengembalikan yang sama persis.
    assert _baca(klien, token).json()["progres"] == progres
    # Baris DB: 2 pesan, 2 inventori, 2 terpasang, hint di pengaturan.
    assert len(_baris(jalur_db, "pesan_chat")) == 2
    assert len(_baris(jalur_db, "inventori")) == 2
    assert len(_baris(jalur_db, "terpasang")) == 2
    pengaturan = _baris(jalur_db, "pengaturan")
    assert len(pengaturan) == 1
    assert '"rina": 2' in pengaturan[0]["preferensi_json"]


@pytest.mark.parametrize("xp,level", [(0, 1), (250, 2), (1000, 4)])
def test_simpan_level(klien, xp, level):
    token = _daftar(klien).json()["token"]
    jawaban = _simpan(klien, token, {"xp": xp, "koin": 0})
    assert jawaban.status_code == 200
    assert jawaban.json()["progres"]["level"] == level


def test_simpan_menimpa(klien, jalur_db):
    token = _daftar(klien).json()["token"]
    assert _simpan(klien, token, _progres_lengkap()).status_code == 200
    jawaban = _simpan(
        klien,
        token,
        {
            "xp": 300,
            "koin": 100,
            "chat": [],
            "hint": {},
            "inventori": [],
            "terpasang": {},
        },
    )
    assert jawaban.status_code == 200
    progres = jawaban.json()["progres"]
    assert progres["xp"] == 300
    assert progres["level"] == 2
    assert progres["chat"] == []
    assert progres["hint"] == {}
    assert progres["inventori"] == []
    assert progres["terpasang"] == {}
    # Tidak ada sisa baris dari simpanan pertama.
    assert len(_baris(jalur_db, "pesan_chat")) == 0
    assert len(_baris(jalur_db, "inventori")) == 0
    assert len(_baris(jalur_db, "terpasang")) == 0


def test_simpan_tanpa_token_dan_token_palsu(klien):
    assert _baca(klien, None).status_code == 401
    assert _baca(klien, "palsu").status_code == 401
    assert _simpan(klien, None, _progres_lengkap()).status_code == 401
    assert _simpan(klien, "palsu", _progres_lengkap()).status_code == 401
    for jawaban in (
        _baca(klien, None),
        _baca(klien, "palsu"),
        _simpan(klien, None, _progres_lengkap()),
    ):
        assert jawaban.json()["detail"]["kode"] == "belum_masuk"


def test_simpan_tidak_valid(klien, jalur_db):
    token = _daftar(klien).json()["token"]
    buruk = [
        {"xp": -1},
        {"koin": 10_000_001},
        {"chat": [{}] * 501},
        {"chat": [{**_chat_contoh()[0], "isi": "x" * 2001}]},
        {"hint": {"rekap_penjualan": {"rina": 4}}},
        {"hint": {"rekap_penjualan": {"rina": True}}},
        {"inventori": [""]},
        {"inventori": ["a"] * 201},
        {"terpasang": {"topi": "topi_jerami"}},
        {"terpasang": {"kepala": ""}},
        {"terpasang": {"kepala": "x", "wajah": "y", "baju": "z", "celana": "w", "sepatu": "v", "meja": "u", "lebih": "t"}},
    ]
    for badan in buruk:
        jawaban = _simpan(klien, token, badan)
        assert jawaban.status_code == 400, badan
        assert jawaban.json()["detail"]["kode"] == "progres_tidak_valid", badan
    # Tipe salah -> 422 bawaan FastAPI, DB tetap baru.
    for badan in (
        {"xp": "banyak"},
        {"chat": "bukan-list"},
        {"hint": []},
        {"inventori": "topi_jerami"},
        {"terpasang": []},
    ):
        jawaban = _simpan(klien, token, badan)
        assert jawaban.status_code == 422, badan
    assert _baca(klien, token).json()["progres"]["xp"] == 0
    assert len(_baris(jalur_db, "pesan_chat")) == 0


def test_simpan_hint_kosong_dan_terpasang_null(klien):
    token = _daftar(klien).json()["token"]
    jawaban = _simpan(
        klien,
        token,
        {"xp": 0, "koin": 0, "hint": {}, "terpasang": {"kepala": None}},
    )
    assert jawaban.status_code == 200
    progres = jawaban.json()["progres"]
    assert progres["hint"] == {}
    assert progres["terpasang"] == {}
