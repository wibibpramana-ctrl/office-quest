"""Validasi unggahan file jawaban (3.5).

Dipanggil sebelum pemeriksa (3.7) supaya file jahat atau rusak ditolak
dengan kode galat yang jelas, sebelum server menghabiskan waktu dan
memori untuk membukanya.

Batas (dipilih supaya file jawaban asli — sekitar 20 KB — jauh di bawah
batas, sementara penyalahgunaan tertahan):
- ukuran file: 2 MB (rujukan 3.8: file 2 MB harus selesai < 5 detik)
- ukuran setelah dekompresi: 20 MB (menahan bom arsip/zip bomb)
- jumlah sel berisi: 100.000
- waktu proses (validasi + periksa): 10 detik

Yang diperiksa, berurutan: ukuran file, ekstensi (.xlsm ditolak),
arsip ZIP valid dan berisi file Excel, ukuran dekompresi, jumlah sel.
Setiap langkah memeriksa tenggat waktu.
"""

import io
import time
import zipfile

from openpyxl import load_workbook

BATAS_UKURAN_FILE = 2 * 1024 * 1024  # 2 MB
BATAS_UKURAN_DEKOMPRESI = 20 * 1024 * 1024  # 20 MB
BATAS_JUMLAH_SEL = 100_000
BATAS_WAKTU_DETIK = 10


class GalatValidasi(Exception):
    """Unggahan ditolak; ``kode`` untuk mesin, ``pesan`` untuk manusia."""

    def __init__(self, kode, pesan):
        super().__init__(pesan)
        self.kode = kode
        self.pesan = pesan


class GalatWaktuHabis(GalatValidasi):
    """Proses melebihi batas waktu."""

    def __init__(self, pesan="Pemeriksaan melebihi batas waktu 10 detik."):
        super().__init__("waktu_habis", pesan)


class BatasWaktu:
    """Tenggat kooperatif: panggil ``periksa()`` di titik-titik aman;
    melempar GalatWaktuHabis bila tenggat lewat."""

    def __init__(self, detik=BATAS_WAKTU_DETIK):
        self.tenggat = time.monotonic() + detik

    def periksa(self):
        if time.monotonic() > self.tenggat:
            raise GalatWaktuHabis()


def _cek_waktu(batas_waktu):
    if batas_waktu is not None:
        batas_waktu.periksa()


def validasi_unggahan(data, nama_file=None, batas_waktu=None):
    """Periksa bytes unggahan. Lolos -> kembalikan info file
    (ukuran, ukuran dekompresi, jumlah sel). Gagal -> raise GalatValidasi
    dengan kode galat yang jelas."""
    if batas_waktu is None:
        batas_waktu = BatasWaktu()

    # 1. Ukuran file.
    if len(data) > BATAS_UKURAN_FILE:
        raise GalatValidasi(
            "file_terlalu_besar",
            "Ukuran file melebihi 2 MB.",
        )
    _cek_waktu(batas_waktu)

    # 2. Ekstensi: .xlsm (bermakro) ditolak; selain .xlsx ditolak.
    if nama_file:
        nama_kecil = str(nama_file).lower()
        if nama_kecil.endswith(".xlsm"):
            raise GalatValidasi(
                "xlsm_ditolak",
                "File .xlsm (bermakro) tidak diterima; kirim file .xlsx tanpa makro.",
            )
        if not nama_kecil.endswith(".xlsx"):
            raise GalatValidasi(
                "ekstensi_salah",
                "File harus berekstensi .xlsx.",
            )
    _cek_waktu(batas_waktu)

    # 3. Arsip ZIP valid dan berisi file Excel.
    bio = io.BytesIO(data)
    if not zipfile.is_zipfile(bio):
        raise GalatValidasi(
            "bukan_arsip_valid",
            "File bukan arsip .xlsx yang valid.",
        )
    try:
        zf = zipfile.ZipFile(bio)
        nama_entri = zf.namelist()
    except zipfile.BadZipFile:
        raise GalatValidasi(
            "bukan_arsip_valid",
            "File bukan arsip .xlsx yang valid.",
        ) from None
    if "[Content_Types].xml" not in nama_entri or "xl/workbook.xml" not in nama_entri:
        raise GalatValidasi(
            "bukan_xlsx",
            "Arsip tidak berisi file Excel (.xlsx).",
        )
    _cek_waktu(batas_waktu)

    # 4. Ukuran setelah dekompresi (dari metadata ZIP, tanpa mengekstrak).
    ukuran_dekompresi = 0
    for info in zf.infolist():
        ukuran_dekompresi += info.file_size
        if ukuran_dekompresi > BATAS_UKURAN_DEKOMPRESI:
            raise GalatValidasi(
                "dekompresi_terlalu_besar",
                "Ukuran file setelah dibuka melebihi 20 MB.",
            )
    _cek_waktu(batas_waktu)

    # 5. Jumlah sel berisi (aliran baca, berhenti dini bila melewati batas).
    try:
        wb = load_workbook(io.BytesIO(data), data_only=True, read_only=True)
    except Exception:
        raise GalatValidasi(
            "bukan_arsip_valid",
            "File bukan arsip .xlsx yang valid.",
        ) from None
    jumlah_sel = 0
    baris_dibaca = 0
    try:
        for ws in wb.worksheets:
            for baris in ws.iter_rows(values_only=True):
                baris_dibaca += 1
                if baris_dibaca % 10000 == 0:
                    _cek_waktu(batas_waktu)
                for nilai in baris:
                    if nilai is not None:
                        jumlah_sel += 1
                        if jumlah_sel > BATAS_JUMLAH_SEL:
                            raise GalatValidasi(
                                "sel_terlalu_banyak",
                                "Jumlah sel melebihi 100.000.",
                            )
    finally:
        wb.close()
    _cek_waktu(batas_waktu)

    return {
        "ukuran_file": len(data),
        "ukuran_dekompresi": ukuran_dekompresi,
        "jumlah_sel": jumlah_sel,
    }
