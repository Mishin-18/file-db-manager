from pathlib import Path
import sqlite3
import time


def _insert_file_row(con, *, name, relpath, fullpath, is_present=1, ext=None):
    con.execute(
        """INSERT INTO files (name, relpath, fullpath, ext, size_bytes, mtime, sha1, is_present)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (name, relpath, fullpath, ext, 123, int(time.time()), None, is_present),
    )
    con.commit()


def test_normalize_path_line(appmod):
    assert appmod.normalize_path_line('  "C:/tmp/a.txt"  ') == "C:/tmp/a.txt"
    assert appmod.normalize_path_line("  'C:/tmp/b.txt' ") == "C:/tmp/b.txt"
    assert appmod.normalize_path_line("   ") == ""
    assert appmod.normalize_path_line(None) == ""


def test_parse_paths_from_text_dedup_and_tabs(appmod):
    text = (
        '  "C:/A/file1.txt"\n'
        'C:/A/file1.txt\n'
        'C:/B/file2.txt\tmeta\n'
        '\n'
        " 'C:/C/file3.txt' \n"
    )
    got = appmod.parse_paths_from_text(text)
    assert got == [
        "C:/A/file1.txt",
        "C:/B/file2.txt",
        "C:/C/file3.txt",
    ]


def test_should_skip_file_rules(appmod):
    assert appmod.should_skip_file("desktop.ini") is True
    assert appmod.should_skip_file("Thumbs.db") is True
    assert appmod.should_skip_file("~$temp.xlsx") is True
    assert appmod.should_skip_file("report.tmp") is True
    assert appmod.should_skip_file("server.log") is True
    assert appmod.should_skip_file("normal_document.docx") is False


def test_init_db_creates_schema_and_meta(appmod, tmp_path):
    db = tmp_path / "index.db"
    con = appmod.init_db(str(db), root_folder=str(tmp_path))
    try:
        tables = {row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table';")}
        # sqlite internal table may appear too; check required app tables
        assert {"meta", "files", "sets", "set_items"}.issubset(tables)

        meta = dict(con.execute("SELECT key, value FROM meta").fetchall())
        assert meta["root_folder"] == str(tmp_path)
        assert "updated_at" in meta and meta["updated_at"].isdigit()
    finally:
        con.close()


def test_resolve_one_exact_found_and_missing_by_presence(appmod, tmp_path):
    db = tmp_path / "index.db"
    con = appmod.init_db(str(db), root_folder=str(tmp_path))
    try:
        _insert_file_row(
            con,
            name="a.txt",
            relpath="a.txt",
            fullpath=str(tmp_path / "a.txt"),
            is_present=1,
            ext="txt",
        )
        _insert_file_row(
            con,
            name="b.txt",
            relpath="sub/b.txt",
            fullpath=str(tmp_path / "sub" / "b.txt"),
            is_present=0,
            ext="txt",
        )

        status, file_id, resolved, note = appmod.resolve_one(con, str(tmp_path / "a.txt"))
        assert status == "FOUND"
        assert file_id is not None
        assert resolved == str(tmp_path / "a.txt")
        assert note is None

        status, file_id, resolved, note = appmod.resolve_one(con, str(tmp_path / "sub" / "b.txt"))
        assert status == "MISSING"
        assert file_id is not None
        assert resolved == str(tmp_path / "sub" / "b.txt")
    finally:
        con.close()


def test_resolve_one_name_match_and_ambiguous(appmod, tmp_path):
    db = tmp_path / "index.db"
    con = appmod.init_db(str(db), root_folder=str(tmp_path))
    try:
        _insert_file_row(con, name="single.doc", relpath="x/single.doc", fullpath=str(tmp_path / "x" / "single.doc"), is_present=1)
        _insert_file_row(con, name="dup.pdf", relpath="a/dup.pdf", fullpath=str(tmp_path / "a" / "dup.pdf"), is_present=1)
        _insert_file_row(con, name="dup.pdf", relpath="b/dup.pdf", fullpath=str(tmp_path / "b" / "dup.pdf"), is_present=1)

        # exact path does not exist, but basename single.doc is unique in DB -> FOUND by name
        status, file_id, resolved, note = appmod.resolve_one(con, str(tmp_path / "oldplace" / "single.doc"))
        assert status == "FOUND"
        assert file_id is not None
        assert resolved.endswith("single.doc")
        assert note == "matched by name"

        # basename dup.pdf appears twice -> AMBIGUOUS
        status, file_id, resolved, note = appmod.resolve_one(con, str(tmp_path / "oldplace" / "dup.pdf"))
        assert status == "AMBIGUOUS"
        assert file_id is None
        assert resolved is None
        assert "multiple matches by name" in note

        # empty path -> MISSING
        status, file_id, resolved, note = appmod.resolve_one(con, "   ")
        assert status == "MISSING"
        assert note == "empty path"
    finally:
        con.close()


def test_upsert_set_creates_then_updates_same_id(appmod, tmp_path):
    db = tmp_path / "index.db"
    con = appmod.init_db(str(db), root_folder=str(tmp_path))
    try:
        set_id_1 = appmod.upsert_set(con, "MySet")
        row1 = con.execute("SELECT id, created_at, updated_at FROM sets WHERE name='MySet'").fetchone()
        assert row1[0] == set_id_1

        # Ensure timestamp can move (or at least call remains idempotent on ID)
        time.sleep(1)
        set_id_2 = appmod.upsert_set(con, "MySet")
        row2 = con.execute("SELECT id, created_at, updated_at FROM sets WHERE name='MySet'").fetchone()

        assert set_id_2 == set_id_1
        assert row2[0] == row1[0]
        assert row2[1] == row1[1]  # created_at unchanged
        assert row2[2] >= row1[2]  # updated_at refreshed
    finally:
        con.close()


def test_sync_set_items_replace_and_append(appmod, tmp_path):
    db = tmp_path / "index.db"
    con = appmod.init_db(str(db), root_folder=str(tmp_path))
    try:
        # present file
        _insert_file_row(con, name="ok.txt", relpath="ok.txt", fullpath=str(tmp_path / "ok.txt"), is_present=1, ext="txt")
        # ambiguous by name
        _insert_file_row(con, name="dup.txt", relpath="a/dup.txt", fullpath=str(tmp_path / "a" / "dup.txt"), is_present=1, ext="txt")
        _insert_file_row(con, name="dup.txt", relpath="b/dup.txt", fullpath=str(tmp_path / "b" / "dup.txt"), is_present=1, ext="txt")
    finally:
        con.close()

    paths_round1 = [
        str(tmp_path / "ok.txt"),          # FOUND exact
        str(tmp_path / "old" / "dup.txt"),  # AMBIGUOUS by name
        str(tmp_path / "missing.bin"),     # MISSING
    ]
    stats1 = appmod.sync_set_items(str(db), "Batch1", paths_round1, replace=True)
    assert stats1 == {"total": 3, "found": 1, "missing": 1, "ambiguous": 1}

    con2 = sqlite3.connect(db)
    try:
        rows = con2.execute(
            "SELECT status, COUNT(*) FROM set_items si JOIN sets s ON s.id=si.set_id WHERE s.name=? GROUP BY status",
            ("Batch1",)
        ).fetchall()
        by_status = {status: cnt for status, cnt in rows}
        assert by_status == {"FOUND": 1, "MISSING": 1, "AMBIGUOUS": 1}
    finally:
        con2.close()

    # Append mode (replace=False) should keep previous rows and add new one
    stats2 = appmod.sync_set_items(str(db), "Batch1", [str(tmp_path / "ok.txt")], replace=False)
    assert stats2 == {"total": 1, "found": 1, "missing": 0, "ambiguous": 0}

    con3 = sqlite3.connect(db)
    try:
        total_rows = con3.execute(
            "SELECT COUNT(*) FROM set_items si JOIN sets s ON s.id=si.set_id WHERE s.name=?",
            ("Batch1",)
        ).fetchone()[0]
        assert total_rows == 4
    finally:
        con3.close()
