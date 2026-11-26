"""Tes validasi unggahan (3.5): file besar, .xlsm, teks bernama .xlsx,
zip bukan xlsx, bom arsip, dan sel terlalu banyak semuanya ditolak
dengan kode galat yang jelas; file valid lolos; batas waktu ditegakkan.

Bom arsip dan file sel-banyak dibuat di memori saat tes berjalan
(tidak disimpan di repo).
"""

import io
import json
import zipfile
from pathlib import Path

import pytest
from openpyxl import Workbook

from app.checker import muat_aturan, periksa_bytes
from app.validasi import (
    BATAS_JUMLAH_SEL,
    BATAS_UKURAN_FILE,
    BatasWaktu,
    GalatValidasi,
    GalatWaktuHabis,
    validasi_unggahan,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _baca_fixture(nama):
    return (FIXTURES / nama).read_bytes()


def _zip_bom():
    """Arsip kecil yang mengembang melewati batas dekompresi (bom arsip)."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("xl/workbook.xml", "<workbook/>")
        zf.writestr("[Content_Types].xml", "<Types/>")
        # 25 MB nol -> terkompresi jadi ~25 KB.
        zf.writestr("xl/worksheets/sheet1.xml", b"\0" * (25 * 1024 * 1024))
    return buf.getvalue()


def _zip_bukan_xlsx():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("catatan.txt", "bukan excel")
    return buf.getvalue()


def _xlsx_banyak_sel(jumlah):
    wb = Workbook()
    ws = wb.active
    ws.title = "Data"
    tersisa = jumlah
    baris = 1
    while tersisa > 0:
        for kolom in range(1, 101):
            if tersisa <= 0:
                break
            ws.cell(row=baris, column=kolom, value=1)
            tersisa -= 1
        baris += 1
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def test_file_valid_lolos():
    manifes = json.loads((FIXTURES / "manifest.json").read_text(encoding="utf-8"))
    data = _baca_fixture("uji-rekap_penjualan-benar.xlsx")
    info = validasi_unggahan(data, "jawaban.xlsx")
    assert info["ukuran_file"] == len(data)
    assert info["ukuran_dekompresi"] > 0
    assert info["jumlah_sel"] > 0
    assert info["jumlah_sel"] <= BATAS_JUMLAH_SEL
    assert manifes["seed"] == "fixture-tahap2"


def test_template_valid_lolos():
    from app.template import template_ke_bytes

    data = template_ke_bytes("absensi", "fixture-tahap2")
    info = validasi_unggahan(data, "Template Absensi Karyawan.xlsx")
    assert info["jumlah_sel"] > 0


def test_file_besar_ditolak():
    data = _baca_fixture("uji-absensi-benar.xlsx") + b"\0" * (BATAS_UKURAN_FILE + 1)
    assert len(data) > BATAS_UKURAN_FILE
    with pytest.raises(GalatValidasi) as exc:
        validasi_unggahan(data, "jawaban.xlsx")
    assert exc.value.kode == "file_terlalu_besar"


def test_xlsm_ditolak():
    data = _baca_fixture("uji-absensi-benar.xlsx")
    with pytest.raises(GalatValidasi) as exc:
        validasi_unggahan(data, "jawaban.xlsm")
    assert exc.value.kode == "xlsm_ditolak"


def test_ekstensi_salah_ditolak():
    data = _baca_fixture("uji-absensi-benar.xlsx")
    with pytest.raises(GalatValidasi) as exc:
        validasi_unggahan(data, "jawaban.csv")
    assert exc.value.kode == "ekstensi_salah"


def test_teks_bernama_xlsx_ditolak():
    with pytest.raises(GalatValidasi) as exc:
        validasi_unggahan(b"halo ini teks biasa, bukan excel", "jawaban.xlsx")
    assert exc.value.kode == "bukan_arsip_valid"


def test_zip_bukan_xlsx_ditolak():
    with pytest.raises(GalatValidasi) as exc:
        validasi_unggahan(_zip_bukan_xlsx(), "jawaban.xlsx")
    assert exc.value.kode == "bukan_xlsx"


def test_bom_arsip_ditolak():
    data = _zip_bom()
    assert len(data) < BATAS_UKURAN_FILE  # kecil saat dikirim, besar saat dibuka
    with pytest.raises(GalatValidasi) as exc:
        validasi_unggahan(data, "jawaban.xlsx")
    assert exc.value.kode == "dekompresi_terlalu_besar"


def test_sel_terlalu_banyak_ditolak():
    data = _xlsx_banyak_sel(BATAS_JUMLAH_SEL + 100)
    with pytest.raises(GalatValidasi) as exc:
        validasi_unggahan(data, "jawaban.xlsx")
    assert exc.value.kode == "sel_terlalu_banyak"


def test_waktu_habis_ditolak():
    data = _baca_fixture("uji-penilaian_magang-benar.xlsx")
    tenggat = BatasWaktu(detik=0)
    with pytest.raises(GalatWaktuHabis) as exc:
        validasi_unggahan(data, "jawaban.xlsx", batas_waktu=tenggat)
    assert exc.value.kode == "waktu_habis"


def test_pemeriksa_menghormati_batas_waktu():
    aturan = muat_aturan("rekap_penjualan")
    data = _baca_fixture("uji-rekap_penjualan-benar.xlsx")
    tenggat = BatasWaktu(detik=0)
    with pytest.raises(GalatWaktuHabis):
        periksa_bytes(data, "fixture-tahap2", aturan, batas_waktu=tenggat)
    # Tanpa batas waktu, hasil normal.
    hasil = periksa_bytes(data, "fixture-tahap2", aturan)
    assert hasil["skor"] == 100
