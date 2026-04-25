from __future__ import annotations
import sqlite3
import unicodedata
from datetime import datetime
import re


def norm_text(s: str) -> str:
    s = s or ''
    s = unicodedata.normalize('NFKC', s)
    return s.casefold().strip()


def py_norm_sql(s):
    if s is None:
        return ''
    return norm_text(str(s))


def escape_like(s: str) -> str:
    return s.replace('!', '!!').replace('%', '!%').replace('_', '!_')


def _parse_size_to_bytes(value: str | None):
    if value in (None, ''):
        return None
    s = str(value).strip().replace(',', '.').replace(' ', ' ')
    if not s:
        return None
    m = re.match(r'^([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Zа-яА-Я]{0,3})$', s)
    if not m:
        return None
    num = float(m.group(1))
    unit = (m.group(2) or '').strip().casefold()
    factors = {
        '': 1, 'b': 1, 'б': 1,
        'k': 1024, 'kb': 1024, 'к': 1024, 'кб': 1024,
        'm': 1024**2, 'mb': 1024**2, 'м': 1024**2, 'мб': 1024**2,
        'g': 1024**3, 'gb': 1024**3, 'г': 1024**3, 'гб': 1024**3,
        't': 1024**4, 'tb': 1024**4, 'т': 1024**4, 'тб': 1024**4,
    }
    if unit not in factors:
        return None
    return int(num * factors[unit])


def _parse_date_to_ts(value: str | None, end: bool = False):
    if not value:
        return None
    raw = value.strip()
    if not raw:
        return None
    for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%d-%m-%Y', '%Y.%m.%d', '%d/%m/%Y', '%Y/%m/%d'):
        try:
            dt = datetime.strptime(raw, fmt)
            if end:
                dt = dt.replace(hour=23, minute=59, second=59)
            return int(dt.timestamp())
        except Exception:
            pass
    return None


def _build_fs_filter_sql(filters: dict | None):
    filters = filters or {}
    where = []
    params = []
    kind = (filters.get('item_kind') or 'all').lower()
    if kind == 'files':
        where.append("item_type='FILE'")
    elif kind == 'folders':
        where.append("item_type='FOLDER'")
    ext = (filters.get('ext') or '').strip().lower().lstrip('.')
    if ext:
        where.append("(item_type='FILE' AND lower(COALESCE(ext,''))=?)")
        params.append(ext)
    size_min = filters.get('size_min')
    if size_min not in (None, ''):
        try:
            parsed = _parse_size_to_bytes(size_min)
            if parsed is not None:
                where.append("COALESCE(size_bytes,0) >= ?")
                params.append(parsed)
        except Exception:
            pass
    size_max = filters.get('size_max')
    if size_max not in (None, ''):
        try:
            parsed = _parse_size_to_bytes(size_max)
            if parsed is not None:
                where.append("COALESCE(size_bytes,0) <= ?")
                params.append(parsed)
        except Exception:
            pass
    ts_from = _parse_date_to_ts(filters.get('date_from'))
    if ts_from is not None:
        where.append("COALESCE(mtime,0) >= ?")
        params.append(ts_from)
    ts_to = _parse_date_to_ts(filters.get('date_to'), end=True)
    if ts_to is not None:
        where.append("COALESCE(mtime,0) <= ?")
        params.append(ts_to)
    return (' AND ' + ' AND '.join(where)) if where else '', params


def search_fs(con: sqlite3.Connection, query: str, only_present: bool = True, limit: int = 500, offset: int = 0, filters: dict | None = None):
    con.create_function('PY_NORM', 1, py_norm_sql)
    q_raw = (query or '').strip()
    q_escaped = escape_like(q_raw)
    like_raw = f'%{q_escaped}%'
    q_norm = norm_text(q_raw)
    like_norm = f'%{escape_like(q_norm)}%' if q_norm else like_raw
    present_sql = ' AND is_present=1 ' if only_present else ''
    extra_sql, extra_params = _build_fs_filter_sql(filters)
    base_union = f'''
    FROM (
      SELECT 'FILE' AS item_type, name, relpath, fullpath, ext, size_bytes, mtime, is_present FROM files WHERE 1=1 {present_sql}
      UNION ALL
      SELECT 'FOLDER' AS item_type, name, relpath, fullpath, NULL AS ext, NULL AS size_bytes, mtime, is_present FROM folders WHERE 1=1 {present_sql}
    )
    WHERE (
      name LIKE ? ESCAPE '!' COLLATE NOCASE OR relpath LIKE ? ESCAPE '!' COLLATE NOCASE OR fullpath LIKE ? ESCAPE '!' COLLATE NOCASE OR
      PY_NORM(name) LIKE ? ESCAPE '!' OR PY_NORM(relpath) LIKE ? ESCAPE '!' OR PY_NORM(fullpath) LIKE ? ESCAPE '!'
    ) {extra_sql}
    '''
    sql = f'''
    SELECT item_type, name, relpath, fullpath, size_bytes, mtime, is_present, '' as status, NULL as set_item_id, NULL as raw_path,
           (
             (CASE WHEN name LIKE ? ESCAPE '!' COLLATE NOCASE THEN 30 ELSE 0 END) +
             (CASE WHEN relpath LIKE ? ESCAPE '!' COLLATE NOCASE THEN 20 ELSE 0 END) +
             (CASE WHEN fullpath LIKE ? ESCAPE '!' COLLATE NOCASE THEN 10 ELSE 0 END) +
             (CASE WHEN PY_NORM(name) LIKE ? ESCAPE '!' THEN 8 ELSE 0 END) +
             (CASE WHEN PY_NORM(relpath) LIKE ? ESCAPE '!' THEN 6 ELSE 0 END) +
             (CASE WHEN PY_NORM(fullpath) LIKE ? ESCAPE '!' THEN 4 ELSE 0 END)
           ) AS _score
    {base_union}
    ORDER BY _score DESC, name COLLATE NOCASE ASC, item_type ASC
    LIMIT ? OFFSET ?
    '''
    params = [like_raw, like_raw, like_raw, like_norm, like_norm, like_norm,
              like_raw, like_raw, like_raw, like_norm, like_norm, like_norm, *extra_params,
              limit, offset]
    rows = con.execute(sql, params).fetchall()
    count_sql = 'SELECT COUNT(*) ' + base_union
    total = con.execute(count_sql, [like_raw, like_raw, like_raw, like_norm, like_norm, like_norm, *extra_params]).fetchone()[0]
    return rows, total



class ContentSearchQueryError(ValueError):
    pass


def _tokenize_content_query(query: str) -> list[str]:
    q_raw = unicodedata.normalize('NFKC', (query or '').strip())
    if not q_raw:
        return []
    tokens = re.findall(r'[^\W_]+', q_raw, flags=re.UNICODE)
    cleaned: list[str] = []
    seen: set[str] = set()
    for token in tokens:
        token = (token or '').strip("_ ").casefold()
        if not token:
            continue
        if len(token) == 1 and not token.isdigit():
            continue
        if token in seen:
            continue
        seen.add(token)
        cleaned.append(token)
        if len(cleaned) >= 8:
            break
    return cleaned


def _prepare_content_fts_query(query: str) -> str:
    tokens = _tokenize_content_query(query)
    if not tokens:
        raise ContentSearchQueryError('empty_or_invalid_query')
    clauses: list[str] = []
    for token in tokens:
        safe = token.replace('"', '""')
        if len(token) >= 3 and not token.isdigit():
            clauses.append(f'{safe}*')
        else:
            clauses.append(f'"{safe}"')
    return ' AND '.join(clauses)

def search_content(con: sqlite3.Connection, query: str, only_present: bool = True, limit: int = 500, offset: int = 0, filters: dict | None = None):
    q_match = _prepare_content_fts_query(query)
    if not q_match:
        return [], 0
    filters = filters or {}
    where_present = ' AND f.is_present=1 ' if only_present else ''
    extra = []
    params = [q_match]
    ext = (filters.get('ext') or '').strip().lower().lstrip('.')
    if ext:
        extra.append(" AND lower(COALESCE(f.ext,'')) = ? ")
        params.append(ext)
    size_min = filters.get('size_min')
    if size_min not in (None, ''):
        try:
            parsed = _parse_size_to_bytes(size_min)
            if parsed is not None:
                extra.append(' AND COALESCE(f.size_bytes,0) >= ? ')
                params.append(parsed)
        except Exception:
            pass
    size_max = filters.get('size_max')
    if size_max not in (None, ''):
        try:
            parsed = _parse_size_to_bytes(size_max)
            if parsed is not None:
                extra.append(' AND COALESCE(f.size_bytes,0) <= ? ')
                params.append(parsed)
        except Exception:
            pass
    ts_from = _parse_date_to_ts(filters.get('date_from'))
    if ts_from is not None:
        extra.append(' AND COALESCE(f.mtime,0) >= ? ')
        params.append(ts_from)
    ts_to = _parse_date_to_ts(filters.get('date_to'), end=True)
    if ts_to is not None:
        extra.append(' AND COALESCE(f.mtime,0) <= ? ')
        params.append(ts_to)
    extra_sql = ''.join(extra)
    sql = f'''
    SELECT 'FILE' AS item_type, f.name, f.relpath, f.fullpath, f.size_bytes, f.mtime, f.is_present,
           COALESCE(fc.status, '') AS status,
           NULL AS set_item_id,
           NULL AS raw_path,
           snippet(file_content_fts, 0, '[', ']', ' … ', 16) AS snippet,
           fc.content_source AS content_source
    FROM file_content_fts
    JOIN file_content fc ON fc.file_id = file_content_fts.rowid
    JOIN files f ON f.id = fc.file_id
    WHERE file_content_fts MATCH ? {where_present} {extra_sql}
    ORDER BY rank
    LIMIT ? OFFSET ?
    '''
    rows = con.execute(sql, [*params, limit, offset]).fetchall()
    count_sql = f'''
    SELECT COUNT(*)
    FROM file_content_fts
    JOIN file_content fc ON fc.file_id = file_content_fts.rowid
    JOIN files f ON f.id = fc.file_id
    WHERE file_content_fts MATCH ? {where_present} {extra_sql}
    '''
    total = con.execute(count_sql, params).fetchone()[0]
    return rows, total
