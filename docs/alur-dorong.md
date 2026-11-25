# Alur Dorong File ke Repo (Tahap 2, Langkah 0.4)

Keputusan D3 sudah terjawab (25 Nov 2026): **Joko mendorong file langsung ke repo
lewat konektor GitHub; Wibi menyetujui tiap dorongan lewat kartu.** Wibi tidak perlu
lagi mengunggah file manual lewat browser HP.

## Cara kerja

1. **Joko menyiapkan file** di salinan kerja lokal (di `~/workspace/`), lalu
   menyalin file yang berubah ke sebuah folder sumber khusus (misalnya
   `~/workspace/oq-nama-langkah/`).
2. **Joko mendorong** lewat perintah `github push-files` dengan:
   - `--owner wibibpramana-ctrl --repo office-quest --branch main`
   - `--message` yang menjelaskan langkahnya (misalnya "Arsip rencana rekonstruksi (0.1 Tahap 2)")
   - `--source-dir` (folder sumber) dan `--paths-file` (daftar file, dipisah NUL).
3. **Wibi menyetujui** dorongan itu di kartu persetujuan yang muncul di chat.
   Tanpa persetujuan, tidak ada yang berubah di repo.
4. **Joko memverifikasi** setelah dorongan: membaca kembali file dari repo dan
   membandingkan isinya (blob SHA-1) dengan file lokal — harus identik.
5. **GitHub Pages** memperbarui alamat publik otomatis (biasanya dalam 1–2 menit)
   bila file yang berubah adalah `index.html` atau `content/`.

## Yang dicatat tiap dorongan

- Commit SHA baru (misalnya `7f387d92`) dicatat di Log rencana Tahap 2.
- Catatan sinkronisasi disimpan di `<folder-sumber>.muse-github-snapshot-sync.json`
  (di luar folder sumber), berisi owner, repo, branch, folder sumber, commit SHA,
  dan daftar file yang didorong.

## Hal yang tidak bisa dilakukan konektor

- **Membuat tag/rilis:** konektor tidak punya alatnya. Tag/rilis dibuat Wibi
  lewat situs GitHub (contoh: `rekonstruksi-final`, dibuat 25 Nov 2026).
- **Menghapus file dari repo:** dorongan hanya menambah/mengubah file, tidak menghapus.
  Bila perlu menghapus, beri tahu Wibi dan lakukan lewat situs GitHub.

## Memeriksa alamat publik

Buka https://wibibpramana-ctrl.github.io/office-quest/ — perubahan `index.html`
tampil setelah Pages selesai memperbarui (biasanya 1–2 menit).
