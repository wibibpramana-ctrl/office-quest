"""Tes layanan akun (Fase 5.2): daftar, masuk, keluar, sesi, ganti kata sandi."""

import hashlib
import sqlite3
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.main import buat_app
from app.tiket import WIB


@pytest.fixture
def jalur_db(tmp_path, monkeypatch):
    jalur = tmp_path / "uji.db"
    monkeypatch.setenv("OFFICE_QUEST_DB", str(jalur))
    return jalur


@pytest.fixture
def klien(jalur_db):
    with TestClient(buat_app(garam="garam-uji")) as c:
        yield c


def _daftar(klien, nama="wibi", sandi="rahasia123", **tambahan):
    data = {"nama_akun": nama, "kata_sandi": sandi}
    data.update(tambahan)
    return klien.post("/akun/daftar", json=data)


def test_daftar_lalu_saya(klien):
    jawaban = _daftar(klien, nama_panggilan="Wibi", email="wibi@contoh.id")
    assert jawaban.status_code == 201
    isi = jawaban.json()
    assert isi["nama_akun"] == "wibi"
    assert isi["nama_panggilan"] == "Wibi"
    assert "token" in isi and isi["token"]
    assert "hash_kata_sandi" not in isi
    saya = klien.get("/akun/saya", headers={"Authorization": f"Bearer {isi['token']}"})
    assert saya.status_code == 200
    assert saya.json()["nama_akun"] == "wibi"
    assert saya.json()["email"] == "wibi@contoh.id"


def test_daftar_nama_duplikat_ditolak(klien):
    assert _daftar(klien).status_code == 201
    jawaban = _daftar(klien)
    assert jawaban.status_code == 409
    assert jawaban.json()["detail"]["kode"] == "nama_sudah_dipakai"


def test_daftar_nama_tidak_valid(klien):
    assert _daftar(klien, nama="ab").status_code == 400
    assert _daftar(klien, nama="1wibi").status_code == 400
    assert _daftar(klien, nama="wibi saya").status_code == 400


def test_daftar_kata_sandi_pendek_ditolak(klien):
    jawaban = _daftar(klien, sandi="pendek")
    assert jawaban.status_code == 400
    assert jawaban.json()["detail"]["kode"] == "kata_sandi_tidak_valid"


def test_daftar_email_tidak_valid_dan_duplikat(klien):
    jawaban = _daftar(klien, email="bukan-email")
    assert jawaban.status_code == 400
    assert jawaban.json()["detail"]["kode"] == "email_tidak_valid"
    assert _daftar(klien, email="wibi@contoh.id").status_code == 201
    jawaban = _daftar(klien, nama="wibi2", email="wibi@contoh.id")
    assert jawaban.status_code == 409
    assert jawaban.json()["detail"]["kode"] == "email_sudah_dipakai"


def test_masuk_berhasil_dan_salah(klien):
    _daftar(klien)
    jawaban = klien.post("/akun/masuk", json={"nama_akun": "wibi", "kata_sandi": "rahasia123"})
    assert jawaban.status_code == 200
    assert jawaban.json()["token"]
    assert jawaban.json()["akun"]["nama_akun"] == "wibi"
    salah = klien.post("/akun/masuk", json={"nama_akun": "wibi", "kata_sandi": "salah1234"})
    assert salah.status_code == 401
    assert salah.json()["detail"]["kode"] == "kredensial_salah"
    tak_ada = klien.post("/akun/masuk", json={"nama_akun": "tidakada", "kata_sandi": "salah1234"})
    assert tak_ada.status_code == 401
    assert tak_ada.json()["detail"]["kode"] == "kredensial_salah"


def test_saya_tanpa_token_dan_token_asal_ditolak(klien):
    _daftar(klien)
    assert klien.get("/akun/saya").status_code == 401
    jawaban = klien.get("/akun/saya", headers={"Authorization": "Bearer token-asal"})
    assert jawaban.status_code == 401
    assert jawaban.json()["detail"]["kode"] == "belum_masuk"


def test_keluar_menghapus_sesi(klien):
    token = _daftar(klien).json()["token"]
    kepala = {"Authorization": f"Bearer {token}"}
    assert klien.post("/akun/keluar", headers=kepala).status_code == 200
    jawaban = klien.get("/akun/saya", headers=kepala)
    assert jawaban.status_code == 401


def test_ganti_kata_sandi(klien):
    token_a = _daftar(klien).json()["token"]
    token_b = klien.post(
        "/akun/masuk", json={"nama_akun": "wibi", "kata_sandi": "rahasia123"}
    ).json()["token"]
    kepala_a = {"Authorization": f"Bearer {token_a}"}
    jawaban = klien.post(
        "/akun/ganti-kata-sandi",
        json={"kata_sandi_lama": "rahasia123", "kata_sandi_baru": "baru45678"},
        headers=kepala_a,
    )
    assert jawaban.status_code == 200
    # Kata sandi lama tidak berlaku lagi, yang baru berlaku.
    assert klien.post(
        "/akun/masuk", json={"nama_akun": "wibi", "kata_sandi": "rahasia123"}
    ).status_code == 401
    assert klien.post(
        "/akun/masuk", json={"nama_akun": "wibi", "kata_sandi": "baru45678"}
    ).status_code == 200
    # Sesi lain ikut keluar, sesi sendiri tetap jalan.
    assert klien.get("/akun/saya", headers={"Authorization": f"Bearer {token_b}"}).status_code == 401
    assert klien.get("/akun/saya", headers=kepala_a).status_code == 200
    # Kata sandi lama yang salah ditolak.
    jawaban = klien.post(
        "/akun/ganti-kata-sandi",
        json={"kata_sandi_lama": "keliru123", "kata_sandi_baru": "lain78901"},
        headers=kepala_a,
    )
    assert jawaban.status_code == 401
    assert jawaban.json()["detail"]["kode"] == "kredensial_salah"


def test_sesi_kedaluwarsa_ditolak(klien, jalur_db):
    isi = _daftar(klien).json()
    token = "token-kedaluwarsa"
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    lampau = (datetime.now(WIB) - timedelta(days=1)).isoformat()
    conn = sqlite3.connect(str(jalur_db))
    conn.execute(
        "INSERT INTO sesi (akun_id, token_hash, dibuat_pada, kedaluwarsa_pada)"
        " VALUES (?, ?, ?, ?)",
        (isi["id"], token_hash, lampau, lampau),
    )
    conn.commit()
    conn.close()
    jawaban = klien.get("/akun/saya", headers={"Authorization": f"Bearer {token}"})
    assert jawaban.status_code == 401
    assert jawaban.json()["detail"]["kode"] == "sesi_kedaluwarsa"


def test_isolasi_antar_akun(klien):
    token_a = _daftar(klien, nama="wibi").json()["token"]
    _daftar(klien, nama="rina", sandi="rahasia123")
    jawaban = klien.get("/akun/saya", headers={"Authorization": f"Bearer {token_a}"})
    assert jawaban.status_code == 200
    assert jawaban.json()["nama_akun"] == "wibi"


def test_pembatas_laju_akun(klien):
    _daftar(klien)
    jawaban = None
    for _ in range(31):
        jawaban = klien.post(
            "/akun/masuk", json={"nama_akun": "wibi", "kata_sandi": "salah1234"}
        )
    assert jawaban.status_code == 429


def test_tanpa_db_503(monkeypatch):
    monkeypatch.delenv("OFFICE_QUEST_DB", raising=False)
    with TestClient(buat_app(garam="garam-uji")) as c:
        jawaban = c.post(
            "/akun/daftar", json={"nama_akun": "wibi", "kata_sandi": "rahasia123"}
        )
    assert jawaban.status_code == 503
    assert jawaban.json()["detail"]["kode"] == "basis_data_belum_diatur"
