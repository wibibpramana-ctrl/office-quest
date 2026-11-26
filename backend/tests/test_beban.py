"""Tes beban (3.8): file 2 MB diperiksa di bawah 5 detik, dan
20 permintaan beruntun tanpa galat.

File besar (~1,8 MB, 60.002 sel) dibuat sekali per sesi tes.
"""

import io
import random
import string
import time

import pytest
from fastapi.testclient import TestClient
from openpyxl import Workbook

from app.main import buat_app

GARAM_TES = "garam-beban-3-8"
JUMLAH_SEL_BESAR = 60_000


@pytest.fixture(scope="module")
def klien():
    return TestClient(buat_app(garam=GARAM_TES))


@pytest.fixture(scope="module")
def tiket(klien):
    resp = klien.post("/tugas/tiket", json={"jenis": "rekap_penjualan", "benih": "benih-beban"})
    assert resp.status_code == 200
    return resp.json()["tiket"]


@pytest.fixture(scope="module")
def file_besar():
    rng = random.Random(42)
    alfabet = string.ascii_letters + string.digits
    wb = Workbook()
    ws = wb.active
    ws.title = "Data"
    ws["A1"] = "Produk"
    ws["A2"] = "Kopi Bubuk"
    ws2 = wb.create_sheet("DataBesar")
    for i in range(JUMLAH_SEL_BESAR):
        ws2.cell(row=i + 1, column=1, value="".join(rng.choice(alfabet) for _ in range(30)))
    buf = io.BytesIO()
    wb.save(buf)
    data = buf.getvalue()
    assert 1_500_000 < len(data) < 2_000_000, len(data)
    return data


def test_file_2mb_di_bawah_5_detik(klien, tiket, file_besar):
    t0 = time.monotonic()
    resp = klien.post("/periksa", data={"tiket": tiket}, files={"file": ("jawaban.xlsx", file_besar)})
    durasi = time.monotonic() - t0
    assert resp.status_code == 200, resp.text
    assert durasi < 5, f"periksa file 2 MB butuh {durasi:.2f} detik"


def test_20_permintaan_beruntun_tanpa_galat(klien, tiket):
    template = klien.get("/tugas/template", params={"tiket": tiket}).content
    assert template
    for i in range(20):
        resp = klien.post("/periksa", data={"tiket": tiket}, files={"file": ("jawaban.xlsx", template)})
        assert resp.status_code == 200, f"permintaan ke-{i + 1}: {resp.status_code} {resp.text}"
