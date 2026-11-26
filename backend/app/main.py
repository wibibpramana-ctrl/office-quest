"""API backend Office Quest (FastAPI).

Endpoint:
- GET  /sehat            — cek hidup
- POST /tugas/tiket      — terbitkan tiket satu jenis tugas
- GET  /tugas/template   — unduh template .xlsx (pakai tiket)
- POST /periksa          — periksa file jawaban (tiket + file)

Aturan keamanan (3.5–3.7):
- CORS hanya untuk alamat GitHub Pages game.
- Pembatas laju per IP (jendela geser 60 detik) untuk endpoint tugas.
- Log hanya mencatat metode/jalan/status/waktu/ukuran/skor/kode —
  TIDAK PERNAH isi file, string tiket, atau garam.
- Garam dibaca dari variabel lingkungan OFFICE_QUEST_GARAM (malas:
  dibaca saat pertama dipakai; bila belum diatur endpoint tugas
  menjawab 503). Login/sesi menyusul di Fase 5 — endpoint ini belum
  memakai otentikasi (mode tamu diizinkan Tahap 2).

Kode galat: 400 permintaan tidak valid, 403 tiket tidak sah,
410 tiket kedaluwarsa, 413 file terlalu besar, 415 bukan .xlsx,
429 terlalu sering, 503 server belum dikonfigurasi / waktu habis.
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from app.checker import muat_aturan, periksa_bytes
from app.template import nama_file_template, template_ke_bytes
from app.tiket import (
    WIB,
    GalatGaram,
    GalatTiket,
    benih_harian,
    data_untuk_tiket,
    garam_dari_lingkungan,
    periksa_tiket,
    terbitkan_tiket,
    turunkan_seed,
)
from app.validasi import BATAS_WAKTU_DETIK, BatasWaktu, GalatValidasi, validasi_unggahan

ASAL_PAGES = "https://wibibpramana-ctrl.github.io"
BATAS_LAJU_PER_MENIT = 30
TIPE_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

logger = logging.getLogger("office_quest")
logger.setLevel(logging.INFO)  # tanpa ini, baris info tidak muncul di log server
if not logger.handlers:
    # Handler sendiri supaya log muncul di stderr server (uvicorn tidak
    # memasang handler untuk logger aplikasi).
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(_handler)

_DIR_CONTENT = Path(__file__).resolve().parent.parent.parent / "content"


def catat(peristiwa, **rincian):
    """Satu baris log key=value. Jangan pernah memasukkan isi file,
    string tiket, atau garam ke rincian."""
    logger.info(peristiwa + " " + " ".join(f"{k}={v}" for k, v in rincian.items()))


class PembatasLaju:
    """Pembatas laju per IP, jendela geser 60 detik, di memori."""

    def __init__(self, batas_per_menit=BATAS_LAJU_PER_MENIT):
        self.batas = batas_per_menit
        self.riwayat = {}

    def izinkan(self, ip):
        sekarang = time.monotonic()
        daftar = [t for t in self.riwayat.get(ip, []) if sekarang - t < 60]
        if len(daftar) >= self.batas:
            self.riwayat[ip] = daftar
            return False
        daftar.append(sekarang)
        self.riwayat[ip] = daftar
        return True

    def reset(self):
        self.riwayat.clear()


def _ip_klien(request):
    teruskan = request.headers.get("x-forwarded-for", "")
    if teruskan:
        return teruskan.split(",")[0].strip()
    return request.client.host if request.client else "tidak-diketahui"


def _galat_tiket_http(e):
    if e.kode == "tiket_kedaluwarsa":
        return HTTPException(410, detail={"kode": e.kode, "pesan": e.pesan})
    return HTTPException(403, detail={"kode": e.kode, "pesan": e.pesan})


_KODE_HTTP_VALIDASI = {
    "file_terlalu_besar": 413,
    "dekompresi_terlalu_besar": 413,
    "sel_terlalu_banyak": 413,
    "xlsm_ditolak": 415,
    "ekstensi_salah": 415,
    "bukan_arsip_valid": 415,
    "bukan_xlsx": 415,
    "waktu_habis": 503,
}


def _muat_deadline(jenis):
    """Deadline dari content/tugas/<jenis>.json; None bila tidak ada."""
    try:
        with open(_DIR_CONTENT / "tugas" / f"{jenis}.json", encoding="utf-8") as f:
            return json.load(f).get("deadline")
    except Exception:
        return None


def _parameter_brief(jenis, aoa):
    """Parameter untuk mengisi placeholder brief ({{jumlah}}, {{deadline}}):
    jumlah = banyak baris data (di antara header dan baris Total/Rata-rata)."""
    jumlah = 0
    for baris in aoa[1:]:
        pertama = baris[0] if baris else None
        if isinstance(pertama, str) and (pertama.startswith("Total") or pertama.startswith("Rata-rata")):
            break
        jumlah += 1
    return {"jumlah": jumlah, "deadline": _muat_deadline(jenis)}


def _dapatkan_garam(request):
    garam = request.app.state.garam
    if garam is None:
        try:
            garam = garam_dari_lingkungan()
        except GalatGaram as e:
            raise HTTPException(503, detail={"kode": "garam_belum_diatur", "pesan": str(e)}) from None
        request.app.state.garam = garam
    return garam


class TiketMinta(BaseModel):
    jenis: str
    tier: int = 1
    id_pemain: str | None = None
    benih: str | None = None
    modifier: str | None = None


def buat_app(garam=None, batas_laju_per_menit=BATAS_LAJU_PER_MENIT):
    app = FastAPI(title="Office Quest Backend")

    app.state.garam = garam
    app.state.pembatas = PembatasLaju(batas_laju_per_menit)

    @app.middleware("http")
    async def pembatas_dan_catat(request, call_next):
        mulai = time.monotonic()
        jalan = request.url.path
        if jalan.startswith("/tugas/") or jalan == "/periksa":
            if request.method in ("GET", "POST") and not request.app.state.pembatas.izinkan(_ip_klien(request)):
                catat("terlalu_sering", metode=request.method, jalan=jalan, ip=_ip_klien(request))
                return JSONResponse(
                    status_code=429,
                    content={"kode": "terlalu_sering", "pesan": "Terlalu banyak permintaan, coba lagi sebentar lagi."},
                )
        respons = await call_next(request)
        catat(
            "permintaan",
            metode=request.method,
            jalan=jalan,
            status=respons.status_code,
            ms=round((time.monotonic() - mulai) * 1000),
        )
        return respons

    # CORS paling luar (ditambahkan terakhir) supaya preflight OPTIONS
    # dijawab sebelum menyentuh pembatas laju.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[ASAL_PAGES],
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @app.get("/sehat")
    def sehat():
        return {"status": "ok"}

    @app.post("/tugas/tiket")
    def buat_tiket(data: TiketMinta, request: Request):
        garam = _dapatkan_garam(request)
        benih = data.benih
        if benih is None and data.id_pemain:
            benih = benih_harian(data.id_pemain, datetime.now(WIB).date().isoformat())
        try:
            tiket = terbitkan_tiket(
                data.jenis, garam, tier=data.tier, benih_publik=benih, modifier=data.modifier
            )
            muatan = periksa_tiket(tiket, garam)
        except GalatTiket as e:
            raise HTTPException(400, detail={"kode": e.kode, "pesan": e.pesan}) from None
        aoa = data_untuk_tiket(muatan, garam)
        catat("tiket", jenis=data.jenis, tier=data.tier, ip=_ip_klien(request))
        return {
            "tiket": tiket,
            "jenis": muatan["jenis"],
            "tier": muatan["tier"],
            "kedaluwarsa": muatan["kedaluwarsa"],
            "parameter_brief": _parameter_brief(muatan["jenis"], aoa),
        }

    @app.get("/tugas/template")
    def unduh_template(tiket: str, request: Request):
        garam = _dapatkan_garam(request)
        try:
            muatan = periksa_tiket(tiket, garam)
        except GalatTiket as e:
            raise _galat_tiket_http(e) from None
        isi = template_ke_bytes(muatan["jenis"], turunkan_seed(muatan["benih"], garam))
        catat("template", jenis=muatan["jenis"], ukuran=len(isi), ip=_ip_klien(request))
        return Response(
            content=isi,
            media_type=TIPE_XLSX,
            headers={"Content-Disposition": f'attachment; filename="{nama_file_template(muatan["jenis"])}"'},
        )

    @app.post("/periksa")
    async def periksa_jawaban(request: Request, tiket: str = Form(...), file: UploadFile = File(...)):
        garam = _dapatkan_garam(request)
        try:
            muatan = periksa_tiket(tiket, garam)
        except GalatTiket as e:
            raise _galat_tiket_http(e) from None
        data = await file.read()
        batas = BatasWaktu(BATAS_WAKTU_DETIK)
        try:
            validasi_unggahan(data, file.filename, batas_waktu=batas)
            aturan = muat_aturan(muatan["jenis"])
            hasil = periksa_bytes(
                data, turunkan_seed(muatan["benih"], garam), aturan, batas_waktu=batas
            )
        except GalatValidasi as e:
            catat("periksa_gagal", jenis=muatan["jenis"], kode=e.kode, ukuran=len(data))
            raise HTTPException(
                status_code=_KODE_HTTP_VALIDASI.get(e.kode, 400),
                detail={"kode": e.kode, "pesan": e.pesan},
            ) from None
        catat(
            "periksa",
            jenis=muatan["jenis"],
            skor=hasil["skor"],
            lulus=hasil["lulus"],
            kode=",".join(hasil["kode"]) or "-",
            ukuran=len(data),
        )
        return {
            "skor": hasil["skor"],
            "lulus": hasil["lulus"],
            "centang": hasil["centang"],
            "kode": hasil["kode"],
            "batas_waktu": "ok",
        }

    return app


app = buat_app()
