# Skema Database Office Quest (Fase 5, Langkah 5.1)

Status: **DISETUJUI Wibi 27 Nov 2026, 18.20 WIB — "Setuju semua".** Keputusan §5:
(1) D6 = ya, nama panggilan ditanyakan di awal; (2) email opsional untuk lupa
kata sandi; (3) sesi 30 hari; (4) slot outfit mengikuti harga yang disetujui;
(5) pergantian hari 00.00 WIB; (6) file database di luar repo + cadangan salin
file. File `database/skema.sql` dibuat di 5.2 dari rancangan ini.
Dokumen ini adalah rancangan (5.1); file `database/skema.sql` dibuat di 5.2 dari
rancangan ini. Tabel inti mengikuti rencana (`akun`, `progres`, `tugas_harian`,
`inventori`, `wawancara`); tabel tambahan di bagian 2 adalah yang sudah pasti
dibutuhkan langkah 5.5/5.6 dan Fase 8 — ikut ditulis sekarang supaya skema tidak
berubah di tengah jalan.

## 0. Ringkasan keputusan teknis

- **SQLite (file), bukan MySQL**: paket gratis PythonAnywhere tidak menyediakan
  MySQL. SQLite sudah ada di Python standar — tanpa layanan tambahan, tanpa biaya.
- **File**: `/home/Wibi/office-quest-data/office-quest.db` — DI LUAR folder repo,
  supaya `git pull` tidak pernah menyentuhnya. Cadangan: salin file (cukup untuk
  skala game ini).
- **Mode**: WAL + `foreign_keys=ON` (dinyalakan tiap koneksi — SQLite tidak
  mengaktifkan foreign key bawaan).
- **Kata sandi**: hanya hash argon2id, tidak pernah teks biasa. **Token sesi**:
  acak 32 byte; yang disimpan hanya hash SHA-256-nya.
- **Migrasi**: tabel `meta` berisi `skema_versi`; perubahan skema sebagai file
  bernomor di `database/migrations/`, diterapkan backend saat start. Jangan ubah
  DB dengan tangan.
- **Kebijakan akses per baris (RLS)**: SQLite tidak punya RLS bawaan. Aturan yang
  sama ("pemain hanya bisa membaca/menulis baris miliknya sendiri") ditegakkan di
  lapisan aplikasi: setiap query difilter `akun_id = akun dari sesi`, dan diuji
  (pemain A meminta data pemain B → ditolak).

## 1. Tabel inti

### 1.1 `akun` — pemilik: layanan akun (5.2)

| Kolom | Tipe | Aturan |
|---|---|---|
| `id` | INTEGER PK AUTOINCREMENT | — |
| `nama_akun` | TEXT NOT NULL UNIQUE | Nama untuk masuk; dipilih saat daftar |
| `nama_panggilan` | TEXT NULL | Nama sapaan di game; NULL = "Kamu" (lihat D6) |
| `email` | TEXT NULL UNIQUE | Opsional; hanya untuk lupa kata sandi |
| `hash_kata_sandi` | TEXT NOT NULL | argon2id |
| `dibuat_pada` | TEXT NOT NULL | ISO 8601 WIB |
| `terakhir_masuk` | TEXT NULL | ISO 8601 WIB |

Catatan: D6 (nama panggilan di awal) masih terbuka — skema ini mendukung
keduanya. Bila D6 = ya, pendaftaran mengisi `nama_panggilan`; bila tidak,
pemain tetap "Kamu" sampai ia mengisinya sendiri.

### 1.2 `sesi` — pemilik: layanan akun (5.2)

| Kolom | Tipe | Aturan |
|---|---|---|
| `id` | INTEGER PK AUTOINCREMENT | — |
| `akun_id` | INTEGER NOT NULL FK → `akun(id)` | — |
| `token_hash` | TEXT NOT NULL UNIQUE | SHA-256 dari token acak 32 byte |
| `dibuat_pada` | TEXT NOT NULL | ISO 8601 WIB |
| `kedaluwarsa_pada` | TEXT NOT NULL | Bawaan 30 hari (keputusan tinjauan no. 3) |
| `perangkat` | TEXT NULL | Label bebas, mis. "HP Wibi" |

Index: `token_hash` (unik), `akun_id`. Keluar = hapus baris sesi. Token
kedaluwarsa ditolak (401).

### 1.3 `progres` — pemilik: layanan progres (5.5)

| Kolom | Tipe | Aturan |
|---|---|---|
| `akun_id` | INTEGER PK FK → `akun(id)` | Satu baris per pemain |
| `xp` | INTEGER NOT NULL DEFAULT 0 | — |
| `koin` | INTEGER NOT NULL DEFAULT 0 | — |
| `level` | INTEGER NOT NULL DEFAULT 1 | 1 Magang, 2 Staff, 3 Senior, 4 Supervisor, 5 Manager, 6 Direktur; diturunkan dari XP (biaya naik level di `backend/rules/ekonomi.json`, Fase 7) |
| `energi` | INTEGER NOT NULL DEFAULT 100 | Maks 100; hanya untuk tantangan |
| `energi_dihitung_pada` | TEXT NOT NULL | Cap waktu terakhir hitung pulih (+1 tiap 5 menit) |
| `streak_absen` | INTEGER NOT NULL DEFAULT 0 | Hari berturut-turut |
| `terakhir_absen` | TEXT NULL | Tanggal YYYY-MM-DD terakhir absen |
| `diperbarui_pada` | TEXT NOT NULL | ISO 8601 WIB |

### 1.4 `tugas_harian` — pemilik: generator tugas harian (Fase 7; dibaca 5.5)

| Kolom | Tipe | Aturan |
|---|---|---|
| `id` | INTEGER PK AUTOINCREMENT | — |
| `akun_id` | INTEGER NOT NULL FK → `akun(id)` | — |
| `tanggal` | TEXT NOT NULL | YYYY-MM-DD WIB (D7: pergantian hari 00.00 WIB — masih diputuskan, rekomendasi rencana) |
| `urutan` | INTEGER NOT NULL | 1..5 (posisi tugas hari itu) |
| `jenis` | TEXT NOT NULL | Mis. `rekap_penjualan` |
| `tier` | INTEGER NOT NULL | 1..3 |
| `status` | TEXT NOT NULL DEFAULT 'baru' | `baru` / `dikerjakan` / `selesai` |
| `skor_terakhir` | INTEGER NULL | 0–100 |
| `lulus` | INTEGER NULL | 0/1 |
| `percobaan` | INTEGER NOT NULL DEFAULT 0 | Jumlah unggah |
| `hint_terpakai` | INTEGER NOT NULL DEFAULT 0 | — |
| `selesai_pada` | TEXT NULL | ISO 8601 WIB |

UNIQUE(`akun_id`, `tanggal`, `urutan`); INDEX(`akun_id`, `tanggal`).
Catatan: tiket tidak disimpan — tiket diterbitkan ulang dari seed harian
(deterministik) bila perlu.

### 1.5 `inventori` — pemilik: Toko (Fase 8; dibaca 5.5)

| Kolom | Tipe | Aturan |
|---|---|---|
| `akun_id` | INTEGER NOT NULL FK → `akun(id)` | PK gabungan |
| `item_id` | TEXT NOT NULL | PK gabungan; id dari katalog (karakter, outfit, meja, habis pakai, eksklusif) |
| `diperoleh_pada` | TEXT NOT NULL | ISO 8601 WIB |
| `sumber` | TEXT NOT NULL | `toko` / `tantangan` / `absen` |

PK(`akun_id`, `item_id`).

### 1.6 `wawancara` — pemilik: wawancara awal (5.6)

| Kolom | Tipe | Aturan |
|---|---|---|
| `akun_id` | INTEGER PK FK → `akun(id)` | — |
| `skor_json` | TEXT NOT NULL | JSON skor per skill, mis. `{"rumus":70,"tabel":60}`; nama skill mengikuti `content/wawancara.json` (5.6) |
| `dilewati` | INTEGER NOT NULL DEFAULT 0 | 0/1 |
| `selesai_pada` | TEXT NULL | ISO 8601 WIB |

## 2. Tabel tambahan

Dibutuhkan langkah 5.5/5.6 dan Fase 8; ditulis sekarang supaya tidak berubah
di tengah jalan.

### 2.1 `terpasang` — pemilik: Koleksi (Fase 7 / Tahap 7)

| Kolom | Tipe | Aturan |
|---|---|---|
| `akun_id` | INTEGER NOT NULL FK → `akun(id)` | PK gabungan |
| `slot` | TEXT NOT NULL | `kepala` / `wajah` / `baju` / `celana` / `sepatu` / `meja` — PK gabungan |
| `item_id` | TEXT NULL | NULL = tidak ada yang terpasang; harus ada di inventori (dicek aplikasi) |

Catatan: rencana §9 menulis slot "kepala, wajah, baju, aksesori, meja",
sedangkan harga outfit yang sudah disetujui memakai Kepala/Wajah/Baju/Celana/
Sepatu. Skema ini mengikuti harga yang disetujui — lihat keputusan tinjauan
no. 4.

### 2.2 `lencana` — pemilik: Tantangan (Fase 8)

| Kolom | Tipe | Aturan |
|---|---|---|
| `akun_id` | INTEGER NOT NULL FK → `akun(id)` | PK gabungan |
| `lencana_id` | TEXT NOT NULL | PK gabungan |
| `diperoleh_pada` | TEXT NOT NULL | ISO 8601 WIB |

### 2.3 `pesan_chat` — pemilik: Chat (5.5)

| Kolom | Tipe | Aturan |
|---|---|---|
| `id` | INTEGER PK AUTOINCREMENT | — |
| `akun_id` | INTEGER NOT NULL FK → `akun(id)` | — |
| `karakter` | TEXT NOT NULL | `bima` / `rina` / `dito` / `miko` / `tono` / `jio` / `olla` |
| `pengirim` | TEXT NOT NULL | `karakter` / `pemain` |
| `isi` | TEXT NOT NULL | — |
| `dibuat_pada` | TEXT NOT NULL | ISO 8601 WIB |
| `dibaca` | INTEGER NOT NULL DEFAULT 0 | 0/1; pesan karakter yang belum dibaca = penanda `belumDibaca` |

INDEX(`akun_id`, `karakter`, `dibuat_pada`).

### 2.4 `absensi` — pemilik: Absen (Log Absensi)

| Kolom | Tipe | Aturan |
|---|---|---|
| `akun_id` | INTEGER NOT NULL FK → `akun(id)` | PK gabungan |
| `tanggal` | TEXT NOT NULL | YYYY-MM-DD — PK gabungan |
| `koin_diberikan` | INTEGER NOT NULL | 50, atau 250 di hari ke-7 beruntun (50 + bonus 200) |

PK(`akun_id`, `tanggal`). Streak dihitung dari baris berurutan;
`progres.streak_absen` adalah cache-nya.

### 2.5 `pengaturan` — pemilik: frontend

| Kolom | Tipe | Aturan |
|---|---|---|
| `akun_id` | INTEGER PK FK → `akun(id)` | — |
| `tema` | TEXT NULL | Mengikuti perangkat bila NULL |
| `preferensi_json` | TEXT NULL | JSON preferensi lain |

### 2.6 `pemulihan_kata_sandi` — pemilik: layanan akun (5.2/5.3)

| Kolom | Tipe | Aturan |
|---|---|---|
| `id` | INTEGER PK AUTOINCREMENT | — |
| `akun_id` | INTEGER NOT NULL FK → `akun(id)` | — |
| `token_hash` | TEXT NOT NULL UNIQUE | SHA-256 |
| `kedaluwarsa_pada` | TEXT NOT NULL | 1 jam |
| `dipakai` | INTEGER NOT NULL DEFAULT 0 | 0/1 |

Catatan: hanya berguna bila pemain mengisi email. Tanpa email, kata sandi
yang lupa tidak bisa dipulihkan — lihat keputusan no. 2.

### 2.7 `tantangan_selesai` — pemilik: Tantangan (Fase 8; dicadangkan)

| Kolom | Tipe | Aturan |
|---|---|---|
| `akun_id` | INTEGER NOT NULL FK → `akun(id)` | PK gabungan |
| `tantangan_id` | TEXT NOT NULL | Mis. `M-01` — PK gabungan |
| `skor` | INTEGER NOT NULL | 0–100 |
| `selesai_pada` | TEXT NOT NULL | ISO 8601 WIB |

Catatan: tiap tantangan sekali selesai; energi dipotong dari
`progres.energi` saat mulai (biaya 10/20/30/40), percobaan ulang gratis.

## 3. Aturan akses (pemilik & siapa boleh apa)

- Satu-satunya penulis: backend (layanan akun/progres/tugas). Pemain tidak
  pernah menyentuh database langsung — hanya lewat API dengan sesi.
- Setiap query pemain difilter `akun_id` = akun dari sesi. Tes di 5.2/5.5:
  pemain A meminta data pemain B → ditolak (401/403).
- Garam tiket (`OFFICE_QUEST_GARAM`) dan hash kata sandi tidak pernah keluar
  lewat API.
- File database hanya bisa dibaca akun server (Wibi); cadangan berupa salinan
  file, disimpan di luar repo.

## 4. Migrasi v1 → v2 (5.4)

- XP, koin, chat, hint dipertahankan dari localStorage v1.
- Status tiga tugas lama diabaikan (diganti tugas harian).
- Level dihitung ulang dari kurva baru dengan aturan tidak menurunkan: bila
  level v1 lebih tinggi, XP dinaikkan ke ambang level v1.
- Setelah pindah, localStorage v1 tidak lagi dipakai.

## 5. Yang diputuskan di langkah ini (mohon ditinjau Wibi)

1. **D6 — nama panggilan di awal: ya atau tidak?** (Skema mendukung keduanya.)
2. **Email opsional untuk lupa kata sandi: setuju?** Tanpa email, kata sandi yang
   lupa tidak bisa dipulihkan.
3. **Sesi berlaku 30 hari: setuju?**
4. **Slot outfit mengikuti harga yang disetujui** (kepala, wajah, baju, celana,
   sepatu, meja), bukan "aksesori" di §9: setuju?
5. **D7 — pergantian hari 00.00 WIB: setuju?** (Rekomendasi rencana.)
6. **Lokasi file database di luar repo + cadangan salin file: setuju?**

Bila semua disetujui, 5.2 membangun `database/skema.sql` dari dokumen ini.
