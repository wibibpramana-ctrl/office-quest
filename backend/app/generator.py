"""Generator data tugas Office Quest (Python, mode paritas).

Port persis dari generator JavaScript di ``index.html``
(``hashSeedFNV1a``, ``mulberry32``, ``buatDataTugas1/2/3``).
Aturan port:
- Hash FNV-1a 32-bit atas unit kode UTF-16 seed (seperti ``charCodeAt``).
- ``Math.imul`` = perkalian 32-bit (bit rendah saja).
- Semua operasi bit (``^``, ``|``, ``>>>``) memakai semantik int32/uint32
  JavaScript; pembagian akhir memakai float ganda (IEEE 754), sama
  seperti di JavaScript.
- Urutan pemanggilan rng tetap, supaya seed yang sama selalu
  menghasilkan data yang sama.

Mode paritas (sampai Langkah 3.6): seed masih publik, belum memakai
garam rahasia.
"""

import json
import math

# ---------------------------------------------------------------------------
# RNG: FNV-1a + mulberry32
# ---------------------------------------------------------------------------

_MASK_32 = 0xFFFFFFFF


def _u32(x):
    """Nilai x sebagai uint32 (``>>> 0`` di JavaScript)."""
    return x & _MASK_32


def _i32(x):
    """Nilai x sebagai int32 bertanda (``| 0`` di JavaScript)."""
    x &= _MASK_32
    return x - 0x100000000 if x >= 0x80000000 else x


def _imul(a, b):
    """Perkalian 32-bit seperti ``Math.imul`` (bit rendah, bertanda)."""
    return _i32(_u32(a) * _u32(b))


def hash_seed_fnv1a(seed):
    """Hash FNV-1a 32-bit untuk string seed (``hashSeedFNV1a`` di JS)."""
    h = 0x811C9DC5
    s = "" if seed is None else str(seed)
    # Unit kode UTF-16, seperti String.charCodeAt di JavaScript.
    data = s.encode("utf-16-le")
    for i in range(0, len(data), 2):
        h ^= data[i] | (data[i + 1] << 8)
        h = _imul(h, 0x01000193)
    return _u32(h)


class Mulberry32:
    """PRNG mulberry32: menghasilkan angka float di [0, 1)."""

    def __init__(self, a):
        self.t = _u32(a)

    def __call__(self):
        self.t = _u32(self.t + 0x6D2B79F5)
        r = _i32(self.t)
        r = _imul(r ^ (_u32(r) >> 15), r | 1)
        r = _i32(r ^ _i32(r + _imul(r ^ (_u32(r) >> 7), r | 61)))
        return _u32(r ^ (_u32(r) >> 14)) / 4294967296


def buat_rng_dari_seed(seed):
    """RNG dari seed string (``buatRngDariSeed`` di JS)."""
    return Mulberry32(hash_seed_fnv1a(seed))


# ---------------------------------------------------------------------------
# Data tugas
# ---------------------------------------------------------------------------

DAFTAR_PRODUK_TUGAS1 = [
    "Kopi Bubuk",
    "Teh Celup",
    "Gula Pasir",
    "Beras Premium",
    "Minyak Goreng",
    "Tepung Terigu",
    "Susu UHT",
    "Mie Instan",
    "Sabun Mandi",
    "Sampo",
]

DAFTAR_NAMA_TUGAS2 = [
    "Andi",
    "Budi",
    "Citra",
    "Dewi",
    "Eko",
    "Fitri",
    "Gilang",
    "Hana",
    "Irfan",
    "Joko",
]

DAFTAR_NAMA_TUGAS3 = [
    "Arif",
    "Bunga",
    "Candra",
    "Dina",
    "Fajar",
    "Gita",
    "Hendra",
    "Intan",
    "Kartika",
    "Lukman",
]


def buat_data_tugas1(seed):
    """Data Tugas 1 (rekap_penjualan) sebagai array of arrays.

    Baris 1 header Produk/Qty/Harga/Total; baris 2-11 produk
    (Qty 5-50, Harga kelipatan 500 dari 2.000-21.500, Total kosong);
    baris 12 "Total Penjualan"; baris 13 "Rata-rata".
    """
    rng = buat_rng_dari_seed(seed)
    aoa = [["Produk", "Qty", "Harga", "Total"]]
    for produk in DAFTAR_PRODUK_TUGAS1:
        qty = 5 + math.floor(rng() * 46)  # 5-50 inklusif
        harga = 2000 + math.floor(rng() * 40) * 500  # 2.000-21.500, kelipatan 500
        aoa.append([produk, qty, harga, None])
    aoa.append(["Total Penjualan", None, None, None])
    aoa.append(["Rata-rata", None, None, None])
    return aoa


def buat_data_tugas2(seed):
    """Data Tugas 2 (absensi) sebagai array of arrays.

    Baris 1 header Nama/hari Senin-Jumat/Hadir/Izin/Alfa;
    baris 2-11 nama karyawan dengan status H/I/A per hari
    (rng < 0,7 -> H; < 0,9 -> I; sisanya A), kolom Hadir/Izin/Alfa
    kosong; baris 12 "Total" dengan semua sel lain kosong.
    """
    rng = buat_rng_dari_seed(seed)
    aoa = [
        ["Nama", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Hadir", "Izin", "Alfa"],
    ]
    for nama in DAFTAR_NAMA_TUGAS2:
        baris = [nama]
        for _ in range(5):
            r = rng()
            baris.append("H" if r < 0.7 else ("I" if r < 0.9 else "A"))
        baris.extend([None, None, None])
        aoa.append(baris)
    aoa.append(["Total", None, None, None, None, None, None, None, None])
    return aoa


def buat_data_tugas3(seed):
    """Data Tugas 3 (penilaian_magang) sebagai array of arrays.

    Baris 1 header Nama/Nilai Teori/Nilai Praktik/Rata-rata/
    Keterangan; baris 2-11 peserta dengan Nilai Teori dan Nilai
    Praktik bilangan bulat 50-100, kolom Rata-rata dan Keterangan
    kosong. Tepat satu peserta dibuat rata-ratanya 75 (B + C = 150):
    baris lain yang kebetulan berjumlah 150 digeser C-nya +-1 supaya
    jumlahnya bukan 150, lalu baris paksa diisi B acak 50-100 dan
    C = 150 - B.
    """
    rng = buat_rng_dari_seed(seed)
    nilai = []
    for _ in DAFTAR_NAMA_TUGAS3:
        teori = 50 + math.floor(rng() * 51)  # 50-100 inklusif
        praktik = 50 + math.floor(rng() * 51)  # 50-100 inklusif
        nilai.append([teori, praktik])
    indeks_paksa = math.floor(rng() * len(DAFTAR_NAMA_TUGAS3))
    for i in range(len(nilai)):
        if i == indeks_paksa:
            continue
        if nilai[i][0] + nilai[i][1] == 150:
            nilai[i][1] = nilai[i][1] + 1 if nilai[i][1] < 100 else nilai[i][1] - 1
    teori_paksa = 50 + math.floor(rng() * 51)  # 50-100 inklusif
    nilai[indeks_paksa] = [teori_paksa, 150 - teori_paksa]
    aoa = [["Nama", "Nilai Teori", "Nilai Praktik", "Rata-rata", "Keterangan"]]
    for i, nama in enumerate(DAFTAR_NAMA_TUGAS3):
        aoa.append([nama, nilai[i][0], nilai[i][1], None, None])
    return aoa


GENERATOR = {
    "rekap_penjualan": buat_data_tugas1,
    "absensi": buat_data_tugas2,
    "penilaian_magang": buat_data_tugas3,
}


def buat_data_tugas(tugas_id, seed):
    """Data tugas sebagai array of arrays untuk sheet "Data".

    ``tugas_id``: rekap_penjualan, absensi, atau penilaian_magang.
    """
    try:
        return GENERATOR[tugas_id](seed)
    except KeyError:
        raise ValueError(f"Jenis tugas tidak dikenal: {tugas_id}") from None


def aoa_ke_json(aoa):
    """Serialisasi kanonis AOA, sama dengan ``JSON.stringify`` di JS
    untuk data ini (tanpa spasi, tanpa escape Unicode)."""
    return json.dumps(aoa, ensure_ascii=False, separators=(",", ":"))
