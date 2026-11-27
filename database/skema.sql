-- Skema database Office Quest (Fase 5.2, dari docs/skema-database.md).
-- SQLite. Diterapkan backend saat start (CREATE TABLE IF NOT EXISTS).

CREATE TABLE IF NOT EXISTS meta (
    kunci TEXT PRIMARY KEY,
    nilai TEXT NOT NULL
);
INSERT OR IGNORE INTO meta (kunci, nilai) VALUES ('skema_versi', '1');

CREATE TABLE IF NOT EXISTS akun (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama_akun TEXT NOT NULL UNIQUE,
    nama_panggilan TEXT,
    email TEXT UNIQUE,
    hash_kata_sandi TEXT NOT NULL,
    dibuat_pada TEXT NOT NULL,
    terakhir_masuk TEXT
);

CREATE TABLE IF NOT EXISTS sesi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    akun_id INTEGER NOT NULL REFERENCES akun(id),
    token_hash TEXT NOT NULL UNIQUE,
    dibuat_pada TEXT NOT NULL,
    kedaluwarsa_pada TEXT NOT NULL,
    perangkat TEXT
);
CREATE INDEX IF NOT EXISTS idx_sesi_akun ON sesi(akun_id);

CREATE TABLE IF NOT EXISTS progres (
    akun_id INTEGER PRIMARY KEY REFERENCES akun(id),
    xp INTEGER NOT NULL DEFAULT 0,
    koin INTEGER NOT NULL DEFAULT 0,
    level INTEGER NOT NULL DEFAULT 1,
    energi INTEGER NOT NULL DEFAULT 100,
    energi_dihitung_pada TEXT NOT NULL,
    streak_absen INTEGER NOT NULL DEFAULT 0,
    terakhir_absen TEXT,
    diperbarui_pada TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tugas_harian (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    akun_id INTEGER NOT NULL REFERENCES akun(id),
    tanggal TEXT NOT NULL,
    urutan INTEGER NOT NULL,
    jenis TEXT NOT NULL,
    tier INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'baru',
    skor_terakhir INTEGER,
    lulus INTEGER,
    percobaan INTEGER NOT NULL DEFAULT 0,
    hint_terpakai INTEGER NOT NULL DEFAULT 0,
    selesai_pada TEXT,
    UNIQUE(akun_id, tanggal, urutan)
);
CREATE INDEX IF NOT EXISTS idx_tugas_harian_akun_tanggal ON tugas_harian(akun_id, tanggal);

CREATE TABLE IF NOT EXISTS inventori (
    akun_id INTEGER NOT NULL REFERENCES akun(id),
    item_id TEXT NOT NULL,
    diperoleh_pada TEXT NOT NULL,
    sumber TEXT NOT NULL,
    PRIMARY KEY(akun_id, item_id)
);

CREATE TABLE IF NOT EXISTS wawancara (
    akun_id INTEGER PRIMARY KEY REFERENCES akun(id),
    skor_json TEXT NOT NULL,
    dilewati INTEGER NOT NULL DEFAULT 0,
    selesai_pada TEXT
);

CREATE TABLE IF NOT EXISTS terpasang (
    akun_id INTEGER NOT NULL REFERENCES akun(id),
    slot TEXT NOT NULL,
    item_id TEXT,
    PRIMARY KEY(akun_id, slot)
);

CREATE TABLE IF NOT EXISTS lencana (
    akun_id INTEGER NOT NULL REFERENCES akun(id),
    lencana_id TEXT NOT NULL,
    diperoleh_pada TEXT NOT NULL,
    PRIMARY KEY(akun_id, lencana_id)
);

CREATE TABLE IF NOT EXISTS pesan_chat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    akun_id INTEGER NOT NULL REFERENCES akun(id),
    karakter TEXT NOT NULL,
    pengirim TEXT NOT NULL,
    isi TEXT NOT NULL,
    dibuat_pada TEXT NOT NULL,
    dibaca INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_pesan_chat_akun_karakter ON pesan_chat(akun_id, karakter, dibuat_pada);

CREATE TABLE IF NOT EXISTS absensi (
    akun_id INTEGER NOT NULL REFERENCES akun(id),
    tanggal TEXT NOT NULL,
    koin_diberikan INTEGER NOT NULL,
    PRIMARY KEY(akun_id, tanggal)
);

CREATE TABLE IF NOT EXISTS pengaturan (
    akun_id INTEGER PRIMARY KEY REFERENCES akun(id),
    tema TEXT,
    preferensi_json TEXT
);

CREATE TABLE IF NOT EXISTS pemulihan_kata_sandi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    akun_id INTEGER NOT NULL REFERENCES akun(id),
    token_hash TEXT NOT NULL UNIQUE,
    kedaluwarsa_pada TEXT NOT NULL,
    dipakai INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS tantangan_selesai (
    akun_id INTEGER NOT NULL REFERENCES akun(id),
    tantangan_id TEXT NOT NULL,
    skor INTEGER NOT NULL,
    selesai_pada TEXT NOT NULL,
    PRIMARY KEY(akun_id, tantangan_id)
);
