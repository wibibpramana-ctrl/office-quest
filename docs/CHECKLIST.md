# CHECKLIST — Cek sebelum mengirim file Office Quest (Tahap 2)

Dipakai setiap kali ada perubahan pada game Office Quest (Tahap 2). File baru dikirim
kalau semua poin di bawah ini lolos; kalau ada yang gagal, revisi dulu sampai lolos.
Acuan: `project_tahap2_poppi.md` (rencana Tahap 2) dan keputusan Wibi 25 Nov 2026.

## Tahap 2 (dicek tiap penyerahan, mulai Langkah 1.1)

Bagian ini dicek Joko sebelum tiap file Tahap 2 dikirim. Semua poin
harus lolos; kalau ada yang gagal, revisi dulu sampai lolos.

**Umum Tahap 2:**
- [ ] File frontend tetap satu index.html; kode tidak dipecah dulu (pecah file adalah Tahap 3).
- [ ] Sintaks JS lolos node --check; kurung CSS seimbang.
- [ ] Teks yang dilihat pemain memakai bahasa Indonesia dan tanda baca tipografis (’ “ ”).
- [ ] Satu langkah kecil per permintaan: tidak ada fitur di luar yang diminta, tidak ada kode yang tidak diminta diubah.

**Perilaku identik (baseline rekonstruksi):**
- [ ] #uji 15 kasus tetap lolos dengan hasil sama seperti baseline rekonstruksi.
- [ ] 10 skenario manual baseline tetap berlaku (alur lulus tiga tugas, gagal, Ulang, simpanan lama, hint, pop-up, tiga lebar layar).
- [ ] Regresi penuh (1055 cek) tetap lolos bila menyentuh Tugas/Chat/Kantor.
- [ ] Simpanan lama (localStorage `office-quest-v1`) tetap terbaca dan termigrasi; tombol Ulang tetap berfungsi.

**Tidak ada rahasia di repo:**
- [ ] Tidak ada garam, kata sandi, token, atau kunci API di repositori (termasuk `backend/rules/`, `content/`, `design/`, `docs/`).
- [ ] Repositori hanya memuat contoh nama variabel rahasia, tanpa nilai.
- [ ] Tidak ada data pribadi pemain di repositori.

**Aturan cek berbentuk data:**
- [ ] Aturan cek ada di `backend/rules/` sebagai JSON, bukan kode yang tersebar.
- [ ] Tidak ada nilai harapan, aturan cek, atau generator jawaban di frontend (`index.html`).
- [ ] Konten game (`content/`) valid: placeholder lengkap, 3 hint dan 3 trik tiap tugas, tanda baca tipografis, tanpa rumus jawaban lengkap.

**Bukti bagian lain tidak berubah:**
- [ ] Bila menyentuh Tugas/Chat: fungsi pemeriksa, penilaian, dan hadiah identik dengan baseline (bukti diff tiap penyerahan).
- [ ] Bila menyentuh backend: 15 dari 15 fixtures paritas cocok (skor dan kode); generator identik untuk 200 seed (perbandingan hash); template identik untuk 20 seed.

**Akun / login / database:**
- [ ] Daftar, masuk, dan keluar akun bekerja di HP; kata sandi salah ditolak; sesi kedaluwarsa meminta masuk ulang.
- [ ] Kata sandi hanya disimpan sebagai hash (tidak pernah teks biasa).
- [ ] Progres (XP, koin, tugas, inventori, chat) tersimpan di server dan sama saat dibuka di perangkat lain.
- [ ] Migrasi simpanan lokal ke akun: XP, koin, chat, dan status tugas lama pindah utuh.

**Wawancara awal:**
- [ ] Wawancara muncul saat login pertama, sebagai percakapan dengan Pak Bima; bisa dilewati pemain.
- [ ] Semua pemain tetap mulai dari Level 1, apa pun hasil wawancaranya.
- [ ] Hasil wawancara tersimpan dan dipakai untuk menyesuaikan hint/kesulitan awal (atau bawaan bila dilewati).

**Tugas harian (bila sudah masuk Fase 7):**
- [ ] Tiga tugas per hari tampil; muat ulang tidak menggantinya; hari berganti memunculkan set baru.
- [ ] Tugas deterministik per pemain per hari; jenis yang sama tidak muncul dua hari berturut-turut.
- [ ] Brief harian masuk chat Pak Bima sekali per tugas.

**Keamanan unggahan (bila sudah masuk Fase 3):**
- [ ] Hanya .xlsx, maks 2 MB; .xlsm ditolak; teks bernama .xlsx ditolak; contoh bom arsip ditolak dengan kode galat jelas.
- [ ] Rumus dan makro tidak pernah dijalankan di server; isi file tidak pernah dicatat di log.

**File dan pengujian:**
- [ ] Tiap penyerahan disertai cara menguji 2–4 langkah + hasil yang seharusnya terlihat.
- [ ] Tiap fase yang mengubah layout diuji di PC sebelum dinyatakan selesai; Wibi menguji di PC minimal tiap akhir fase.
- [ ] Ukuran dan performa sesuai anggaran (Bagian 16 rencana Tahap 2) atau ada catatan pengecualian.

## Rekonstruksi (dicek tiap penyerahan, mulai Langkah 0.3)

Bagian ini dicek Poppi sebelum tiap file rekonstruksi dikirim. Semua poin
harus lolos; kalau ada yang gagal, revisi dulu sampai lolos. Acuan:
`project_rekontruksi_poppi.md` §4–§5 dan keputusan Wibi 23 Nov 2026 (§9/§10).

**Kerangka — berlaku semua halaman:**
- [ ] Rel ikon fiks di semua halaman termasuk Kantor: fixed di kiri tengah, 64 px saat tertutup → 224 px saat mengembang (hover/fokus), ikon garis SVG 22 px (bukan emoji), tepat 6 menu.
- [ ] Background sama di semua halaman: latar kantor cat air yang sudah ada dipakai ulang, tanpa gambar latar baru.
- [ ] Palet tetap Forest Cream; warna lewat variabel tema, tidak ditulis langsung di tiap halaman.
- [ ] Konten mengisi layar lebar: di 1366/1440/1920 px konten tidak tampak kecil di tengah (maks 1600 px, rata tengah).
- [ ] Navigasi 6 menu berpindah tanpa memuat ulang; di HP tetap bar bawah + lembar “Lainnya” seperti Tahap 1 (sampai versi HP dibangun — PC dulu, HP menyusul, Q11).

**Tiap halaman dalam (Chat, Tugas, Toko, Tantangan, Koleksi):**
- [ ] Layout 3 grid di samping rel ikon, pola sama di semua halaman; isi grid mengikuti brief §5 dokumen rencana (bila mockup dan brief berbeda, brief yang menang).
- [ ] Teks terbaca di atas panel kaca: panel cukup pekat, kontras dicek tiap penyerahan; brief, chat, dan harga tetap mudah dibaca.
- [ ] Target sentuh ≥44 px; fokus keyboard terlihat; dialog memakai role yang benar; hormati hemat gerak.

**Chat:**
- [ ] Chat tetap terpandu: tanpa kolom ketik, hanya chip + tombol hint/trik.
- [ ] List kontak hanya Pak Bima, Rina, Dito (+ monyet sebagai kontak placeholder; percakapannya menyusul di Tahap 2, Q9); “Kamu” tidak tampil di list kontak (Q10).
- [ ] Brief, hint/trik, dan balasan Pak Bima tetap seperti Tahap 1.

**Logika Tahap 1 tidak berubah:**
- [ ] Pemeriksa/penilaian tidak berubah: fungsi pemeriksa, penilaian, hadiah, dan generator identik dengan baseline (bukti diff tiap penyerahan yang menyentuh Tugas/Chat).
- [ ] #uji 15 kasus tetap lolos dengan hasil sama seperti baseline (`docs/baseline_rekonstruksi.md`), tiap fase yang menyentuh Tugas/Chat.
- [ ] 10 skenario manual baseline tetap berlaku (Kantor, pop-up karakter, navigasi, Chat, hint/trik, unggah benar/salah, tugas berikutnya terbuka, progres tersimpan, tombol Ulang).
- [ ] Simpanan lama (localStorage) tetap terbaca; tombol Ulang tetap berfungsi.

**Placeholder (keputusan Wibi 23 Nov 2026):**
- [ ] Tombol Beli (Toko) dan Ambil Tantangan tampil dulu dengan pesan “Segera hadir”; koin tidak berkurang, belum ada fungsi ekonomi (Q1).
- [ ] Ilustrasi baru (monyet, koala, pinguin, panda raksasa, beruang full-body) memakai placeholder emoji + nama sampai ilustrasi final dibuat (Q13).
- [ ] Harga, hadiah, dan daftar item/tantangan memakai nilai placeholder dari mockup, bukan keputusan final (Q4/Q5/Q6).
- [ ] Tombol di Koleksi tertulis “Simpan” (bukan “Save”) (Q12).

**File dan pengujian:**
- [ ] File tetap satu index.html; kode tidak dipecah dulu selama rekonstruksi (R1).
- [ ] Sintaks JS lolos node --check; kurung CSS seimbang.
- [ ] Ukuran file diabaikan selama fase rekonstruksi (R10).
- [ ] Tiap fase yang mengubah layout diuji di PC sebelum dinyatakan selesai; Wibi menguji di PC minimal tiap akhir fase (R11).

## Kembali ke Final Tahap 1 (23 Nov 2026)
- [x] Wibi membatalkan perombakan V5 (19.33 WIB) dan meminta kembali ke Final Tahap 1: file yang dikirim adalah arsip Tahap 1 (`workspace/your_files/office-quest/index.html`, 2.624.812 byte) — diverifikasi: 3 data URI gambar, nol penanda V5 (tanpa layar-chat, renderInfoChat, terapkanFilterKontak, jelaskanTugasLagi, foto karakter, chat-cari), 3 tugas + panel “Sebelum mulai” + halaman #uji ada, sintaks JS lolos node --check.
- [x] Versi V5 terakhir (tema inbox, 3.004.177 byte) disimpan sebagai cadangan (`office-quest-repo/index-v5-inbox-20261123.html`), tidak dihapus — bisa dikembalikan bila Wibi berubah pikiran.
- [x] Salinan repo (frontend/index.html) dipulihkan ke Final Tahap 1 (SHA-256 sama dengan arsip) supaya salinan kerja Poppi cocok dengan yang live.
- [x] Catatan: Final Tahap 1 ini SEBELUM perbaikan tata letak desktop (23 Nov 2026) — layar dalam di PC kembali kecil seperti semula. Bila Wibi mau perbaikan itu dipertahankan, pasang ulang di atas file ini.

## Poles Chat V5 — tema inbox, lepas Forest Cream (23 Nov 2026)
- [x] Tema inbox mengikuti referensi inbox (keputusan Wibi 17.44 WIB, membalik keputusan 15.46 WIB): latar abu terang #ececec, panel putih, teks gelap #1f2937, tombol/lencana gelap #111827, balon masuk hijau muda #dcf8c6, balon pemain putih bergaris tepi; diterapkan lewat override variabel di body.layar-chat sehingga Kantor dan halaman lain tetap Forest Cream.
- [x] Latar kantor tidak lagi dipakai di Chat (pengecualian latarChat di tampilkanLayar dihapus; aturan latar adegan + panel kaca dihapus; tidak ada sisa latarChat, blur 14 px, atau brightness 0.6); rel ikon kini solid (putih di Chat, hijau gelap di halaman lain) karena kaca tidak ada gunanya di atas latar datar.
- [x] Judul dan kepala memakai huruf biasa Nunito (bukan Patrick Hand); judul layar teks biasa tanpa pil; foto profil tanpa cincin emas; baris aktif kontak abu terang #f3f4f6 (lewat variabel).
- [x] Daftar kontak padat seperti mockup: tanpa baris peran (nama + pratinjau saja); kotak pencarian “Cari berdasarkan nama…” di atas daftar (menyaring tanpa membedakan huruf besar/kecil; filter bertahan setelah daftar dirender ulang).
- [x] Kontras tema inbox lolos WCAG AA: teks/panel 14,68; redup/panel 4,83; teks/gelembung hijau 12,78; putih/tombol gelap 17,74.
- [x] Tetap tanpa ketik bebas: chip balasan cepat seperti sebelumnya (chip utama kini gelap #111827, teks putih).
- [x] Pemeriksa/penilaian tidak berubah: diff fungsi — hanya init, perbaruiPenandaKontak, perbaruiTombolBantuan, renderDaftarKontak, renderPercakapan, tampilkanLayar yang berubah + 4 fungsi baru (jelaskanTugasLagi, perbaruiPratinjauKontak, renderInfoChat, terapkanFilterKontak); 101 fungsi lain identik dengan Tahap 1; tidak ada fungsi hilang.
- [x] Diuji Node (64 skenario: kelas layar, latar dihapus, chip, Jelaskan, panel kanan, foto, pratinjau, pencarian, regresi hint/trik/hadiah) — semua lolos; sintaks JS lolos node --check; kurung CSS seimbang (364/364); ukuran file 3.004.177 byte.

## Revisi Chat V5 — mendekati mockup (23 Nov 2026)
- [x] Rel ikon jadi navigasi global: tampil di SEMUA halaman kecuali Kantor (Kantor memakai sidebar melayangnya sendiri yang sudah disetujui Wibi); posisi tetap (fixed, tengah kiri, 14 px dari tepi) di tiap halaman; hover/fokus mengembang 64 → 224 px dan menampilkan teks menu (desktop ≥900 px); tidak ada lagi aturan rel ber-scope layar-chat.
- [x] Ikon navigasi garis (SVG) menggantikan emoji di 13 item (sidebar 6, menu bawah 4 + Lainnya, lembar Lainnya 2): gedung, balon chat, papan klip, tas belanja, trofi, bintang, hamburger; ukuran 22 px, warna mengikuti teks.
- [x] Foto profil memakai ilustrasi karakter (field foto di DATA_KARAKTER, data URI webp): daftar kontak, kepala percakapan, samping balon pesan (kiri untuk pesan masuk, kanan untuk pesan pemain), profil pemain dan daftar karakter di panel kanan; potongan bulat dengan wajah sebagai fokus (object-position 25%) di atas lingkaran krem; total data URI gambar kini 7, ukuran file 2.995.418 byte.
- [x] Panel kanan mengikuti mockup (≥1200 px): Profil Kamu (foto pemain, “Beruang Cokelat · jabatan Level n”), Poin & XP, Tugas Terkait (ketiga tugas + status: Selesai/Sedang dikerjakan/Baru/Terkunci), Profil Karakter (3 kartu rekan, klik membuka percakapannya, karakter aktif ditandai), tombol “Lihat Tantangan Mingguan” (membuka layar Tantangan); tombol “Buka Tugas” dan baris sisa hint dihapus (hitungan tetap di chip).
- [x] Daftar kontak: pratinjau pesan terakhir per kontak (diperbarui saat pesan baru masuk, termasuk hint/trik dan brief), titik hijau “online” di sudut foto; kepala percakapan: baris “● Online” di bawah peran.
- [x] Tetap tanpa ketik bebas: chip balasan cepat seperti sebelumnya (Jelaskan + Kirim laporan di chat Bima, hint/trik di Rina/Dito); tidak ada kolom ketik.
- [x] Halaman Tugas dan lainnya belum diberi latar kantor (menyusul sesuai pilihan Wibi); HP (<900 px) tidak berubah alurnya.
- [x] Pemeriksa/penilaian tidak berubah: diff fungsi — hanya init, perbaruiPenandaKontak, perbaruiTombolBantuan, renderDaftarKontak, renderPercakapan, tampilkanLayar yang berubah + 3 fungsi baru (jelaskanTugasLagi, perbaruiPratinjauKontak, renderInfoChat); 101 fungsi lain identik dengan Tahap 1; tidak ada fungsi hilang.
- [x] Diuji Node (56 skenario: kelas layar, chip, Jelaskan, panel kanan baru, foto, pratinjau, foto pesan, regresi hint/trik/hadiah) — semua lolos; sintaks JS lolos node --check; kurung CSS seimbang (364/364); tidak ada rujukan tersisa ke ID yang dihapus.

## Halaman Chat V5 (Glassy Sidebar) — digantikan revisi mockup di atas untuk panel kanan, rel, dan ikon
- [x] Latar halaman Chat memakai adegan kantor yang sudah ada (dipakai ulang lewat `.scene-wrap`, tanpa file gambar baru): jumlah data URI gambar tetap 3; ukuran file 2.644.237 byte (hanya +19 KB kode).
- [x] Panel daftar kontak, percakapan, panel kanan, dan bar atas menjadi kaca (color-mix 84% + blur 14 px); bila browser tidak mendukung, jatuh ke permukaan solid; balon pesan tetap solid sehingga teks terbaca.
- [x] Rel ikon melayang di tengah sisi kiri (desktop ≥900 px): lebar 64 px, tinggi 348 px, tidak menabrak bar atas di tinggi 600–1080 px; hover/fokus keyboard mengembang ke 224 px dan menampilkan teks menu; konten digeser 96 px ke kanan.
- [x] Panel kanan kontekstual tampil di ≥1200 px (info karakter, Poin & XP, tugas terkait + tombol Buka Tugas); tersembunyi di bawah 1200 px; grid chat tiga kolom (kontak 280–360 px, percakapan 496–587 px, panel 280 px) diverifikasi di 1200/1366/1440/1920 px.
- [x] Balasan cepat berbentuk chip: Pak Bima “Jelaskan lagi tugasnya” + “Kirim laporan”; Rina “Minta hint (n/3)”, Dito “Minta trik (n/3)”; chip min. 44 px; tidak ada kolom ketik bebas (tanpa AI chatbot).
- [x] “Jelaskan lagi tugasnya” menambahkan pesan pemain + brief tugas aktif dari Pak Bima dan tersimpan ke localStorage; tidak berfungsi bila bukan chat Bima atau tanpa tugas aktif.
- [x] Panel kanan mengikuti percakapan dan progres terkini (karakter aktif, sisa hint/trik, XP/koin, tugas aktif; semua tugas selesai → tombol Buka Tugas hidden).
- [x] HP (<900 px) tidak berubah alurnya (daftar → percakapan layar penuh + tombol kembali); menu bawah dan lembar “Lainnya” tidak berubah.
- [x] Halaman lain tidak berubah (Kantor, Tugas, Toko, Tantangan, Koleksi memakai navigasi dan tampilan lama).
- [x] Pemeriksa/penilaian tidak berubah: diff fungsi — hanya tampilkanLayar, renderPercakapan, perbaruiTombolBantuan, init yang berubah + 2 fungsi baru (jelaskanTugasLagi, renderInfoChat); 103 fungsi lain identik dengan Tahap 1.
- [x] Diuji Node (64 skenario: kelas layar, latar adegan, chip, Jelaskan, panel kanan, regresi hint/trik) — semua lolos; sintaks JS lolos node --check; kurung CSS seimbang (347/347).

## Perbaikan tata letak desktop (regresi)
- [x] Layar dalam (Tugas, Chat, Toko, Tantangan, Koleksi) melebar di desktop: konten mengisi area hingga maks 1200 px, rata tengah (1200 px → 972 px, 1366 px → 1113 px, 1440 px → 1176 px, 1920/2560 px → 1200 px).
- [x] Ukuran berskala proporsional (clamp/vw), bukan angka tetap: sidebar 180–240 px (205 di 1366, 216 di 1440, 240 di 1920), teks menu 1,05–1,15 rem, kolom kontak 300–360 px, Koleksi 615–760 px — diverifikasi di 1366, 1440, dan 1920 px.
- [x] Sidebar melayang Kantor memakai rumus yang sama (15vw, 180–240 px) dan tidak menutupi hotspot Rina di semua lebar (jarak 10 px di 1200, 13 px di 1366, 15 px di 1440).
- [x] Chat mengisi tinggi layar di desktop (panel percakapan memanjang ke bawah; tepi bawah 33 px di atas tepi layar di tinggi 768/1080/1440 px, tanpa gulir halaman).
- [x] HP (<900 px) dan desktop 900–1199 px tidak berubah (aturan baru hanya berlaku ≥1200 px).
- [x] Hanya CSS yang berubah: diff hanya penambahan 113 baris di satu media query baru, 0 baris diubah/dihapus; script identik dengan Tahap 1.
- [x] Kriteria baru "konten mengisi layar lebar" dicatat untuk dimasukkan ke CHECKLIST.md di Langkah 0.2.

## Fase 0, Langkah 0.1: Arsip Tahap 1 (regresi)
- [x] Salinan PROJECT.md Tahap 1 identik byte-per-byte dengan versi yang dipakai sekarang (checksum sama).
- [x] Salinan ditaruh di docs/arsip/ dengan nama project_tahap1.md (penamaan §7: huruf kecil + garis bawah).
- [x] PROJECT.md Tahap 1 tidak diubah.
- [x] Petunjuk membuat tag/rilis tahap1-final lewat browser HP sudah diberikan dan benar.
- [x] PROJECT.md Tahap 2 §3 dan §20 diperbarui.

## Panel “Sebelum mulai” (regresi)
- [x] Panel muncul hanya pertama kali (belum pernah ditutup); setelah ditutup tidak muncul lagi.
- [x] Isi panel: cara bermain 4 langkah, catatan progres tersimpan di browser, catatan butuh aplikasi spreadsheet.
- [x] Menutup panel (tombol/Esc/ketuk di luar) menandai sudah dilihat; Ulang tidak memunculkannya lagi.
- [x] Panel tidak muncul saat alamat berakhiran #uji.
- [x] Panel bisa dioperasikan keyboard (fokus masuk, perangkap Tab, Esc menutup, fokus kembali).
- [x] Panel tidak mengubah state game.
- [x] Fungsi game tidak berubah.

## Tinjauan lebar 360/768/1440 px (regresi)
- [x] Tidak ada elemen terpotong di 360, 768, dan 1440 px (semua layar: Kantor, Chat, Tugas, Toko, Tantangan, Koleksi, Uji).
- [x] Hotspot, label, dan pop-up tidak saling menutupi di ketiga lebar.
- [x] Semua area sentuh/klik minimal 44 px.
- [x] Kontras teks memenuhi ambang (teks biasa ≥4,5:1, teks besar ≥3:1).
- [x] Fokus keyboard terlihat di semua elemen interaktif.
- [x] Animasi mati saat prefers-reduced-motion: reduce.
- [x] Fungsi game tidak berubah (pemeriksa, penilaian, navigasi, penyimpanan).

## Halaman uji tersembunyi #uji (regresi)
- [x] Halaman hanya muncul bila alamat berakhiran #uji; tidak ada di navigasi; ada tombol kembali ke Kantor.
- [x] Lima varian jawaban dibuat dari template seed saat ini untuk tiap tugas (benar+rumus, nilai salah, manual, error, data diubah).
- [x] Tabel menampilkan skor/lulus/kode yang diharapkan vs sebenarnya untuk 15 file, dengan penanda cocok/beda + ringkasan.
- [x] Halaman uji tidak mengubah state game (tanpa chat/hadiah/penyimpanan).
- [x] Bila SheetJS belum termuat, tampil pesan ramah (tanpa crash).
- [x] Pemeriksa file dan penilaian tidak berubah.

## Catatan “Lihat hasil” tanpa hasil tersimpan (regresi)
- [x] “Lihat hasil” pada tugas tanpa hasil tersimpan menampilkan catatan penjelasan, bukan bagian hasil kosong.
- [x] Catatan hanya tampil di tampilan “Lihat hasil” tanpa hasil; hasil pemeriksaan normal tidak berubah.
- [x] Pemeriksa file dan penilaian tidak berubah.

## Sinkronisasi status tugas (regresi)
- [x] Satu sumber kebenaran: state.tugas[id].status (terkunci/baru/dikerjakan/selesai) + state.tugasAktif; semua layar membaca lewat satu fungsi.
- [x] Saat lulus: tugas selesai, berikutnya baru, tugasAktif pindah, brief terkirim sekali (tidak ganda).
- [x] Kartu Kantor: terkunci (gembok, tombol nonaktif), baru (“Baru” + “Mulai Tugas”), dikerjakan (“Lanjutkan”), selesai (“✓ Selesai” + “Lihat hasil”, tanpa “Baru”).
- [x] “Mulai Tugas”/“Lanjutkan” mengatur tugasAktif lalu membuka layar Tugas (tugas itu); “Lihat hasil” membuka layar Tugas dengan hasil terakhir.
- [x] Layar Tugas menampilkan tugasAktif; setelah lulus ada hasil + “Lanjut ke Tugas berikutnya”; semua selesai → ringkasan “Semua tugas selesai”.
- [x] Unduh template, “Kirim laporan”, lampiran merujuk tugas aktif; tugas terkunci tidak bisa dibuka.
- [x] Migrasi simpanan lama: status dihitung ulang dari progres tersimpan (tanpa konflik); tanpa hasil tersimpan, “Lihat hasil” tidak menampilkan hasil lama.
- [x] Pemeriksa file dan penilaian tidak berubah (regresi: skor/hadiah Tugas 1–3 tetap).

## Brief tugas di chat Pak Bima (regresi)
- [ ] Brief Tugas 1 terkirim saat permainan mulai; Tugas 2 setelah Tugas 1 lulus; Tugas 3 setelah Tugas 2 lulus.
- [ ] Tiap brief terkirim hanya sekali (tidak dobel setelah muat ulang/pindah layar); simpanan lama tanpa penanda tidak memicu kirim ulang Tugas 1.
- [ ] Pesan brief berisi teks brief + lampiran; tombol unduh mengunduh template tugas brief itu.
- [ ] Brief tersimpan di riwayat chat dan menambah penanda belum dibaca (menu Chat, daftar kontak, pop-up Pak Bima).
- [ ] Ucapan pop-up Pak Bima mengikuti tugas aktif (baru/dikerjakan; selesai bila semua tugas selesai).
- [ ] Tombol “Kirim laporan” di percakapan Pak Bima membuka halaman Tugas (tugas aktif); tersembunyi bila tidak ada tugas aktif.
- [ ] Tombol Ulang menghapus semua pesan brief dan membuat ulang dari Tugas 1.
- [ ] Pemeriksa file dan penilaian tidak berubah (regresi: skor/hadiah Tugas 1–3 tetap).

## Tugas 3 Penilaian Magang (regresi)
- [ ] DATA_TUGAS.penilaian_magang diisi: brief, hint Rina (3), trik Dito (3), checks JSON persis §12 (pass 70).
- [ ] Generator buatDataTugas3: seed sama → data sama; 10 nama peserta, Teori/Praktik 50–100, tepat satu peserta rata-rata 75.
- [ ] Tombol Unduh Template tampil untuk Tugas 3 dan mengunduh template Penilaian Magang.
- [ ] Mesin pemeriksa memakai generator Tugas 3 (dispatch dari aturan.task); nilai harapan dari seed; deteksi data diubah mencakup A2:C11.
- [ ] Evaluator mendukung avg(B,C) dan if(D>=75,'Lulus','Remedial'); batas 75 inklusif (>=) — peserta tepat 75 adalah Lulus.
- [ ] value_each mendukung nilai harapan teks (Lulus/Remedial) dengan perbandingan persis.
- [ ] Diuji dengan file uji Tugas 3: benar, nilai salah, teks salah, batas 75 (>) salah, angka manual, fungsi salah, ada error, data diubah, tanpa cache.
- [ ] Tugas 1 dan 2 tidak berubah (regresi).

## Tugas 2 Absensi Karyawan (regresi)
- [ ] DATA_TUGAS.absensi diisi: brief, hint Rina (3), trik Dito (3), checks JSON persis §12 (pass 70).
- [ ] Generator buatDataTugas2: seed sama → data sama; 10 nama karyawan, status H/I/A (±70/20/10%), G/H/I kosong, A12 “Total”.
- [ ] Tombol Unduh Template tampil untuk Tugas 2 dan mengunduh template Absensi.
- [ ] Mesin pemeriksa memakai generator Tugas 2 (dispatch dari aturan.task); nilai harapan dari seed; deteksi data diubah mencakup A2:F11.
- [ ] Evaluator mendukung ekspresi countif (kriteria per kolom) dan sum(kolom); JSON §12 dipakai apa adanya (value_each, tanpa jenis cek baru).
- [ ] Kode value_each yang gagal: “sum” bila rangenya di baris 12 ke bawah (baris total), selain itu “rowval”.
- [ ] Diuji dengan file uji Tugas 2: benar, nilai salah, angka manual, fungsi salah, ada error, data diubah, tanpa cache.
- [ ] Tugas 1 tidak berubah (regresi: generator, template, pemeriksaan Tugas 1 tetap jalan).

## Hadiah dan progres tugas (regresi)
- [ ] Lulus (≥70) memberi +100 XP dan +100 koin; skor ≥90 memberi +150 XP dan +150 koin (bukan +250).
- [ ] Level tiap 250 XP (Magang, Staff, Senior, Manager; maks Level 4); bar atas menampilkan level, jabatan, bar XP, dan koin terbaru.
- [ ] Hadiah hanya diberikan sekali (saat pertama lulus); gagal (<70) tanpa hadiah, status jadi “dikerjakan”, bisa unggah ulang.
- [ ] Tugas yang lulus ditandai “Selesai” di panel Jobdesk (tampil juga setelah muat ulang).
- [ ] Tugas berikutnya menjadi tugas aktif (halaman Tugas menampilkan tugas berikutnya).
- [ ] Tugas selesai tidak bisa diunggah ulang (kontrol unggah hanya untuk tugas aktif yang belum selesai); tombol Ulang mengembalikan semua tugas ke awal.
- [ ] Baris hadiah tampil di bagian hasil saat lulus (“Hadiah: +100 XP, +100 koin” / “Bonus: +150 XP, +150 koin”).
- [ ] Fitur lain tidak berubah.

## Balasan Pak Bima dan hasil pemeriksaan (regresi)
- [ ] Kalimat balasan Pak Bima tersimpan per kode (altered, nocache, err, rowval, sum, hard, ok90, ok70, fail), 2–3 variasi tiap kode, kalimat §13 sebagai variasi pertama.
- [ ] Kode masalah pertama (urutan mesin) memilih balasan; tanpa kode masalah, balasan dari skor (≥90 ok90, ≥70 ok70, <70 fail).
- [ ] Setelah pemeriksaan: chat Pak Bima mendapat pesan “Laporan terkirim” (pemain) + balasan bos, tersimpan di localStorage, lencana belum dibaca muncul.
- [ ] Halaman Tugas menampilkan skor, status lulus/belum lulus, dan daftar centang per aturan (label + poin + detail).
- [ ] Tombol “Lihat balasan Pak Bima” membuka percakapan Pak Bima di Chat.
- [ ] Tombol unggah .xlsx di halaman Tugas (asumsi: pemicu pemeriksaan) — hanya .xlsx, maks 2 MB, pesan ramah bila ditolak/rusak/offline.
- [ ] Fitur lain tidak berubah; tanpa perubahan XP/koin/status tugas di langkah ini.

## Mesin pemeriksa (regresi)
- [ ] Aturan cek Tugas 1 tersimpan sebagai JSON di data tugas (dari §12, pass 70).
- [ ] Mesin membaca .xlsx dengan SheetJS (cellFormula aktif); nilai dibaca dari cache, rumus dari .f.
- [ ] Jenis cek didukung: value, value_each, is_formula, formula_uses, no_errors, deteksi data diubah.
- [ ] Angka dibandingkan dengan toleransi 0,01.
- [ ] Keluaran: skor 0–100, lulus (≥70), daftar centang per aturan, kode masalah (altered, nocache, err, rowval, sum, hard).
- [ ] Diuji dengan 5 file uji: benar, nilai salah, angka manual, ada error, data diubah (plus rumus tanpa cache).
- [ ] Belum ada tampilan baru (mesin saja, unggah menyusul); fitur lain tidak berubah.

## Generator data dan unduh template (regresi)
- [ ] Generator pseudo-random memakai seed per pemain; data sama setiap kali seed sama.
- [ ] Template Tugas 1 sesuai §12: sheet “Data”, A Produk (10 baris), B Qty acak 5–50, C Harga acak kelipatan 500 (2.000–21.500), D Total kosong, A12 “Total Penjualan”, A13 “Rata-rata”.
- [ ] SheetJS dimuat dari CDN dengan versi dipatok.
- [ ] Tombol “Unduh Template” di halaman Tugas mengunduh file “Template Rekap Penjualan Mingguan.xlsx”.
- [ ] Tombol “Unduh Template” di lampiran chat Pak Bima mengunduh file yang sama.
- [ ] Bila SheetJS belum termuat, muncul pesan ramah (tidak error diam-diam).
- [ ] Fitur lain tidak berubah (pop-up, chip, navigasi, Chat, hint/trik, localStorage, efek adegan).

## Penyimpanan localStorage dan tombol Ulang (regresi)
- [ ] Progres tersimpan di localStorage: seed, xp, koin, status tugas, hint, riwayat chat, belum dibaca.
- [ ] Semua baca/tulis dibungkus try/catch; halaman tetap berjalan bila penyimpanan kosong/diblokir.
- [ ] Memuat ulang halaman memulihkan progres (riwayat chat, hitungan hint, penanda belum dibaca).
- [ ] Tombol “Ulang” di bar atas membuka konfirmasi; konfirmasi menghapus progres dan membuat seed baru, lalu kembali ke layar Kantor.
- [ ] Membatalkan konfirmasi tidak mengubah apa pun.
- [ ] Fitur lain tidak berubah (pop-up, chip, navigasi, Chat, Jobdesk, XP, efek adegan).

## Tombol hint dan trik di Chat (regresi)
- [ ] Chat Rina menampilkan tombol “Minta hint (n/3)”; chat Dito menampilkan tombol “Minta trik (n/3)”; chat Pak Bima tidak menampilkan tombol.
- [ ] Tiap klik menambahkan pesan pemain (“Boleh minta hint?” / “Boleh minta trik?”) lalu balasan berikutnya dari data (hint Rina / trik Dito).
- [ ] Balasan hint berlabel kecil “Hint”; balasan trik berlabel kecil “Trik”.
- [ ] Hitungan terpisah per karakter per tugas, maks 3 masing-masing; setelah 3 kali tombol nonaktif dan label menunjukkan (3/3).
- [ ] Teks diambil dari data tugas (field hint untuk Rina, field trik untuk Dito); tidak ada duplikasi teks hint/trik.
- [ ] Tidak ada pengurangan skor; fitur lain tidak berubah (daftar kontak, balon, lampiran, pop-up, navigasi, Jobdesk, XP, efek adegan).

## Layar Chat (regresi)
- [ ] Daftar kontak menampilkan Pak Bima, Rina, Dito (avatar, nama) dengan penanda belum dibaca (Bima: 1).
- [ ] Percakapan berupa balon: pesan masuk krem, pesan pemain emas muda.
- [ ] Pesan brief Pak Bima menampilkan lampiran file (chip nama file).
- [ ] Desktop: daftar kontak dan percakapan berdampingan.
- [ ] HP: daftar satu layar; ketuk kontak membuka percakapan layar penuh dengan tombol kembali.
- [ ] Tombol “Lanjut ke chat” di pop-up membuka chat karakter itu.
- [ ] Isi pesan dari data (sapaan DATA_KARAKTER, brief DATA_TUGAS); membuka percakapan menandai pesan sudah dibaca (lencana hilang).
- [ ] Tidak ada tampilan/perilaku lain yang berubah (pop-up, chip, navigasi, Jobdesk, XP, efek adegan).

## Objek data karakter dan tugas (regresi)
- [ ] DATA_KARAKTER berisi Pak Bima, Rina, Dito (dan Kamu tetap ada): nama, peran, avatar emoji, sapaan, ucapan {baru, dikerjakan, selesai}.
- [ ] Kalimat ucapan pop-up tidak digandakan — hanya satu salinan di DATA_KARAKTER, pop-up tetap membacanya dari sana.
- [ ] DATA_TUGAS Tugas 1 (rekap_penjualan) berisi id, judul, brief, hint Rina (3) dan hint Dito (3) persis dari PROJECT.md §12.
- [ ] Tugas 2 dan 3 tidak diubah (belum diisi).
- [ ] Tidak ada tampilan baru; pop-up, chip, navigasi, Jobdesk, XP berperilaku sama seperti sebelumnya.

## Efek ringan adegan (regresi)
- [ ] Hover atau fokus pada hotspot menampilkan sorotan emas tipis (outline lembut) pada area karakter.
- [ ] Saat ditekan, cincin emas berdenyut sekali (±300 ms), lalu pop-up muncul dengan transisi singkat.
- [ ] Cahaya lampu meja pemain berdenyut halus di sekitar 61/70; kilau layar di sekitar 66/78; uap tipis naik dari mug Rina di sekitar 27/57 (posisi dalam persen, mudah diubah lewat variabel).
- [ ] Animasi hanya memakai transform dan opacity, tanpa pustaka tambahan.
- [ ] Semua animasi mati jika prefers-reduced-motion aktif; animasi berhenti saat tab tidak aktif (document.hidden).
- [ ] Efek tidak menutupi hotspot atau label (klik hotspot tetap berfungsi).
- [ ] Karakter tidak bergerak; perilaku lain (pop-up, chip 2 detik, navigasi, Jobdesk, XP) tidak berubah.

## Pop-up percakapan karakter (regresi)
- [ ] Menekan karakter TIDAK langsung membuka Chat; tampil pop-up (avatar emoji, nama dan peran, satu kalimat ucapan, tombol “Lanjut ke chat” dan “Tutup”).
- [ ] HP: pop-up berupa lembar dari bawah layar. Desktop: kartu kecil dekat karakter.
- [ ] Tekan di luar pop-up atau Esc menutup pop-up.
- [ ] Pop-up memakai role="dialog" dan aria-modal; fokus masuk ke pop-up saat dibuka dan kembali ke karakter saat ditutup.
- [ ] “Lanjut ke chat” membuka layar Chat dan menandai percakapan karakter itu aktif (disimpan di state).
- [ ] Menekan “Kamu” membuka pop-up profil: nama, level, tombol “Buka Koleksi” (membuka layar Koleksi).
- [ ] Kalimat ucapan berasal dari data per karakter dan kondisi tugas (baru/dikerjakan/selesai); saat ini kondisi “baru” (Pak Bima “Pagi! Sudah cek jobdesk hari ini?”, Rina “Bingung rumus? Tanya aku ya.”, Dito “Butuh trik cepat? Aku ada.”).
- [ ] Gaya Forest Cream; chip label 2 detik, posisi hotspot, navigasi, Jobdesk, XP tidak berubah.
- [ ] Layar Chat tetap judul saja (isinya belum dibangun).

## Label adegan Kantor (regresi)
- [ ] HP (di bawah 900 px): label “Kamu” font 11 px, padding 2 px 8 px, hanya tulisan “Kamu” (tanpa jabatan), di atas kepala (transform translate(-50%, -100%)), titik jangkar x 75,1% y 66% dari pembungkus adegan.
- [ ] Desktop: label “Kamu” tidak berubah (tetap “Kamu · Magang” 12,5 px).
- [ ] Chip karakter lain hanya nama (tanpa jabatan), font 12–13 px, muncul di atas kepala saat ditekan/difokus, titik jangkar Pak Bima 48,7/25, Rina 24,5/39, Dito 87,7/39.
- [ ] Label tidak menutupi wajah karakter.
- [ ] Perilaku tampil tidak berubah: chip muncul saat ditekan/difokus/di-hover dan hilang sendiri setelah 2 detik.
- [ ] HP: tombol “Mulai Tugas” tidak tertutup bar bawah di 360 dan 768 px (padding bawah sudah cukup atau diperbaiki).
- [ ] Fitur lain tidak berubah: klik hotspot tetap membuka Chat; posisi hotspot, adegan, navigasi, Jobdesk, XP tidak berubah.

## Label karakter hilang 2 detik (regresi)
- [ ] Label semua karakter (termasuk “Kamu”) hanya muncul saat hotspot disentuh, di-hover, atau difokus; tidak ada label yang selalu tampil.
- [ ] Label karakter yang diklik hilang sendiri setelah 2 detik.
- [ ] Label tidak tertinggal tampil setelah kembali ke layar Kantor (tidak ada hover menempel di layar sentuh).
- [ ] Klik hotspot membuka pop-up (tidak lagi langsung ke Chat); label tetap hilang setelah 2 detik.
- [ ] Label tetap terbaca: chip nama 12–13 px (HP: label “Kamu” 11 px), satu baris, maks 35% lebar adegan.
- [ ] Fokus keyboard tetap terlihat jelas pada hotspot.
- [ ] Logika lain (posisi hotspot, adegan, navigasi, Jobdesk, XP) tidak berubah.

## Navigasi 6 menu (regresi)
- [ ] Keenam layar (Kantor, Chat, Tugas, Toko, Tantangan, Koleksi) berpindah tanpa memuat ulang halaman.
- [ ] Desktop (900 px ke atas): keenam menu ada di sidebar kiri.
- [ ] HP: bar bawah 5 slot (Kantor, Chat, Tugas, Toko, Lainnya); “Lainnya” membuka lembar dari bawah berisi Tantangan dan Koleksi.
- [ ] Lembar “Lainnya” bisa ditutup (tombol tutup, ketuk di luar, tombol Esc); memilih Tantangan atau Koleksi memindah layar dan menutup lembar.
- [ ] Saat Tantangan atau Koleksi aktif di HP, slot “Lainnya” ditandai aktif.
- [ ] Penanda belum dibaca tetap di Chat.
- [ ] Konten punya padding bawah agar elemen terakhir tidak tertutup bar bawah di HP.
- [ ] Chat dan Tugas: judul saja.
- [ ] Toko: judul, satu kalimat penjelasan, dan kartu “Segera hadir”.
- [ ] Tantangan: judul, satu kalimat penjelasan, dan kartu “Segera hadir”.
- [ ] Koleksi: pesan “Belum ada item. Beli di Toko.” dan lima slot kosong berlabel Kepala, Wajah, Baju, Aksesori, Meja di sekitar pratinjau pemain (emoji sementara).
- [ ] Menu aktif ditandai dan sinkron di sidebar, bar bawah, dan lembar Lainnya.
- [ ] Semua menu dan lembar bisa dioperasikan dengan keyboard (Tab, Enter/Spasi, Esc), fokus terlihat jelas.
- [ ] Gaya Forest Cream; logika lain (adegan, hotspot, Jobdesk, XP, koin) tidak berubah.

## Adegan gambar utuh + hotspot (regresi)
- [ ] Adegan memakai satu gambar bg_kantor_karakter.webp sebagai latar (lebar penuh, tinggi menyesuaikan); karakter terpisah dan placeholder emoji dihapus dari tampilan utama.
- [ ] 4 hotspot transparan di posisi persen yang disetujui: Pak Bima left 42% top 22% w 13% h 22%; Rina left 17% top 39% w 14% h 25%; Dito left 81% top 40% w 13% h 31%; Kamu left 68% top 68% w 13% h 31%.
- [ ] Klik atau Enter pada hotspot membuka layar Chat.
- [ ] Label chip kecil (font 12–13 px, satu baris “Nama · Peran”, maks 35% lebar adegan), muncul saat disentuh atau difokus; label “Kamu” selalu tampil kecil.
- [ ] Fokus keyboard terlihat jelas pada hotspot.
- [ ] Bila gambar gagal dimuat, tampil adegan lama dengan emoji sebagai cadangan.
- [ ] Gambar disimpan sebagai file di assets/, bukan di dalam HTML.
- [ ] Halaman Chat dan Tugas tidak berubah isinya; tidak ada fitur baru di luar langkah ini.

## Layout overlay latar penuh (regresi)
- [ ] Gambar latar kantor (bg_kantor.webp) memenuhi satu layar penuh di 360, 768, dan 1440 px, tanpa ruang kosong atau terpotong.
- [ ] Bar atas, Jobdesk, dan navigasi menjadi panel mengambang di atas gambar latar, bukan kolom terpisah di samping adegan.
- [ ] Panel terbaca jelas di atas gambar: latar panel cukup kontras dan konsisten dengan Forest Cream, teks tidak tenggelam di gambar.
- [ ] Karakter dan hotspot-nya tetap di tempat yang benar dan tidak tertutup panel.
- [ ] Di HP (di bawah 900 px): panel menumpuk rapi di atas gambar tanpa menutupi karakter atau satu sama lain, menu bawah tetap.
- [ ] Isi tidak berubah: karakter, tugas, navigasi, dan palet Forest Cream sama seperti sebelumnya.

## Navigasi (regresi)
- [ ] Keenam menu memindahkan layar dengan benar.
- [ ] Menu aktif ditandai, dan penandanya sinkron antara sidebar (desktop), menu bawah (HP), dan lembar Lainnya.
- [ ] Halaman Chat dan Tugas masih kosong, hanya judul saja (belum ada isi lain).
- [ ] Hotspot karakter di adegan membuka pop-up saat diklik atau ditekan Enter (tidak langsung membuka Chat).
- [ ] Semua tombol dan menu bisa dioperasikan dengan keyboard (Tab, lalu Enter atau Spasi), dan fokus keyboard terlihat jelas.

## Tata letak dan adegan (regresi dari langkah 1.3)
- [ ] Di bawah 900 px: satu kolom, panel menumpuk rapi di atas gambar latar, menu bawah tetap terlihat.
- [ ] Di 900 px ke atas: panel mengambang di atas gambar latar penuh, tanpa menu bawah.
- [ ] Adegan mengisi lebar layar dan tingginya menyesuaikan, tanpa ruang kosong besar di bawahnya.
- [ ] Posisi karakter benar: Pak Bima tengah atas di ruang kaca, Rina kiri, Dito kanan, pemain kanan bawah.
- [ ] Di kartu Jobdesk, “Dari Pak Bima” dan “Kirim sebelum jam 5” tampil sebagai dua baris terpisah dan tidak terpotong.
- [ ] Bar XP: jalur gelap (#0F2A24) dengan isi emas (#D8C28A); pada 0 XP terlihat kosong.
- [ ] Teks label karakter 12–13 px dan tetap terbaca.

## Tampilan umum
- [ ] Tidak ada elemen terpotong dan tidak ada gulir horizontal pada lebar 360, 768, dan 1440 px.
- [ ] Mode gelap dan mode terang sama-sama terbaca (warna mengikuti pengaturan perangkat).
- [ ] Font judul tulisan tangan dan isi Nunito tampil, dengan fallback bila font gagal dimuat.
- [ ] Tidak ada fitur baru di luar yang diminta pada langkah ini.
- [ ] File tetap satu `index.html` dan namanya benar.
