"""Tes paritas generator (3.2): untuk 200 seed, data Python identik
dengan keluaran JS (perbandingan sha256 dari JSON kanonis).

Fixture ``fixtures/paritas-generator.json`` berisi sha256 dari
``JSON.stringify(aoa)`` keluaran JS (``buatDataTugas1/2/3``) untuk
200 seed x 3 tugas; dibuat oleh harness
``~/workspace/oq-test/uji-paritas-3.2.js``.
"""

import hashlib
import json
from pathlib import Path

from app.generator import aoa_ke_json, buat_data_tugas

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "paritas-generator.json"


def _muat_fixture():
    with open(FIXTURE, encoding="utf-8") as f:
        return json.load(f)


def test_paritas_200_seed():
    data = _muat_fixture()
    assert data["jumlah_seed"] == 200
    assert len(data["entri"]) == 600
    gagal = []
    for entri in data["entri"]:
        aoa = buat_data_tugas(entri["tugas"], entri["seed"])
        sha = hashlib.sha256(aoa_ke_json(aoa).encode("utf-8")).hexdigest()
        if sha != entri["sha256"]:
            gagal.append(f'{entri["tugas"]} [{entri["seed"]!r}]')
    assert not gagal, f"paritas gagal untuk {len(gagal)} entri: {gagal[:5]}"


def test_bentuk_dan_batas_tugas1():
    aoa = buat_data_tugas("rekap_penjualan", "fixture-tahap2")
    assert len(aoa) == 13
    assert all(len(baris) == 4 for baris in aoa)
    assert aoa[0] == ["Produk", "Qty", "Harga", "Total"]
    assert aoa[11] == ["Total Penjualan", None, None, None]
    assert aoa[12] == ["Rata-rata", None, None, None]
    for baris in aoa[1:11]:
        assert 5 <= baris[1] <= 50  # Qty
        assert 2000 <= baris[2] <= 21500 and baris[2] % 500 == 0  # Harga
        assert baris[3] is None  # Total kosong


def test_bentuk_dan_status_tugas2():
    aoa = buat_data_tugas("absensi", "fixture-tahap2")
    assert len(aoa) == 12
    assert all(len(baris) == 9 for baris in aoa)
    assert aoa[0][0] == "Nama" and aoa[0][6:] == ["Hadir", "Izin", "Alfa"]
    assert aoa[11][0] == "Total"
    for baris in aoa[1:11]:
        assert all(s in ("H", "I", "A") for s in baris[1:6])
        assert baris[6:] == [None, None, None]


def test_tugas3_tepat_satu_jumlah_150():
    for seed in ["fixture-tahap2", "", "seed-paritas-000", "seed-paritas-197"]:
        aoa = buat_data_tugas("penilaian_magang", seed)
        assert len(aoa) == 11
        assert all(len(baris) == 5 for baris in aoa)
        jumlah = [baris[1] + baris[2] for baris in aoa[1:]]
        assert jumlah.count(150) == 1, f"seed {seed!r}: {jumlah}"
        assert all(50 <= baris[1] <= 100 and 50 <= baris[2] <= 100 for baris in aoa[1:])


def test_tugas_tidak_dikenal_ditolak():
    try:
        buat_data_tugas("tugas_asing", "seed-paritas-000")
    except ValueError:
        return
    raise AssertionError("tugas asing seharusnya ditolak")
