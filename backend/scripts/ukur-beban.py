"""Ukur waktu dan beban backend Office Quest (3.8).

Jalankan dari folder backend:
    python scripts/ukur-beban.py

Mengukur, lewat TestClient (tanpa jaringan):
- /periksa untuk file .xlsx ~2 MB (harus < 5 detik)
- 20 permintaan /periksa beruntun (harus tanpa galat)

File besar dibuat di memori: sheet "Data" berisi 2 sel + sheet
"DataBesar" berisi 60.000 sel string acak (total < 100.000 sel,
ukuran ~1,8 MB, di bawah batas unggahan 2 MB).
"""

import io
import os
import platform
import random
import string
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import buat_app  # noqa: E402

GARAM_UKUR = "garam-ukur-beban-3-8"
JUMLAH_SEL_BESAR = 60_000
BATAS_FILE_2MB_DETIK = 5


def bangun_file_besar():
    """Bangun bytes .xlsx ~1,8 MB (deterministik, seed 42)."""
    rng = random.Random(42)
    alfabet = string.ascii_letters + string.digits
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "Data"
    ws["A1"] = "Produk"
    ws["A2"] = "Kopi Bubuk"
    ws2 = wb.create_sheet("DataBesar")
    for i in range(JUMLAH_SEL_BESAR):
        ws2.cell(row=i + 1, column=1, value="".join(rng.choice(alfabet) for _ in range(30)))
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def utama():
    print("Ukur beban backend Office Quest (3.8)")
    print(f"Lingkungan: Python {platform.python_version()}, {platform.system()} {platform.machine()}, "
          f"CPU {os.cpu_count()}")
    klien = TestClient(buat_app(garam=GARAM_UKUR, batas_laju_per_menit=1000))
    tiket = klien.post("/tugas/tiket", json={"jenis": "rekap_penjualan", "benih": "benih-ukur"}).json()["tiket"]

    data_besar = bangun_file_besar()
    print(f"File besar: {len(data_besar)} byte ({len(data_besar) / 1024 / 1024:.2f} MB), "
          f"{JUMLAH_SEL_BESAR + 2} sel")
    t0 = time.monotonic()
    resp = klien.post("/periksa", data={"tiket": tiket}, files={"file": ("jawaban.xlsx", data_besar)})
    durasi_besar = time.monotonic() - t0
    print(f"/periksa file 2 MB: status {resp.status_code}, {durasi_besar:.2f} detik "
          f"(batas {BATAS_FILE_2MB_DETIK} detik) -> "
          f"{'LOLOS' if resp.status_code == 200 and durasi_besar < BATAS_FILE_2MB_DETIK else 'GAGAL'}")

    template = klien.get("/tugas/template", params={"tiket": tiket}).content
    waktu = []
    gagal = 0
    for _ in range(20):
        t0 = time.monotonic()
        r = klien.post("/periksa", data={"tiket": tiket}, files={"file": ("jawaban.xlsx", template)})
        waktu.append(time.monotonic() - t0)
        if r.status_code != 200:
            gagal += 1
    print(f"20x /periksa beruntun: {20 - gagal}/20 tanpa galat, total {sum(waktu):.2f} detik, "
          f"rata-rata {sum(waktu) / len(waktu) * 1000:.0f} ms, "
          f"tercepat {min(waktu) * 1000:.0f} ms, terlambat {max(waktu) * 1000:.0f} ms -> "
          f"{'LOLOS' if gagal == 0 else 'GAGAL'}")


if __name__ == "__main__":
    utama()
