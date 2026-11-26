# Uji keamanan rilis (Langkah 4.4)

Tujuan: sebelum backend dipakai pemain, buktikan tiga hal secara tertulis:

1. tidak ada rahasia di repo,
2. tiket palsu ditolak,
3. generator dengan garam salah menghasilkan data berbeda.

**Status: DRAF — cek lokal LOLOS; cek langsung (live) menunggu backend
tayang (4.2).** Setelah 4.2, jalankan bagian "Verifikasi langsung" di tiap
seksi, lalu ubah statusnya dan catat tanggal + alamat layanan saat itu.

## 1. Tidak ada rahasia di repo — LOLOS (lokal + CI)

- Pemindaian rahasia (gitleaks) di workflow Tes: run #1 dan #2 HIJAU,
  "No leaks detected ✅".
- `render.yaml`: `OFFICE_QUEST_GARAM` memakai `generateValue: true` —
  Render membuat nilainya sendiri; tidak ada nilai garam di repo.
- `backend/.env.example`: hanya nama variabel (`OFFICE_QUEST_GARAM=`
  kosong) + peringatan jangan isi rahasia.
- `backend/app/tiket.py`, `garam_dari_lingkungan()`: gagal keras
  (`GalatGaram`) bila variabel belum diatur — tidak ada garam
  bawaan/publik.
- Pencarian lokal 26 Nov 2026 di `backend/app/` + `render.yaml`: tidak
  ada string hex 64 karakter, tidak ada penugasan nilai garam;
  `secrets.token_hex(32)` hanya ada di fungsi `buat_garam()` (pembuat
  garam, bukan nilai tersimpan).
- File `.env` asli / kunci privat: tidak ada di folder yang didorong
  (yang ada hanya bundle CA publik di dalam venv lokal, yang tidak
  masuk repo).

## 2. Tiket palsu ditolak — LOLOS (lokal); verifikasi langsung MENUNGGU

Bukti lokal (seluruh suite backend 55/55):

- `backend/tests/test_tiket.py` 12/12: tiket yang diubah satu karakter
  di 3 posisi ditolak (`tiket_tidak_sah`); garam salah ditolak; tiket
  kedaluwarsa ditolak (`tiket_kedaluwarsa`); tiket rusak/jenis asing
  ditolak.
- `backend/tests/test_api.py` 15/15: tiket palsu → HTTP 403; tiket
  kedaluwarsa → HTTP 410; fixture seed publik (tanpa garam server) →
  skor < 70 + kode `altered`.

Verifikasi langsung (setelah 4.2):

- `GET <alamat>/tugas/template?tiket=<tiket yang diubah satu karakter>`
  → harus 403.
- `POST <alamat>/periksa` dengan tiket kedaluwarsa → harus 410.

## 3. Garam salah → data berbeda — LOLOS (lokal); verifikasi langsung MENUNGGU

Bukti lokal:

- `test_tiket.py`: garam berbeda → data tugas berbeda; garam sama +
  benih sama → data sama (deterministik).
- `test_api.py`: file jawaban yang dibuat dari seed publik (tanpa garam
  server) ditolak pemeriksa (`altered`) — membuktikan pemeriksa memakai
  seed turunan garam, bukan seed publik.

Verifikasi langsung (setelah 4.2):

- Minta satu tiket dari server, unduh template-nya. Baca benih publik
  dari isi tiket (muatannya bukan rahasia), lalu buat data yang sama
  secara lokal dengan garam uji (bukan garam server) — isinya harus
  BERBEDA dari template server. Bila sama, garam server bocor/sama
  dengan garam uji → hentikan layanan.

## 4. Batas & perlindungan lain — LOLOS (lokal); verifikasi langsung MENUNGGU

- Unggahan: file > 2 MB → 413; `.xlsm` → 415; bom arsip (dekompresi
  > 20 MB) ditolak; > 100.000 sel ditolak (`test_validasi.py` 11/11;
  `test_api.py` 413/415).
- Pembatas laju: 30/menit per IP → 429 (`test_api.py`).
- CORS: hanya `https://wibibpramana-ctrl.github.io` (`test_api.py`).
- Log: tidak memuat isi file, string tiket, atau garam (`test_api.py`
  caplog).
- Verifikasi langsung: ulangi satu kasus tiap baris di atas terhadap
  alamat tayang (file besar, `.xlsm`, 31 permintaan beruntun, origin
  asing); baca log Render dan pastikan tidak ada string tiket/garam.

## Cara menjalankan ulang

- Lokal: jalankan pytest dari folder `backend` (lihat
  `backend/README.md`) — 55 tes.
- Pemindaian rahasia: otomatis di workflow Tes setiap dorongan
  (job `rahasia`).
- Langsung: ganti `<alamat>` dengan alamat layanan tayang, jalankan
  perintah di bagian verifikasi langsung tiap seksi.

## Status akhir

- [x] Daftar tertulis dibuat (draf ini).
- [ ] Verifikasi langsung seksi 2, 3, 4 dijalankan setelah 4.2 — ubah
  status di atas dan catat tanggal + alamat layanan saat itu.
