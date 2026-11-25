"""Pengaturan bersama pytest: pastikan folder backend/ bisa diimpor
sebagai paket `app`, dari mana pun pytest dijalankan."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
