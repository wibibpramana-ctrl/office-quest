"""Tes ujung ke ujung API (3.7): tiket -> template -> periksa,
plus kode galat 400/403/410/413/415/429, CORS hanya Pages,
dan log tanpa isi file.
"""

import io
import logging
from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient
from openpyxl import Workbook, load_workbook

from app.main import buat_app
from app.tiket import data_untuk_tiket, periksa_tiket, terbitkan_tiket

GARAM_TES = "garam-tes-3-7"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _klien(batas_laju=30):
    return TestClient(buat_app(garam=GARAM_TES, batas_laju_per_menit=batas_laju))


def _minta_tiket(klien, jenis="rekap_penjualan", **extra):
    resp = klien.post("/tugas/tiket", json={"jenis": jenis, **extra})
    assert resp.status_code == 200, resp.text
    return resp.json()


def _bangun_jawaban_manual(tugas, aoa):
    """File jawaban berisi nilai saja (tanpa rumus) dari AOA data tiket."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Data"
    for r, baris in enumerate(aoa, start=1):
        for c, nilai in enumerate(baris, start=1):
            if nilai is not None:
                ws.cell(row=r, column=c, value=nilai)
    if tugas == "rekap_penjualan":
        total = []
        for r in range(2, 12):
            nilai = aoa[r - 1][1] * aoa[r - 1][2]
            ws.cell(row=r, column=4, value=nilai)
            total.append(nilai)
        ws.cell(row=12, column=4, value=sum(total))
        ws.cell(row=13, column=4, value=sum(total) / len(total))
    elif tugas == "absensi":
        for r in range(2, 12):
            for ci, kriteria in enumerate(["H", "I", "A"]):
                ws.cell(row=r, column=7 + ci, value=sum(1 for v in aoa[r - 1][1:6] if v == kriteria))
        for ci in range(3):
            ws.cell(row=12, column=7 + ci, value=sum(ws.cell(row=r, column=7 + ci).value for r in range(2, 12)))
    elif tugas == "penilaian_magang":
        for r in range(2, 12):
            rata = (aoa[r - 1][1] + aoa[r - 1][2]) / 2
            ws.cell(row=r, column=4, value=rata)
            ws.cell(row=r, column=5, value="Lulus" if rata >= 75 else "Remedial")
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _periksa(klien, tiket, data, nama="jawaban.xlsx"):
    return klien.post("/periksa", data={"tiket": tiket}, files={"file": (nama, data)})


def test_sehat():
    assert _klien().get("/sehat").json() == {"status": "ok"}


def test_tiket_parameter_brief():
    hasil = _minta_tiket(_klien(), "rekap_penjualan", id_pemain="pemain-1")
    assert hasil["jenis"] == "rekap_penjualan"
    assert hasil["tier"] == 1
    assert hasil["kedaluwarsa"]
    assert hasil["parameter_brief"] == {"jumlah": 10, "deadline": "Kirim sebelum jam 5"}
    hasil2 = _minta_tiket(_klien(), "absensi")
    assert hasil2["parameter_brief"] == {"jumlah": 10, "deadline": None}


def test_tiket_pemain_sama_hari_sama_data_sama():
    klien = _klien()
    t1 = _minta_tiket(klien, "absensi", id_pemain="pemain-7")
    t2 = _minta_tiket(klien, "absensi", id_pemain="pemain-7")
    m1 = periksa_tiket(t1["tiket"], GARAM_TES)
    m2 = periksa_tiket(t2["tiket"], GARAM_TES)
    assert m1["benih"] == m2["benih"]
    assert data_untuk_tiket(m1, GARAM_TES) == data_untuk_tiket(m2, GARAM_TES)


def test_tiket_jenis_tidak_dikenal_400():
    resp = _klien().post("/tugas/tiket", json={"jenis": "tugas_asing"})
    assert resp.status_code == 400


def test_template_ujung_ke_ujung():
    klien = _klien()
    hasil = _minta_tiket(klien, "rekap_penjualan", benih="benih-e2e")
    resp = klien.get("/tugas/template", params={"tiket": hasil["tiket"]})
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert "Template Rekap Penjualan Mingguan.xlsx" in resp.headers["content-disposition"]
    wb = load_workbook(io.BytesIO(resp.content), data_only=True)
    assert wb.sheetnames == ["Data"]
    ws = wb["Data"]
    assert ws.max_row == 13
    muatan = periksa_tiket(hasil["tiket"], GARAM_TES)
    aoa = data_untuk_tiket(muatan, GARAM_TES)
    assert ws.cell(row=2, column=1).value == aoa[1][0]
    assert ws.cell(row=2, column=2).value == aoa[1][1]


def test_template_tiket_palsu_403_dan_kedaluwarsa_410():
    klien = _klien()
    hasil = _minta_tiket(klien, "absensi")
    palsu = hasil["tiket"][:-1] + ("A" if hasil["tiket"][-1] != "A" else "B")
    assert klien.get("/tugas/template", params={"tiket": palsu}).status_code == 403
    kemarin = datetime(2026, 11, 25, 3, 0, 0, tzinfo=timezone.utc)
    lama = terbitkan_tiket("absensi", GARAM_TES, sekarang=kemarin)
    assert klien.get("/tugas/template", params={"tiket": lama}).status_code == 410


def test_periksa_manual_70_ketiga_tugas():
    klien = _klien()
    for tugas in ("rekap_penjualan", "absensi", "penilaian_magang"):
        hasil = _minta_tiket(klien, tugas, benih=f"benih-{tugas}")
        muatan = periksa_tiket(hasil["tiket"], GARAM_TES)
        data = _bangun_jawaban_manual(tugas, data_untuk_tiket(muatan, GARAM_TES))
        resp = _periksa(klien, hasil["tiket"], data)
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["skor"] == 70, (tugas, body)
        assert body["lulus"] is True
        assert body["kode"] == ["hard"]
        assert body["batas_waktu"] == "ok"


def test_periksa_template_kosong_skor_5():
    klien = _klien()
    hasil = _minta_tiket(klien, "rekap_penjualan", benih="benih-kosong")
    template = klien.get("/tugas/template", params={"tiket": hasil["tiket"]}).content
    resp = _periksa(klien, hasil["tiket"], template)
    assert resp.status_code == 200
    assert resp.json()["skor"] == 5
    assert resp.json()["kode"] == []


def test_periksa_fixture_seed_publik_ditolak_altered():
    # Jawaban untuk seed publik TIDAK cocok dengan data dari tiket bergaram.
    klien = _klien()
    hasil = _minta_tiket(klien, "rekap_penjualan", benih="benih-lain")
    data = (FIXTURES / "uji-rekap_penjualan-benar.xlsx").read_bytes()
    resp = _periksa(klien, hasil["tiket"], data)
    assert resp.status_code == 200
    body = resp.json()
    assert body["skor"] < 70
    assert "altered" in body["kode"]


def test_periksa_tiket_palsu_403_dan_kedaluwarsa_410():
    klien = _klien()
    hasil = _minta_tiket(klien, "rekap_penjualan")
    data = (FIXTURES / "uji-rekap_penjualan-benar.xlsx").read_bytes()
    palsu = hasil["tiket"][:-1] + ("A" if hasil["tiket"][-1] != "A" else "B")
    assert _periksa(klien, palsu, data).status_code == 403
    kemarin = datetime(2026, 11, 25, 3, 0, 0, tzinfo=timezone.utc)
    lama = terbitkan_tiket("rekap_penjualan", GARAM_TES, sekarang=kemarin)
    assert _periksa(klien, lama, data).status_code == 410


def test_periksa_bukan_xlsx_415_dan_file_besar_413():
    klien = _klien()
    hasil = _minta_tiket(klien, "absensi")
    resp = _periksa(klien, hasil["tiket"], b"halo ini teks", "jawaban.xlsx")
    assert resp.status_code == 415
    assert resp.json()["detail"]["kode"] == "bukan_arsip_valid"
    besar = (FIXTURES / "uji-absensi-benar.xlsx").read_bytes() + b"\0" * (2 * 1024 * 1024 + 1)
    resp = _periksa(klien, hasil["tiket"], besar, "jawaban.xlsx")
    assert resp.status_code == 413
    assert resp.json()["detail"]["kode"] == "file_terlalu_besar"


def test_cors_hanya_pages():
    klien = _klien()
    resp = klien.get("/sehat", headers={"Origin": "https://wibibpramana-ctrl.github.io"})
    assert resp.headers.get("access-control-allow-origin") == "https://wibibpramana-ctrl.github.io"
    resp = klien.get("/sehat", headers={"Origin": "https://evil.example"})
    assert "access-control-allow-origin" not in resp.headers


def test_pembatas_laju_429():
    klien = _klien(batas_laju=3)
    for _ in range(3):
        assert klien.post("/tugas/tiket", json={"jenis": "absensi"}).status_code == 200
    resp = klien.post("/tugas/tiket", json={"jenis": "absensi"})
    assert resp.status_code == 429
    assert resp.json()["kode"] == "terlalu_sering"


def test_log_tanpa_isi_file_dan_tiket(caplog):
    klien = _klien()
    hasil = _minta_tiket(klien, "rekap_penjualan")
    with caplog.at_level(logging.INFO, logger="office_quest"):
        resp = _periksa(klien, hasil["tiket"], b"RAHASIA-ISI-FILE-987", "jawaban.xlsx")
        assert resp.status_code == 415
        data = (FIXTURES / "uji-rekap_penjualan-benar.xlsx").read_bytes()
        resp = _periksa(klien, hasil["tiket"], data)
        assert resp.status_code == 200
    assert "RAHASIA-ISI-FILE-987" not in caplog.text
    assert hasil["tiket"] not in caplog.text


def test_garam_belum_diatur_503(monkeypatch):
    monkeypatch.delenv("OFFICE_QUEST_GARAM", raising=False)
    klien = TestClient(buat_app(garam=None))
    resp = klien.post("/tugas/tiket", json={"jenis": "absensi"})
    assert resp.status_code == 503
    assert resp.json()["detail"]["kode"] == "garam_belum_diatur"
