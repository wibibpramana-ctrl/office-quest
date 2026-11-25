# Skema Aturan Cek (Tahap 2, Langkah 2.1)

Dokumen ini merancang format file aturan cek di `backend/rules/` — tempat semua
aturan penilaian pindah dari `index.html` (DATA_TUGAS `checks`). Tujuannya:
aturan bisa dibaca dan diubah tanpa menyentuh kode, dan backend Python bisa
menilai file .xlsx dengan aturan yang sama persis seperti pemeriksa browser.

- **Format:** JSON, UTF-8, tanpa komentar. Satu file per jenis tugas:
  `backend/rules/<tugas>.json` (mis. `backend/rules/rekap_penjualan.json`).
- **Prinsip (dari rencana §10):** nilai harapan dihitung oleh **evaluator
  bernama** di kode backend, bukan ekspresi teks yang dieksekusi. Ekspresi teks
  seperti `avg(B,C)` diganti nama evaluator ditambah parameter (lihat §4).
- **Toleransi angka 0,01.** Nilai sel dibaca dari cache file (`.v` SheetJS),
  rumus dibaca dari teks rumus (`.f`). Hanya `.xlsx`. Rumus dan makro tidak
  pernah dijalankan di server.
- **Menilai hasil, bukan cara:** beberapa fungsi setara bisa diterima bila
  ditetapkan di aturan (mis. `SUM` atau `SUBTOTAL` untuk penjumlahan).
- **Validasi:** satu aturan contoh di §7 lolos validasi skema ini.

## 1. Format file aturan

| Field | Jenis | Wajib | Keterangan |
|---|---|---|---|
| `tugas` | string | Ya | Id jenis tugas, sama dengan nama file (tanpa `.json`) |
| `sheet` | string | Ya | Nama sheet yang diperiksa (Tahap 1: `"Data"`) |
| `pass` | number | Ya | Batas lulus (Tahap 1: `70`) |
| `checks` | array objek | Ya | Daftar aturan cek; jumlah `points` harus tepat 100 |

## 2. Skema satu cek

| Field | Jenis | Wajib | Keterangan |
|---|---|---|---|
| `type` | string | Ya | Jenis cek (lihat §3) |
| `range` | string | Bila range | Alamat range A1, mis. `"D2:D11"` (untuk `value_each`, `is_formula`, `formula_uses`, `urutan`, `filter_aktif`, `format_angka`, `bersih`) |
| `cell` | string | Bila sel | Alamat satu sel A1, mis. `"D12"` (untuk `value`, `formula_uses` satu sel) |
| `evaluator` | objek | Bila nilai | Evaluator nilai harapan (lihat §4; untuk `value` dan `value_each`) |
| `functions` | array string | Bila fungsi | Fungsi yang diizinkan (untuk `formula_uses`; huruf besar, mis. `["SUM", "SUBTOTAL"]`) |
| `points` | number | Ya | Poin bila cek lulus (bilangan bulat ≥ 0) |
| `label` | string | Ya | Teks tampil di daftar centang hasil |
| `nama` | string | Bila sheet | Nama sheet yang harus ada (untuk `sheet_ada`) |
| `arah` | string | Bila urutan | `"naik"` atau `"turun"` (untuk `urutan`) |
| `format` | string | Bila format | `"mata_uang"` atau `"persen"` (untuk `format_angka`) |

Satu cek memakai `range` ATAU `cell`, tidak keduanya. `evaluator` hanya untuk
cek yang membandingkan nilai (`value`, `value_each`).

## 3. Katalog jenis cek

Jenis yang dipakai pemeriksa browser Tahap 1 (perilaku di bawah ini persis
seperti `periksaWorkbook` di `index.html`):

| Jenis | Arti | Kode bila gagal |
|---|---|---|
| `value` | Nilai satu sel (`cell`) cocok dengan nilai harapan (toleransi 0,01). Rumus tanpa cache → `nocache`. Nilai terbaca tapi salah → `sum`. | `sum`, `nocache` |
| `value_each` | Tiap sel di `range` cocok dengan nilai harapan (angka dengan toleransi 0,01, atau teks persis sama, peka huruf). Nilai terbaca tapi salah → `rowval`, kecuali bila seluruh range di baris total (baris ≥ 12) maka `sum`. Rumus tanpa cache → `nocache`. | `rowval`, `sum`, `nocache` |
| `is_formula` | Semua sel di `range` berisi rumus. Angka ketikan tanpa rumus → `hard`. Sel kosong tidak menghasilkan kode. | `hard` |
| `formula_uses` | Semua sel di sasaran berisi rumus yang memakai salah satu fungsi di `functions`. Fungsi lain → `sum`. Angka ketikan → `hard`. | `sum`, `hard` |
| `no_errors` | Tidak ada sel error (tipe `e`) di sheet. Ada → `err`. | `err` |

Jenis baru (untuk tugas Fase 7; mesinnya dibuat di Fase 3/7):

| Jenis | Arti | Kode bila gagal |
|---|---|---|
| `sheet_ada` | Sheet bernama `nama` ada di workbook. | `altered` |
| `urutan` | Data di `range` terurut `arah` (`naik`/`turun`) dengan tiap baris tetap utuh (tidak ada baris yang tertukar isinya). | `urutan` |
| `filter_aktif` | Filter otomatis terpasang pada `range`. | `filter` |
| `format_angka` | Format `format` (`mata_uang`/`persen`) terpasang pada `range`. | `format` |
| `bersih` | Data rusak di `range` sudah dibersihkan (angka bertipe teks jadi angka, baris ganda hilang, spasi liar terpotong, sel error teratasi) — untuk modifier "Perbaiki file rusak". | `bersih` |

Ditunda (Tahap 5): `chart_ada` (grafik ada), `pivot_ada` (PivotTable ada).

**Kode `altered`** (di luar jenis cek): data sumber diubah — sel tak-kosong
baris 2–11 di luar range cek berubah, sheet tidak ada, atau tugas pada aturan
tidak dikenal. Skor 0 bila sheet tidak ada atau tugas tidak dikenal.

## 4. Katalog evaluator (nilai harapan)

Evaluator menghitung nilai harapan satu sel dari data seed (AOA generator
tugas itu). `evaluator` selalu objek `{ "jenis": ..., ...parameter }`.

| Jenis | Parameter | Menggantikan ekspresi JS | Arti |
|---|---|---|---|
| `tetap` | `nilai` (number/string) | `expected` berupa angka | Nilai tetap, mis. `{ "jenis": "tetap", "nilai": 75 }` |
| `agregat` | `fungsi` (`"sum"`/`"avg"`), `range` | `sum(RANGE)`, `avg(RANGE)` | Jumlah/rata-rata nilai harapan range itu |
| `kali` | `kolom` (array, mis. `["B", "C"]`) | `B*C` | Perkalian nilai harapan kolom-kolom itu pada baris yang sama |
| `rata_kolom` | `kolom` (array, mis. `["B", "C"]`) | `avg(B,C)` | Rata-rata nilai harapan kolom-kolom itu pada baris yang sama |
| `hitung_kriteria` | `kolom` (range kolom, mis. `"B:F"`), `kriteria` (array, mis. `["H", "I", "A"]`) | `countif(B:F, H\|I\|A)` | Hitung sel pada rentang kolom di baris yang sama yang sama dengan kriteria. Kriteria dipilih dari daftar berurutan menurut urutan kolom target dalam range cek: kolom target pertama memakai kriteria pertama, dan seterusnya |
| `jumlah_kolom` | `baris_awal` (2), `baris_akhir` (11) | `sum(kolom)` | Jumlah nilai harapan sel pada kolom yang sama di baris `baris_awal`–`baris_akhir`; tiap nilai harapan dihitung dari aturan `value_each` `hitung_kriteria` yang mencakup kolom itu |
| `ambang` | `kolom`, `operator` (`>=`, `>`, `<=`, `<`, `=`, `<>`), `ambang` (number), `maka`, `selain` | `if(D>=75,'Lulus','Remedial')` | Bandingkan nilai harapan kolom rujukan pada baris yang sama dengan angka; hasilnya `maka` bila benar, `selain` bila salah (teks atau angka) |
| `bagi` | `pembilang` (evaluator), `penyebut` (evaluator) | — (direncanakan) | Pembagian dua nilai harapan (untuk margin/markup) |
| `tambah` | `suku` (array evaluator) | — (direncanakan) | Jumlah beberapa nilai harapan |
| `kurang` | `a` (evaluator), `b` (evaluator) | — (direncanakan) | Selisih dua nilai harapan |
| `bulat` | `nilai` (evaluator), `tempat` (number) | — (direncanakan) | Pembulatan (ROUND) ke `tempat` desimal |
| `jumlah_bersyarat` | `range`, `kriteria` | — (direncanakan, SUMIF) | Jumlah sel di range yang memenuhi kriteria |
| `hitung_bersyarat` | `range`, `kriteria` | — (direncanakan, COUNTIFS) | Hitung sel di range yang memenuhi kriteria |

Evaluator `direncanakan` belum dipakai tugas Tahap 1; dipakai saat jenis tugas
baru dibuat (Fase 7) dan mesinnya dibuat di Fase 3/7. Parameter evaluator boleh
berisi evaluator lain (bersarang) bila nilainya perlu dihitung dulu.

**Nilai harapan kolom rujukan:** bila evaluator membaca kolom lain (mis.
`ambang` membaca kolom `D`), nilainya diambil dari nilai harapan kolom itu —
dari data seed, atau dari aturan `value_each` lain yang menghitung kolom itu
(bukan dari aturan `ambang` lain).

## 5. Kode masalah dan urutan pemilihan balasan

Kode masalah yang mungkin muncul, selalu dalam urutan tetap ini dan tanpa
duplikat: `altered`, `nocache`, `err`, `rowval`, `urutan`, `filter`, `format`,
`sum`, `hard`, `telat`.

- `altered`, `nocache`, `err`, `rowval`, `sum`, `hard` — dari pemeriksa (lihat §3).
- `urutan`, `filter`, `format`, `bersih` — dari jenis cek baru (§3).
- `telat` — dari modifier Batas waktu (Tantangan selesai melewati batas).
- Bila tidak ada kode masalah, balasan dari skor: `ok90` (≥ 90), `ok70`
  (70–89), `fail` (< 70).
- Kode baru (`urutan`, `filter`, `format`, `telat`, `bersih`) perlu 3 variasi
  kalimat masing-masing di `content/feedback.json` (dibuat saat jenis ceknya
  dipakai, paling lambat Fase 7).

## 6. Penilaian

- Skor 0–100: jumlah `points` cek yang lulus. Jumlah `points` semua cek dalam
  satu file aturan harus tepat 100. Lulus bila skor ≥ `pass` (Tahap 1: 70).
  Bonus bila skor ≥ 90 (hadiah 150 XP/150 koin menggantikan 100/100).
- `label` tiap cek tampil di daftar centang hasil, apa pun hasilnya.
- Nilai harapan `null` (tidak bisa dihitung dari seed) membuat cek itu tidak
  bisa lulus; bukan kesalahan file aturan.

## 7. Contoh lengkap (`rekap_penjualan` — data asli, ekspresi diganti evaluator)

```json
{
  "tugas": "rekap_penjualan",
  "sheet": "Data",
  "pass": 70,
  "checks": [
    {
      "type": "value_each",
      "range": "D2:D11",
      "evaluator": { "jenis": "kali", "kolom": ["B", "C"] },
      "points": 30,
      "label": "Total per produk benar (D2:D11)"
    },
    {
      "type": "is_formula",
      "range": "D2:D11",
      "points": 15,
      "label": "Total diisi dengan rumus (D2:D11)"
    },
    {
      "type": "value",
      "cell": "D12",
      "evaluator": { "jenis": "agregat", "fungsi": "sum", "range": "D2:D11" },
      "points": 20,
      "label": "Total penjualan benar (D12)"
    },
    {
      "type": "formula_uses",
      "cell": "D12",
      "functions": ["SUM", "SUBTOTAL"],
      "points": 10,
      "label": "Total penjualan memakai rumus jumlah (D12)"
    },
    {
      "type": "value",
      "cell": "D13",
      "evaluator": { "jenis": "agregat", "fungsi": "avg", "range": "D2:D11" },
      "points": 15,
      "label": "Rata-rata benar (D13)"
    },
    {
      "type": "formula_uses",
      "cell": "D13",
      "functions": ["AVERAGE"],
      "points": 5,
      "label": "Rata-rata memakai rumus rata-rata (D13)"
    },
    {
      "type": "no_errors",
      "points": 5,
      "label": "Tidak ada error di file"
    }
  ]
}
```

Pemetaan ekspresi di contoh ini: `B*C` → `kali`, `sum(D2:D11)` → `agregat`
(`sum`), `avg(D2:D11)` → `agregat` (`avg`).

## 8. Aturan validasi (untuk file aturan, dipakai Langkah 2.2)

- File JSON valid; `tugas` cocok dengan nama file; `sheet` tidak kosong;
  `pass` bilangan 70 (Tahap 1) atau sesuai jenis tugas.
- Tiap cek: `type` dikenal (§3); `range` atau `cell` ada (tepat satu);
  `points` bilangan bulat ≥ 0; `label` tidak kosong.
- `value`/`value_each` wajib punya `evaluator` dengan `jenis` dikenal (§4)
  dan parameter lengkap; `formula_uses` wajib punya `functions` tidak kosong.
- Jumlah `points` semua cek tepat 100.
- Tidak ada ekspresi teks (`expected` berupa string) di file aturan mana pun.
