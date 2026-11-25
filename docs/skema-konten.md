# Skema JSON Konten Game (Tahap 2, Langkah 1.1)

Dokumen ini merancang format file JSON di `content/` — tempat semua teks game
(brief, hint, trik, balasan, ucapan, katalog toko) tinggal setelah dipindah dari
`index.html`. Tujuannya: teks bisa diubah tanpa menyentuh kode, dan backend bisa
membaca brief tanpa kunci jawaban.

- **Format:** JSON, UTF-8, tanpa komentar. Teks memakai tanda baca tipografis (’ “ ”).
- **Aturan umum:** semua id huruf kecil dengan garis bawah (`rekap_penjualan`).
  Tidak ada rumus jawaban lengkap di file konten mana pun.
- **Validasi:** skrip validasi dibuat di Langkah 1.6; skema di sini adalah acuannya.
  Satu contoh tiap jenis di bawah ini lolos validasi.

## 1. Daftar file

| File | Isi |
|---|---|
| `content/karakter.json` | Semua karakter: nama, peran, avatar, foto, sapaan, ucapan |
| `content/feedback.json` | Balasan Pak Bima per kode masalah (9 kode × 3 variasi) |
| `content/tugas/<id>.json` | Satu file per jenis tugas: brief, hint, trik (tanpa aturan cek) |
| `content/toko.json` | Kategori dan katalog barang Toko |
| `content/wawancara.json` | Soal wawancara awal (dipakai Fase 5) |

Aturan cek (`checks`) TIDAK ada di `content/` — aturan cek tinggal di
`backend/rules/` (Fase 2).

## 2. Skema karakter (`karakter.json`)

Satu objek; kunci = id karakter (`bima`, `rina`, `dito`, `kamu`).

| Field | Jenis | Wajib | Keterangan |
|---|---|---|---|
| `nama` | string | Ya | Nama tampil, mis. “Pak Bima” |
| `peran` | string | Ya | Peran tampil, mis. “Bos” |
| `avatar` | string | Ya | Satu emoji, mis. “🐻‍❄️” |
| `foto` | string | Ya* | URL relatif ke file potret (mis. `../public/assets/bima.webp`); saat migrasi (1.2) data URI lama dipindah ke file |
| `sapaan` | string | Ya* | Sapaan pembuka di Chat (1 kalimat) |
| `ucapan` | objek | Ya* | Ucapan pop-up per kondisi tugas: `baru`, `dikerjakan`, `selesai` (masing-masing 1 kalimat) |
| `placeholder` | boolean | Tidak | `true` bila karakter ini placeholder (isinya menyusul, mis. Monyet) |

\* `foto`, `sapaan`, dan `ucapan` wajib untuk karakter NPC biasa (Bima, Rina, Dito).
Boleh kosong/tidak ada untuk: (a) karakter dengan `placeholder: true` (Monyet —
nama/sifat menyusul, Q8), dan (b) pemain (`kamu` — pemain tidak menyapa dirinya
sendiri dan fotonya menyusul di Koleksi).

**Contoh (Pak Bima — data asli dari game):**

```json
{
  "bima": {
    "nama": "Pak Bima",
    "peran": "Bos",
    "avatar": "🐻‍❄️",
    "foto": "../public/assets/bima.webp",
    "sapaan": "Pagi. Saya Pak Bima, bosmu. Kalau ada yang belum jelas soal tugas, tanya Rina atau Dito.",
    "ucapan": {
      "baru": "Pagi! Sudah cek jobdesk hari ini?",
      "dikerjakan": "Gimana laporannya? Jangan lupa deadline ya.",
      "selesai": "Kerja bagus hari ini. Istirahat dulu."
    }
  }
}
```

**Aturan validasi:** tiap karakter punya `nama`, `peran`, `avatar` (tidak kosong).
`foto`, `sapaan`, dan `ucapan` (berisi ketiga kunci `baru`, `dikerjakan`, `selesai`)
wajib ada dan tidak kosong, KECUALI untuk karakter dengan `placeholder: true`
dan untuk pemain (`kamu`). `foto` boleh berupa URL relatif atau data URI
(data URI dicatat sebagai utang migrasi, lihat §8).

## 3. Skema tugas (`tugas/<id>.json`)

Satu objek per jenis tugas. Nama file = `<id>.json` (mis. `rekap_penjualan.json`).

| Field | Jenis | Wajib | Keterangan |
|---|---|---|---|
| `id` | string | Ya | Sama dengan nama file (tanpa `.json`) |
| `judul` | string | Ya | Judul tampil, mis. “Rekap Penjualan Mingguan” |
| `dari` | string | Ya | Pemberi tugas, mis. “Pak Bima” |
| `deadline` | string | Ya* | Teks deadline, mis. “Kirim sebelum jam 5”. Hanya bila tugas itu punya deadline (lihat catatan di bawah tabel) |
| `skill` | array string | Ya | Skill yang dilatih, mis. `["perkalian", "SUM", "AVERAGE"]` |
| `brief` | string atau array | Ya | Teks brief; boleh memakai placeholder (lihat §6). Bila array, tiap entri satu varian brief |
| `ringkas` | string | Ya | Ringkasan satu baris untuk kartu Jobdesk |
| `lampiran` | objek | Ya | `{ "nama": "Template Rekap Penjualan Mingguan.xlsx" }` |
| `hint` | array string | Ya | Tepat 3 hint Rina (konsep → nama fungsi/lokasi → cara kerja), tanpa jawaban langsung |
| `trik` | array string | Ya | Tepat 3 trik Dito (shortcut, cara mengecek, cara menyimpan), tanpa membocorkan jawaban |

**Contoh (`rekap_penjualan` — data asli dari game, tanpa `checks`):**

```json
{
  "id": "rekap_penjualan",
  "judul": "Rekap Penjualan Mingguan",
  "dari": "Pak Bima",
  "deadline": "Kirim sebelum jam 5",
  "skill": ["perkalian", "SUM", "AVERAGE"],
  "brief": "Pagi! Tolong rekap penjualan minggu ini ya. Isi kolom Total, lalu hitung total seluruh penjualan dan rata-rata per produk. Kirim balik sebelum jam 5.",
  "ringkas": "Isi kolom Total, lalu hitung total dan rata-rata.",
  "lampiran": { "nama": "Template Rekap Penjualan Mingguan.xlsx" },
  "hint": [
    "Total per produk = Qty dikali Harga.",
    "Menjumlahkan banyak sel punya fungsi yang namanya mirip “jumlah” dalam bahasa Inggris.",
    "Tulis rumus, jangan ketik angkanya."
  ],
  "trik": [
    "Klik dua kali pojok kanan bawah sel untuk mengisi ke bawah.",
    "Blok D2:D11 dan lihat bar status untuk cek cepat.",
    "Simpan dengan Ctrl+S dari Excel."
  ]
}
```

**Aturan validasi:** `id` cocok dengan nama file; `hint` dan `trik` masing-masing
tepat 3 entri dan tidak kosong; tidak ada field `checks` (aturan cek dilarang di sini);
tidak ada rumus jawaban lengkap di `brief`, `hint`, atau `trik`.

\* `deadline` hanya wajib bila tugas itu memang punya deadline di data asli.
Di Tahap 1 hanya `rekap_penjualan` yang punya deadline (“Kirim sebelum jam 5”);
`absensi` dan `penilaian_magang` tidak punya field `deadline`, dan kartu Jobdesk
hanya menampilkan deadline bila field itu ada (lihat baris 10254 `index.html`).
Jangan mengarang deadline untuk tugas yang tidak punya.

## 4. Skema feedback (`feedback.json`)

Satu objek; kunci = kode masalah atau kode skor. Tiap kode berisi tepat 3 variasi kalimat.

| Kode | Arti |
|---|---|
| `altered` | Data asli diubah |
| `nocache` | Rumus ada tapi hasil belum tersimpan |
| `err` | Ada sel error (#VALUE!, #REF!, dsb.) |
| `rowval` | Ada baris yang nilainya salah |
| `sum` | Total/rata-rata bawah salah |
| `hard` | Ada angka diketik manual (bukan rumus) |
| `ok90` | Lulus skor ≥90 |
| `ok70` | Lulus skor 70–89 |
| `fail` | Gagal skor <70 |

**Contoh (kode `altered` — data asli dari game):**

```json
{
  "altered": [
    "Kok datanya beda dari file yang saya kirim? Tolong pakai file aslinya.",
    "Hmm, angka di file ini tidak sama dengan yang saya kirim. Coba unduh ulang templatenya, ya.",
    "Sepertinya data aslinya ikut berubah. Pakai file template yang saya kirim, jangan diubah angkanya."
  ]
}
```

File lengkap berisi kesembilan kode di atas, masing-masing tepat 3 variasi.

**Aturan validasi:** kesembilan kode ada; tiap kode tepat 3 variasi dan tidak kosong;
tidak ada kode lain.

## 5. Skema toko (`toko.json`)

Satu objek dengan dua kunci: `kategori` (array) dan `barang` (objek).

| Field | Jenis | Wajib | Keterangan |
|---|---|---|---|
| `kategori` | array objek | Ya | Tiap entri `{ "id", "nama" }`; entri pertama selalu `{ "id": "semua", "nama": "Semua" }` |
| `barang` | objek | Ya | Kunci = id barang; tiap barang satu objek |

Skema satu barang:

| Field | Jenis | Wajib | Keterangan |
|---|---|---|---|
| `id` | string | Ya | Sama dengan kunci objeknya |
| `nama` | string | Ya | Nama tampil |
| `kategori` | string | Ya | Harus cocok dengan salah satu id di `kategori` (selain `semua`) |
| `harga` | number | Ya | Harga koin (bilangan bulat ≥ 0) |
| `emoji` | string | Ya | Satu emoji sebagai cadangan bila ikon gagal dimuat |
| `ikon` | string | Tidak | URL relatif ke file ikon (bila ada); bila tidak ada, emoji dipakai |
| `deskripsi` | string | Tidak | Efek barang, mis. “Menambah energi.” |

**Contoh (satu kategori + satu barang — data asli dari game):**

```json
{
  "kategori": [
    { "id": "semua", "nama": "Semua" },
    { "id": "kepala", "nama": "Kepala" }
  ],
  "barang": {
    "topi_jerami": {
      "id": "topi_jerami",
      "nama": "Topi Jerami",
      "kategori": "kepala",
      "harga": 150,
      "emoji": "👒"
    }
  }
}
```

**Aturan validasi:** `kategori` pertama adalah `semua`; tiap barang `id`-nya cocok
dengan kuncinya; `kategori` barang ada di daftar kategori; `harga` bilangan bulat ≥ 0.

## 6. Brief bertemplat (placeholder)

Brief boleh memakai placeholder `{{nama}}` yang diisi saat tampil. Placeholder yang
diizinkan:

| Placeholder | Arti |
|---|---|
| `{{nama}}` | Nama panggilan pemain (atau “Kamu” bila belum diisi) |
| `{{jumlah}}` | Jumlah baris/produk pada tugas itu (dari tiket) |
| `{{deadline}}` | Teks deadline tugas itu |

Aturan: placeholder hanya yang ada di tabel ini; placeholder yang tidak dikenal
membuat validasi gagal. Brief yang sekarang (Tahap 1) tidak memakai placeholder —
tetap valid sebagai teks biasa.

**Contoh brief bertemplat:**

```json
{
  "brief": "Pagi, {{nama}}! Tolong rekap {{jumlah}} produk minggu ini ya. Isi kolom Total, lalu hitung total dan rata-rata. Kirim balik {{deadline}}."
}
```

## 7. Skema wawancara (`wawancara.json`, dipakai Fase 5)

Satu objek dengan kunci `soal` (array). Tiap soal satu objek:

| Field | Jenis | Wajib | Keterangan |
|---|---|---|---|
| `id` | string | Ya | Id soal |
| `teks` | string | Ya | Pertanyaan/perintah (gaya percakapan Pak Bima) |
| `skill` | string | Ya | Skill yang diukur (mis. `SUM`, `AVERAGE`, `IF`) |
| `jawaban` | string | Ya | Jawaban benar (tidak pernah ditampilkan ke pemain; hanya untuk menilai) |
| `petunjuk` | string | Tidak | Petunjuk bila pemain bingung |

**Contoh:**

```json
{
  "soal": [
    {
      "id": "w1",
      "teks": "Coba jumlahkan kolom ini ya. Rumus apa yang kamu pakai?",
      "skill": "SUM",
      "jawaban": "SUM",
      "petunjuk": "Fungsi untuk menjumlahkan banyak sel."
    }
  ]
}
```

**Aturan validasi:** tiap soal punya `id`, `teks`, `skill`, `jawaban`; `id` tidak boleh
dobel. Jawaban benar tidak pernah dikirim ke frontend sebagai teks tampil.

## 8. Catatan migrasi (untuk Langkah 1.2–1.4)

- `foto` karakter saat ini masih data URI di `index.html`. Saat migrasi (1.2),
  tiap potret diekstrak ke file di `public/assets/` dan field `foto` diisi URL
  relatifnya. Bila ekstraksi tertunda, `foto` boleh berisi data URI sementara —
  validasi menerima keduanya, tetapi data URI dicatat sebagai utang migrasi.
- `ikon` barang Toko mengikuti pola yang sama (file di `public/assets/` bila ada,
  emoji sebagai cadangan).
- `checks` tiap tugas TIDAK ikut ke `content/` — pindah ke `backend/rules/` (Fase 2).
