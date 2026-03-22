from __future__ import annotations

import sqlite3
import sys
import types
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
MODULAR_ROOT = ROOT / "modular_version"
if str(MODULAR_ROOT) not in sys.path:
    sys.path.insert(0, str(MODULAR_ROOT))

fake_shell = types.ModuleType("core.shell")
fake_shell.is_hidden_or_system = lambda path: False
sys.modules.setdefault("core.shell", fake_shell)

from core.db import init_db
from core.resolver import parse_paths_from_text, read_paths_from_xlsx, sync_set_items
from core.scanner import scan_folders_to_db


def test_parse_paths_from_text_strips_quotes_tabs_and_duplicates():
    text = (
        '  "C:/data/report 1.xlsx"  \n'
        "'C:/data/report 1.xlsx'\n"
        'C:/docs/a.txt\tFOUND\n'
        '   \n'
        'C:/docs/a.txt\n'
        'D:/music/song.mp3\n'
    )

    assert parse_paths_from_text(text) == [
        "C:/data/report 1.xlsx",
        "C:/docs/a.txt",
        "D:/music/song.mp3",
    ]


def test_read_paths_from_xlsx_uses_path_header_and_deduplicates(tmp_path: Path):
    xlsx = tmp_path / "paths.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["ID", "Полный путь", "Comment"])
    ws.append([1, '"C:/alpha/file1.txt"', "ok"])
    ws.append([2, "C:/beta/file2.txt", "ok"])
    ws.append([3, "C:/beta/file2.txt", "duplicate"])
    ws.append([4, None, "empty"])
    wb.save(xlsx)
    wb.close()

    assert read_paths_from_xlsx(str(xlsx)) == [
        "C:/alpha/file1.txt",
        "C:/beta/file2.txt",
    ]


def test_sync_set_items_resolves_found_missing_and_ambiguous(tmp_path: Path):
    db_path = tmp_path / "files.db"
    con = init_db(str(db_path))
    cur = con.cursor()
    rows = [
        ("file.txt", "[01_ROOT_A] docs/file.txt", str(tmp_path / "A" / "docs" / "file.txt"), "txt", 10, 100, None, 1),
        ("dup.txt", "[01_ROOT_A] docs/dup.txt", str(tmp_path / "A" / "docs" / "dup.txt"), "txt", 10, 100, None, 1),
        ("dup.txt", "[02_ROOT_B] docs/dup.txt", str(tmp_path / "B" / "docs" / "dup.txt"), "txt", 10, 100, None, 1),
        ("gone.txt", "[01_ROOT_A] docs/gone.txt", str(tmp_path / "A" / "docs" / "gone.txt"), "txt", 10, 100, None, 0),
    ]
    cur.executemany(
        "INSERT INTO files (name, relpath, fullpath, ext, size_bytes, mtime, sha1, is_present) VALUES (?,?,?,?,?,?,?,?);",
        rows,
    )
    con.commit()
    con.close()

    paths = [
        str(tmp_path / "A" / "docs" / "file.txt"),
        str(tmp_path / "A" / "docs" / "gone.txt"),
        str(tmp_path / "X" / "docs" / "dup.txt"),
        str(tmp_path / "X" / "docs" / "missing.txt"),
    ]

    stats = sync_set_items(str(db_path), "check-1", paths, replace=True)
    assert stats == {"total": 4, "found": 1, "missing": 2, "ambiguous": 1}

    con = sqlite3.connect(db_path)
    items = con.execute("SELECT raw_path, status, note FROM set_items ORDER BY id").fetchall()
    con.close()

    assert items[0][1] == "FOUND"
    assert items[1][1] == "MISSING"
    assert items[1][2] is None
    assert items[2][1] == "AMBIGUOUS"
    assert "multiple matches by name" in items[2][2]
    assert items[3][1] == "MISSING"
    assert items[3][2] == "not found"


def test_scan_folders_to_db_handles_multiple_roots_and_incremental_missing(tmp_path: Path):
    root_a = tmp_path / "root_a"
    root_b = tmp_path / "root_b"
    root_a.mkdir()
    root_b.mkdir()

    (root_a / "same.txt").write_text("v1", encoding="utf-8")
    (root_a / "keep.txt").write_text("keep", encoding="utf-8")
    (root_b / "same.txt").write_text("v2", encoding="utf-8")

    db_path = tmp_path / "scan.db"

    first = scan_folders_to_db([str(root_a), str(root_b)], str(db_path), incremental=False, recursive=False)
    assert first["files_total"] == 3
    assert first["new"] == 3
    assert first["missing"] == 0
    assert first["roots"] == [str(root_a), str(root_b)]
    assert sorted(first["per_folder"].values()) == [1, 2]

    con = sqlite3.connect(db_path)
    relpaths = [r[0] for r in con.execute("SELECT relpath FROM files ORDER BY relpath").fetchall()]
    con.close()
    assert any("same.txt" in r and r.startswith("[01_") for r in relpaths)
    assert any("same.txt" in r and r.startswith("[02_") for r in relpaths)

    (root_a / "keep.txt").unlink()
    second = scan_folders_to_db([str(root_a), str(root_b)], str(db_path), incremental=True, recursive=False)
    assert second["files_total"] == 2
    assert second["missing"] == 1

    con = sqlite3.connect(db_path)
    missing = con.execute("SELECT COUNT(*) FROM files WHERE is_present=0").fetchone()[0]
    keep_row = con.execute("SELECT is_present FROM files WHERE relpath LIKE '%keep.txt'").fetchone()
    con.close()
    assert missing == 1
    assert keep_row == (0,)
