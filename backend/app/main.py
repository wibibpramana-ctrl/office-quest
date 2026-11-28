"""API backend Office Quest (FastAPI).

Endpoint:
- GET  /sehat            — cek hidup
- POST /tugas/tiket      — terbitkan tiket satu jenis tugas
- GET  /tugas/template   — unduh template .xlsx (pakai tiket)
- POST /periksa          — periksa file jawaban (tiket + file)
- POST /akun/daftar      — daftar akun baru (Fase 5.2)
- POST /akun/masuk       — masuk, terbitkan token sesi (Fase 5.2)
- POST /akun/keluar      — keluar, hapus sesi (Fase 5.2)
- GET  /akun/saya        — info akun sendiri (Fase 5.2)
- POST /akun/ganti-kata-sandi — ganti kata sandi (Fase 5.2)
- POST /akun/migrasi      — pindahkan progres lokal ke akun (Fase 5.4)

Aturan keamanan (3.5–3.7):
- CORS hanya untuk alamat GitHub Pages game.
- Pembatas laju per IP (jendela geser 60 detik) untuk endpoint tugas,
  periksa, dan akun.
- Log hanya mencatat metode/jalan/status/waktu/ukuran/skor/kode —
  TIDAK PERNAH isi file, string tiket, token sesi, atau garam.
- Garam dibaca dari variabel lingkungan OFFICE_QUEST_GARAM (malas:
  dibaca saat pertama dipakai; bila belum diatur endpoint tugas
  menjawab 503). Akun/sesi (Fase 5.2): kata sandi hanya hash argon2id,
  token sesi disimpan sebagai hash SHA-256; basis data SQLite dari
  OFFICE_QUEST_DB (bila belum diatur endpoint akun menjawab 503).
  Endpoint tugas/periksa belum memakai otentikasi (mode tamu diizinkan
  Tahap 2).

Kode galat: 400 permintaan tidak valid, 401 belum masuk / sesi habis /
kredensial salah, 403 tiket tidak sah, 409 nama/email sudah dipakai,
410 tiket kedaluwarsa, 413 file terlalu besar, 415 bukan .xlsx,
429 terlalu sering, 503 server belum dikonfigurasi / waktu habis.
"""

import json
import logging
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from app import akun as layanan_akun
from app.akun import GalatAkun
from app.checker import muat_aturan, periksa_bytes
from app.db import buka_db
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
        if (
            jalan.startswith("/tugas/")
            or jalan == "/periksa"
            or jalan.startswith("/akun/")
        ):
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
        allow_headers=["Content-Type", "Authorization"],  # Authorization: token sesi (5.2)
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

    # --- Akun & sesi (Fase 5.2) ---

    @contextmanager
    def _db():
        conn = buka_db()
        if conn is None:
            raise HTTPException(
                503,
                detail={
                    "kode": "basis_data_belum_diatur",
                    "pesan": "Basis data belum diatur di server.",
                },
            )
        try:
            yield conn
        finally:
            conn.close()

    def _galat_akun_http(e):
        return HTTPException(e.status, detail={"kode": e.kode, "pesan": e.pesan})

    def _token_dari_header(request):
        auth = request.headers.get("authorization", "")
        if auth.lower().startswith("bearer "):
            return auth[7:].strip()
        return None

    def _akun_saat_ini(request, conn):
        try:
            akun, _sesi = layanan_akun.akun_dari_token(
                conn, _token_dari_header(request)
            )
        except GalatAkun as e:
            raise _galat_akun_http(e) from None
        return akun

    class DaftarMinta(BaseModel):
        nama_akun: str
        kata_sandi: str
        nama_panggilan: str | None = None
        email: str | None = None
        perangkat: str | None = None

    class MasukMinta(BaseModel):
        nama_akun: str
        kata_sandi: str
        perangkat: str | None = None

    class GantiKataSandiMinta(BaseModel):
        kata_sandi_lama: str
        kata_sandi_baru: str

    class MigrasiMinta(BaseModel):
        xp: int
        koin: int
        chat: list[dict] = []

    @app.post("/akun/daftar", status_code=201)
    def daftar(data: DaftarMinta, request: Request):
        with _db() as conn:
            try:
                akun_id = layanan_akun.buat_akun(
                    conn, data.nama_akun, data.nama_panggilan, data.email, data.kata_sandi
                )
                token = layanan_akun.buat_sesi(conn, akun_id, data.perangkat)
            except GalatAkun as e:
                raise _galat_akun_http(e) from None
            akun = layanan_akun.cari_akun_id(conn, akun_id)
        catat("daftar", ip=_ip_klien(request))
        return {**layanan_akun.info_akun_publik(akun), "token": token}

    @app.post("/akun/masuk")
    def masuk(data: MasukMinta, request: Request):
        with _db() as conn:
            try:
                akun = layanan_akun.periksa_masuk(conn, data.nama_akun, data.kata_sandi)
                token = layanan_akun.buat_sesi(conn, akun["id"], data.perangkat)
            except GalatAkun as e:
                raise _galat_akun_http(e) from None
        catat("masuk", ip=_ip_klien(request))
        return {"token": token, "akun": layanan_akun.info_akun_publik(akun)}

    @app.post("/akun/keluar")
    def keluar(request: Request):
        with _db() as conn:
            try:
                token = _token_dari_header(request)
                layanan_akun.akun_dari_token(conn, token)
                layanan_akun.hapus_sesi(conn, token)
            except GalatAkun as e:
                raise _galat_akun_http(e) from None
        catat("keluar", ip=_ip_klien(request))
        return {"status": "ok"}

    @app.get("/akun/saya")
    def saya(request: Request):
        with _db() as conn:
            akun = _akun_saat_ini(request, conn)
        return layanan_akun.info_akun_publik(akun)

    @app.post("/akun/ganti-kata-sandi")
    def ganti_kata_sandi(data: GantiKataSandiMinta, request: Request):
        with _db() as conn:
            try:
                token = _token_dari_header(request)
                akun, _sesi = layanan_akun.akun_dari_token(conn, token)
                if not layanan_akun.periksa_kata_sandi(
                    akun["hash_kata_sandi"], data.kata_sandi_lama
                ):
                    raise GalatAkun("kredensial_salah", "Kata sandi lama salah.", 401)
                layanan_akun.validasi_kata_sandi(data.kata_sandi_baru)
                layanan_akun.ganti_kata_sandi(
                    conn, akun["id"], layanan_akun.hash_kata_sandi(data.kata_sandi_baru)
                )
                layanan_akun.hapus_sesi_lain(conn, akun["id"], token)
            except GalatAkun as e:
                raise _galat_akun_http(e) from None
        catat("ganti_kata_sandi", ip=_ip_klien(request))
        return {"status": "ok"}

    @app.post("/akun/migrasi")
    def migrasi(data: MigrasiMinta, request: Request):
        with _db() as conn:
            try:
                akun = _akun_saat_ini(request, conn)
                hasil = layanan_akun.migrasi_progres(
                    conn, akun["id"], data.xp, data.koin, data.chat
                )
            except GalatAkun as e:
                raise _galat_akun_http(e) from None
        catat(
            "migrasi",
            akun_id=akun["id"],
            xp=data.xp,
            koin=data.koin,
            pesan=hasil["pesan_chat"],
        )
        return {"status": "ok", "progres": hasil}

    return app


app = buat_app()
