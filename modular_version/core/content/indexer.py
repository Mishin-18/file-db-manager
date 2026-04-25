from __future__ import annotations
import sqlite3
import time
from typing import Callable

from .extractors import extract_content


def _select_rows(con: sqlite3.Connection, mode: str):
    mode = (mode or 'changed').lower()
    base = """
        SELECT f.id, f.fullpath, f.ext, f.mtime
        FROM files f
        LEFT JOIN file_content fc ON fc.file_id = f.id
        WHERE f.is_present = 1
          AND lower(COALESCE(f.ext,'')) IN ('docx','xlsx','pdf')
    """
    if mode == 'all':
        sql = base + " ORDER BY f.relpath COLLATE NOCASE"
    elif mode == 'errors':
        sql = base + " AND (fc.file_id IS NULL OR COALESCE(fc.status,'') <> 'OK') ORDER BY f.relpath COLLATE NOCASE"
    else:
        sql = base + " AND (fc.file_id IS NULL OR fc.content_mtime IS NULL OR fc.content_mtime <> f.mtime) ORDER BY f.relpath COLLATE NOCASE"
    return con.execute(sql).fetchall()


def index_document_contents(db_path: str, *, status_cb: Callable | None = None, stop_flag=None, limit: int | None = None, mode: str = 'changed') -> dict:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    rows = _select_rows(con, mode)
    if limit:
        rows = rows[:limit]
    stats = {"mode": mode, "queued": len(rows), "processed": 0, "ok": 0, "errors": 0, "stopped": False, "by_status": {}}
    for row in rows:
        if stop_flag and stop_flag.get('stop'):
            stats['stopped'] = True
            break
        try:
            result = extract_content(row['fullpath'], row['ext'], stop_flag=stop_flag)
        except InterruptedError:
            stats['stopped'] = True
            break
        now = int(time.time())
        con.execute(
            """
            INSERT INTO file_content (file_id, content_text, content_mtime, indexed_at, status, content_source, quality_score, page_count, text_length, error_text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(file_id) DO UPDATE SET
                content_text=excluded.content_text,
                content_mtime=excluded.content_mtime,
                indexed_at=excluded.indexed_at,
                status=excluded.status,
                content_source=excluded.content_source,
                quality_score=excluded.quality_score,
                page_count=excluded.page_count,
                text_length=excluded.text_length,
                error_text=excluded.error_text
            """,
            (row['id'], result.text, row['mtime'], now, result.status, result.source, result.quality_score, result.page_count, result.text_length, result.error_text),
        )
        con.commit()
        stats['processed'] += 1
        stats['by_status'][result.status] = stats['by_status'].get(result.status, 0) + 1
        if result.status == 'OK':
            stats['ok'] += 1
        elif result.status not in ('NO_TEXT', 'LOW_QUALITY', 'TOO_LARGE', 'UNSUPPORTED'):
            stats['errors'] += 1
        if status_cb:
            try:
                status_cb({"phase": "content_index", "processed": stats['processed'], "total": stats['queued'], "file": row['fullpath'], "status": result.status, "source": result.source, "mode": mode})
            except Exception:
                pass
    con.close()
    return stats
