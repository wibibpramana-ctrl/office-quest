# Ukur beban backend (3.8)

Diukur 26 Nov 2026 dengan `backend/scripts/ukur-beban.py`
(`cd backend && python scripts/ukur-beban.py`).

## Lingkungan ukur

- Python 3.12.3, Linux x86_64, 4 CPU (mesin pengembangan ini)
- Pengukuran lewat TestClient (tanpa jaringan, tanpa cold start)

## Hasil

| Ukuran | Hasil | Batas | Status |
| --- | --- | --- | --- |
| `/periksa` file 1,79 MB (60.002 sel) | **3,68 detik** | < 5 detik | LOLOS |
| 20x `/periksa` beruntun (file template 5 KB) | **20/20 tanpa galat**, total 0,35 detik, rata-rata 18 ms, tercepat 16 ms, terlambat 21 ms | tanpa galat | LOLOS |

File besar dibuat deterministik (seed 42): sheet "Data" berisi 2 sel
+ sheet "DataBesar" berisi 60.000 sel string acak 30 karakter —
di bawah batas unggahan (2 MB) dan batas sel (100.000).

## Catatan

- File 2 MB memakai 73% anggaran waktu (3,68 dari 5 detik) karena
  file dibaca 3 kali: sekali oleh validasi (aliran baca) dan dua kali
  oleh pemeriksa (rumus + nilai cache). Masih di bawah batas waktu
  proses 10 detik (3.5).
- Mesin gratis Render berbagi CPU dan bisa lebih lambat, ditambah
  cold start saat server baru bangun. **Ukur ulang setelah deploy
  (4.2)**; bila melewati 5 detik di sana, pilihannya: naikkan batas
  atau kurangi jumlah pembacaan file.
