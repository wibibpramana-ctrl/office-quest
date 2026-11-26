"""Tes tiket tugas (3.6): tiket lolos, diubah satu karakter ditolak,
garam salah ditolak, kedaluwarsa ditolak, garam berbeda -> data
berbeda, kedaluwarsa = 02.00 WIB hari berikutnya.
"""

from datetime import datetime, timezone

import pytest

from app.generator import buat_data_tugas
from app.tiket import (
    GalatGaram,
    GalatTiket,
    benih_harian,
    buat_garam,
    data_untuk_tiket,
    garam_dari_lingkungan,
    periksa_tiket,
    terbitkan_tiket,
    turunkan_seed,
)

GARAM_A = "garam-rahasia-a-untuk-tes"
GARAM_B = "garam-rahasia-b-untuk-tes"

# 26 Nov 2026, 10.00 WIB = 03.00 UTC.
SEkarang = datetime(2026, 11, 26, 3, 0, 0, tzinfo=timezone.utc)


def test_tiket_lolos_dan_muatan_utuh():
    tiket = terbitkan_tiket("rekap_penjualan", GARAM_A, tier=1, benih_publik="benih-1", sekarang=SEkarang)
    muatan = periksa_tiket(tiket, GARAM_A, sekarang=SEkarang)
    assert muatan["jenis"] == "rekap_penjualan"
    assert muatan["tier"] == 1
    assert muatan["benih"] == "benih-1"
    assert muatan["modifier"] is None
    assert muatan["diterbitkan"] == "2026-11-26T03:00:00Z"
    assert muatan["kedaluwarsa"] == "2026-11-26T19:00:00Z"  # 27 Nov 02.00 WIB


def test_kedaluwarsa_0200_wib_besok_dari_malam_hari():
    # Diterbitkan 26 Nov 23.30 WIB -> tetap kedaluwarsa 27 Nov 02.00 WIB.
    malam = datetime(2026, 11, 26, 16, 30, 0, tzinfo=timezone.utc)
    tiket = terbitkan_tiket("absensi", GARAM_A, sekarang=malam)
    muatan = periksa_tiket(tiket, GARAM_A, sekarang=malam)
    assert muatan["kedaluwarsa"] == "2026-11-26T19:00:00Z"


def test_tiket_diubah_satu_karakter_ditolak():
    tiket = terbitkan_tiket("absensi", GARAM_A, benih_publik="benih-2", sekarang=SEkarang)
    for posisi in (0, len(tiket) // 2, len(tiket) - 1):
        diubah = tiket[:posisi] + ("A" if tiket[posisi] != "A" else "B") + tiket[posisi + 1:]
        with pytest.raises(GalatTiket) as exc:
            periksa_tiket(diubah, GARAM_A, sekarang=SEkarang)
        assert exc.value.kode in ("tiket_tidak_sah", "tiket_rusak")


def test_garam_salah_ditolak():
    tiket = terbitkan_tiket("penilaian_magang", GARAM_A, sekarang=SEkarang)
    with pytest.raises(GalatTiket) as exc:
        periksa_tiket(tiket, GARAM_B, sekarang=SEkarang)
    assert exc.value.kode == "tiket_tidak_sah"


def test_tiket_kedaluwarsa_ditolak():
    kemarin = datetime(2026, 11, 25, 3, 0, 0, tzinfo=timezone.utc)
    tiket = terbitkan_tiket("rekap_penjualan", GARAM_A, sekarang=kemarin)
    with pytest.raises(GalatTiket) as exc:
        periksa_tiket(tiket, GARAM_A, sekarang=SEkarang)
    assert exc.value.kode == "tiket_kedaluwarsa"


def test_tiket_rusak_ditolak():
    for buruk in ("bukan-tiket", "", "!!!", "eyJtdWF0YW4iOiB7fX0"):
        with pytest.raises(GalatTiket) as exc:
            periksa_tiket(buruk, GARAM_A, sekarang=SEkarang)
        assert exc.value.kode == "tiket_rusak"


def test_jenis_tidak_dikenal_ditolak():
    with pytest.raises(GalatTiket) as exc:
        terbitkan_tiket("tugas_asing", GARAM_A, sekarang=SEkarang)
    assert exc.value.kode == "tiket_tidak_sah"


def test_garam_berbeda_data_berbeda():
    seed_a = turunkan_seed("benih-sama", GARAM_A)
    seed_b = turunkan_seed("benih-sama", GARAM_B)
    assert seed_a != seed_b
    assert buat_data_tugas("rekap_penjualan", seed_a) != buat_data_tugas("rekap_penjualan", seed_b)
    # Garam sama + benih sama -> data sama (deterministik).
    assert buat_data_tugas("rekap_penjualan", seed_a) == buat_data_tugas(
        "rekap_penjualan", turunkan_seed("benih-sama", GARAM_A)
    )


def test_data_untuk_tiket_sesuai_seed_turunan():
    tiket = terbitkan_tiket("absensi", GARAM_A, benih_publik="benih-3", sekarang=SEkarang)
    muatan = periksa_tiket(tiket, GARAM_A, sekarang=SEkarang)
    assert data_untuk_tiket(muatan, GARAM_A) == buat_data_tugas(
        "absensi", turunkan_seed("benih-3", GARAM_A)
    )


def test_benih_harian():
    assert benih_harian("pemain-1", "2026-11-26") == benih_harian("pemain-1", "2026-11-26")
    assert benih_harian("pemain-1", "2026-11-26") != benih_harian("pemain-1", "2026-11-27")
    assert benih_harian("pemain-1", "2026-11-26") != benih_harian("pemain-2", "2026-11-26")


def test_garam_dari_lingkungan(monkeypatch):
    monkeypatch.setenv("OFFICE_QUEST_GARAM", "garam-env-tes")
    assert garam_dari_lingkungan() == "garam-env-tes"
    monkeypatch.delenv("OFFICE_QUEST_GARAM")
    with pytest.raises(GalatGaram):
        garam_dari_lingkungan()


def test_buat_garam_acak_dan_panjang():
    assert len(buat_garam()) == 64
    assert buat_garam() != buat_garam()
