# Backend Office Quest

Layanan API game Office Quest (Python, FastAPI). Frontend statis tetap di
GitHub Pages; layanan ini dihosting terpisah (lihat D1 di
`docs/project_tahap2_poppi.md` — Render, tier gratis).

> Kunci jawaban dan garam tidak pernah ada di frontend. Garam rahasia
> hanya ada di variabel lingkungan hosting (`OFFICE_QUEST_GARAM`).
> Jangan simpan rahasia apa pun di repo ini — repositori bersifat publik.

## Menjalankan

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Buka http://localhost:8000/sehat — jawabannya:

```json
{"status": "ok"}
```

Dokumentasi API otomatis (Swagger): http://localhost:8000/docs

## Menjalankan tes

```bash
cd backend
pytest
```

Ukur beban: `python scripts/ukur-beban.py` (laporan di `docs/ukur-beban.md`).

## Endpoint

| Metode | Jalan | Keterangan |
| --- | --- | --- |
| GET | `/sehat` | Cek hidup |
| POST | `/tugas/tiket` | Terbitkan tiket satu jenis tugas (jenis, tier, id_pemain, benih, modifier) |
| GET | `/tugas/template?tiket=...` | Unduh template .xlsx untuk tiket itu |
| POST | `/periksa` | Periksa file jawaban (form: tiket + file) |

CORS hanya untuk `https://wibibpramana-ctrl.github.io`. Pembatas laju:
30 permintaan/menit per IP untuk endpoint tugas (429 bila lewat).
Log hanya mencatat metode/jalan/status/waktu/ukuran/skor/kode — tidak
pernah isi file, string tiket, atau garam.

## Variabel lingkungan

| Variabel | Isi |
| --- | --- |
| `OFFICE_QUEST_GARAM` | Garam rahasia untuk tanda tangan tiket (buat dengan `python -c "import secrets; print(secrets.token_hex(32))"`). Isi di dashboard hosting, bukan di repo. |

Contoh nama variabel (tanpa nilai) ada di `.env.example`.

## Struktur

```
backend/
  app/            kode layanan (FastAPI)
    main.py       titik masuk + endpoint + CORS + pembatas laju + log
    generator.py  generator data tugas (port persis dari JS, mode paritas)
    template.py   pembuat template .xlsx (openpyxl, sheet "Data")
    checker.py    mesin pemeriksa file .xlsx (port periksaWorkbook)
    validasi.py   validasi unggahan (ukuran, .xlsm, arsip, sel, waktu)
    tiket.py      tiket tugas bertanda tangan HMAC + seed dari garam
  rules/          aturan cek tiap tugas (JSON, evaluator)
  scripts/
    ukur-beban.py ukur waktu /periksa file 2 MB + 20 permintaan beruntun
  tests/          tes pytest + fixtures
    fixtures/     15 file uji pemeriksa (#uji) + manifest.json
                  paritas-generator.json (sha256 AOA JS untuk 200 seed)
                  paritas-template.json (isi sheet Data template browser, 20 seed)
    test_sehat.py
    test_generator_paritas.py
    test_template.py
    test_checker.py
    test_validasi.py
    test_tiket.py
    test_api.py
    test_beban.py
  requirements.txt
  .env.example
```

Batas unggahan (validasi.py): file 2 MB, dekompresi 20 MB, 100.000 sel,
waktu proses 10 detik; file .xlsm ditolak. Tiket berlaku sampai 02.00 WIB
hari berikutnya.

Fase 3 selesai. Berikutnya: Fase 4 (deploy backend).
