# Catatan Operasional Backend Office Quest

Backend tayang di PythonAnywhere (paket gratis, akun Wibi) sejak 27 Nov 2026.
Auto-deploy (Langkah 4.3) aktif sejak 27 Nov 2026.

## 1. Alamat dan akun

- Backend: <https://Wibi.pythonanywhere.com> — cek sehat: `/sehat` → `{"status":"ok"}`
- Repo: `github.com/wibibpramana-ctrl/office-quest` (branch `main`)
- Hosting: PythonAnywhere, akun Wibi, paket Beginner (gratis)
- Kode di server: `/home/Wibi/office-quest` (clone repo, branch `main`)

## 2. Pembaruan otomatis (cara biasa)

Dorong perubahan ke `main`. Bila yang berubah ada di `backend/`, workflow GitHub
Actions **"Perbarui backend"** (`.github/workflows/perbarui.yml`) jalan otomatis:
memanggil API reload PythonAnywhere, lalu skrip peluncur server menarik kode
terbaru (`git pull --ff-only`) sebelum menyalakan ulang aplikasi. Setiap Reload —
otomatis maupun manual — menarik kode terbaru dulu.

- Waktu: sekitar 1 menit dari dorongan sampai server nyala lagi.
- Memeriksa: tab Actions di GitHub (run harus hijau), lalu buka `/sehat`.
- Perubahan di luar `backend/` (mis. dokumen, `.gitignore`) TIDAK memicu reload —
  server memang tidak perlu diperbarui untuk itu.
- **Dependensi baru:** bila pembaruan menambah paket di
  `backend/requirements.txt`, pasang dulu dari konsol Bash PythonAnywhere
  (`/home/Wibi/.virtualenvs/office-quest/bin/pip install -r
  ~/office-quest/backend/requirements.txt`) SEBELUM reload — proses webapp di
  paket gratis tidak bisa mengunduh dari PyPI, dan skrip peluncur tidak lagi
  mencoba `pip install` (dihapus 27 Nov 2026 setelah insiden argon2-cffi
  membuat server 502).

## 3. Pembaruan manual (bila otomatis gagal)

1. Buka konsol Bash PythonAnywhere.
2. `cd ~/office-quest && git pull --ff-only origin main`
3. Buka tab Web → tekan Reload.
4. Buka `/sehat` — harus `{"status":"ok"}`.

Bila `git pull` menolak (bukan fast-forward): JANGAN paksa. Ada perubahan di server
yang tidak ada di repo — periksa dulu dengan `git status` dan `git log`.
Bila auto-deploy tidak bisa, Joko yang menangani pembaruan manual setiap ada
perbaharuan.

## 4. Mengembalikan versi (rollback)

Cara aman (disarankan): batalkan commit yang bermasalah dengan `git revert` di repo
lokal, lalu dorong — auto-deploy jalan seperti biasa.

Cara darurat di server: `git reset --hard <commit>` lalu Reload. Setelah itu server
tidak lagi sejalan dengan `main` — sebelum pembaruan berikutnya, kembalikan dulu
dengan `git reset --hard origin/main` + Reload, kalau tidak `git pull` otomatis
akan gagal (bukan fast-forward).

## 5. Batas paket gratis (yang perlu diingat)

- 1 web worker: pemeriksaan yang datang bersamaan antre (menunggu, bukan gagal).
- Kuota CPU 100 detik/hari hanya untuk konsol dan tugas terjadwal, BUKAN untuk
  aplikasi web. Bila kuota habis, yang melambat adalah konsol; aplikasi web
  tetap jalan.
- Tidak ada MySQL, tugas terjadwal, dan SSH di paket gratis — database Tahap 2
  memakai SQLite (file di server).
- GitHub Pages: batas lunak 100 GB/bulan (sekitar 28.000 kali muat file game
  3,5 MB); bila lewat, GitHub memperlambat atau mengirim email — tidak pernah
  menagih.

## 6. Rahasia — jangan masuk repo

- Garam server (`OFFICE_QUEST_GARAM`): hanya di file privat server
  `~/.office-quest-garam` (chmod 600). Tidak ada di repo, tidak ada di `.env`.
- Token API PythonAnywhere: hanya sebagai rahasia GitHub
  `PYTHONANYWHERE_API_TOKEN` (Settings → Secrets and variables → Actions).
- `.env` dilindungi `.gitignore` (ditambahkan 27 Nov 2026); yang ada di repo
  hanya `backend/.env.example` (kosong, tanpa nilai).
- Bila rahasia bocor: ganti nilainya di tempat asalnya (buat garam baru di server
  + Reload; buat token API baru + perbarui rahasia GitHub). Jangan hanya
  menghapus dari repo — riwayat git tetap menyimpannya.

## 7. Bila ada yang rusak

- `/sehat` tidak menjawab: buka tab Web PythonAnywhere, tekan Reload, tunggu
  30 detik, cek lagi.
- Workflow merah: buka log run di tab Actions — lihat langkah mana yang gagal
  (reload API, atau `/sehat`). Bila reload API gagal, periksa rahasia
  `PYTHONANYWHERE_API_TOKEN` masih ada.
- Log galat: tab Web → Log files → Error log. Token tiket kadang tercatat di
  server log (access log) — itu diketahui dan perbaikannya ditunda
  (lihat `docs/keamanan-rilis.md`).
