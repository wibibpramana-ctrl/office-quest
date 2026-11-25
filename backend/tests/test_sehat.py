"""Tes kerangka layanan: endpoint /sehat mengembalikan ok."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_sehat_mengembalikan_ok():
    jawaban = client.get("/sehat")
    assert jawaban.status_code == 200
    assert jawaban.json() == {"status": "ok"}
