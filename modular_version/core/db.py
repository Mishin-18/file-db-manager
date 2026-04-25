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

CREATE TABLE IF NOT EXISTS folders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    relpath TEXT NOT NULL UNIQUE,
    fullpath TEXT NOT NULL,
    mtime INTEGER,
    is_present INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_folders_name ON folders(name);
CREATE INDEX IF NOT EXISTS idx_folders_relpath ON folders(relpath);
CREATE INDEX IF NOT EXISTS idx_folders_present ON folders(is_present);

CREATE TABLE IF NOT EXISTS file_content (
    file_id INTEGER PRIMARY KEY,
    content_text TEXT,
    content_mtime INTEGER,
    indexed_at INTEGER,
    status TEXT,
    content_source TEXT,
    quality_score REAL,
    page_count INTEGER,
    text_length INTEGER,
    error_text TEXT,
    FOREIGN KEY(file_id) REFERENCES files(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_file_content_status ON file_content(status);
CREATE INDEX IF NOT EXISTS idx_file_content_mtime ON file_content(content_mtime);

CREATE VIRTUAL TABLE IF NOT EXISTS file_content_fts USING fts5(
    content_text,
    content='file_content',
    content_rowid='file_id'
);

CREATE TRIGGER IF NOT EXISTS file_content_ai AFTER INSERT ON file_content BEGIN
    INSERT INTO file_content_fts(rowid, content_text) VALUES (new.file_id, COALESCE(new.content_text, ''));
END;

CREATE TRIGGER IF NOT EXISTS file_content_ad AFTER DELETE ON file_content BEGIN
    INSERT INTO file_content_fts(file_content_fts, rowid, content_text) VALUES('delete', old.file_id, COALESCE(old.content_text, ''));
END;

CREATE TRIGGER IF NOT EXISTS file_content_au AFTER UPDATE ON file_content BEGIN
    INSERT INTO file_content_fts(file_content_fts, rowid, content_text) VALUES('delete', old.file_id, COALESCE(old.content_text, ''));
    INSERT INTO file_content_fts(rowid, content_text) VALUES (new.file_id, COALESCE(new.content_text, ''));
END;

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

UPSERT_FOLDER_SQL = """
INSERT INTO folders (name, relpath, fullpath, mtime, is_present)
VALUES (?, ?, ?, ?, 1)
ON CONFLICT(relpath) DO UPDATE SET
    name=excluded.name,
    fullpath=excluded.fullpath,
    mtime=excluded.mtime,
    is_present=1
;
"""

MARK_ALL_MISSING_SQL = "UPDATE files SET is_present=0;"
MARK_ALL_FOLDERS_MISSING_SQL = "UPDATE folders SET is_present=0;"

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


def get_existing_tables(con: sqlite3.Connection) -> set[str]:
    rows = con.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    return {r[0] for r in rows}


def get_missing_required_tables(con: sqlite3.Connection) -> list[str]:
    required = {"files", "folders", "file_content", "sets", "set_items"}
    existing = get_existing_tables(con)
    return sorted(required - existing)


def is_supported_db_schema(con: sqlite3.Connection) -> bool:
    return not get_missing_required_tables(con)


def validate_db_path(db_path: str) -> list[str]:
    """Validate that a SQLite database exists and contains the required File DB Manager schema.

    Returns a list of missing required tables. Raises sqlite3.Error/OSError when the file
    cannot be opened as a SQLite database.
    """
    con = sqlite3.connect(db_path)
    try:
        return get_missing_required_tables(con)
    finally:
        con.close()
