"""Tes paritas template (3.3): isi sel dan nama sheet template Python
(openpyxl) identik dengan template browser (SheetJS) untuk 20 seed.

Fixture ``fixtures/paritas-template.json`` berisi isi sheet "Data"
template browser yang dibaca kembali dengan SheetJS, untuk 20 seed
x 3 tugas; dibuat oleh harness ``~/workspace/oq-test/uji-template-3.3.js``.
"""

import io
import json
from pathlib import Path

from openpyxl import load_workbook

from app.template import NAMA_SHEET, buat_template, nama_file_template, template_ke_bytes

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "paritas-template.json"


def _muat_fixture():
    with open(FIXTURE, encoding="utf-8") as f:
        return json.load(f)


def _normalisasi(baris_list):
    """Samakan panjang baris (sel kosong di ujung = None).

    SheetJS menulis rentang sheet selebar AOA, sedangkan openpyxl
    hanya selebar kolom yang berisi nilai — sel kosong di ujung
    baris tetaplah sel kosong di kedua sisi.
    """
    lebar = max((len(b) for b in baris_list), default=0)
    return [list(b) + [None] * (lebar - len(b)) for b in baris_list]


def test_template_identik_dengan_browser_20_seed():
    data = _muat_fixture()
    assert data["jumlah_seed"] == 20
    assert len(data["entri"]) == 60
    gagal = []
    for entri in data["entri"]:
        berkas = template_ke_bytes(entri["tugas"], entri["seed"])
        assert len(berkas) > 1000
        wb = load_workbook(io.BytesIO(berkas), data_only=True)
        if wb.sheetnames != [NAMA_SHEET]:
            gagal.append(f'{entri["tugas"]} [{entri["seed"]}] sheet {wb.sheetnames}')
            continue
        ws = wb[NAMA_SHEET]
        didapat = _normalisasi([list(r) for r in ws.values])
        diharapkan = _normalisasi(entri["baris"])
        if didapat != diharapkan:
            gagal.append(f'{entri["tugas"]} [{entri["seed"]}] isi berbeda')
    assert not gagal, f"paritas template gagal: {gagal[:5]}"


def test_nama_file_template():
    assert nama_file_template("rekap_penjualan") == "Template Rekap Penjualan Mingguan.xlsx"
    assert nama_file_template("absensi") == "Template Absensi Karyawan.xlsx"
    assert nama_file_template("penilaian_magang") == "Template Penilaian Magang.xlsx"
    try:
        nama_file_template("tugas_asing")
    except ValueError:
        return
    raise AssertionError("tugas asing seharusnya ditolak")


def test_buat_template_mengembalikan_workbook():
    wb = buat_template("absensi", "fixture-tahap2")
    assert wb.sheetnames == ["Data"]
    ws = wb["Data"]
    assert ws["A1"].value == "Nama"
    assert ws["B1"].value == "Senin"
    assert ws["A12"].value == "Total"
