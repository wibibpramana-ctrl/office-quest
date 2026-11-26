"""Mesin pemeriksa file .xlsx Office Quest (Python).

Port dari ``periksaWorkbook`` di ``index.html``. Aturan cek dibaca dari
``backend/rules/<tugas>.json`` (bentuk evaluator, lihat
``docs/skema-aturan.md``). Nilai harapan selalu dihitung dari data seed
(generator), bukan dari file — jadi mengubah angka di file tidak bisa
mengubah target.

Sel dibaca dengan openpyxl dua kali: sekali tanpa ``data_only`` (rumus)
dan sekali dengan ``data_only`` (nilai cache), karena satu pemuatan
openpyxl tidak bisa memberi keduanya sekaligus. Model selnya meniru
sel SheetJS: ``rumus`` (= ``sel.f``, tanpa "="), ``nilai`` (= ``sel.v``,
nilai cache atau literal), ``error`` (= ``sel.t === "e"``).

Jenis cek Tahap 1 yang didukung: value, value_each, is_formula,
formula_uses, no_errors. (Jenis baru — sheet_ada, urutan, filter_aktif,
format_angka, bersih — dibuat saat dibutuhkan, lihat skema 2.1.)
"""

import io
import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path

from openpyxl import load_workbook

from app.generator import buat_data_tugas

TOLERANSI_NILAI = 0.01
URUTAN_KODE = ["altered", "nocache", "err", "rowval", "sum", "hard"]

_DIR_RULES = Path(__file__).resolve().parent.parent / "rules"


# ---------------------------------------------------------------------------
# Alamat sel & range (A1)
# ---------------------------------------------------------------------------

def kolom_ke_indeks(huruf):
    """'A' -> 0, 'B' -> 1, 'AA' -> 26 (``kolomKeIndeks`` di JS)."""
    idx = 0
    for ch in str(huruf).upper():
        idx = idx * 26 + (ord(ch) - 64)
    return idx - 1


def indeks_ke_kolom(idx):
    """0 -> 'A', 26 -> 'AA' (``indeksKeKolom`` di JS)."""
    s = ""
    n = idx + 1
    while n > 0:
        sisa = (n - 1) % 26
        s = chr(65 + sisa) + s
        n = (n - 1) // 26
    return s


def parse_alamat_sel(teks):
    """'D12' -> {'kolom': 3, 'baris': 12} (baris 1-based)."""
    m = re.match(r"^\s*\$?([A-Za-z]+)\$?(\d+)\s*$", str(teks))
    if not m:
        return None
    return {"kolom": kolom_ke_indeks(m.group(1)), "baris": int(m.group(2))}


def nama_sel(kolom, baris):
    return indeks_ke_kolom(kolom) + str(baris)


def parse_range(teks):
    """'D2:D11' (atau satu sel 'D12') -> daftar alamat urut baris."""
    bagian = str(teks).split(":")
    awal = parse_alamat_sel(bagian[0])
    if not awal:
        return []
    akhir = parse_alamat_sel(bagian[1]) if len(bagian) > 1 else awal
    if not akhir:
        return []
    daftar = []
    for b in range(awal["baris"], akhir["baris"] + 1):
        for k in range(awal["kolom"], akhir["kolom"] + 1):
            daftar.append({"kolom": k, "baris": b})
    return daftar


def alamat_sasaran(cek):
    """Daftar alamat sasaran satu aturan cek (range, kalau tidak cell)."""
    if cek.get("range"):
        return parse_range(cek["range"])
    if cek.get("cell"):
        a = parse_alamat_sel(cek["cell"])
        return [a] if a else []
    return []


def teks_sasaran(cek):
    return cek.get("range") or cek.get("cell") or ""


# ---------------------------------------------------------------------------
# Model sel (meniru sel SheetJS)
# ---------------------------------------------------------------------------

@dataclass
class Sel:
    rumus: str | None = None  # tanpa "=", seperti sel.f
    nilai: object = None      # nilai cache / literal, seperti sel.v
    error: bool = False       # sel.t === "e"


@dataclass
class Lembar:
    nama: str
    sel: dict = field(default_factory=dict)  # (kolom, baris) -> Sel


def _sel_dari_openpyxl(ws_rumus, ws_cache):
    """Gabung dua pemuatan openpyxl menjadi peta sel model SheetJS."""
    peta = {}
    coords = set()
    for ws in (ws_rumus, ws_cache):
        if ws is None:
            continue
        for (baris, kolom), _sel in ws._cells.items():
            coords.add((kolom - 1, baris))
    for (kolom, baris) in coords:
        sel_rumus = ws_rumus.cell(row=baris, column=kolom + 1) if ws_rumus is not None else None
        sel_cache = ws_cache.cell(row=baris, column=kolom + 1) if ws_cache is not None else None
        rumus = None
        error = False
        if sel_rumus is not None:
            if sel_rumus.data_type == "f":
                rumus = str(sel_rumus.value)[1:] if str(sel_rumus.value).startswith("=") else str(sel_rumus.value)
            if sel_rumus.data_type == "e":
                error = True
        nilai = None
        if sel_cache is not None:
            nilai = sel_cache.value
            if sel_cache.data_type == "e":
                error = True
        # Sel yang benar-benar kosong di kedua pemuatan tidak dicatat.
        if rumus is None and nilai is None and not error:
            continue
        peta[(kolom, baris)] = Sel(rumus=rumus, nilai=nilai, error=error)
    return peta


def muat_lembar(data, nama_sheet):
    """Baca bytes .xlsx, kembalikan Lembar bernama itu, atau None bila
    sheet tidak ada / file tidak bisa dibaca (diperlakukan seperti
    sheet tidak ada, sama seperti wb null di periksaWorkbook)."""
    try:
        wb_rumus = load_workbook(io.BytesIO(data), data_only=False)
        wb_cache = load_workbook(io.BytesIO(data), data_only=True)
    except Exception:
        return None
    if nama_sheet not in wb_rumus.sheetnames:
        return None
    ws_rumus = wb_rumus[nama_sheet]
    ws_cache = wb_cache[nama_sheet] if nama_sheet in wb_cache.sheetnames else None
    return Lembar(nama=nama_sheet, sel=_sel_dari_openpyxl(ws_rumus, ws_cache))


def ambil_sel(lembar, kolom, baris):
    if lembar is None:
        return None
    return lembar.sel.get((kolom, baris))


# ---------------------------------------------------------------------------
# Helper nilai sel
# ---------------------------------------------------------------------------

def nilai_cache_angka(sel):
    """Nilai cache sel sebagai angka; None bila kosong/bukan angka/error."""
    if sel is None or sel.error or sel.nilai is None or sel.nilai == "":
        return None
    if isinstance(sel.nilai, bool):
        return 1.0 if sel.nilai else 0.0
    if isinstance(sel.nilai, (int, float)):
        n = float(sel.nilai)
        return n if math.isfinite(n) else None
    if isinstance(sel.nilai, str):
        try:
            n = float(sel.nilai)
        except ValueError:
            return None
        return n if math.isfinite(n) else None
    return None


def sel_berisi_angka(sel):
    """Sel 'berisi angka': nilai cache berupa angka (bukan error/kosong)."""
    return (
        sel is not None
        and not sel.error
        and isinstance(sel.nilai, (int, float))
        and not isinstance(sel.nilai, bool)
        and math.isfinite(sel.nilai)
    )


def sel_punya_rumus(sel):
    return sel is not None and isinstance(sel.rumus, str) and sel.rumus.strip() != ""


def cache_kosong(sel):
    return sel is None or sel.nilai is None or sel.nilai == ""


def angka_sama(a, b):
    return abs(a - b) <= TOLERANSI_NILAI


def format_angka(n):
    """Seperti formatAngka di JS: bulatkan ke 2 desimal (Math.round)."""
    if not isinstance(n, (int, float)) or isinstance(n, bool) or not math.isfinite(n):
        return "—"
    bulat = math.floor(n * 100 + 0.5) / 100
    if bulat == int(bulat):
        return str(int(bulat))
    return repr(bulat)


def nama_fungsi_rumus(rumus):
    """Nama fungsi dari teks rumus (tanpa '='), huruf besar, tanpa duplikat."""
    hasil = []
    for m in re.finditer(r"([A-Za-z][A-Za-z0-9_.]*)\s*\(", str(rumus)):
        nama = m.group(1).upper()
        if nama not in hasil:
            hasil.append(nama)
    return hasil


# ---------------------------------------------------------------------------
# Nilai harapan dari data seed
# ---------------------------------------------------------------------------

def nilai_harapan_sel(aoa, kolom, baris):
    """Port nilaiHarapanSel: baca sel AOA seed; kolom D baris 2-11 = B*C."""
    if baris - 1 < 0 or baris - 1 >= len(aoa):
        return None
    baris_data = aoa[baris - 1]
    if kolom < 0 or kolom >= len(baris_data):
        return None
    langsung = baris_data[kolom]
    if isinstance(langsung, (int, float)) and not isinstance(langsung, bool):
        return langsung
    if langsung is not None:
        return langsung
    if kolom == 3 and 2 <= baris <= 11:
        qty = baris_data[1]
        harga = baris_data[2]
        if (
            isinstance(qty, (int, float))
            and isinstance(harga, (int, float))
            and not isinstance(qty, bool)
            and not isinstance(harga, bool)
        ):
            return qty * harga
    return None


def _agregat(fungsi, aoa, range_teks):
    daftar = parse_range(range_teks)
    if not daftar:
        return None
    total = 0
    hitung = 0
    for a in daftar:
        n = nilai_harapan_sel(aoa, a["kolom"], a["baris"])
        if isinstance(n, (int, float)) and not isinstance(n, bool) and math.isfinite(n):
            total += n
            hitung += 1
    if not hitung:
        return None
    return total if fungsi == "sum" else total / hitung


def nilai_harapan_kolom_rujukan(cek_ini, aoa, kolom, baris, daftar_cek):
    """Nilai harapan kolom rujukan: pertama dari aturan value_each LAIN
    (bukan ambang) yang mencakup sel itu, kalau tidak ada dari data seed."""
    if daftar_cek:
        for lain in daftar_cek:
            if lain is cek_ini:
                continue
            ev = lain.get("evaluator") or {}
            if lain.get("type") != "value_each" or ev.get("jenis") == "ambang":
                continue
            if any(a["kolom"] == kolom and a["baris"] == baris for a in alamat_sasaran(lain)):
                n = nilai_harapan(lain, aoa, kolom, baris, daftar_cek)
                if n is not None:
                    return n
    return nilai_harapan_sel(aoa, kolom, baris)


def nilai_harapan(cek, aoa, kolom, baris, daftar_cek):
    """Nilai harapan untuk satu aturan cek pada satu sel (evaluator)."""
    ev = cek.get("evaluator")
    if ev is None:
        return None
    jenis = ev.get("jenis")

    if jenis == "tetap":
        return ev.get("nilai")

    if jenis == "agregat":
        return _agregat(str(ev.get("fungsi", "sum")).lower(), aoa, ev.get("range", ""))

    if jenis == "kali":
        hasil = 1
        for huruf in ev.get("kolom", []):
            n = nilai_harapan_sel(aoa, kolom_ke_indeks(huruf), baris)
            if not isinstance(n, (int, float)) or isinstance(n, bool) or not math.isfinite(n):
                return None
            hasil *= n
        return hasil

    if jenis == "rata_kolom":
        total = 0
        daftar_kolom = ev.get("kolom", [])
        for huruf in daftar_kolom:
            n = nilai_harapan_sel(aoa, kolom_ke_indeks(huruf), baris)
            if not isinstance(n, (int, float)) or isinstance(n, bool) or not math.isfinite(n):
                return None
            total += n
        return total / len(daftar_kolom) if daftar_kolom else None

    if jenis == "hitung_kriteria":
        kriteria_daftar = ev.get("kriteria", [])
        kolom_target = []
        for a in alamat_sasaran(cek):
            if a["kolom"] not in kolom_target:
                kolom_target.append(a["kolom"])
        if kolom not in kolom_target:
            return None
        idx = kolom_target.index(kolom)
        if idx >= len(kriteria_daftar):
            return None
        kriteria = kriteria_daftar[idx]
        if baris - 1 < 0 or baris - 1 >= len(aoa):
            return None
        baris_data = aoa[baris - 1]
        kol_awal, kol_akhir = 0, 0
        bagian = str(ev.get("kolom", "")).split(":")
        kol_awal = kolom_ke_indeks(bagian[0])
        kol_akhir = kolom_ke_indeks(bagian[1]) if len(bagian) > 1 else kol_awal
        hitung = 0
        for k in range(kol_awal, kol_akhir + 1):
            if 0 <= k < len(baris_data) and baris_data[k] == kriteria:
                hitung += 1
        return hitung

    if jenis == "jumlah_kolom":
        cek_countif = None
        for lain in daftar_cek or []:
            ev_lain = lain.get("evaluator") or {}
            if (
                lain.get("type") == "value_each"
                and ev_lain.get("jenis") == "hitung_kriteria"
                and any(a["kolom"] == kolom for a in alamat_sasaran(lain))
            ):
                cek_countif = lain
                break
        if cek_countif is None:
            return None
        total = 0
        for b in range(int(ev.get("baris_awal", 2)), int(ev.get("baris_akhir", 11)) + 1):
            n = nilai_harapan(cek_countif, aoa, kolom, b, daftar_cek)
            if n is None:
                return None
            total += n
        return total

    if jenis == "ambang":
        nilai_rujukan = nilai_harapan_kolom_rujukan(
            cek, aoa, kolom_ke_indeks(ev.get("kolom", "")), baris, daftar_cek
        )
        if not isinstance(nilai_rujukan, (int, float)) or isinstance(nilai_rujukan, bool) or not math.isfinite(nilai_rujukan):
            return None
        ambang = ev.get("ambang")
        op = ev.get("operator")
        if op == ">=":
            kondisi = nilai_rujukan >= ambang
        elif op == ">":
            kondisi = nilai_rujukan > ambang
        elif op == "<=":
            kondisi = nilai_rujukan <= ambang
        elif op == "<":
            kondisi = nilai_rujukan < ambang
        elif op == "=":
            kondisi = angka_sama(nilai_rujukan, ambang)
        elif op == "<>":
            kondisi = not angka_sama(nilai_rujukan, ambang)
        else:
            return None
        return ev.get("maka") if kondisi else ev.get("selain")

    return None


# ---------------------------------------------------------------------------
# Label & detail centang
# ---------------------------------------------------------------------------

def label_cek(cek, nama_sheet):
    if cek.get("label"):
        return cek["label"]
    sasaran = teks_sasaran(cek)
    tipe = cek.get("type")
    if tipe == "value":
        return "Nilai " + sasaran + " sesuai harapan"
    if tipe == "value_each":
        return "Nilai " + sasaran + " benar di semua baris"
    if tipe == "is_formula":
        return sasaran + " diisi rumus, bukan angka ketikan"
    if tipe == "formula_uses":
        return "Rumus " + sasaran + " memakai " + " atau ".join(cek.get("functions") or [])
    if tipe == "no_errors":
        return "Tidak ada sel error di sheet " + nama_sheet
    return "Cek " + str(tipe) + (" " + sasaran if sasaran else "")


def data_diubah(lembar, aoa, daftar_cek):
    """Sel sumber tak-kosong baris 2-11 di luar range cek berubah?"""
    tercakup = set()
    for cek in daftar_cek or []:
        for a in alamat_sasaran(cek):
            tercakup.add((a["kolom"], a["baris"]))
    for baris in range(2, 12):
        if baris - 1 >= len(aoa):
            continue
        baris_data = aoa[baris - 1]
        for kolom in range(len(baris_data)):
            if (kolom, baris) in tercakup:
                continue
            mentah = baris_data[kolom]
            if mentah is None or mentah == "":
                continue
            harapan = nilai_harapan_sel(aoa, kolom, baris)
            sel = ambil_sel(lembar, kolom, baris)
            if isinstance(harapan, (int, float)) and not isinstance(harapan, bool):
                aktual = nilai_cache_angka(sel)
                if aktual is None or not angka_sama(aktual, harapan):
                    return True
            else:
                teks_aktual = "" if sel is None or sel.nilai is None else str(sel.nilai)
                teks_harapan = "" if harapan is None else str(harapan)
                if teks_aktual != teks_harapan:
                    return True
    return False


# ---------------------------------------------------------------------------
# Mesin utama
# ---------------------------------------------------------------------------

def _gagal_semua(daftar_cek, nama_sheet, detail):
    return {
        "skor": 0,
        "lulus": False,
        "centang": [
            {
                "label": label_cek(cek, nama_sheet),
                "lulus": False,
                "poin": 0,
                "poinMaks": cek.get("points") or 0,
                "detail": detail,
            }
            for cek in daftar_cek
        ],
        "kode": ["altered"],
    }


def periksa_lembar(lembar, seed, aturan):
    """Periksa satu lembar (sheet) dengan aturan cek. Mirip
    periksaWorkbook di JS; lembar=None berarti sheet tidak ada."""
    nama_sheet = (aturan or {}).get("sheet") or "Data"
    batas_lulus = aturan.get("pass") if isinstance(aturan.get("pass"), (int, float)) else 70
    daftar_cek = aturan.get("checks") if isinstance(aturan.get("checks"), list) else []
    tugas_id = (aturan or {}).get("tugas")

    if tugas_id not in ("rekap_penjualan", "absensi", "penilaian_magang"):
        return _gagal_semua(daftar_cek, nama_sheet, "Aturan cek untuk tugas ini tidak dikenal.")
    if lembar is None:
        return _gagal_semua(daftar_cek, nama_sheet, f"Sheet \u201c{nama_sheet}\u201d tidak ditemukan di file.")

    aoa = buat_data_tugas(tugas_id, seed)
    kode_ada = set()

    def tandai(kode):
        kode_ada.add(kode)

    if data_diubah(lembar, aoa, daftar_cek):
        tandai("altered")

    skor = 0
    centang = []
    for cek in daftar_cek:
        poin_maks = cek.get("points") or 0
        lulus = False
        detail = ""
        tipe = cek.get("type")

        if tipe == "value":
            sasaran = alamat_sasaran(cek)
            target = sasaran[0] if sasaran else None
            sel = ambil_sel(lembar, target["kolom"], target["baris"]) if target else None
            harapan = nilai_harapan(cek, aoa, target["kolom"], target["baris"], daftar_cek) if target else None
            if sel_punya_rumus(sel) and cache_kosong(sel):
                tandai("nocache")
            aktual = nilai_cache_angka(sel)
            if harapan is not None and aktual is not None and angka_sama(aktual, harapan):
                lulus = True
                detail = teks_sasaran(cek) + " = " + format_angka(aktual) + ", sesuai harapan."
            elif aktual is None:
                detail = (
                    "Nilai " + teks_sasaran(cek) + " tidak bisa dibaca"
                    + (" (diharapkan " + format_angka(harapan) + ")" if harapan is not None else "")
                    + "."
                )
            else:
                if harapan is not None:
                    tandai("sum")
                detail = (
                    teks_sasaran(cek) + " = " + format_angka(aktual)
                    + ", diharapkan " + format_angka(harapan) + "."
                )

        elif tipe == "value_each":
            sasaran = alamat_sasaran(cek)
            benar = 0
            ada_salah_terbaca = False
            for a in sasaran:
                sel = ambil_sel(lembar, a["kolom"], a["baris"])
                if sel_punya_rumus(sel) and cache_kosong(sel):
                    tandai("nocache")
                harapan = nilai_harapan(cek, aoa, a["kolom"], a["baris"], daftar_cek)
                if isinstance(harapan, str):
                    if sel is not None and not sel.error and isinstance(sel.nilai, str) and sel.nilai != "":
                        if sel.nilai == harapan:
                            benar += 1
                        else:
                            ada_salah_terbaca = True
                    elif sel_berisi_angka(sel):
                        ada_salah_terbaca = True
                    continue
                aktual = nilai_cache_angka(sel)
                if harapan is not None and aktual is not None:
                    if angka_sama(aktual, harapan):
                        benar += 1
                    else:
                        ada_salah_terbaca = True
            lulus = len(sasaran) > 0 and benar == len(sasaran)
            if not lulus and ada_salah_terbaca:
                semua_baris_total = len(sasaran) > 0 and all(a["baris"] >= 12 for a in sasaran)
                tandai("sum" if semua_baris_total else "rowval")
            detail = f"{benar} dari {len(sasaran)} sel benar."

        elif tipe == "is_formula":
            sasaran = alamat_sasaran(cek)
            berumus = 0
            ada_hard = False
            for a in sasaran:
                sel = ambil_sel(lembar, a["kolom"], a["baris"])
                if sel_punya_rumus(sel):
                    berumus += 1
                elif sel_berisi_angka(sel):
                    ada_hard = True
            if ada_hard:
                tandai("hard")
            lulus = len(sasaran) > 0 and berumus == len(sasaran)
            detail = f"{berumus} dari {len(sasaran)} sel berisi rumus."

        elif tipe == "formula_uses":
            sasaran = alamat_sasaran(cek)
            diizinkan = [str(f).upper() for f in (cek.get("functions") or [])]
            semua_ok = len(sasaran) > 0
            terdeteksi = []
            for a in sasaran:
                sel = ambil_sel(lembar, a["kolom"], a["baris"])
                if sel_punya_rumus(sel):
                    fungsi = nama_fungsi_rumus(sel.rumus)
                    for f in fungsi:
                        if f not in terdeteksi:
                            terdeteksi.append(f)
                    if not any(f in diizinkan for f in fungsi):
                        semua_ok = False
                        tandai("sum")
                elif sel_berisi_angka(sel):
                    semua_ok = False
                    tandai("hard")
                else:
                    semua_ok = False
            lulus = semua_ok
            detail = (
                "Fungsi terdeteksi: " + ", ".join(terdeteksi)
                + " (diizinkan: " + ", ".join(diizinkan) + ")."
                if terdeteksi
                else "Tidak ada rumus di " + teks_sasaran(cek) + "."
            )

        elif tipe == "no_errors":
            sel_error = []
            for (kolom, baris), sel in lembar.sel.items():
                if sel.error:
                    sel_error.append(nama_sel(kolom, baris))
            lulus = len(sel_error) == 0
            if not lulus:
                tandai("err")
            detail = "Tidak ada sel error." if lulus else "Sel error ditemukan: " + ", ".join(sel_error) + "."

        else:
            detail = "Jenis cek belum didukung: " + str(tipe) + "."

        poin = poin_maks if lulus else 0
        skor += poin
        centang.append(
            {"label": label_cek(cek, nama_sheet), "lulus": lulus, "poin": poin, "poinMaks": poin_maks, "detail": detail}
        )

    return {
        "skor": skor,
        "lulus": skor >= batas_lulus,
        "centang": centang,
        "kode": [k for k in URUTAN_KODE if k in kode_ada],
    }


def periksa_bytes(data, seed, aturan):
    """Periksa bytes file .xlsx dengan aturan cek."""
    nama_sheet = (aturan or {}).get("sheet") or "Data"
    lembar = muat_lembar(data, nama_sheet)
    return periksa_lembar(lembar, seed, aturan)


def muat_aturan(tugas_id):
    """Muat aturan cek JSON untuk satu jenis tugas."""
    path = _DIR_RULES / f"{tugas_id}.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)
