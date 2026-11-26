"""Tes mesin pemeriksa (3.4): 15 fixtures #uji cocok (skor dan kode)
dengan manifest, plus kasus sheet hilang, tugas tidak dikenal, dan
file bukan .xlsx.

Fixture berasal dari Langkah 2.3 (backend/tests/fixtures/); manifes
mencatat skor/lulus/kode yang diharapkan dari pemeriksa JavaScript.
"""

import io
import json
from pathlib import Path

from openpyxl import Workbook

from app.checker import muat_aturan, periksa_bytes, periksa_lembar

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _muat_manifes():
    with open(FIXTURES / "manifest.json", encoding="utf-8") as f:
        return json.load(f)


def test_15_fixtures_cocok():
    manifes = _muat_manifes()
    assert len(manifes["fixtures"]) == 15
    cache_aturan = {}
    gagal = []
    for entri in manifes["fixtures"]:
        tugas = entri["tugas"]
        if tugas not in cache_aturan:
            cache_aturan[tugas] = muat_aturan(tugas)
        data = (FIXTURES / entri["file"]).read_bytes()
        hasil = periksa_bytes(data, manifes["seed"], cache_aturan[tugas])
        if (
            hasil["skor"] != entri["skor"]
            or hasil["lulus"] != entri["lulus"]
            or hasil["kode"] != entri["kode"]
        ):
            gagal.append(
                f'{entri["file"]}: dapat skor={hasil["skor"]} lulus={hasil["lulus"]} '
                f'kode={hasil["kode"]}, manifes skor={entri["skor"]} '
                f'lulus={entri["lulus"]} kode={entri["kode"]}'
            )
    assert not gagal, "; ".join(gagal)


def test_centang_lengkap_dan_poin_total_100():
    manifes = _muat_manifes()
    for tugas in ["rekap_penjualan", "absensi", "penilaian_magang"]:
        aturan = muat_aturan(tugas)
        assert sum(c.get("points") or 0 for c in aturan["checks"]) == 100
        data = (FIXTURES / f"uji-{tugas}-benar.xlsx").read_bytes()
        hasil = periksa_bytes(data, manifes["seed"], aturan)
        assert hasil["skor"] == 100
        assert len(hasil["centang"]) == len(aturan["checks"])
        assert all(c["lulus"] for c in hasil["centang"])
        assert sum(c["poin"] for c in hasil["centang"]) == 100


def test_sheet_hilang_skor_0_kode_altered():
    aturan = muat_aturan("rekap_penjualan")
    aturan_lain = dict(aturan, sheet="TidakAda")
    wb = Workbook()
    ws = wb.active
    ws.title = "Data"
    ws["A1"] = "Produk"
    buf = io.BytesIO()
    wb.save(buf)
    hasil = periksa_bytes(buf.getvalue(), "fixture-tahap2", aturan_lain)
    assert hasil["skor"] == 0
    assert hasil["lulus"] is False
    assert hasil["kode"] == ["altered"]
    assert all(not c["lulus"] for c in hasil["centang"])


def test_tugas_tidak_dikenal_skor_0_kode_altered():
    aturan = muat_aturan("rekap_penjualan")
    aturan_asing = dict(aturan, tugas="tugas_asing")
    data = (FIXTURES / "uji-rekap_penjualan-benar.xlsx").read_bytes()
    hasil = periksa_bytes(data, "fixture-tahap2", aturan_asing)
    assert hasil["skor"] == 0
    assert hasil["lulus"] is False
    assert hasil["kode"] == ["altered"]


def test_file_bukan_xlsx_skor_0_kode_altered():
    aturan = muat_aturan("absensi")
    hasil = periksa_bytes(b"ini bukan file xlsx", "fixture-tahap2", aturan)
    assert hasil["skor"] == 0
    assert hasil["lulus"] is False
    assert hasil["kode"] == ["altered"]


def test_lembar_kosong_tanpa_rumus():
    """Template kosong (tanpa jawaban): nilai tidak terbaca, tanpa kode
    nilai — hanya nocache bila ada rumus tanpa cache (di sini tidak ada)."""
    from app.template import template_ke_bytes

    aturan = muat_aturan("rekap_penjualan")
    data = template_ke_bytes("rekap_penjualan", "fixture-tahap2")
    hasil = periksa_bytes(data, "fixture-tahap2", aturan)
    # Hanya no_errors yang lulus (5 poin); sisanya gagal tanpa hard/sum.
    assert hasil["skor"] == 5
    assert hasil["kode"] == []
