"""Layanan backend Office Quest (FastAPI).

Fase 3 Tahap 2 — mode paritas: endpoint di sini belum memakai garam
rahasia. Kunci jawaban dan garam tidak pernah ada di frontend.
"""

from fastapi import FastAPI

app = FastAPI(title="Office Quest API")


@app.get("/sehat")
def sehat():
    """Pemeriksaan kesehatan layanan; mengembalikan ok bila layanan hidup."""
    return {"status": "ok"}
