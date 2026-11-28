"""Tes hasil wawancara tersimpan di server (Fase 5.6)."""

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


def _skor(benar=4):
    return {
        "benar": benar,
        "total": 5,
        "jawaban": {"w1": 1, "w2": 0, "w3": 2, "w4": 0, "w5": 1},
        "tingkat": "menengah",
    }


def test_tanpa_token_401(klien):
    assert klien.get("/akun/wawancara").status_code == 401
    assert (
        klien.post("/akun/wawancara", json={"skor": _skor()}).status_code == 401
    )


def test_baca_sebelum_ada_none(klien):
    token = _daftar(klien).json()["token"]
    r = klien.get("/akun/wawancara", headers=_kepala(token))
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "wawancara": None}


def test_simpan_lalu_baca(klien):
    token = _daftar(klien).json()["token"]
    r = klien.post(
        "/akun/wawancara", json={"skor": _skor(4)}, headers=_kepala(token)
    )
    assert r.status_code == 200
    isi = r.json()["wawancara"]
    assert isi["skor"] == _skor(4)
    assert isi["dilewati"] is False
    assert isi["selesai_pada"]
    r = klien.get("/akun/wawancara", headers=_kepala(token))
    assert r.json()["wawancara"]["skor"]["benar"] == 4


def test_lewati(klien):
    token = _daftar(klien).json()["token"]
    r = klien.post(
        "/akun/wawancara", json={"dilewati": True}, headers=_kepala(token)
    )
    assert r.status_code == 200
    assert r.json()["wawancara"]["dilewati"] is True
    assert r.json()["wawancara"]["skor"] == {}


def test_skor_tidak_valid_400(klien):
    token = _daftar(klien).json()["token"]
    # benar lebih besar dari total.
    r = klien.post(
        "/akun/wawancara",
        json={"skor": {"benar": 6, "total": 5}},
        headers=_kepala(token),
    )
    assert r.status_code == 400
    # benar bukan angka.
    r = klien.post(
        "/akun/wawancara",
        json={"skor": {"benar": "empat", "total": 5}},
        headers=_kepala(token),
    )
    assert r.status_code == 400


def test_skor_bukan_objek_422(klien):
    token = _daftar(klien).json()["token"]
    r = klien.post(
        "/akun/wawancara", json={"skor": "bagus"}, headers=_kepala(token)
    )
    assert r.status_code == 422


def test_simpan_dua_kali_nilai_terakhir(klien):
    token = _daftar(klien).json()["token"]
    klien.post("/akun/wawancara", json={"skor": _skor(2)}, headers=_kepala(token))
    r = klien.post(
        "/akun/wawancara", json={"skor": _skor(5)}, headers=_kepala(token)
    )
    assert r.json()["wawancara"]["skor"]["benar"] == 5
    r = klien.get("/akun/wawancara", headers=_kepala(token))
    assert r.json()["wawancara"]["skor"]["benar"] == 5


def test_akun_lain_tidak_terlihat(klien):
    token1 = _daftar(klien, "wibi").json()["token"]
    token2 = _daftar(klien, "rina").json()["token"]
    klien.post("/akun/wawancara", json={"skor": _skor(5)}, headers=_kepala(token1))
    r = klien.get("/akun/wawancara", headers=_kepala(token2))
    assert r.json() == {"status": "ok", "wawancara": None}
