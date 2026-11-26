"""Pembuat template .xlsx Office Quest (openpyxl).

Port dari ``unduhTemplate`` di ``index.html`` (SheetJS):
data AOA dari generator -> satu sheet bernama "Data" -> file .xlsx.
Tidak ada rumus, format, atau kolom tambahan — isi sel dan nama sheet
harus identik dengan template browser (lihat tes paritas 3.3).
"""

import io

from openpyxl import Workbook

from app.generator import buat_data_tugas

NAMA_SHEET = "Data"

# Nama file template, sama dengan GENERATOR_TEMPLATE di index.html.
NAMA_FILE_TEMPLATE = {
    "rekap_penjualan": "Template Rekap Penjualan Mingguan.xlsx",
    "absensi": "Template Absensi Karyawan.xlsx",
    "penilaian_magang": "Template Penilaian Magang.xlsx",
}


def buat_template(tugas_id, seed):
    """Workbook openpyxl berisi satu sheet "Data" dari data tugas."""
    aoa = buat_data_tugas(tugas_id, seed)
    wb = Workbook()
    ws = wb.active
    ws.title = NAMA_SHEET
    for baris in aoa:
        ws.append(list(baris))
    return wb


def template_ke_bytes(tugas_id, seed):
    """Template .xlsx sebagai bytes (siap diunduh / dikirim API)."""
    wb = buat_template(tugas_id, seed)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def nama_file_template(tugas_id):
    """Nama file template untuk jenis tugas."""
    try:
        return NAMA_FILE_TEMPLATE[tugas_id]
    except KeyError:
        raise ValueError(f"Jenis tugas tidak dikenal: {tugas_id}") from None
