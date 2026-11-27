# Uji keamanan rilis (Langkah 4.4)

Tujuan: sebelum backend dipakai pemain, buktikan tiga hal secara tertulis:

1. tidak ada rahasia di repo,
2. tiket palsu ditolak,
3. generator dengan garam salah menghasilkan data berbeda.

**Status: VERIFIKASI LANGSUNG SELESAI 27 Nov 2026 — alamat layanan
https://Wibi.pythonanywhere.com (PythonAnywhere, paket gratis Beginner).
Cek lokal LOLOS; cek langsung 7 dari 8 LOLOS (lihat tiap seksi).**

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

Verifikasi langsung (27 Nov 2026): garam live TIDAK ada di repo —
disimpan di file privat `~/.office-quest-garam` (chmod 600) di server
PythonAnywhere dan dimuat sebagai variabel lingkungan oleh skrip
peluncur. Nilai garam tidak tertulis di dokumen ini maupun di repo.

## 2. Tiket palsu ditolak — LOLOS (lokal + live, kecuali 410)

Bukti lokal (seluruh suite backend 55/55):

- `backend/tests/test_tiket.py` 12/12: tiket yang diubah satu karakter
  di 3 posisi ditolak (`tiket_tidak_sah`); garam salah ditolak; tiket
  kedaluwarsa ditolak (`tiket_kedaluwarsa`); tiket rusak/jenis asing
  ditolak.
- `backend/tests/test_api.py` 15/15: tiket palsu → HTTP 403; tiket
  kedaluwarsa → HTTP 410; fixture seed publik (tanpa garam server) →
  skor < 70 + kode `altered`.

Verifikasi langsung (27 Nov 2026, alamat di atas):

- `GET /tugas/template?tiket=<tiket yang diubah satu karakter>`
  → 403 (`tiket_rusak`, "Tiket tidak bisa dibaca.") — LOLOS.
- `POST /periksa` dengan tiket kedaluwarsa → TIDAK DAPAT DIUJI LIVE:
  membuat tiket kedaluwarsa yang sah butuh tanda tangan HMAC dengan garam
  server — justru itu yang dirahasiakan. Jalur kodenya terbukti oleh suite
  lokal 55/55; berkas yang mengatur kedaluwarsa (`tiket.py`, `main.py`)
  tidak berubah sejak commit aeecc7eb, dan yang ter-deploy adalah
  commit 55c5e36. Tiket yang diterbitkan hari ini (kedaluwarsa 02.00 WIB
  28 Nov 2026) tersimpan di luar repo; mengulang `/periksa` dengannya
  setelah waktu itu harus menjawab 410.

## 3. Garam salah → data berbeda — LOLOS (lokal + live)

Bukti lokal:

- `test_tiket.py`: garam berbeda → data tugas berbeda; garam sama +
  benih sama → data sama (deterministik).
- `test_api.py`: file jawaban yang dibuat dari seed publik (tanpa garam
  server) ditolak pemeriksa (`altered`) — membuktikan pemeriksa memakai
  seed turunan garam, bukan seed publik.

Verifikasi langsung (27 Nov 2026):

- Satu tiket diminta dari server (`benih` publik: `benih-ukur-live`),
  template-nya diunduh. Data yang sama dibuat ulang secara lokal dengan
  garam uji (bukan garam server) memakai `generator.py` dari repo:
  20 dari 52 sel BERBEDA, dan pembuatan ulang dengan garam uji yang sama
  menghasilkan data identik (deterministik) — LOLOS. Bila isinya sama,
  garam server bocor/sama dengan garam uji; tidak terjadi.

## 4. Batas & perlindungan lain — LOLOS (lokal + live, dengan dua catatan)

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

Verifikasi langsung (27 Nov 2026; "log Render" dibaca sebagai log
PythonAnywhere, karena layanan tayangnya di sana):

- File 2,23 MB → 413 (`file_terlalu_besar`) — LOLOS.
- File `.xlsm` → 415 (`xlsm_ditolak`) — LOLOS.
- 31 permintaan beruntun → 30 dijawab 200, ke-31 dijawab 429; setelah
  jeda 65 detik permintaan berikutnya dijawab 200 (pulih) — LOLOS.
- CORS: preflight dari origin asing dijawab tanpa `allow-origin`;
  preflight dari `https://wibibpramana-ctrl.github.io` dijawab 200 dengan
  `allow-origin` yang benar; POST nyata dari origin asing dijawab 200
  tanpa `allow-origin` — LOLOS.
- Log — CATATAN 1 (penyimpangan kecil): Error log bersih dari string
  tiket (hanya nama variabel `OFFICE_QUEST_GARAM` di ~40 baris error
  startup lama, tanpa nilai). Server log (access log) mencatat token
  tiket di 2 baris (`GET /tugas/template?tiket=...`, satu 200 dan satu
  403) karena uvicorn mencatat URL lengkap termasuk query string. Dampak
  rendah: log hanya bisa dibaca pemilik akun PythonAnywhere, dan tiket
  kedaluwarsa < 24 jam. Perbaikan (pindah tiket dari query URL ke body)
  DITUNDA — diputuskan nanti, bukan penghalang rilis.
- CATATAN 2 (beban, terkait 3.8): file 1,79 MB (di bawah batas 2 MB)
  awalnya dijawab 503 `waktu_habis` setelah 12,39 detik — melewati batas
  proses 10 detik di CPU gratis (lokal: 3,68 detik). Perbaikan
  27 Nov 2026 (commit 55c5e36): pemeriksa membaca hanya sheet Data
  secara aliran (`checker.py`); file yang sama dijawab 200 dalam
  6,19 detik (lokal: 1,03 detik) dengan skor dihitung benar. Masih di atas
  target lokal 5 detik karena jaringan + CPU berbagi, tapi sudah di bawah
  batas 10 detik, dan file jawaban asli pemain (~20 KB) hanya butuh
  ~138 ms. Tidak ada perbaikan lanjutan untuk saat ini.
- Bom arsip (> 20 MB dekompresi) dan > 100.000 sel tidak termasuk daftar
  verifikasi langsung dokumen ini — terbukti lokal saja; jalurnya sama
  dengan file > 2 MB yang sudah terbukti live.

## Cara menjalankan ulang

- Lokal: jalankan pytest dari folder `backend` (lihat
  `backend/README.md`) — 55 tes.
- Pemindaian rahasia: otomatis di workflow Tes setiap dorongan
  (job `rahasia`).
- Langsung: ganti `<alamat>` dengan alamat layanan tayang, jalankan
  perintah di bagian verifikasi langsung tiap seksi.
- Skrip verifikasi live 27 Nov 2026 (`ukur-live.py`, memakai requests +
  openpyxl + `generator.py` dari repo) beserta laporan JSON-nya tersimpan
  di luar repo (workspace Joko).

## Status akhir

- [x] Daftar tertulis dibuat (draf ini).
- [x] Verifikasi langsung seksi 2, 3, 4 dijalankan setelah 4.2 — selesai
  27 Nov 2026, alamat https://Wibi.pythonanywhere.com (commit ter-deploy
  55c5e36). Hasil: 7 dari 8 LOLOS; 410 tidak dapat diuji live (butuh
  garam); 2 catatan ditunda (token tiket di server log; file 1,79 MB
  6,19 detik, di atas target 5 detik tapi di bawah batas 10 detik).
