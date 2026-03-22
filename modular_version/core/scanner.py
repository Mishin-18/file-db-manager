import os
import time
import json
import hashlib
import sqlite3
from pathlib import Path
from collections import defaultdict
from typing import Callable, Any

from core.env import IS_WIN
from core.i18n import i18n
from core.db import init_db, MARK_ALL_MISSING_SQL, UPSERT_SQL
from core.shell import is_hidden_or_system

EXCLUDE_DIR_NAMES = {
    "$RECYCLE.BIN",
    "System Volume Information",
    "Windows",
    "Program Files",
    "Program Files (x86)",
    "ProgramData",
    "AppData",
}

EXCLUDE_FILE_NAMES = {
    "desktop.ini",
    "thumbs.db",
}

EXCLUDE_FILE_PREFIXES = (
    "~$",      # temporary Office files
    ".~",      # sometimes temporary
)

EXCLUDE_FILE_EXTS = {
    "tmp",
    "log",
}


def should_skip_file(filename: str) -> bool:
    """Check if file should be excluded (temporary, system, etc.)"""
    if not filename:
        return True
    low = filename.lower()
    if low in EXCLUDE_FILE_NAMES:
        return True
    for p in EXCLUDE_FILE_PREFIXES:
        if low.startswith(p.lower()):
            return True
    ext = os.path.splitext(low)[1].lstrip(".")
    if ext in EXCLUDE_FILE_EXTS:
        return True
    return False

class ScanStopped(Exception):
    """Raised when user stops scanning."""


def sha1_file(path: str, chunk: int = 1024 * 1024, *, stop_flag=None) -> str:
    """Calculate SHA1 hash of file with cooperative cancel support."""
    h = hashlib.sha1()
    with open(path, "rb") as f:
        while True:
            if stop_flag and stop_flag.get("stop"):
                raise ScanStopped()
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


# ---------------------------
# scanning folder(s) -> DB
# ---------------------------

def _make_root_tag(root_folder: str, index: int) -> str:
    root_abs = os.path.abspath(root_folder)
    drive, tail = os.path.splitdrive(root_abs)
    drive_tag = (drive.rstrip(':/\\') or 'ROOT').replace(':', '')
    tail_tag = tail.strip('/\\') or drive_tag or f'ROOT{index + 1}'
    return f"{index + 1:02d}_{drive_tag}_{tail_tag}".replace('/', '_').replace('\\', '_')


def _iter_dir_and_files(root_folder: str, recursive: bool):
    if recursive:
        root_norm = os.path.normcase(os.path.abspath(root_folder))
        for dirpath, dirnames, filenames in os.walk(root_folder):
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIR_NAMES]
            if IS_WIN:
                dirnames[:] = [d for d in dirnames if not is_hidden_or_system(os.path.join(dirpath, d))]
            dir_norm = os.path.normcase(os.path.abspath(dirpath))
            if dir_norm != root_norm:
                if os.path.basename(dirpath) in EXCLUDE_DIR_NAMES:
                    continue
                if IS_WIN and is_hidden_or_system(dirpath):
                    continue
            yield dirpath, filenames
    else:
        names = []
        with os.scandir(root_folder) as it:
            for e in it:
                try:
                    is_dir = e.is_dir(follow_symlinks=False)
                except Exception:
                    is_dir = False
                if is_dir:
                    try:
                        if e.name in EXCLUDE_DIR_NAMES:
                            continue
                        if IS_WIN and is_hidden_or_system(e.path):
                            continue
                    except Exception:
                        pass
                    continue
                try:
                    is_file = e.is_file(follow_symlinks=False)
                except Exception:
                    is_file = False
                if not is_file:
                    try:
                        is_file = os.path.isfile(e.path)
                    except Exception:
                        is_file = False
                if not is_file:
                    continue
                try:
                    if should_skip_file(e.name):
                        continue
                    if IS_WIN and is_hidden_or_system(e.path):
                        continue
                    names.append(e.name)
                except Exception:
                    continue
        yield root_folder, names




def _count_candidate_files(root_folders: list[str], recursive: bool, *, status_cb: Callable[[Any], None] | None = None, stop_flag=None) -> tuple[int, bool]:
    total = 0
    stopped = False
    last_report = 0
    for root_index, root_folder in enumerate(root_folders):
        root_tag = _make_root_tag(root_folder, root_index)
        for dirpath, filenames in _iter_dir_and_files(root_folder, recursive):
            if stop_flag and stop_flag.get("stop"):
                stopped = True
                break
            for fn in filenames:
                if stop_flag and stop_flag.get("stop"):
                    stopped = True
                    break
                if should_skip_file(fn):
                    continue
                full = os.path.join(dirpath, fn)
                if IS_WIN and is_hidden_or_system(full):
                    continue
                total += 1
                if status_cb and (total - last_report >= 500):
                    try:
                        status_cb({"phase": "count", "counted": total, "root": root_folder, "root_tag": root_tag})
                    except Exception:
                        pass
                    last_report = total
            if stopped:
                break
        if stopped:
            break
    if status_cb:
        try:
            status_cb({"phase": "count_done", "counted": total})
        except Exception:
            pass
    return total, stopped

def scan_folders_to_db(
    root_folders: list[str],
    db_path: str,
    *,
    incremental: bool = True,
    compute_sha1: bool = False,
    recursive: bool = True,
    status_cb=None,
    stop_flag=None,
) -> dict:
    """Scan multiple folders and update database with file information."""
    roots: list[str] = []
    seen = set()
    for folder in root_folders:
        folder = os.path.abspath(str(folder))
        root = Path(folder)
        if not root.exists() or not root.is_dir():
            raise ValueError(f"Folder does not exist or is not a directory: {folder}")
        key = os.path.normcase(folder)
        if key not in seen:
            seen.add(key)
            roots.append(folder)
    if not roots:
        raise ValueError("No folders selected for scanning")

    total_candidates, stopped_before_scan = _count_candidate_files(roots, recursive, status_cb=status_cb, stop_flag=stop_flag)
    if stopped_before_scan:
        return {
            "files_total": 0,
            "files_planned": total_candidates,
            "errors": 0,
            "new": 0,
            "updated": 0,
            "unchanged": 0,
            "missing": 0,
            "sha1_computed": 0,
            "skipped": 0,
            "per_folder": {},
            "roots": roots,
            "stopped": True,
        }

    con = init_db(db_path, json.dumps(roots, ensure_ascii=False))
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    con.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('root_folders', ?);", (json.dumps(roots, ensure_ascii=False),))
    con.commit()

    existing = {}
    for row in cur.execute("SELECT relpath, size_bytes, mtime, sha1 FROM files;"):
        existing[row["relpath"]] = (row["size_bytes"], row["mtime"], row["sha1"])

    if incremental:
        cur.execute(MARK_ALL_MISSING_SQL)
        con.commit()
    else:
        cur.execute("DELETE FROM files;")
        con.commit()
        try:
            con.execute("VACUUM")
        except Exception:
            pass
        existing.clear()

    stats = {
        "files_total": 0,
        "files_planned": total_candidates,
        "errors": 0,
        "new": 0,
        "updated": 0,
        "unchanged": 0,
        "missing": 0,
        "sha1_computed": 0,
        "skipped": 0,
        "per_folder": {},
        "roots": roots,
        "stopped": False,
    }
    per_folder_counts = defaultdict(int)
    batch = []
    batch_size = 800
    scan_mode = i18n.t('scan_mode_recursive') if recursive else i18n.t('scan_mode_norec')
    last_ui_report = 0.0
    last_ui_processed = 0
    ui_every_files = 20
    ui_min_gap = 0.10

    def report_scan_progress(force: bool = False):
        nonlocal last_ui_report, last_ui_processed
        if not status_cb:
            return
        now = time.monotonic()
        processed = int(stats["files_total"])
        if not force:
            if processed <= 0:
                return
            if (processed - last_ui_processed) < ui_every_files and (now - last_ui_report) < ui_min_gap:
                return
        try:
            status_cb({
                "phase": "scan",
                "mode": scan_mode,
                "processed": processed,
                "total": total_candidates,
                "new": stats["new"],
                "updated": stats["updated"],
                "skipped": stats["skipped"],
                "errors": stats["errors"],
                "sha1": stats["sha1_computed"],
            })
        except Exception:
            return
        last_ui_report = now
        last_ui_processed = processed

    def flush():
        nonlocal batch
        if not batch:
            return
        cur.executemany(UPSERT_SQL, batch)
        con.commit()
        batch = []

    for root_index, root_folder in enumerate(roots):
        root_tag = _make_root_tag(root_folder, root_index)
        for dirpath, filenames in _iter_dir_and_files(root_folder, recursive):
            if stop_flag and stop_flag.get("stop"):
                stats["stopped"] = True
                break
            for fn in filenames:
                if stop_flag and stop_flag.get("stop"):
                    stats["stopped"] = True
                    break
                if should_skip_file(fn):
                    stats["skipped"] += 1
                    continue
                full = os.path.join(dirpath, fn)
                if IS_WIN and is_hidden_or_system(full):
                    stats["skipped"] += 1
                    continue
                try:
                    st = os.stat(full)
                    rel_inner = os.path.relpath(full, root_folder)
                    rel = f"[{root_tag}] {rel_inner}"
                    ext = os.path.splitext(fn)[1].lstrip('.').lower()
                    size = int(st.st_size)
                    mtime = int(st.st_mtime)
                    prev = existing.get(rel)
                    sha1 = None
                    if prev is None:
                        stats["new"] += 1
                        if compute_sha1:
                            sha1 = sha1_file(full, stop_flag=stop_flag)
                            stats["sha1_computed"] += 1
                    else:
                        prev_size, prev_mtime, prev_sha1 = prev
                        if prev_size == size and prev_mtime == mtime:
                            stats["unchanged"] += 1
                            if compute_sha1 and not prev_sha1:
                                sha1 = sha1_file(full, stop_flag=stop_flag)
                                stats["sha1_computed"] += 1
                            else:
                                sha1 = prev_sha1
                        else:
                            stats["updated"] += 1
                            if compute_sha1:
                                sha1 = sha1_file(full, stop_flag=stop_flag)
                                stats["sha1_computed"] += 1
                            else:
                                sha1 = prev_sha1
                    batch.append((fn, rel, full, ext, size, mtime, sha1))
                    stats["files_total"] += 1
                    try:
                        rel_dir = os.path.relpath(dirpath, root_folder)
                    except Exception:
                        rel_dir = "."
                    if rel_dir in (".", os.curdir):
                        rel_dir = "."
                    per_folder_counts[f"[{root_tag}] {rel_dir}"] += 1
                    report_scan_progress(force=False)
                    if len(batch) >= batch_size:
                        flush()
                        report_scan_progress(force=True)
                except ScanStopped:
                    stats["stopped"] = True
                    break
                except Exception:
                    stats["errors"] += 1
                    continue
            if stats["stopped"]:
                break
        if stats["stopped"]:
            break

    flush()
    stats["missing"] = cur.execute("SELECT COUNT(*) FROM files WHERE is_present=0;").fetchone()[0]
    con.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('updated_at', ?);", (str(int(time.time())),))
    con.commit()
    stats["per_folder"] = dict(per_folder_counts)
    report_scan_progress(force=True)
    con.close()
    return stats


def scan_folder_to_db(root_folder: str, db_path: str, **kwargs) -> dict:
    """Backward-compatible single-folder wrapper."""
    return scan_folders_to_db([root_folder], db_path, **kwargs)
