# Backend Office Quest

Layanan API game Office Quest (Python, FastAPI). Frontend statis tetap di
GitHub Pages; layanan ini dihosting terpisah (lihat D1 di
`docs/project_tahap2_poppi.md` — Render, tier gratis).

> Mode paritas (sampai Langkah 3.6): endpoint di sini belum memakai garam
> rahasia. Kunci jawaban dan garam tidak pernah ada di frontend. Jangan
> simpan rahasia apa pun di repo ini — repositori bersifat publik.

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

## Struktur

```
backend/
  app/            kode layanan (FastAPI)
    main.py       titik masuk + endpoint /sehat
    generator.py  generator data tugas (port persis dari JS, mode paritas)
  tests/          tes pytest + fixtures
    fixtures/     15 file uji pemeriksa (#uji) + manifest.json
                  paritas-generator.json (sha256 AOA JS untuk 200 seed)
    test_sehat.py
    test_generator_paritas.py
  requirements.txt
```

Langkah berikutnya (Fase 3): 3.3 pembuat template .xlsx, 3.4 mesin
pemeriksa, 3.5 validasi unggahan, 3.6 garam + tiket, 3.7 endpoint tugas,
3.8 ukur beban.
