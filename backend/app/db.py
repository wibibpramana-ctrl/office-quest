"""Akses database SQLite Office Quest (Fase 5).

- Jalur database dari variabel lingkungan OFFICE_QUEST_DB (malas: dibaca
  saat pertama dipakai; bila belum diatur, endpoint akun menjawab 503 —
  pola yang sama dengan garam di tiket.py).
- File skema: database/skema.sql (CREATE TABLE IF NOT EXISTS, idempotent).
- Mode WAL + foreign_keys=ON di tiap koneksi.
"""

import os
import sqlite3
from pathlib import Path

_SKEMA = Path(__file__).resolve().parent.parent.parent / "database" / "skema.sql"
_sudah_disiapkan = set()


def jalur_db():
    """Jalur file database dari lingkungan, atau None bila belum diatur."""
    jalur = os.environ.get("OFFICE_QUEST_DB")
    if not jalur:
        return None
    return Path(jalur)


def buka_db():
    """Buka koneksi (sekaligus siapkan skema bila file baru).

    Mengembalikan None bila OFFICE_QUEST_DB belum diatur — pemanggil
    (endpoint) yang mengubahnya menjadi 503.
    """
    jalur = jalur_db()
    if jalur is None:
        return None
    jalur.parent.mkdir(parents=True, exist_ok=True)
    koneksi = sqlite3.connect(str(jalur))
    koneksi.row_factory = sqlite3.Row
    koneksi.execute("PRAGMA journal_mode=WAL")
    koneksi.execute("PRAGMA foreign_keys=ON")
    if str(jalur) not in _sudah_disiapkan:
        with open(_SKEMA, encoding="utf-8") as f:
            koneksi.executescript(f.read())
        koneksi.commit()
        _sudah_disiapkan.add(str(jalur))
    return koneksi
