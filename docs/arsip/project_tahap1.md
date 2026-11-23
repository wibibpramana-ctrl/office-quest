# PROJECT.md: Office Quest (Tahap 1)

> Tempel seluruh file ini di awal setiap sesi baru dengan AI. Perbarui bagian 3 (Status) dan bagian 20 (Log) setelah tiap langkah selesai.

## 1. Ringkasan
Office Quest adalah website game belajar Excel yang dikemas sebagai simulasi kerja di kantor. Pemain menerima tugas dari bos lewat chat, mengunduh file Excel, mengerjakannya di aplikasi spreadsheet, lalu mengunggah hasilnya. Sistem memeriksa file dan bos membalas dengan feedback. Rekan kerja memberi hint. Pemain mendapat XP dan koin, lalu naik jabatan.

- **Pemilik:** pemula total dalam membuat website, bekerja dari browser HP.
- **Bahasa antarmuka:** Indonesia, santai tapi sopan, memakai "kamu".
- **Tahap sekarang:** Tahap 1, prototipe yang bisa dimainkan, tanpa akun dan tanpa server.

## 2. Aturan kerja untuk AI
1. Jelaskan dengan bahasa sederhana. Pemilik pemula dan tidak membaca kode.
2. Kerjakan **satu langkah kecil per permintaan**. Jangan menambah fitur di luar yang diminta.
3. Selalu beri **kode lengkap** untuk file yang diubah (jangan potongan), dan sebutkan bagian mana yang berubah.
4. Jangan menghapus atau menulis ulang fitur yang sudah jalan kecuali diminta.
5. Setelah kode, beri **cara menguji** dalam 2 sampai 4 langkah dan hasil yang seharusnya terlihat.
6. Jika ada pilihan teknis, rekomendasikan satu dan beri alasan satu kalimat.
7. Jika permintaan ambigu, ajukan maksimal satu pertanyaan, atau nyatakan asumsimu lalu lanjut.
8. Teks yang terlihat pemain memakai tanda baca tipografis (’ “ ”) dan bahasa Indonesia.
9. Jangan meminta atau menulis kunci rahasia. Tidak ada kunci rahasia di tahap ini.

## 3. Status saat ini
- **Sudah ada:** prototipe awal satu file HTML (Kantor, Chat, Tugas 1 dengan pemeriksaan di browser) sebagai referensi. Halaman Kantor Forest Cream dengan adegan satu gambar utuh (`assets/bg_kantor_karakter.webp`, 2096x1184, 335 KB) dan empat hotspot. Tampilan desktop sudah oke. Navigasi 6 menu selesai 22 Nov 2026: Kantor, Chat, Tugas, Toko, Tantangan, Koleksi berpindah layar tanpa memuat ulang; desktop keenamnya di sidebar kiri; HP bar bawah 5 slot (Kantor, Chat, Tugas, Toko, Lainnya) dengan lembar dari bawah berisi Tantangan dan Koleksi; Toko dan Tantangan placeholder “Segera hadir”; Koleksi placeholder 5 slot kosong; Chat dan Tugas tetap judul saja. Dicek dengan CHECKLIST.md, semua poin lolos. Label karakter diseragamkan 22 Nov 2026: “Kamu · Magang” tidak lagi selalu tampil; semua chip hanya muncul saat hotspot disentuh, di-hover (hanya perangkat hover asli), atau difokus, lalu hilang sendiri setelah 2 detik; pindah layar membersihkan semua chip dan timer. Dicek dengan CHECKLIST.md, semua poin lolos. Label adegan Kantor diperbaiki 22 Nov 2026: chip Pak Bima/Rina/Dito hanya nama (12,5 px) di atas kepala pada titik jangkar (Bima 48,7/25, Rina 24,5/39, Dito 87,7/39); HP: label “Kamu” 11 px, padding 2 px 8 px, hanya “Kamu”, di atas kepala pada jangkar 75,1/66; desktop label “Kamu” tidak berubah; padding bawah HP 96 px sudah cukup untuk bar bawah 60 px. Dicek dengan CHECKLIST.md, semua poin lolos. Pop-up percakapan karakter selesai 22 Nov 2026: menekan karakter membuka pop-up (avatar emoji, nama dan peran, ucapan dari data per kondisi tugas — saat ini “baru”), bukan langsung Chat; HP lembar dari bawah, desktop kartu 300 px dekat karakter; tutup lewat tombol, ketuk di luar, atau Esc; role="dialog" + aria-modal, fokus masuk ke pop-up dan kembali ke karakter; “Lanjut ke chat” membuka Chat dan menyimpan karakter aktif di state.chatAktif; “Kamu” membuka pop-up profil (nama, level, “Buka Koleksi”). Dicek dengan CHECKLIST.md, semua poin lolos. Efek ringan adegan selesai 22 Nov 2026: sorotan emas tipis saat hover/fokus hotspot; cincin emas berdenyut sekali ±300 ms saat ditekan lalu pop-up muncul (transisi 0,18 dtk); efek lingkungan via variabel CSS --fx-* (lampu 61/70, layar 66/78, uap 27/57); hanya transform/opacity; mati saat prefers-reduced-motion, berhenti saat tab tidak aktif. Dicek dengan CHECKLIST.md, semua poin lolos. Objek data karakter dan tugas selesai 22 Nov 2026: DATA_KARAKTER (Pak Bima, Rina, Dito) dilengkapi field sapaan (usulan, karena §8 belum memuat teks resmi); ucapan tetap satu salinan di objek yang sama; DATA_TUGAS Tugas 1 diisi id, brief, hint Rina/Dito (3 tiap karakter) persis dari §12; Tugas 2/3 belum diisi; hanya data, tanpa tampilan baru. Dicek dengan CHECKLIST.md, semua poin lolos. Layar Chat selesai 22 Nov 2026: daftar kontak (avatar, nama, peran, penanda belum dibaca; Bima: 1), balon percakapan (masuk krem, pemain emas muda), chip lampiran “Template Rekap Penjualan Mingguan.xlsx” di brief Pak Bima (tampilan saja); desktop daftar kiri + percakapan kanan berdampingan (bawaan Pak Bima); HP daftar satu layar, ketuk kontak membuka percakapan layar penuh dengan tombol kembali; “Lanjut ke chat” membuka chat karakter itu; isi pesan dari data; membuka percakapan menandai sudah dibaca; belum ada tombol hint dan kolom kirim pesan. Dicek dengan CHECKLIST.md, semua poin lolos. Tombol hint dan trik di Chat selesai 22 Nov 2026: Rina “Minta hint (n/3)” (3 tingkat: konsep, nama fungsi/lokasi sel, cara kerja), Dito “Minta trik (n/3)” (shortcut, cek hasil, simpan file); tiap klik menambah pesan pemain + balasan berlabel “Hint”/“Trik”; hitungan per karakter per tugas, maks 3, nonaktif di (3/3); data direstrukturisasi jadi field hint (Rina) dan trik (Dito); tanpa pengurangan skor. Dicek dengan CHECKLIST.md, semua poin lolos. Penyimpanan localStorage dan tombol Ulang selesai 22 Nov 2026: kunci “office-quest-v1” berisi seed, xp, koin, tugas, hint, chat, belumDibaca; dimuat sebelum render (validasi bentuk, gagal → mulai segar); simpan otomatis setelah perubahan state; semua baca/tulis try/catch; tombol “Ulang” di bar atas + dialog konfirmasi kustom; “Ya, ulang” menghapus progres, seed baru, kembali ke Kantor. Dicek dengan CHECKLIST.md, semua poin lolos. Generator data dan unduh template selesai 22 Nov 2026: PRNG seed per pemain (FNV-1a + mulberry32; seed sama → data sama, diverifikasi Node 200 seed); template Tugas 1 sesuai §12 (sheet “Data”, 10 produk tetap, Qty 5–50, Harga kelipatan 500 2.000–21.500, Total kosong, A12/A13); SheetJS 0.18.5 cdnjs; tombol “Unduh Template” di halaman Tugas dan lampiran chat Bima; offline → toast ramah. Dicek dengan CHECKLIST.md, semua poin lolos. Mesin pemeriksa generik selesai 22 Nov 2026: aturan cek Tugas 1 tersimpan sebagai JSON di data tugas persis dari §12 (7 cek, total 100 poin, lulus ≥70); mesin murni membaca workbook SheetJS (cellFormula aktif), nilai harapan dihitung dari data seed, toleransi 0,01, nilai dari cache, rumus dari .f; mendukung value, value_each, is_formula, formula_uses, no_errors, dan deteksi data diubah; keluaran skor, lulus, daftar centang per aturan, dan kode masalah terurut tetap (altered, nocache, err, rowval, sum, hard); nilai total yang salah → sum, rowval hanya bila ada nilai terbaca yang salah; belum ada UI unggah/tampilan hasil. Diuji dengan Node + SheetJS 0.18.5 pada 7 skenario file uji (benar 100, satu baris salah 35, angka manual 70, ada error 50, data diubah 100, tanpa cache 35, nilai D12 salah 80) — semua lolos. Dicek dengan CHECKLIST.md, semua poin lolos. Balasan Pak Bima dan hasil pemeriksaan selesai 22 Nov 2026: kalimat balasan per kode tersimpan di DATA_FEEDBACK (9 kode: altered, nocache, err, rowval, sum, hard, ok90, ok70, fail; 3 variasi tiap kode, kalimat §13 sebagai variasi pertama, variasi 2–3 usulan); kode masalah pertama (urutan mesin) memilih balasan, tanpa kode masalah balasan dari skor (≥90 ok90, ≥70 ok70, <70 fail), variasi dipilih acak; tombol “Unggah Laporan (.xlsx)” di kartu tugas aktif (hanya .xlsx, maks 2 MB, pesan toast ramah bila ditolak/rusak/offline; input dikosongkan setelah ditangani; kontrol disembunyikan bila tugas aktif belum punya checks); setelah pemeriksaan chat Pak Bima menerima “Laporan terkirim” + balasan bos (tersimpan, lencana belum dibaca naik 1); halaman Tugas menampilkan bagian hasil (skor, Lulus/Belum lulus, daftar centang per aturan dengan detail) + tombol “Lihat balasan Pak Bima” yang membuka chat Pak Bima; hasil tampil di sesi ini saja; tanpa perubahan XP/koin/status tugas. Diuji dengan Node + SheetJS 0.18.5 pada 9 skenario ujung-ke-ujung (benar 100→ok90, angka manual 70→hard, satu baris salah 35→rowval, data diubah 100→altered, nilai D12 salah 80→sum, ada error 50→err, D12 kosong 70→ok70, semua kosong 5→fail, tanpa cache 35→nocache) — semua lolos. Dicek dengan CHECKLIST.md, semua poin lolos. Hadiah dan progres tugas selesai 22 Nov 2026: lulus (≥70) +100 XP/+100 koin, skor ≥90 +150 XP/+150 koin (bonus menggantikan, bukan ditambah), gagal tanpa hadiah dan status jadi “dikerjakan”; hadiah hanya sekali (penjaga status “selesai”); level tiap 250 XP (Magang, Staff, Senior, Manager; maks Level 4), bar atas dirender dari state (level, jabatan, bar XP dalam level — penuh di Manager, koin); Jobdesk menampilkan “✓ Selesai” dari state tersimpan; tugas berikutnya menjadi aktif (halaman Tugas menampilkannya; tombol Unduh Template hanya untuk Tugas 1, brief kosong bila belum ada); unggah tugas selesai ditolak dengan toast; hasil pemeriksaan menampilkan baris hadiah/bonus hanya saat hadiah baru diberikan; pop-up profil memakai jabatan dari level. Diuji dengan Node pada 26 kasus (batas level 0/250/500/750, batas skor 69/70/90, penjaga unggah ulang, alur naik level) — semua lolos. Dicek dengan CHECKLIST.md, semua poin lolos. Tugas 2 (Absensi Karyawan) selesai 22 Nov 2026: DATA_TUGAS.absensi diisi (brief, hint Rina 3, trik Dito 3, checks JSON persis §12 — 5 cek, 100 poin, lulus ≥70); generator buatDataTugas2 (PRNG sama; header Nama/Senin–Jumat/Hadir/Izin/Alfa; 10 nama tetap Andi–Joko (asumsi); status H/I/A ±70/20/10%; G–I kosong; A12 “Total”); tombol Unduh Template tampil untuk Tugas 2 (“Template Absensi Karyawan.xlsx”) lewat GENERATOR_TEMPLATE + unduhTemplate; mesin pemeriksa yang sama memilih generator dari aturan.task (task tidak dikenal → skor 0 + altered); evaluator mendukung “countif(B:F, H|I|A)” (kriteria per urutan kolom target) dan “sum(kolom)” (jumlah nilai harapan countif baris 2–11); dataDiubah digeneralisasikan (baris 2–11 kecuali sel tercakup cek: Tugas 1 A2:C11, Tugas 2 A2:F11); value_each gagal → “sum” bila range di baris ≥12, selain itu “rowval”; detail daftar centang memakai kata “sel”. Diuji dengan Node + SheetJS 0.18.5 (generator: deterministik 200 seed, distribusi H 69,5%/I 20,5%/A 10,0%; mesin Tugas 2: benar 100, satu hitung salah 55, total salah 85, angka manual 70, fungsi salah 75, ada error 20, status/nama diubah 100, tanpa cache 40, task tidak dikenal 0; regresi Tugas 1 lolos) — semua lolos. Dicek dengan CHECKLIST.md, semua poin lolos. Tugas 3 (Penilaian Magang) selesai 22 Nov 2026: DATA_TUGAS.penilaian_magang diisi (brief, hint Rina 3, trik Dito 3, checks JSON persis §12 — 5 cek, 100 poin, lulus ≥70); generator buatDataTugas3 (PRNG sama; header Nama/Nilai Teori/Nilai Praktik/Rata-rata/Keterangan; 10 nama tetap Arif–Lukman (asumsi); Teori/Praktik bilangan bulat 50–100; D/E kosong; tepat satu peserta rata-rata 75 di setiap seed — satu baris dipaksa B+C = 150, baris lain yang jumlahnya 150 digeser); tombol Unduh Template tampil untuk Tugas 3 (“Template Penilaian Magang.xlsx”) lewat GENERATOR_TEMPLATE; mesin pemeriksa yang sama memilih generator dari aturan.task; evaluator mendukung “avg(B,C)” dan “if(D>=75,'Lulus','Remedial')” (nilai D dari aturan avg pada baris yang sama; batas inklusif — tepat 75 adalah Lulus); value_each mendukung nilai harapan teks (perbandingan persis, peka huruf). Diuji dengan Node + SheetJS 0.18.5 (generator: deterministik 200 seed, tepat satu rata-rata 75 di 200 seed; mesin Tugas 3: benar 100, satu rata-rata salah 75, satu keterangan salah 65, batas 75 pakai > 65, teks huruf kecil 65, angka/teks manual 70, D tanpa AVERAGE 90, ada error 55, nilai/nama diubah 100, E kosong 45, tanpa cache 40; regresi Tugas 1 dan 2 lolos) — semua lolos. Dicek dengan CHECKLIST.md, semua poin lolos. Ketiga tugas Tahap 1 kini lengkap dan bisa dimainkan. Brief tugas di chat Pak Bima selesai 22 Nov 2026: brief dikirim otomatis saat tugas terbuka (Tugas 1 saat mulai, Tugas 2 setelah Tugas 1 lulus, Tugas 3 setelah Tugas 2 lulus); pesan berisi teks brief + lampiran template (tombol unduh mengunduh template tugas brief itu via penanda briefUntuk); terkirim hanya sekali per tugas (riwayat chat adalah catatannya, kompatibel simpanan lama tanpa penanda); menambah penanda belum dibaca (menu Chat, daftar kontak, lencana baru di pop-up); ucapan pop-up mengikuti tugas aktif (baru/dikerjakan; selesai bila semua selesai); tombol “Kirim laporan” baru di percakapan Pak Bima membuka halaman Tugas (tampil hanya bila ada tugas aktif); tombol Ulang menghapus semua brief dan membuat ulang dari Tugas 1. Pemeriksa file dan penilaian tidak diubah (18 fungsi diverifikasi identik). Diuji dengan Node (24 skenario: alur lulus penuh, urutan chat, tidak dobel, simpanan lama, Ulang, kondisiTugas) — semua lolos. Dicek dengan CHECKLIST.md, semua poin lolos. Sinkronisasi status tugas selesai 22 Nov 2026 (perbaikan dari hasil uji main Wibi: kartu Kantor masih “Terkunci” setelah Tugas 1 lulus, tombol “Mulai Tugas” tidak berfungsi, halaman Tugas tidak tampak berganti): satu sumber kebenaran state.tugas[id] = {status, hasilTerakhir} (terkunci/baru/dikerjakan/selesai) + state.tugasAktif, dibaca semua layar lewat statusTugas()/tugasAktifId(); saat lulus tugas jadi selesai, berikutnya jadi baru, tugasAktif pindah, brief terkirim sekali; kartu Jobdesk dirender penuh dari status (terkunci: gembok + tombol nonaktif; baru: lencana “Baru” + “Mulai Tugas”; dikerjakan: “Lanjutkan”; selesai: “✓ Selesai” + “Lihat hasil”, tanpa “Baru”); “Mulai Tugas”/“Lanjutkan” mengatur tugasAktif lalu membuka layar Tugas; “Lihat hasil” menampilkan kartu + hasil terakhir tersimpan (tanpa unduh/unggah); layar Tugas selalu menampilkan tugasAktif (masuk layar selalu render ulang + sembunyikan hasil lama); setelah lulus ada tombol “Lanjut ke Tugas berikutnya” (tampil hanya bila lulus dan ada tugas berikutnya); semua selesai → ringkasan “Semua tugas selesai”; tugas terkunci tidak bisa dibuka; simpanan lama (string status) dimigrasikan otomatis saat dimuat (dihitung ulang dari status tersimpan — simpanan lama tidak menyimpan skor) lalu disimpan kembali dalam bentuk baru. Pemeriksa file dan penilaian tidak diubah (18 fungsi diverifikasi identik; terapkanHadiah hanya penulisan statusnya yang menyesuaikan bentuk baru). Diuji dengan Node (33 skenario: alur lulus penuh, gagal, penjaga terkunci, batas hadiah 69/70/89/90, migrasi 6 bentuk simpanan, brief sekali saja, “Lihat hasil”, Ulang) — semua lolos. Dicek dengan CHECKLIST.md, semua poin lolos. Catatan “Lihat hasil” tanpa hasil tersimpan selesai 22 Nov 2026 (laporan Wibi: “Lihat hasil” Tugas 1 tidak menampilkan apa pun — Tugas 1 diselesaikan sebelum hasil mulai disimpan, simpanan lama tidak menyimpan skor sehingga tidak ada yang bisa dipulihkan): tampilkanHasilTersimpan kini menampilkan catatan “Hasil pemeriksaan tidak tersimpan. Tugas ini diselesaikan sebelum hasil mulai disimpan.” bila hasilTerakhir null (skor, status, hadiah, daftar centang, dan kedua tombol disembunyikan); bila hasil ada, hasil ditampilkan dan catatan disembunyikan; tampilkanHasilPemeriksaan selalu menyembunyikan catatan. Pemeriksa file dan penilaian tidak diubah (30 fungsi diverifikasi identik). Diuji dengan Node (13 skenario: catatan tampil, elemen hasil disembunyikan, hasil tersimpan normal, pemeriksaan baru menyembunyikan catatan, regresi alur lulus) — semua lolos. Dicek dengan CHECKLIST.md, semua poin lolos. Halaman uji tersembunyi #uji selesai 22 Nov 2026: hanya muncul bila alamat berakhiran #uji (tidak ada di navigasi; hash diperiksa saat muat + hashchange; bila hash dihapus saat layar uji tampil, kembali ke Kantor); tombol “Jalankan ulang” dan “Kembali ke Kantor” (menghapus hash via replaceState); untuk tiap tugas dibuat 5 file jawaban contoh dari template seed saat ini — benar+rumus, nilai salah (nilai cache sel pertama +1, rumus tetap, agregat tidak dihitung ulang), angka manual (nilai benar tanpa rumus), ada error (sel pertama #DIV/0!), data diubah (B2 diubah, jawaban tetap benar untuk seed asli) — lalu diperiksa dengan periksaFileXlsx yang sama; nilai cache selalu dari nilaiHarapanUntuk dan rumus dari peta rumus per tugas; tabel 15 baris membandingkan skor/lulus/kode yang diharapkan vs sebenarnya (T1: 100/70/70/50/100; T2: 100/55/70/20/100; T3: 100/75/70/55/100) dengan penanda ✓ Cocok/✗ Beda (baris beda berlatar merah muda), ringkasan “X dari 15 cocok”, seed yang dipakai, dan tautan Unduh .xlsx per baris; tabel digulir horizontal di HP; halaman uji tidak mengubah state game (tanpa chat/hadiah/penyimpanan); bila SheetJS belum termuat tampil pesan ramah tanpa crash. Pemeriksa file dan penilaian tidak diubah (30 fungsi diverifikasi identik). Diuji dengan Node + SheetJS 0.18.5 (21 skenario: 15/15 cocok pada 2 seed berbeda, state dan localStorage tidak berubah, render + jalur offline) — semua lolos. Dicek dengan CHECKLIST.md, semua poin lolos. Tinjauan lebar 360/768/1440 px selesai 22 Nov 2026: 10 masalah ditemukan dan diperbaiki — (1) hotspot di 360 px diperbesar (Bima 14%×24%, Dito lebar 14%, pemain left 67% + lebar 14%; semua ≥47×45 px, tanpa tumpang tindih; posisi chip label disesuaikan: Bima 47,9%/12,5%, Dito 47,9%/−3,2%, Kamu HP 57,9%/−6,5%, jangkar adegan tetap), (2–7) area sentuh 44 px untuk tombol Ulang, tombol kembali chat, tombol tutup lembar “Lainnya”, tombol unduh kecil di balon chat, tombol tugas di Jobdesk, dan tautan Unduh tabel uji, (8) sidebar melayang Kantor di 900–1199 px dipersempit jadi 132 px + nav dipadatkan agar tidak menutupi hotspot Rina (di ≥1200 px tetap 180 px), (9) teks lencana “🔒 Terkunci” memakai --card-text (kontras 10,1:1/11,6:1), (10) teks redup mode terang digelapkan ke #547065 (4,67:1). Diperiksa dan lolos tanpa perbaikan: tidak ada elemen terpotong di ketiga lebar, fokus keyboard terlihat di semua elemen interaktif, animasi mengikuti hemat gerak, pop-up desktop dijaga di dalam adegan, panel Jobdesk berhenti 12 px di atas Dito. Fungsi game tidak diubah (30 fungsi identik). Dicek dengan CHECKLIST.md, semua poin lolos. Panel “Sebelum mulai” selesai 22 Nov 2026: kartu kecil di tengah layar (maks 440 px, bisa digulir bila lebih tinggi dari layar) yang muncul sekali saja saat game pertama kali dibuka — cara bermain 4 langkah (baca brief Pak Bima di Chat, unduh template di halaman Tugas, kerjakan di spreadsheet + hint Rina/trik Dito, unggah hasil dan lihat skor), catatan progres tersimpan otomatis di browser, catatan butuh aplikasi spreadsheet (Excel/Google Sheets), tombol “Mulai bermain” lebar penuh; tanda “sudah dilihat” di kunci localStorage terpisah “office-quest-sebelum-mulai-v1” sehingga Ulang tidak memunculkannya lagi; panel tidak tampil di #uji; menutup lewat tombol/Esc/ketuk di luar menandai sudah dilihat; fokus masuk ke tombol, Tab terjaga di dalam, fokus kembali ke judul Kantor. Fungsi game tidak diubah (diff script hanya penambahan: blok panel + kait init, tanpa satu baris pun yang diubah). Diuji Node (14 skenario: tampil pertama kali, tanda tersimpan, Ulang mempertahankan tanda, state tidak berubah) — semua lolos. Dicek dengan CHECKLIST.md, semua poin lolos.
- **Sedang dikerjakan:** [isi]
- **Berikutnya:** Draf PROJECT.md Tahap 2 (Wibi menyusun di Claude dengan prompt yang sudah disiapkan; model konten sudah diputuskan: game harian tanpa akhir dengan kesulitan meningkat seiring level).

## 4. Ruang lingkup Tahap 1

**P0 (wajib):**
- Halaman Kantor: adegan satu gambar utuh, karakter bisa ditekan (membuka pop-up percakapan), bar atas (level, XP, koin), panel Jobdesk, navigasi
- Menu 6 item: Kantor, Chat, Tugas, Toko, Tantangan, Koleksi. Toko dan Tantangan hanya halaman “Segera hadir”, Koleksi menampilkan lima slot kosong
- Chat dengan 3 karakter, riwayat tersimpan, hint bertahap
- Halaman Tugas: brief, unduh template, unggah .xlsx
- Pemeriksaan file di browser dengan aturan cek berbentuk data
- 3 tugas: Rekap Penjualan, Absensi, Penilaian Magang
- XP, koin, level Magang, tombol Ulang
- Responsif HP dan desktop, mode terang dan gelap

**P1 (jika sempat):** timer deadline, ekspor progres, efek lingkungan ringan pada adegan (lihat bagian 18).

**Bukan tujuan:** gerakan karakter, Toko dan Koleksi yang berfungsi, kustomisasi aktif, login, server, leaderboard, placement test, level menengah, jalur konteks lain, editor spreadsheet di browser, anti-curang yang kuat.

## 5. Alur pemain
1. Buka Kantor, lihat notifikasi tugas dari Pak Bima. Menekan karakter membuka pop-up percakapan dengan tombol “Lanjut ke chat”.
2. Buka chat bos, baca brief, unduh template.
3. Kerjakan di spreadsheet. Jika bingung, minta hint ke Rina atau Dito (maks 3 per karakter per tugas).
4. Unggah file di halaman Tugas.
5. Lihat skor dan daftar pengecekan. Bos membalas di chat.
6. Lulus (skor 70 ke atas): XP dan koin bertambah, tugas berikutnya terbuka. Belum lulus: perbaiki dan unggah ulang.

## 6. Layar dan tata letak

**Desktop (lebar 900 px ke atas):**
- Bar atas penuh, tinggi sekitar 10 persen
- Sidebar kiri sekitar 12 persen lebar (Kantor, Chat, Tugas, Toko, Tantangan, Koleksi)
- Area tengah: adegan kantor
- Panel kanan sekitar 17 persen lebar: Jobdesk Hari Ini
- Chat: daftar kontak di kiri, percakapan di kanan

**HP:**
- Satu kolom, bar bawah 5 slot (Kantor, Chat, Tugas, Toko, Lainnya). “Lainnya” membuka lembar berisi Tantangan dan Koleksi. Konten diberi padding bawah agar tidak tertutup bar
- Adegan kantor di atas, panel Jobdesk berupa kartu di bawahnya
- Chat: daftar kontak satu layar, ketuk kontak membuka percakapan layar penuh dengan tombol kembali

**Komposisi adegan:** satu gambar utuh yang sudah memuat keempat karakter duduk di mejanya (lihat bagian 17). Karakter tidak ditumpuk sebagai gambar terpisah. Meja pemain di kanan bawah dengan sorotan emas. Panel Jobdesk berada di kolom terpisah dan tidak menutupi gambar.

## 7. Identitas visual: Forest Cream

| Peran | Warna |
|---|---|
| Latar | #0F2A24 |
| Permukaan | #173B32 |
| Teks | #F2EEE3 |
| Aksen | #D8C28A |
| Redup | #8FA39B |

- Gaya ilustrasi: cat air dan tinta, karakter hewan berbentuk kubus, garis tebal tidak rata.
- Tipografi yang disarankan: judul font tulisan tangan yang ramah (misalnya Patrick Hand), isi Nunito, dengan fallback sistem.
- Komponen: kartu krem untuk panel dan balon chat, tombol utama emas dengan teks gelap, bar progres emas.
- Mode gelap adalah tampilan utama. Mode terang memakai latar krem dengan teks hijau tua.
- Aksesibilitas: kontras teks cukup, area sentuh minimal 44 px, fokus keyboard terlihat, animasi mengikuti pengaturan hemat gerak.
- Placeholder sampai aset siap: bentuk CSS dan emoji pada posisi yang sama dengan rencana aset.

**Nama aset (folder `assets/`):** `bg_kantor_karakter.webp` (adegan utama), `bg_kantor.webp` (latar kosong untuk tahap berikutnya), `bima_netral.webp`, `bima_senang.webp`, `bima_kesal.webp`, `rina_*.webp`, `dito_*.webp`, `pemain_*.webp`, ikon dalam `.svg`.

## 8. Karakter

| Karakter | Peran | Gaya bicara |
|---|---|---|
| Pak Bima (beruang kutub, mahkota emas kecil) | Bos | Tegas tapi adil, kalimat singkat, suka deadline |
| Rina (domba, kacamata bulat, kardigan hijau) | Senior Admin | Sabar, hint bertahap, menyebut konsep bukan jawaban |
| Dito (panda merah, headphone) | Staf IT | Santai, suka shortcut dan trik |
| Pemain (beruang cokelat, tunas di kepala) | Magang | Tidak berbicara, avatar pemain |

Karakter tambahan (Tahap 2): OB (kapibara, menawarkan kopi dan mengenalkan Toko), penjaga warung (kambing, pemilik Toko), satpam (bulldog, pengumuman event), kurir (landak, mengantar paket bonus), Bu Wati HRD (burung hantu, pemberi tugas Absensi), akuntan (rakun), cleaning service (berang-berang), kucing kantor (maskot). Maksimal 6 sampai 7 karakter terlihat sekaligus.

Aturan hint: tidak pernah memberi jawaban langsung. Hint 1 menyebut konsep, hint 2 menyebut nama fungsi atau lokasi sel, hint 3 mengingatkan cara kerja yang benar.

## 9. Format keluaran teknis
- Aplikasi statis: **satu file `index.html`** (CSS dan JavaScript di dalam file) agar mudah disalin dari HP. Aset gambar dirujuk dengan jalur relatif `assets/...` dan memiliki cadangan emoji bila gagal dimuat.
- Library: SheetJS (xlsx) dari CDN dengan versi dipatok, untuk membaca dan membuat .xlsx.
- Penyimpanan: `localStorage` dengan `try/catch`. Halaman tetap berfungsi jika penyimpanan kosong atau diblokir.
- Data tugas, naskah chat, dan aturan cek diletakkan di bagian atas script sebagai objek terpisah dari logika tampilan, agar mudah dipindah ke server di Tahap 3.
- Data acak memakai generator pseudo-random dengan seed per pemain (disimpan di browser).
- Browser: Chrome dan Safari terbaru di Android, iOS, dan desktop. Berat halaman awal di bawah 3 MB.
- Unduhan file memakai Blob dan tautan unduh. Jika platform hosting membatasi unduhan, ikuti mekanisme unduh yang disediakan platform itu.

## 10. Data dan penyimpanan (localStorage)

| Bidang | Isi |
|---|---|
| seed | Angka acak untuk data tugas |
| xp, koin | Angka |
| tugas | Per tugas: status (baru, dikerjakan, selesai), skor terbaik, jumlah percobaan |
| hint | Jumlah hint terpakai per karakter per tugas |
| chat | Riwayat pesan per karakter: pengirim, teks, lampiran |
| belumDibaca | Jumlah pesan baru per karakter |

## 11. Sistem penilaian
- Skor 0 sampai 100. Lulus: 70 ke atas. Bonus: 90 ke atas.
- Lulus: koin +100, XP +100. Bonus: koin +150, XP +150. Gagal: tidak ada pengurangan, boleh unggah ulang.
- Level: tiap 250 XP naik satu level (Magang, Staff, Senior, Manager).
- Jenis pengecekan: nilai sel, penggunaan fungsi pada rumus, keberadaan sheet, tidak ada sel error, data asli tidak diubah.
- Bandingkan angka dengan toleransi 0,01. Kenali hasil dari **cache nilai** file. Jika rumus ada tetapi nilainya kosong, minta pemain menyimpan ulang dari Excel.
- Terima beberapa fungsi setara bila ditetapkan (misalnya SUM atau SUBTOTAL). Fokus pada hasil yang benar.

## 12. Spesifikasi tugas

### Tugas 1: Rekap Penjualan Mingguan
- **Skill:** perkalian, SUM, AVERAGE. **Sheet:** `Data`.
- **Data:** A Produk (10 baris, A2:A11), B Qty acak 5 sampai 50, C Harga acak kelipatan 500 (2.000 sampai 21.500), D Total kosong. Baris 12: A12 “Total Penjualan”. Baris 13: A13 “Rata-rata”.
- **Brief bos:** “Pagi! Tolong rekap penjualan minggu ini ya. Isi kolom Total, lalu hitung total seluruh penjualan dan rata-rata per produk. Kirim balik sebelum jam 5.”
```json
{ "task": "rekap_penjualan", "sheet": "Data", "pass": 70, "checks": [
  { "range": "D2:D11", "type": "value_each", "expected": "B*C", "points": 30 },
  { "range": "D2:D11", "type": "is_formula", "points": 15 },
  { "cell": "D12", "type": "value", "expected": "sum(D2:D11)", "points": 20 },
  { "cell": "D12", "type": "formula_uses", "functions": ["SUM", "SUBTOTAL"], "points": 10 },
  { "cell": "D13", "type": "value", "expected": "avg(D2:D11)", "points": 15 },
  { "cell": "D13", "type": "formula_uses", "functions": ["AVERAGE"], "points": 5 },
  { "type": "no_errors", "points": 5 } ] }
```
- **Hint Rina:** (1) total per produk = Qty dikali Harga; (2) menjumlahkan banyak sel punya fungsi yang namanya mirip “jumlah” dalam bahasa Inggris; (3) tulis rumus, jangan ketik angkanya.
- **Hint Dito:** (1) klik dua kali pojok kanan bawah sel untuk mengisi ke bawah; (2) blok D2:D11 dan lihat bar status untuk cek cepat; (3) simpan dengan Ctrl+S dari Excel.

### Tugas 2: Absensi Karyawan
- **Skill:** COUNTIF, SUM. **Sheet:** `Data`.
- **Data:** A Nama (10 baris, A2:A11), B sampai F status Senin sampai Jumat berisi H (hadir), I (izin), atau A (alfa) dengan peluang kira-kira 70, 20, 10 persen. G “Hadir”, H “Izin”, I “Alfa” kosong. Baris 12: A12 “Total”.
- **Brief bos:** “Bu Wati dari HRD minta rekap absensi minggu ini. Hitung hadir, izin, dan alfa tiap karyawan, lalu totalnya di bawah.”
```json
{ "task": "absensi", "sheet": "Data", "pass": 70, "checks": [
  { "range": "G2:I11", "type": "value_each", "expected": "countif(B:F, H|I|A)", "points": 45 },
  { "range": "G2:I11", "type": "formula_uses", "functions": ["COUNTIF"], "points": 25 },
  { "range": "G12:I12", "type": "value_each", "expected": "sum(kolom)", "points": 15 },
  { "range": "G12:I12", "type": "formula_uses", "functions": ["SUM", "SUBTOTAL"], "points": 5 },
  { "type": "no_errors", "points": 10 } ] }
```
- **Hint Rina:** (1) ada fungsi yang menghitung sel yang cocok dengan satu kriteria; (2) kriterianya berupa huruf, ditulis dalam tanda kutip; (3) rentang hitung B sampai F pada baris yang sama.
- **Hint Dito:** (1) tulis rumus di G2 lalu tarik ke kanan dan ke bawah; (2) kunci rentang dengan F4 bila perlu; (3) cek total di bawah harus 50 jika dijumlahkan semua kolom.

### Tugas 3: Penilaian Magang
- **Skill:** AVERAGE, IF. **Sheet:** `Data`.
- **Data:** A Nama (10 baris), B Nilai Teori acak 50 sampai 100, C Nilai Praktik acak 50 sampai 100, D “Rata-rata” kosong, E “Keterangan” kosong. Generator memastikan ada satu peserta dengan rata-rata tepat 75.
- **Brief bos:** “Tolong nilai anak magang. Hitung rata-rata teori dan praktik, lalu beri keterangan Lulus jika 75 ke atas, selain itu Remedial.”
```json
{ "task": "penilaian_magang", "sheet": "Data", "pass": 70, "checks": [
  { "range": "D2:D11", "type": "value_each", "expected": "avg(B,C)", "points": 25 },
  { "range": "D2:D11", "type": "formula_uses", "functions": ["AVERAGE"], "points": 10 },
  { "range": "E2:E11", "type": "value_each", "expected": "if(D>=75,'Lulus','Remedial')", "points": 35 },
  { "range": "E2:E11", "type": "formula_uses", "functions": ["IF"], "points": 20 },
  { "type": "no_errors", "points": 10 } ] }
```
- **Hint Rina:** (1) rata-rata punya fungsi sendiri; (2) pengambilan keputusan dua pilihan memakai fungsi IF; (3) perhatikan peserta yang nilainya tepat di batas.
- **Hint Dito:** (1) pakai >= bukan >; (2) teks dalam rumus ditulis dengan tanda kutip; (3) sebelum kirim, cek ada satu orang tepat 75.

## 13. Naskah feedback bos (kode masalah ke kalimat)
Sediakan 2 sampai 3 variasi per kode agar tidak monoton.

| Kode | Arti | Contoh kalimat Pak Bima |
|---|---|---|
| altered | Data asli diubah atau sheet hilang | “Kok datanya beda dari file yang saya kirim? Tolong pakai file aslinya.” |
| nocache | Rumus ada, hasil tidak terbaca | “Hasilnya belum terbaca. Buka di Excel, simpan dengan Ctrl+S, lalu kirim lagi.” |
| err | Ada sel error | “Ada tulisan aneh seperti #REF! atau #VALUE! di laporanmu. Tolong dicek.” |
| rowval | Nilai per baris salah | “Masih ada baris yang tidak sesuai. Cek lagi rumusnya.” |
| sum | Total atau rata-rata salah | “Angka di bagian bawah belum tepat.” |
| hard | Angka diketik manual | “Ada angka yang diketik manual. Kalau data berubah, laporan ikut salah. Pakai rumus ya.” |
| ok90 | Skor 90 ke atas | “Rapi dan akurat. Terima kasih, bonus masuk ya.” |
| ok70 | Lulus dengan catatan | “Cukup baik, tapi ada catatan.” |
| fail | Skor di bawah 70 | “Belum bisa saya terima. Perbaiki lalu kirim ulang.” |

## 14. Keamanan dan privasi
- Tidak ada akun dan tidak ada data pribadi yang dikumpulkan.
- File unggahan hanya dibaca di browser dan tidak dikirim ke mana pun. Isi file tidak pernah dijalankan.
- Hanya .xlsx, maksimal 2 MB. Tolak .xlsm dan format lain dengan pesan yang ramah.
- Tampilkan catatan: progres tersimpan di browser dan hilang jika data browser dihapus.
- Kunci jawaban ada di dalam kode dan bisa diintip. Ini diterima untuk Tahap 1.

## 15. Kriteria selesai Tahap 1
- [ ] Semua P0 berjalan di Chrome Android, Safari iOS, dan Chrome desktop
- [ ] Tugas 1 sampai 3 lolos lima file uji masing-masing (benar, nilai salah, angka manual, ada error, data diubah)
- [ ] Tidak ada elemen terpotong pada lebar 360, 768, dan 1440 px
- [ ] Website bisa dibuka lewat tautan publik
- [ ] Minimal 8 penguji mencoba dan umpan balik tercatat

**Target metrik:** 7 dari 10 penguji menyelesaikan Tugas 1 tanpa bantuan luar, waktu median di bawah 15 menit, kegagalan baca file teknis di bawah 15 persen, kepuasan tampilan 4 dari 5.

## 16. Keputusan dan pertanyaan terbuka
- Nama final tetap Office Quest? Domain sudah dicek?
- Apakah pemain memasukkan nama panggilan di awal?
- Diputuskan: Toko, Tantangan, dan Koleksi hanya halaman placeholder di Tahap 1, berfungsi di Tahap 2.
- Diputuskan (22 Nov 2026): Office Quest adalah game harian tanpa akhir — tugas harian dari generator, bukan kampanye yang bisa ditamatkan; kesulitan meningkat seiring bertambahnya level pemain.
- Arti Tantangan: tugas ekstra berhadiah koin dan item eksklusif (asumsi, perlu dikonfirmasi).
- Platform hosting statis yang dipilih, dan apakah mendukung unduhan file langsung?

## 17. Adegan, hotspot, dan pop-up (Tahap 1)

**Adegan:** satu gambar `assets/bg_kantor_karakter.webp` (2096x1184, 16:9). Keempat karakter sudah ada di dalam gambar. Di atasnya hanya ada hotspot transparan dan label.

**Struktur:** kontainer berisi satu kotak pembungkus yang memuat gambar dan semua hotspot. Hotspot memakai posisi dan ukuran dalam persen dari kotak pembungkus, agar ikut bergeser saat gambar dipotong di HP.

| Karakter | Kiri | Atas | Lebar | Tinggi | Label di atas kepala (x, y) |
|---|---|---|---|---|---|
| Pak Bima | 43,9% | 27,0% | 9,5% | 19,4% | 48,7%, 25% |
| Rina | 18,8% | 41,4% | 11,5% | 21,0% | 24,5%, 39% |
| Dito | 82,0% | 41,4% | 11,5% | 28,7% | 87,7%, 39% |
| Kamu | 68,7% | 68,4% | 12,9% | 28,7% | 75,1%, 66% |

**Tampilan HP (di bawah 900 px):** kontainer `aspect-ratio: 3/2` dengan overflow hidden, pembungkus lebar 118,5% dan `margin-left: -11,85%`. Hotspot minimal 44 x 44 px.

**Label:** chip kecil di atas kepala. HP: font 11 px, hanya “Kamu” (tanpa jabatan). Nama karakter lain hanya muncul saat ditekan atau difokus. “Kamu” selalu tampil kecil. Label tidak boleh menutupi wajah karakter.

**Pop-up percakapan:**
- Menekan karakter tidak langsung membuka Chat. Tampil pop-up berisi avatar kecil, nama dan peran, satu kalimat ucapan, tombol “Lanjut ke chat” dan “Tutup”.
- HP: lembar dari bawah layar. Desktop: kartu dekat karakter.
- Tekan di luar atau Esc menutup. `role="dialog"` dan `aria-modal`, fokus masuk ke pop-up dan kembali ke karakter saat ditutup.
- Menekan “Kamu” membuka pop-up profil (nama, level, tombol “Buka Koleksi”).
- Kalimat ucapan berasal dari data per karakter dan kondisi tugas (baru, dikerjakan, selesai). Contoh: Pak Bima “Pagi! Sudah cek jobdesk hari ini?”, Rina “Bingung rumus? Tanya aku ya.”, Dito “Butuh trik cepat? Aku ada.”

## 18. Animasi dan interaksi karakter (roadmap)

Karena karakter menyatu dengan gambar latar, gerakan karakter tidak bisa dibuat langsung. Pendekatannya bertahap:

| Tahap | Pendekatan | Isi |
|---|---|---|
| 1 | Efek ringan, karakter tidak bergerak | Sorotan emas tipis saat hover atau fokus, denyut cincin singkat saat ditekan, pop-up muncul dengan transisi pendek, efek lingkungan (cahaya lampu berdenyut halus, uap mug Rina, kilau layar laptop pemain) hanya dengan opacity dan transform |
| 2 | Animasi bingkai | Untuk tiap karakter dibuat 2 bingkai idle dan 1 bingkai reaksi dari adegan yang sama (hanya pose yang berubah), dipotong per area hotspot dan bergantian (crossfade) dengan jeda acak per karakter agar tidak serempak. Reaksi saat ditekan: ganti ke bingkai reaksi sekitar 1 detik, pantulan kecil, lalu pop-up. Karakter tambahan (OB, kurir, kucing) berupa sprite terpisah yang berjalan di jalur lantai kosong |
| 5 (opsional) | Adegan berlapis | Latar kosong, lapisan karakter, dan lapisan meja depan, sehingga gerak sejati (napas, mengetik, berkedip) dan kostum pemain tampak di adegan |

**Gerak per karakter (rencana Tahap 2):**

| Karakter | Idle tanpa klik | Reaksi saat ditekan |
|---|---|---|
| Pak Bima | Membalik kertas, melirik laptop | Menatap ke depan sambil mengangkat clipboard |
| Rina | Menyeruput mug, uap naik | Melambai |
| Dito | Mengetik, mengangguk mengikuti irama | Acungan jempol |
| Pemain | Mengetik di laptop | Mengangkat satu tangan |

**Aturan teknis animasi:**
- Hanya `transform` dan `opacity`.
- Tiap bingkai maksimal 60 KB, total aset animasi maksimal 400 KB.
- Jeda acak 6 sampai 15 detik per karakter. Hentikan saat tab tidak aktif (`document.hidden`).
- Hormati `prefers-reduced-motion`: semua animasi mati, interaksi tetap berfungsi lewat pop-up.
- Animasi tidak boleh menutupi hotspot atau label.
- Sediakan bingkai pertama sebagai gambar cadangan bila bingkai gagal dimuat.

## 19. Jalur kustomisasi pemain

**Alur:** kerjakan tugas, dapat koin, beli di Toko, item masuk Koleksi, tekan “Pakai”, penampilan berubah.

**Lima slot, satu item per slot:** kepala (tunas, topi), wajah (kacamata), baju (sweter, kemeja), aksesori (ransel, lanyard), meja (lampu, kaktus, mug).

**Tampil di mana:**
- Koleksi dan profil: pratinjau pemain tampak depan dengan lapisan item bertumpuk.
- Avatar kecil: bar atas, balon chat pemain, pop-up.
- Adegan Kantor (Tahap 1 dan 2): pemain terlihat dari samping dalam gambar utuh, jadi kostum tidak tampak. Hanya dekorasi meja yang bisa ditumpuk sebagai gambar kecil di atas meja pemain.
- Adegan Kantor (Tahap 5, adegan berlapis, opsional): kostum ikut tampak.
- Lencana jabatan otomatis dari level, tidak dibeli.

**Aset:** `pemain_depan.webp` (badan dasar, transparan, 600x800 px), satu file per item dengan kanvas dan pose yang sama persis (urutan tumpuk: badan, baju, wajah, kepala, aksesori), dan ikon 200x200 px per item.

**Data (kerangka):**
```js
KATALOG=[{id:'tunas',slot:'kepala',nama:'Tunas Semangat',harga:60,aset:'item_tunas.webp'}]
state.koleksi=['tunas']
state.dipakai={kepala:'tunas',wajah:null,baju:null,aksesori:null,meja:null}
```

**Pembagian tahap:**
- Tahap 1: menu Toko dan Koleksi ada, halaman placeholder, slot kosong di Koleksi.
- Tahap 2: Toko, Koleksi, dan Ruang Ganti berfungsi.
- Tahap 5 (opsional): kostum tampak di adegan lewat adegan berlapis.

## 20. Log perubahan
- 2026-11-21: Kerangka index.html dibuat — variabel warna Forest Cream di :root, mode terang mengikuti pengaturan perangkat, font Patrick Hand dan Nunito dengan fallback, gaya dasar tombol emas, kartu krem, bar progres emas, satu kartu contoh dan satu tombol.
- 2026-11-21: Halaman Kantor ditambahkan — bar atas (logo, level/XP, koin), sidebar desktop / menu bawah HP, adegan kantor placeholder emoji (bos tengah atas, rekan kerja kiri-kanan, meja pemain bawah kanan “Kamu”), panel Jobdesk Hari Ini dengan 3 tugas. Belum ada fungsi klik.
- 2026-11-21: Perbaikan 1.3 — satu kolom di bawah 900 px (adegan penuh di atas, Jobdesk penuh di bawah, menu bawah tetap); jarak meja Dito–pemain; “Dari Pak Bima” dan “Kirim sebelum jam 5” dua baris terpisah; adegan mengisi lebar tanpa ruang kosong besar; bar XP jalur gelap #0F2A24 isi emas #D8C28A; teks peran karakter 13 px lebih terang.
- 2026-11-21: Perpindahan layar Kantor/Chat/Tugas — menu aktif ditandai sinkron di sidebar dan menu bawah, Chat dan Tugas masih kosong (hanya judul), karakter adegan menjadi tombol yang menampilkan nama dan peran, bisa dioperasikan dengan keyboard. Dicek dengan CHECKLIST.md, semua poin lolos.
- 2026-11-21: Gambar latar bg_kantor.webp dipasang sebagai latar adegan Kantor; posisi karakter disesuaikan dengan gambar.
- 2026-11-21: Layout Kantor diubah jadi latar satu layar penuh + panel mengambang (bar atas, navigasi, Jobdesk, status karakter); isi tetap sama. Perbaikan: tinggi panel Jobdesk dibatasi agar tidak menutupi Dito di desktop (isi digulir di dalam panel bila perlu). Dicek dengan CHECKLIST.md, semua poin lolos.
- 2026-11-21: Gambar karakter dipasang di adegan Kantor — bima/rina/dito/pemain_netral.webp (pose netral, setengah badan, tepi bawah sejajar garis meja); posisi di kursi masing-masing; ukuran satu variabel CSS per karakter agar mudah diubah belakangan; emoji tetap sebagai cadangan bila gambar gagal dimuat. Dicek dengan CHECKLIST.md, semua poin lolos.
- 2026-11-21: Keputusan Wibi — kustomisasi pemain DITUNDA, nanti ada fitur market tempat pemain membeli kustomisasinya sendiri; pemain tampil polos di Tahap 1. Batas berat halaman 3 MB diabaikan sementara (file kini ±3,2 MB karena gambar tersimpan di dalam file).
- 2026-11-21: Gambar latar kantor dipasang — assets/bg_kantor.webp (cat air Forest Cream 2048×1152) jadi latar adegan Kantor; placeholder ruang kaca, batang meja, dan tanaman CSS dihapus; adegan tepat 16:9 di semua lebar; posisi Pak Bima, Rina, Dito, dan pemain disesuaikan dengan kursi/meja di gambar (label pemain di atas avatar, peran pil gelap 13 px). Dicek dengan CHECKLIST.md (tangkapan layar 1440 dan 390; 768 se-breakpoint dengan 390, 360 dari geometri).
- 2026-11-22: Adegan Kantor diganti jadi satu gambar utuh bg_kantor_karakter.webp (keempat karakter duduk di mejanya) + 4 hotspot transparan di posisi yang disetujui Wibi; klik/Enter membuka layar Chat; chip nama kecil muncul saat disentuh/difokus, label “Kamu” selalu tampil; baris status nama karakter dihapus; cadangan adegan lama dengan emoji bila gambar gagal dimuat. Dicek dengan CHECKLIST.md, semua poin lolos. File dibersihkan dari duplikasi gambar (komentar dan lapisan latar ganda): 4,37 → 2,44 MB, kembali di bawah batas 3 MB.
- 22 November 2026: adegan Kantor diganti satu gambar utuh dengan karakter di dalamnya, hotspot dan label, pop-up percakapan karakter, menu 6 item, roadmap animasi, jalur kustomisasi, karakter tambahan, dan keputusan cakupan Toko, Tantangan, Koleksi.
- 2026-11-22: Navigasi 6 menu selesai — Kantor, Chat, Tugas, Toko, Tantangan, Koleksi berpindah layar tanpa memuat ulang; desktop keenamnya di sidebar kiri; HP bar bawah 5 slot (Kantor, Chat, Tugas, Toko, Lainnya) dengan lembar dari bawah berisi Tantangan dan Koleksi (tutup: tombol ✕, ketuk di luar, Esc; fokus kembali ke “Lainnya”); slot “Lainnya” ditandai aktif saat Tantangan/Koleksi terbuka; lencana belum dibaca disiapkan di item Chat (tersembunyi karena belum ada pesan); Toko dan Tantangan placeholder (judul + satu kalimat + kartu “Segera hadir”); Koleksi placeholder (“Belum ada item. Beli di Toko.” + 5 slot kosong di sekitar pratinjau pemain emoji); Chat dan Tugas tetap judul saja. Dicek dengan CHECKLIST.md, semua poin lolos.
- 2026-11-22: Label karakter diseragamkan — “Kamu · Magang” tidak lagi selalu tampil; semua chip hanya muncul saat hotspot disentuh, di-hover (hanya perangkat dengan hover asli, supaya tidak menempel di layar sentuh), atau difokus, lalu hilang sendiri setelah 2 detik (timer); pindah layar membersihkan semua chip dan timer supaya tidak ada label tertinggal. Klik hotspot tetap membuka layar Chat langsung. Dicek dengan CHECKLIST.md, semua poin lolos.
- 2026-11-22: Label adegan Kantor diperbaiki — chip Pak Bima/Rina/Dito hanya nama (12,5 px) di atas kepala pada titik jangkar yang diminta (Bima 48,7/25, Rina 24,5/39, Dito 87,7/39); HP: label “Kamu” 11 px, padding 2 px 8 px, hanya “Kamu”, di atas kepala pada jangkar 75,1/66; desktop label “Kamu” tidak berubah; perilaku tampil (2 detik) dan klik membuka Chat tidak berubah; padding bawah HP 96 px sudah cukup untuk bar bawah 60 px, jadi tidak diubah. Dicek dengan CHECKLIST.md, semua poin lolos.
- 2026-11-22: Pop-up percakapan karakter selesai — menekan karakter tidak lagi langsung membuka Chat; pop-up berisi avatar emoji, nama dan peran, satu kalimat ucapan dari data per karakter dan kondisi tugas (baru/dikerjakan/selesai; saat ini “baru”), tombol “Lanjut ke chat” dan “Tutup”; HP lembar dari bawah, desktop kartu 300 px dekat karakter; tutup lewat tombol, ketuk di luar, atau Esc; role="dialog" + aria-modal, fokus masuk ke pop-up dan kembali ke karakter; “Lanjut ke chat” membuka Chat dan menyimpan karakter aktif di state.chatAktif; “Kamu” membuka pop-up profil (nama, level, tombol “Buka Koleksi”); stasiun cadangan berperilaku sama. Dicek dengan CHECKLIST.md, semua poin lolos.
- 2026-11-22: Efek ringan adegan selesai — hover/fokus hotspot menampilkan sorotan emas tipis (outline 2 px + cahaya halus); saat ditekan, cincin emas berdenyut sekali (±300 ms) lalu pop-up muncul dengan transisi masuk singkat (0,18 dtk); efek lingkungan: cahaya lampu meja pemain berdenyut halus (61/70), kilau layar (66/78), uap tipis naik dari mug Rina (27/57), posisi lewat variabel CSS --fx-* di :root; semua animasi hanya transform dan opacity, tanpa pustaka; mati saat prefers-reduced-motion aktif, berhenti saat tab tidak aktif (visibilitychange); lapisan efek tidak menangkap klik dan berada di bawah hotspot/label. Dicek dengan CHECKLIST.md, semua poin lolos.
- 2026-11-22: Objek data karakter dan tugas selesai — DATA_KARAKTER (Pak Bima, Rina, Dito) dilengkapi field sapaan (usulan, karena §8 belum memuat teks resmi; ditandai di komentar); nama, peran, avatar emoji, dan ucapan per kondisi tugas tetap satu salinan di objek yang sama, pop-up tetap membacanya dari sana, entri “Kamu” tidak diubah. DATA_TUGAS Tugas 1 (rekap_penjualan) diisi id, judul, brief, dan hint Rina/Dito (3 tiap karakter) persis dari §12; Tugas 2 dan 3 belum diisi. Hanya data, tanpa tampilan baru. Dicek dengan CHECKLIST.md, semua poin lolos.
- 2026-11-22: Layar Chat selesai — daftar kontak (Pak Bima, Rina, Dito) berupa tombol berisi avatar, nama, peran, dan penanda belum dibaca; percakapan berupa balon (masuk krem, pemain emas muda); pesan brief Pak Bima menampilkan chip lampiran “Template Rekap Penjualan Mingguan.xlsx” (tampilan saja, unduhan disambung di langkah Tugas); desktop daftar kiri + percakapan kanan berdampingan (bawaan Pak Bima); HP daftar satu layar, ketuk kontak membuka percakapan layar penuh dengan tombol kembali (fokus kembali ke kontak); “Lanjut ke chat” di pop-up membuka chat karakter itu; isi pesan dibaca dari data (brief DATA_TUGAS, sapaan DATA_KARAKTER); belum dibaca awal {bima: 1}, membuka percakapan menandai sudah dibaca dan lencana hilang; belum ada tombol hint dan kolom kirim pesan. Dicek dengan CHECKLIST.md, semua poin lolos.
- 2026-11-22: Tombol hint dan trik di Chat selesai — chat Rina menampilkan tombol “Minta hint (n/3)”, chat Dito “Minta trik (n/3)”, chat Pak Bima tidak ada tombol; tiap klik menambah pesan pemain (“Boleh minta hint?”/“Boleh minta trik?”) lalu balasan berikutnya dari data berlabel kecil “Hint”/“Trik”; hitungan terpisah per karakter per tugas di state.hint[tugasId][karakter], maks 3 masing-masing, tombol nonaktif pada (3/3); data direstrukturisasi (field hint berisi 3 hint Rina, field baru trik berisi 3 trik Dito, teks sama persis tanpa duplikasi); tugas aktif adalah tugas pertama yang belum selesai; belum ada pengurangan skor. Dicek dengan CHECKLIST.md, semua poin lolos.
- 2026-11-22: Penyimpanan localStorage dan tombol Ulang selesai — progres tersimpan dalam satu kunci berversi “office-quest-v1” berisi seed, xp, koin, tugas, hint, chat, belumDibaca; dimuat sebelum render awal dengan validasi bentuk (kosong/rusak/diblokir → mulai segar); seedChat hanya bila tidak ada riwayat tersimpan; simpan otomatis setelah seedChat, tandaiSudahDibaca, dan mintaBantuan; semua baca/tulis try/catch. Tombol “Ulang” kecil di bar atas membuka dialog konfirmasi kustom (role=dialog, aria-modal, fokus masuk ke “Batal”, perangkap Tab, Esc/ketuk di luar menutup); “Ya, ulang” menghapus kunci, membuat seed baru, mengembalikan state ke bawaan, seed ulang chat, render ulang, dan kembali ke layar Kantor; “Batal” tidak mengubah apa pun. Dicek dengan CHECKLIST.md, semua poin lolos.
- 2026-11-22: Generator data dan unduh template selesai — PRNG seed per pemain (hash FNV-1a + mulberry32, tanpa Math.random di jalur generator; seed sama → data sama, diverifikasi dengan Node pada 200 seed); template Tugas 1 sesuai §12 (sheet “Data”, header Produk/Qty/Harga/Total, 10 produk tetap, Qty 5–50, Harga kelipatan 500 2.000–21.500, kolom Total kosong, A12 “Total Penjualan”, A13 “Rata-rata”); SheetJS 0.18.5 dipatok dari cdnjs; tombol “Unduh Template” di halaman Tugas (kartu tugas aktif: judul + brief dari data) dan di lampiran chat Pak Bima (tombol kecil di samping chip), keduanya mengunduh “Template Rekap Penjualan Mingguan.xlsx” via Blob; bila SheetJS belum termuat, tampil toast ramah. Dicek dengan CHECKLIST.md, semua poin lolos.
- 2026-11-22: Mesin pemeriksa generik selesai — aturan cek Tugas 1 tersimpan sebagai JSON di DATA_TUGAS.rekap_penjualan.checks persis dari §12 (7 cek, total 100 poin, lulus ≥70); fungsi murni periksaWorkbook(wb, seed, aturan) + bacaWorkbookXlsx/periksaFileXlsx membaca file lewat SheetJS dengan cellFormula aktif; nilai harapan selalu dihitung dari data seed (buatDataTugas1), bukan dari file; evaluator ekspresi kecil tanpa eval (B*C per baris, sum/avg range); toleransi angka 0,01; nilai dari cache (.v), rumus dari .f; mendukung value, value_each, is_formula, formula_uses, no_errors, dan deteksi data diubah (A/B/C baris 2–11 vs seed); keluaran {skor, lulus, centang, kode} dengan kode terurut tetap altered, nocache, err, rowval, sum, hard; pemetaan kode diperbaiki setelah pengujian: cek value yang gagal karena nilai terbaca tapi salah → sum, value_each hanya → rowval bila ada nilai terbaca yang salah (kegagalan murni cache kosong hanya nocache); sheet “Data” hilang → skor 0 + altered. Belum ada UI unggah/tampilan hasil. Diuji dengan Node + SheetJS 0.18.5 pada 7 skenario file uji sungguhan (benar 100 tanpa kode; satu baris salah 35 [rowval, sum]; angka manual 70 [hard]; ada error 50 [err]; data diubah 100 [altered]; rumus tanpa cache 35 [nocache]; nilai D12 salah 80 [sum]) — semua lolos. Dicek dengan CHECKLIST.md, semua poin lolos.
- 2026-11-22: Balasan Pak Bima dan hasil pemeriksaan selesai — DATA_FEEDBACK berisi 9 kode (altered, nocache, err, rowval, sum, hard, ok90, ok70, fail) dengan 3 variasi tiap kode (kalimat §13 sebagai variasi pertama, variasi 2–3 usulan); pilihBalasanBima memakai kode masalah pertama menurut urutan mesin, atau ok90/ok70/fail dari skor bila tidak ada kode masalah, lalu memilih satu variasi acak; tombol “Unggah Laporan (.xlsx)” di kartu tugas aktif membuka pemilih file (accept .xlsx, maks 2 MB; file salah format/terlalu besar/rusak atau SheetJS belum termuat → toast ramah tanpa pemeriksaan; input dikosongkan setelah ditangani); file dibaca sebagai ArrayBuffer lalu periksaFileXlsx; setelah pemeriksaan, chat Pak Bima menerima pesan pemain “Laporan terkirim” dan balasan bos (disimpan via simpanProgres, belumDibaca.bima naik 1, lencana dan penanda kontak diperbarui, percakapan dirender bila sedang terbuka); halaman Tugas menampilkan #tugas-hasil (skor “Skor X dari 100”, status Lulus/Belum lulus, daftar centang per aturan dengan tanda ✓/✗, label, poin, detail) dan tombol “Lihat balasan Pak Bima” yang membuka chat Pak Bima; hasil hanya tampil di sesi ini (tidak disimpan permanen); tanpa perubahan XP/koin/status tugas. Diuji dengan Node + SheetJS 0.18.5 pada 9 skenario ujung-ke-ujung (semua kode balasan teruji) — semua lolos. Dicek dengan CHECKLIST.md, semua poin lolos.
- 2026-11-22: Hadiah dan progres tugas selesai — terapkanHadiah (fungsi murni, tanpa DOM): lulus skor 70–89 +100 XP/+100 koin, skor ≥90 +150 XP/+150 koin (bonus menggantikan hadiah biasa), gagal tanpa hadiah dan status jadi “dikerjakan”, lulus → status “selesai”, status “selesai” tidak bisa diberi hadiah lagi; hitungLevel tiap 250 XP (maks Level 4) dengan jabatan Magang/Staff/Senior/Manager; renderBarAtas memperbarui level, jabatan, bar XP (progres dalam level, penuh di Manager), dan koin, dipanggil di init, setelah hadiah, dan saat Ulang; Jobdesk menampilkan penanda “✓ Selesai” (data-penanda-selesai) dari state tersimpan; tugas berikutnya menjadi aktif lewat tugasAktifId + renderTugasAktif di prosesHasilPemeriksaan; tombol Unduh Template hanya tampil untuk rekap_penjualan (plus penjaga di handler klik), brief dikosongkan bila belum ada; tanganiUnggahLaporan menolak tugas selesai dengan toast; tampilkanHasilPemeriksaan(hasil, hadiah) menampilkan baris “Hadiah: …”/“Bonus: …” hanya bila hadiah baru diberikan; pop-up profil “Kamu” memakai jabatan dari level. Diuji dengan Node pada 26 kasus — semua lolos. Dicek dengan CHECKLIST.md, semua poin lolos.
- 2026-11-22: Tugas 2 (Absensi Karyawan) selesai — DATA_TUGAS.absensi diisi id, judul, dari, skill [COUNTIF, SUM], brief, lampiran, hint Rina 3 dan trik Dito 3 persis §12, checks JSON persis §12 (5 cek, 100 poin, pass 70); buatDataTugas2(seed) memakai PRNG yang sama (tanpa Math.random): header 9 kolom, 10 nama tetap (Andi, Budi, Citra, Dewi, Eko, Fitri, Gilang, Hana, Irfan, Joko — asumsi, §12 tidak menyebut nama), status H/I/A (rng <0,7 H, <0,9 I, sisanya A), G–I kosong, baris 12 “Total”; unduh digeneralisasikan lewat GENERATOR_TEMPLATE + unduhTemplate(tugasId) (Tugas 2: “Template Absensi Karyawan.xlsx”); tombol lampiran chat Bima tetap Tugas 1; periksaWorkbook memilih generator dari aturan.task (task tidak dikenal → skor 0 + altered); evaluator nilaiHarapanUntuk mendukung “countif(B:F, H|I|A)” dan “sum(kolom)” (tanpa eval; JSON §12 dipakai apa adanya, tanpa jenis cek baru); dataDiubah digeneralisasikan (sel tak-kosong AOA seed baris 2–11 kecuali tercakup cek); value_each gagal → “sum” bila range di baris ≥12, selain itu “rowval”; detail daftar centang memakai kata “sel”. Diuji dengan Node + SheetJS 0.18.5 (generator deterministik 200 seed, distribusi H 69,5%/I 20,5%/A 10,0%; 9 skenario mesin Tugas 2 dan regresi Tugas 1) — semua lolos. Dicek dengan CHECKLIST.md, semua poin lolos.
- 2026-11-22: Tugas 3 (Penilaian Magang) selesai — DATA_TUGAS.penilaian_magang diisi id, judul, dari, skill [AVERAGE, IF], brief, lampiran, hint Rina 3 dan trik Dito 3 persis §12, checks JSON persis §12 (5 cek, 100 poin, pass 70); buatDataTugas3(seed) memakai PRNG yang sama (tanpa Math.random): header 5 kolom, 10 nama tetap (Arif, Bunga, Candra, Dina, Fajar, Gita, Hendra, Intan, Kartika, Lukman — asumsi, §12 tidak menyebut nama), Teori/Praktik bilangan bulat 50–100, D/E kosong, tanpa baris total; tepat satu peserta rata-rata 75 di setiap seed (satu baris dipaksa B+C = 150, baris lain yang jumlahnya 150 digeser C ±1); penilaian_magang ditambahkan ke GENERATOR_TEMPLATE (“Template Penilaian Magang.xlsx”) dan ke pemilihan generator di periksaWorkbook; evaluator nilaiHarapanUntuk mendukung “avg(B,C)” dan “if(D>=75,'Lulus','Remedial')” (nilai rujukan dari aturan value_each yang mencakup sel itu, atau data seed; operator >=, >, <=, <, =, <>; batas inklusif — tepat 75 adalah Lulus; tanpa eval); value_each mendukung nilai harapan teks (perbandingan persis, peka huruf; teks terbaca yang salah → rowval). Diuji dengan Node + SheetJS 0.18.5 (generator deterministik 200 seed, tepat satu rata-rata 75 di 200 seed; 12 skenario mesin Tugas 3 dan regresi Tugas 1–2) — semua lolos. Dicek dengan CHECKLIST.md, semua poin lolos. Ketiga tugas Tahap 1 kini lengkap.
- 2026-11-22: Brief tugas di chat Pak Bima selesai — mekanisme kirimBriefTugas/kirimBriefTugasAktif: brief dikirim saat tugas terbuka (Tugas 1 saat mulai via init, Tugas 2/3 di akhir prosesHasilPemeriksaan setelah balasan Pak Bima, urutan chat “Laporan terkirim” → balasan → brief baru); pesan {dari: “bima”, teks: brief, lampiran, briefUntuk: tugasId}; terkirim hanya sekali (cek briefUntuk atau, untuk simpanan lama, kecocokan teks + nama lampiran; tanpa field state baru; tidak dipanggil saat pindah layar); menambah belumDibaca.bima 1 + simpan + render lencana/penanda; seedChat kini hanya menyemai sapaan Rina/Dito; tombol unduh lampiran memanggil unduhTemplate(pesan.briefUntuk || “rekap_penjualan”) dan unduhTemplateTugas1 dihapus; kondisiTugas() mengikuti tugas aktif (tanpa tugas aktif → “selesai”); lencana #popup-badge di pop-up menampilkan jumlah belum dibaca karakter itu; tombol “Kirim laporan” baru (#chat-btn-kirim-laporan) di #chat-aksi tampil hanya saat chatAktif bima dan ada tugas aktif, klik membuka layar Tugas; ulangDariAwal memanggil mekanisme setelah seedChat. Pemeriksa file dan penilaian tidak diubah (18 fungsi diverifikasi identik byte-per-byte). Diuji dengan Node (24 skenario: permainan baru, muat ulang, alur lulus penuh, gagal, semua selesai, simpanan lama, Ulang, kondisiTugas) — semua lolos. Dicek dengan CHECKLIST.md, semua poin lolos.
- 2026-11-22: Sinkronisasi status tugas selesai (perbaikan dari uji main Wibi) — satu sumber kebenaran state.tugas[id] = {status, hasilTerakhir} + state.tugasAktif; semua layar membaca lewat statusTugas()/tugasAktifId() (tugasAktifId kini mengembalikan state.tugasAktif); inisialisasiStatusTugas (Tugas 1 baru, Tugas 2/3 terkunci, aktif Tugas 1) di init dan ulangDariAwal; bukaTugasBerikutnya (lulus → berikutnya baru, tugasAktif pindah/null); hasilTerakhir disimpan sebagai salinan di prosesHasilPemeriksaan untuk “Lihat hasil”; perbaruiJobdesk merender seluruh kartu dari status (lencana, class task--locked, tombol “Terkunci” nonaktif/“Mulai Tugas”/“Lanjutkan”/“Lihat hasil”); tombol kartu disambung (Mulai/Lanjutkan → aturTugasAktif + layar Tugas; Lihat hasil → tampilkanHasilTersimpan); renderKartuTugas(id, modeSelesai) + renderTugasAktif menampilkan tugasAktif, null → ringkasan “Semua tugas selesai”; tampilkanLayar selalu merender ulang tugas aktif dan menyembunyikan hasil lama saat masuk layar Tugas; tombol “Lanjut ke Tugas berikutnya” di bagian hasil (tampil bila lulus dan ada tugas berikutnya; klik menyembunyikan hasil, merender tugas berikutnya, gulir ke kartu); aturTugasAktif menolak tugas terkunci/id tidak dikenal; muatProgres menormalisasi simpanan lama lewat normalisasiStatusTugas (string → objek; status dihitung ulang dari tugas sebelumnya; tugasAktif dari simpanan bila valid, bila tidak dari status; hasilTerakhir dipertahankan bila ada) lalu init menyimpan kembali bentuk baru; kondisiTugas dan penjaga unggah memakai bentuk baru. Pemeriksa file dan penilaian tidak diubah (18 fungsi identik byte-per-byte). Diuji dengan Node (33 skenario) — semua lolos. Dicek dengan CHECKLIST.md, semua poin lolos.
- 2026-11-22: Catatan “Lihat hasil” tanpa hasil tersimpan selesai (laporan Wibi: “Lihat hasil” Tugas 1 tidak menampilkan apa pun) — penyebabnya migrasi: Tugas 1 diselesaikan sebelum hasilTerakhir mulai disimpan, simpanan lama tidak menyimpan skor sehingga tidak ada yang bisa dipulihkan; tampilkanHasilTersimpan kini menampilkan catatan “Hasil pemeriksaan tidak tersimpan. Tugas ini diselesaikan sebelum hasil mulai disimpan.” (#tugas-hasil-catatan di dalam #tugas-hasil) bila hasilTerakhir null, dengan skor/status/hadiah/daftar centang/kedua tombol disembunyikan; bila hasil ada, hasil ditampilkan dan catatan disembunyikan; tampilkanHasilPemeriksaan selalu menyembunyikan catatan saat menampilkan hasil sungguhan. Pemeriksa file dan penilaian tidak diubah (30 fungsi identik byte-per-byte). Diuji dengan Node (13 skenario) — semua lolos. Dicek dengan CHECKLIST.md, semua poin lolos.
- 2026-11-22: Halaman uji tersembunyi #uji selesai — <section data-layar="uji"> + entri JUDUL_LAYAR (“Uji Pemeriksa”), tanpa item navigasi; tanganiHashUji dipanggil di init dan pada hashchange (#uji → tampilkanLayar + renderHasilUji; hash lain saat layar uji tampil → kembali ke Kantor); tombol “Kembali ke Kantor” menghapus hash via history.replaceState lalu ke Kantor, “Jalankan ulang” memanggil renderHasilUji; buatFileUji(tugasId, varianId) membangun .xlsx dari template seed saat ini (AOA generator → aoa_to_sheet → isi sel jawaban dari nilaiHarapanUntuk + peta rumus per tugas → XLSX.write array); varian: benar (rumus + cache benar), nilai-salah (cache sel pertama value_each +1, rumus tetap, agregat tidak dihitung ulang), manual (nilai benar tanpa rumus), error (sel pertama #DIV/0!), data-diubah (B2 diubah: T1/T3 +1, T2 status lain yang valid); jalankanUjiPemeriksaan menjalankan periksaFileXlsx ke 15 file dan membandingkan dengan HASIL_UJI_DIHARAPKAN (T1: 100/70/70/50/100; T2: 100/55/70/20/100; T3: 100/75/70/55/100; kode []/[rowval]/[hard]/[err]/[altered]); tabel 15 baris (Tugas | Varian | Diharapkan | Sebenarnya | Hasil | Unduh) + ringkasan “X dari 15 cocok” + seed + tautan Unduh (Blob dari byte yang sama); baris tidak cocok class uji__baris--beda; tabel overflow-x auto di HP; renderHasilUji menampilkan pesan ramah bila XLSX belum termuat; halaman uji tidak mengubah state (tanpa simpanProgres/prosesHasilPemeriksaan). Pemeriksa file dan penilaian tidak diubah (30 fungsi identik byte-per-byte). Diuji dengan Node + SheetJS 0.18.5 (21 skenario: 15/15 cocok pada 2 seed, state/localStorage tidak berubah, render + offline) — semua lolos. Dicek dengan CHECKLIST.md, semua poin lolos.
- 2026-11-22: Tinjauan lebar 360/768/1440 px selesai — 10 perbaikan: hotspot diperbesar (Bima 42%/22%/14%×24%, Dito 81%/40%/14%×31%, pemain 67%/68%/14%×31%, Rina tetap) + chip label disesuaikan (Bima 47,9%/12,5%, Dito 47,9%/−3,2%, Kamu HP 57,9%/−6,5%; jangkar adegan 48,7%/25%, 87,7%/39%, 75,1%/66% tetap) sehingga semua ≥44 px di 360 px tanpa tumpang tindih; min-height 44 px untuk .btn-ulang, .btn-unduh-kecil, .task .btn-primary; 44×44 px untuk .chat__kembali dan .sheet__close; .uji__unduh inline-flex min-height 44 px; media query 900–1199 px: body.layar-kantor .sidebar width 132 px + nav-item dipadatkan (0.85rem, padding 8px 10px, gap 6px) agar tidak menutupi hotspot Rina (tepi kanan 146 px < 153 px); .badge--locked color var(--card-text); mode terang --muted/--card-muted #5a7268 → #547065. Diperiksa dan lolos tanpa perbaikan: tidak ada elemen terpotong di ketiga lebar, fokus keyboard terlihat (outline 3 px global + sorotan hotspot), animasi mengikuti hemat gerak (aturan global + scrollIntoView auto + denyut dilewati), pop-up desktop dijaga di dalam adegan (clamp JS 8 px), Jobdesk desktop berhenti 12 px di atas Dito. Fungsi game tidak diubah (30 fungsi identik byte-per-byte). Dicek dengan CHECKLIST.md, semua poin lolos.
- 2026-11-22: Panel “Sebelum mulai” selesai — <div id="panel-panduan" class="dialog-backdrop" hidden> + <div class="popup popup--panduan" role="dialog" aria-modal="true" aria-labelledby="panel-panduan-judul"> mengikuti pola dialog Ulang (kartu tengah maks 440 px, max-height calc(100dvh − 32px) + overflow-y auto); isi: judul “Sebelum mulai”, daftar ol 4 langkah (brief Pak Bima di Chat; unduh template di halaman Tugas; kerjakan di spreadsheet + hint Rina/trik Dito; unggah hasil dan lihat skor), catatan 💾 progres tersimpan otomatis di browser, catatan 📊 butuh Excel/Google Sheets, tombol .btn-primary--full “Mulai bermain”; JS: KUNCI_PANDUAN = “office-quest-sebelum-mulai-v1” (try/catch; terpisah dari simpanan game, Ulang tidak menghapusnya), panduanSudahDilihat/tandaiPanduanDilihat/bukaPanelPanduan/tutupPanelPanduan; init() di akhir menampilkan panel bila tanda belum ada dan hash bukan #uji; semua jalur tutup (tombol, Esc, ketuk di luar) menandai “sudah”; fokus masuk ke tombol, perangkap Tab, fokus kembali ke #kantor-title. Fungsi game tidak diubah (diff script vs versi tinjauan: hanya 76 baris penambahan, 0 baris diubah/dihapus). Diuji Node (14 skenario) — semua lolos. Dicek dengan CHECKLIST.md, semua poin lolos.
- 2026-11-22: Kerangka struktur repo Tahap 2+ dibuat (tanpa kode baru) — office-quest/ dengan frontend/ (salinan index.html Tahap 1 + public/assets/ berisi 6 gambar siap pakai), backend/ (app, rules, tests/fixtures), database/, content/, design/ (Character_Sheet.md + 6 gambar mentah: latar, adegan, 4 sheet karakter), docs/ (PROJECT.md, PRD, CHECKLIST.md, PROMPTS.md kerangka), scripts/, .github/; tiap folder berisi README penjelas (16 README); disimpan sebagai office-quest-struktur.zip (6,2 MB). Deploy Tahap 1 (satu index.html di akar repo) tidak berubah.
- 2026-11-22: Prompt untuk menyusun PROJECT.md Tahap 2 di Claude dibuat (PROMPT_CLAUDE_TAHAP_2.md) — berisi konteks Tahap 1, struktur repo Tahap 2+, usulan urutan kerja (pecah frontend → content/ → rules/ → backend Python → sambung frontend-backend → deploy otomatis → Toko/Tantangan/Koleksi berfungsi), dan aturan cara kerja Poppi agar dokumen yang dihasilkan Claude selaras; keputusan model konten (kampanye / harian tanpa akhir / hibrida) ditulis sebagai pertanyaan terbuka, bukan diputuskan sepihak.
- 2026-11-22: Keputusan model konten dibuat Wibi — game harian tanpa akhir dengan kesulitan yang meningkat seiring bertambahnya level (bukan kampanye yang bisa ditamatkan, bukan hibrida). Implikasi: tugas harian dari generator (±15–25 jenis tugas, 3/hari dengan seed harian), jenis tugas baru terbuka seiring jabatan, tiap jenis punya tangga kesulitan yang naik mengikuti level; PROMPT_CLAUDE_TAHAP_2.md diperbarui dengan keputusan ini (bagian 5 prompt kini berisi model yang diputuskan + catatan soal batas Level 4). Perhatian untuk draf Tahap 2: sistem level Tahap 1 berhenti di Level 4 (Manager) — draf harus mengusulkan penanganan pemain level tertinggi dalam game tanpa akhir.
- [tanggal]: [apa yang selesai atau berubah]
