# Baseline Perilaku Rekonstruksi (Tahap 2, Langkah 0.3)

Dokumen ini merekam perilaku game Office Quest versi rekonstruksi (Fase 0–12 + 12.4–12.6)
sebelum pekerjaan Tahap 2 dimulai. Setiap perubahan Tahap 2 harus menjaga perilaku ini
tetap sama, kecuali yang memang diubah oleh langkah itu sendiri (dan dicatat di Log).

- **Sumber:** `index.html` 3.068.361 byte, SHA-256 `e8a8831175193382…`
- **Commit:** `8d4b237f` ("Alih ke versi rekonstruksi (Fase 0-12 + 12.4-12.6)")
- **Tag:** `rekonstruksi-final` (menunjuk commit `7f387d92`, beserta arsip rencana di `docs/arsip/`)
- **Alamat publik:** https://wibibpramana-ctrl.github.io/office-quest/
- **Kunci simpanan:** `office-quest-v1` (localStorage)
- **CSS:** 679/679 aturan seimbang; **JS:** lolos `node --check`
- **Direkam:** 25 Nov 2026 (Langkah 0.3)

## 1. Hasil `#uji` (15 kasus)

Halaman uji tersembunyi `#uji` menjalankan pemeriksa ke 15 file (3 tugas × 5 varian).
Skor yang diharapkan vs sebenarnya harus cocok semua (15/15).

| Tugas | Benar | Nilai salah | Angka manual | Ada error | Data diubah |
|---|---|---|---|---|---|
| Rekap Penjualan (T1) | 100, [] | 70, [rowval] | 70, [hard] | 50, [err] | 100, [altered] |
| Absensi (T2) | 100, [] | 55, [rowval] | 70, [hard] | 20, [err] | 100, [altered] |
| Penilaian Magang (T3) | 100, [] | 75, [rowval] | 70, [hard] | 55, [err] | 100, [altered] |

## 2. Sepuluh skenario manual

1. **Alur lulus tiga tugas:** Tugas 1 → 2 → 3 lulus berurutan; tiap lulus memberi hadiah (+100/+100, atau +150/+150 bila ≥90); tugas berikutnya terbuka; brief berikutnya terkirim sekali.
2. **Gagal (skor <70):** tanpa hadiah, status tugas jadi “dikerjakan”, bisa unggah ulang.
3. **Tombol Ulang:** konfirmasi → progres terhapus, seed baru, kembali ke layar Kantor, Tugas 1 jadi tugas aktif.
4. **Simpanan lama dimuat:** muat ulang memulihkan XP, koin, status tugas, chat, hint, dan penanda belum dibaca; simpanan lama (format lama) dimigrasikan otomatis.
5. **Hint Rina:** tombol “Minta hint (n/3)” di chat Rina; maks 3 per tugas; balasan berlabel “Hint”.
6. **Trik Dito:** tombol “Minta trik (n/3)” di chat Dito; maks 3 per tugas; balasan berlabel “Trik”.
7. **Pop-up karakter:** klik hotspot → pop-up (nama, peran, ucapan sesuai kondisi tugas); “Lanjut ke chat” membuka chat karakter itu; “Kamu” membuka pop-up profil.
8. **Lebar 360 px (HP):** tidak ada elemen terpotong; menu bawah 6 item mengambang; header dua baris (Level + angka XP + bar XP).
9. **Lebar 768 px:** tidak ada elemen terpotong; layout satu kolom di bawah 900 px.
10. **Lebar 1440 px (PC):** konten mengisi layar (maks 1200 px, rata tengah); sidebar 180–240 px; Chat tiga kolom 25%/1fr/27% di ≥1200 px, tinggi tetap 590 px.

## 3. Hasil uji Node (regresi penuh)

Dijalankan 25 Nov 2026 dari `~/workspace/oq-test/` (harness uji-2.4 s.d. uji-11).
**Total: 1055 lolos, 0 gagal.**

| Harness | Lolos | Gagal |
|---|---|---|
| uji-2.4 | 55 | 0 |
| uji-2.5 | 46 | 0 |
| uji-2.6 | 25 | 0 |
| uji-3.1 | 32 | 0 |
| uji-3.2 | 17 | 0 |
| uji-3.3 | 18 | 0 |
| uji-3.4 | 21 | 0 |
| uji-3.5 | 16 | 0 |
| uji-4.1 | 19 | 0 |
| uji-4.2 | 12 | 0 |
| uji-4.3 | 18 | 0 |
| uji-4.4 | 9 | 0 |
| uji-5.1 | 22 | 0 |
| uji-5.2 | 21 | 0 |
| uji-5.3 | 21 | 0 |
| uji-6.1 | 30 | 0 |
| uji-6.2 | 21 | 0 |
| uji-6.3 | 15 | 0 |
| uji-6.4 | 19 | 0 |
| uji-6.5 | 62 | 0 |
| uji-6.6 | 36 | 0 |
| uji-7.1 | 15 | 0 |
| uji-7.2 | 15 | 0 |
| uji-8.1 | 25 | 0 |
| uji-8.2 | 8 | 0 |
| uji-9.1 | 31 | 0 |
| uji-9.2 | 20 | 0 |
| uji-9.3 | 26 | 0 |
| uji-9.4 | 24 | 0 |
| uji-9.5 | 24 | 0 |
| uji-9.6 | 15 | 0 |
| uji-10.1 | 17 | 0 |
| uji-10.2 | 44 | 0 |
| uji-10.3 | 40 | 0 |
| uji-10.4 | 57 | 0 |
| uji-10.5 | 33 | 0 |
| uji-10.6 | 23 | 0 |
| uji-11 | 103 | 0 |
| **Total** | **1055** | **0** |

## 4. Perilaku kunci yang harus dipertahankan

- **Hadiah:** lulus ≥70 → +100 XP/+100 koin; ≥90 → +150/+150 (bonus menggantikan); sekali saja per tugas.
- **Level:** tiap 250 XP (Magang/Staff/Senior/Manager, maks L4).
- **Status tugas:** satu sumber kebenaran `state.tugas[id] = {status, hasilTerakhir}` + `state.tugasAktif`.
- **Brief:** terkirim sekali per tugas; brief tugas selesai yang hilang dipulihkan `perbaikiRiwayatChat()` (12.4).
- **Bar aksi chat:** bila tidak ada tugas aktif dan semua tugas selesai → tampil “Semua tugas selesai 🎉” (12.5).
- **Bar XP HP:** pil Level + angka XP + bar emas tampil di HP seperti PC (12.6).
- **Pemeriksa/penilaian:** fungsi pemeriksa, penilaian, dan hadiah identik dengan baseline ini.
- **Koleksi:** hanya Beruang terbuka; Panda/Koala/Pinguin terkunci (Koala 500, Pinguin 800); pratinjau mengikuti karakter pilihan.
- **Chat terpandu:** tanpa kolom ketik bebas; hanya chip + tombol hint/trik.
