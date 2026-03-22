import time
import sqlite3

SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;

CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    relpath TEXT NOT NULL UNIQUE,
    fullpath TEXT NOT NULL,
    ext TEXT,
    size_bytes INTEGER,
    mtime INTEGER,
    sha1 TEXT,
    is_present INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_files_name ON files(name);
CREATE INDEX IF NOT EXISTS idx_files_relpath ON files(relpath);
CREATE INDEX IF NOT EXISTS idx_files_present ON files(is_present);

CREATE TABLE IF NOT EXISTS sets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS set_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    set_id INTEGER NOT NULL,
    raw_path TEXT NOT NULL,
    file_id INTEGER,
    resolved_path TEXT,
    status TEXT NOT NULL, -- FOUND | MISSING | AMBIGUOUS
    note TEXT,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    FOREIGN KEY(set_id) REFERENCES sets(id) ON DELETE CASCADE,
    FOREIGN KEY(file_id) REFERENCES files(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_set_items_set ON set_items(set_id);
CREATE INDEX IF NOT EXISTS idx_set_items_status ON set_items(status);
"""

UPSERT_SQL = """
INSERT INTO files (name, relpath, fullpath, ext, size_bytes, mtime, sha1, is_present)
VALUES (?, ?, ?, ?, ?, ?, ?, 1)
ON CONFLICT(relpath) DO UPDATE SET
    name=excluded.name,
    fullpath=excluded.fullpath,
    ext=excluded.ext,
    size_bytes=excluded.size_bytes,
    mtime=excluded.mtime,
    sha1=excluded.sha1,
    is_present=1
;
"""

MARK_ALL_MISSING_SQL = "UPDATE files SET is_present=0;"


def init_db(db_path: str, root_folder: str | None = None) -> sqlite3.Connection:
    """Initialize database with schema and metadata"""
    con = sqlite3.connect(db_path)
    con.execute("PRAGMA foreign_keys=ON;")
    con.executescript(SCHEMA_SQL)
    if root_folder is not None:
        con.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('root_folder', ?);", (root_folder,))
    con.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('updated_at', ?);", (str(int(time.time())),))
    con.commit()
    return con
