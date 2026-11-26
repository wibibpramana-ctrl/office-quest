# Office Quest

Game simulasi kantor berbasis web untuk belajar Excel. Pemain menerima
tugas dari bos lewat chat, mengunduh template `.xlsx`, mengerjakannya di
aplikasi spreadsheet, lalu mengunggah hasilnya untuk diperiksa.

[![Tes](https://github.com/wibibpramana-ctrl/office-quest/actions/workflows/tes.yml/badge.svg)](https://github.com/wibibpramana-ctrl/office-quest/actions/workflows/tes.yml)

- Mainkan: https://wibibpramana-ctrl.github.io/office-quest/
- Rencana Tahap 2: `docs/project_tahap2_poppi.md`
- Backend (Python, FastAPI): `backend/` — lihat `backend/README.md`

## Tes otomatis

Tiap dorongan ke `main` menjalankan workflow **Tes** (`.github/workflows/tes.yml`):
tes backend (pytest), validasi konten, regresi frontend, dan pemindaian
rahasia. Push dengan tes gagal ditandai merah; push bersih hijau.

Jalankan lokal sebelum mendorong:

```bash
cd backend && python -m pytest -q   # tes backend
node scripts/validasi-konten.js     # validasi konten
node scripts/uji-frontend.js        # regresi frontend (butuh: npm install --no-save xlsx@0.18.5)
```
