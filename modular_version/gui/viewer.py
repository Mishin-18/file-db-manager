import os
import logging
import re
import csv
import time
import threading
import sqlite3
from pathlib import Path
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog
from ttkbootstrap.widgets import ToastNotification

from core.i18n import i18n
from core.ui_common import apply_app_icon
from core.shell import reveal_in_folder
from gui.widgets import CustomMessagebox as Messagebox, ToolTip, Spinner
from gui.dialogs import ResolveDialog

class Viewer(ttk.Toplevel):
    """Database viewer window with language support"""

    @staticmethod
    def _py_norm_sql(s: str) -> str:
        """
        Unicode-safe normalization for SQL search:
        - casefold (better than lower for Unicode)
        - unify slashes
        - remove whitespace (spaces, tabs, newlines)
        - remove common separators/punctuation
        """
        s = (s or "").strip()
        if not s:
            return ""
        s = s.casefold()
        s = s.replace("\\", "/")
        s = "".join(s.split())
        drop = "/-_.;,:( )[]{}'\"`+=|"
        return s.translate({ord(ch): None for ch in drop})

    def _escape_like(self, s: str) -> str:
        """Escape special chars for SQL LIKE using ESCAPE '!'.

        Rules:
          - '!'  -> '!!'
          - '%'  -> '!%'
          - '_'  -> '!_'
        """
        s = (s or "")
        s = s.replace("!", "!!")
        s = s.replace("%", "!%")
        s = s.replace("_", "!_")
        return s

    def _norm_for_search(self, s: str) -> str:
        """Aggressive normalization for user query (matches PY_NORM logic)."""
        return Viewer._py_norm_sql(s)

    def _ui_alive(self) -> bool:
        """Return True only while the window and key widgets still exist."""
        try:
            if getattr(self, "_closing", False):
                return False
            if not self.winfo_exists():
                return False
            tree = getattr(self, "tree", None)
            if tree is None or not tree.winfo_exists():
                return False
            return True
        except Exception:
            return False

    def _safe_after(self, ms, callback, *args):
        if getattr(self, "_closing", False):
            return None
        holder = {"id": None}

        def _runner():
            aid = holder.get("id")
            if aid:
                self._after_ids.discard(aid)
            if getattr(self, "_closing", False):
                return
            if not self._ui_alive() and callback.__name__ not in {"_set_export_state"}:
                return
            try:
                callback(*args)
            except tk.TclError:
                return
            except Exception:
                return

        try:
            aid = self.after(ms, _runner)
            holder["id"] = aid
            if aid:
                self._after_ids.add(aid)
            return aid
        except Exception:
            return None

    def _cancel_all_afters(self):
        for aid in list(getattr(self, "_after_ids", set())):
            try:
                self.after_cancel(aid)
            except Exception:
                pass
        self._after_ids.clear()

    def __init__(self, master: ttk.Window, db_path: str):
        super().__init__(master)
        # Hide immediately to avoid Windows showing a blank white rectangle
        # before the Toplevel is fully configured/positioned.
        self.withdraw()
        apply_app_icon(self)
        self.title(i18n.t('viewer_title') + Path(db_path).name)
        self.geometry("1280x760")

        self.db_path = db_path
        self.con = sqlite3.connect(db_path)
        self.con.row_factory = sqlite3.Row
        self.logger = logging.getLogger("FileDBManager")
        self.export_running = False
        self._closing = False
        self._after_ids = set()
        self.progress_dialog = None
        self.progress_spinner = None

        # Unicode-safe normalization function for forgiving search (incl. Cyrillic)
        self.con.create_function('PY_NORM', 1, Viewer._py_norm_sql)

        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=10, pady=10)

        # Set selection
        self.set_label = ttk.Label(toolbar, text=i18n.t('set_label'), font=("Segoe UI", 9, "bold"))
        self.set_label.pack(side="left")
        
        self.set_var = ttk.StringVar(value=i18n.t('set_all'))
        self.set_combo = ttk.Combobox(toolbar, textvariable=self.set_var, width=28, state="readonly")
        self.set_combo.pack(side="left", padx=6)
        self.set_combo.bind("<<ComboboxSelected>>", lambda e: self.reset())

        # Status filter
        self.status_label = ttk.Label(toolbar, text=i18n.t('status_label'), font=("Segoe UI", 9, "bold"))
        self.status_label.pack(side="left", padx=(12, 0))
        
        self.status_var = ttk.StringVar(value=i18n.t('set_all'))
        self.status_combo = ttk.Combobox(toolbar, textvariable=self.status_var, width=14, state="readonly")
        # Localized display values but keep internal codes in SQL
        self._status_display_to_code = {
            i18n.t('status_found'): 'FOUND',
            i18n.t('status_missing'): 'MISSING',
            i18n.t('status_ambiguous'): 'AMBIGUOUS',
        }
        self._status_code_to_display = {v: k for k, v in self._status_display_to_code.items()}
        self.status_combo["values"] = [
            i18n.t('set_all'),
            i18n.t('status_found'),
            i18n.t('status_missing'),
            i18n.t('status_ambiguous'),
        ]
        self.status_combo.pack(side="left", padx=6)
        self.status_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_view())

        # Status help
        self.status_help_btn = ttk.Button(
            toolbar,
            text="?",
            width=3,
            bootstyle="secondary",
            command=self._show_status_help,
        )
        self.status_help_btn.pack(side="left", padx=(0, 10))

        # Search
        self.search_label = ttk.Label(toolbar, text=i18n.t('search_label'), font=("Segoe UI", 9, "bold"))
        self.search_label.pack(side="left", padx=(12, 0))
        
        self.q = ttk.StringVar()
        self.entry = ttk.Entry(toolbar, textvariable=self.q, width=40)
        self.entry.pack(side="left", padx=8)
        self.entry.bind("<Return>", lambda e: self.search(reset=True))

        # Paste shortcuts in search field (works in EN/RU layout on Windows)
        # Reason: with RU layout Tk often sends keysym 'Cyrillic_ve' instead of 'v', so <Control-v> won't fire.
        def _paste_to_search(event=None):
            try:
                (event.widget if event else self.entry).event_generate("<<Paste>>")
            except Exception:
                pass
            return "break"

        def _on_search_keypress(event):
            try:
                ctrl = bool(event.state & 0x4)  # Control mask (Windows)
                if ctrl and (event.keycode == 86 or event.keysym in ("v", "V", "Cyrillic_ve")):
                    return _paste_to_search(event)
            except Exception:
                pass
            return None

        self.entry.bind("<KeyPress>", _on_search_keypress, add="+")
        self.entry.bind("<Shift-Insert>", _paste_to_search, add="+")

        self.search_btn = ttk.Button(toolbar, text=i18n.t('search_btn'), 
                                    command=lambda: self.search(reset=True),
                                    bootstyle="primary")
        self.search_btn.pack(side="left")
        
        self.reset_btn = ttk.Button(toolbar, text=i18n.t('reset_btn'), 
                                   command=self.reset,
                                   bootstyle="secondary-outline")
        self.reset_btn.pack(side="left", padx=6)

        # Only present checkbox
        self.only_present = ttk.BooleanVar(value=True)
        self.only_present_check = ttk.Checkbutton(toolbar, text=i18n.t('only_existing'), 
                                                 variable=self.only_present, 
                                                 command=self._on_only_present_toggle,
                                                 bootstyle="info")
        self.only_present_check.pack(side="left", padx=10)

        self.only_present_help_btn = ttk.Button(toolbar, text="?", width=3,
                                                command=self._show_only_present_help,
                                                bootstyle="secondary")
        self.only_present_help_btn.pack(side="left", padx=(0, 10))

        self.tt_only_present_check = ToolTip(self.only_present_check, i18n.t('tt_only_existing'))
        self.tt_only_present_help_btn = ToolTip(self.only_present_help_btn, i18n.t('tt_help_btn'))


        # Treeview
        cols = ("name", "relpath", "size", "mtime", "present", "status", "fullpath")

        # Make header column separators visible (some ttkbootstrap themes flatten headings too much).
        # We use a dedicated style for the search/result tree so only this window is affected.
        try:
            _tv_style = ttk.Style()
            _tv_style.configure("ViewerSearch.Treeview", borderwidth=1, relief="solid")
            _tv_style.configure(
                "ViewerSearch.Treeview.Heading",
                relief="raised",
                borderwidth=1,
                padding=(6, 4),
                font=("Segoe UI", 9, "bold"),
            )
            _tv_style.map(
                "ViewerSearch.Treeview.Heading",
                relief=[("active", "raised"), ("pressed", "sunken")],
            )
            self.tree = ttk.Treeview(
                self,
                columns=cols,
                show="headings",
                height=22,
                bootstyle="primary",
                style="ViewerSearch.Treeview",
            )
        except Exception:
            self.tree = ttk.Treeview(self, columns=cols, show="headings", height=22, bootstyle="primary")

        headers = {
            "name": i18n.t('header_name'),
            "relpath": i18n.t('header_relpath'),
            "size": i18n.t('header_size'),
            "mtime": i18n.t('header_mtime'),
            "present": i18n.t('header_present'),
            "status": i18n.t('header_status'),
            "fullpath": i18n.t('header_fullpath'),
        }
        
        for c in cols:
            self.tree.heading(c, text=headers[c], anchor="w")

        self.tree.column("name", width=220, anchor="w")
        self.tree.column("relpath", width=380, anchor="w")
        self.tree.column("size", width=90, anchor="e")
        self.tree.column("mtime", width=130, anchor="w")
        self.tree.column("present", width=55, anchor="center")
        self.tree.column("status", width=120, anchor="center")
        self.tree.column("fullpath", width=1, stretch=True, anchor="w")

        # Scrollbars
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.pack(fill="both", expand=True, padx=10)
        vsb.place(in_=self.tree, relx=1.0, rely=0, relheight=1.0, anchor="ne")
        hsb.pack(fill="x", padx=10, pady=(0, 8))

        self.row_meta = {}
        self.tree.bind("<Double-1>", self.on_double_click)

        # Bottom buttons
        bottom = ttk.Frame(self)
        bottom.pack(fill="x", padx=10, pady=(0, 10))

        self.show_btn = ttk.Button(bottom, text=i18n.t('show_in_folder'), 
                                  command=self.reveal_selected,
                                  bootstyle="info")
        self.show_btn.pack(side="left")
        self.export_btn = ttk.Button(bottom, text=i18n.t('export_csv'), 
                                    command=self.export_csv,
                                    bootstyle="success")
        self.export_btn.pack(side="left", padx=8)
        
        self.close_btn = ttk.Button(bottom, text=i18n.t('close'), 
                                   command=self.destroy,
                                   bootstyle="secondary")
        self.close_btn.pack(side="right")

        # Navigation
        nav = ttk.Frame(self)
        nav.pack(fill="x", padx=10, pady=(0, 10))
        
        self.first_btn = ttk.Button(nav, text=i18n.t('first'), command=self.first_page)
        self.first_btn.pack(side="left")
        
        self.prev_btn = ttk.Button(nav, text=i18n.t('previous'), command=self.prev_page)
        self.prev_btn.pack(side="left", padx=6)
        
        self.next_btn = ttk.Button(nav, text=i18n.t('next'), command=self.next_page)
        self.next_btn.pack(side="left", padx=6)
        
        self.last_btn = ttk.Button(nav, text=i18n.t('last'), command=self.last_page)
        self.last_btn.pack(side="left", padx=6)
        
        self.page_label = ttk.Label(nav, text="")
        self.page_label.pack(side="left", padx=12)

        self.limit = 500
        self.offset = 0
        self.last_query = None
        self.last_count = 0

        self.reload_sets()
        self.reset()

        # Finalize layout/position while still hidden, then show fully-built window.
        try:
            self.update_idletasks()
            self.lift()
            self.deiconify()
            self.focus_force()
        except Exception:
            try:
                self.deiconify()
            except Exception:
                pass

    def show_search_progress(self):
        """Show progress dialog during search"""
        self.progress_dialog = ttk.Toplevel(self)
        try:
            self.progress_dialog.withdraw()
        except Exception:
            pass
        apply_app_icon(self.progress_dialog)
        self.progress_dialog.title(i18n.t('search_btn'))
        self.progress_dialog.geometry("560x230")
        self.progress_dialog.transient(self)
        self.progress_dialog.grab_set()
        
        # Center on parent
        self.progress_dialog.update_idletasks()
        width = 560
        height = 230
        x = self.winfo_x() + (self.winfo_width() // 2) - (width // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (height // 2)
        self.progress_dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        frame = ttk.Frame(self.progress_dialog, padding=15)
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text=i18n.t('searching'), 
                 font=("Segoe UI", 10)).pack(pady=(0, 10))
        
        self.progress_spinner = Spinner(frame, size=24, line_width=3, speed_ms=70, bootstyle='info')
        self.progress_spinner.pack(pady=5)
        self.progress_spinner.start()
        
        self.progress_label = ttk.Label(
            frame,
            text=f"'{self.q.get()}'",
            font=("Segoe UI", 9),
            justify="center",
            anchor="center",
            wraplength=500,
        )
        self.progress_label.pack(fill="x", padx=8, pady=8)
        
        try:
            self.progress_dialog.deiconify()
            self.progress_dialog.lift()
        except Exception:
            try:
                self.progress_dialog.deiconify()
            except Exception:
                pass

        self.progress_dialog.update()

    def hide_search_progress(self):
        """Hide search progress dialog (if any)."""
        try:
            if getattr(self, 'progress_spinner', None):
                try:
                    self.progress_spinner.stop()
                except Exception:
                    pass
            if getattr(self, 'progress_dialog', None) and self.progress_dialog.winfo_exists():
                try:
                    self.progress_dialog.grab_release()
                except Exception:
                    pass
                try:
                    self.progress_dialog.destroy()
                except Exception:
                    pass
            self.progress_dialog = None
            self.progress_spinner = None
        except Exception:
            pass
        self.progress_dialog = None
        self.progress_spinner = None

    def update_language(self):
        """Update viewer texts when language changes"""
        self.title(i18n.t('viewer_title') + Path(self.db_path).name)
        
        # Update labels
        self.set_label.config(text=i18n.t('set_label'))
        self.status_label.config(text=i18n.t('status_label'))
        self.search_label.config(text=i18n.t('search_label'))
        
        # Update combobox values
        sets = [i18n.t('set_all')] + [r["name"] for r in self.con.execute("SELECT name FROM sets ORDER BY updated_at DESC;").fetchall()]
        self.set_combo['values'] = sets
        if self.set_var.get() not in sets:
            self.set_var.set(i18n.t('set_all'))
        # Status combobox: show localized labels, keep codes internally
        self._status_display_to_code = {
            i18n.t('status_found'): 'FOUND',
            i18n.t('status_missing'): 'MISSING',
            i18n.t('status_ambiguous'): 'AMBIGUOUS',
        }
        self._status_code_to_display = {v: k for k, v in self._status_display_to_code.items()}

        self.status_combo['values'] = [
            i18n.t('set_all'),
            i18n.t('status_found'),
            i18n.t('status_missing'),
            i18n.t('status_ambiguous'),
        ]
        if self.status_var.get() not in self.status_combo['values']:
            self.status_var.set(i18n.t('set_all'))
        # Update headers
        headers = {
            "name": i18n.t('header_name'),
            "relpath": i18n.t('header_relpath'),
            "size": i18n.t('header_size'),
            "mtime": i18n.t('header_mtime'),
            "present": i18n.t('header_present'),
            "status": i18n.t('header_status'),
            "fullpath": i18n.t('header_fullpath'),
        }
        for c in self.tree['columns']:
            self.tree.heading(c, text=headers[c])
        
        # Update buttons
        self.search_btn.config(text=i18n.t('search_btn'))
        self.reset_btn.config(text=i18n.t('reset_btn'))
        self.only_present_check.config(text=i18n.t('only_existing'))
        try:
            self.tt_only_present_check.text = i18n.t('tt_only_existing')
            self.tt_only_present_help_btn.text = i18n.t('tt_help_btn')
        except Exception:
            pass
        self.show_btn.config(text=i18n.t('show_in_folder'))
        self.export_btn.config(text=i18n.t('export_csv'))
        self.close_btn.config(text=i18n.t('close'))
        self.first_btn.config(text=i18n.t('first'))
        self.prev_btn.config(text=i18n.t('previous'))
        self.next_btn.config(text=i18n.t('next'))
        self.last_btn.config(text=i18n.t('last'))
        
        # Update page label
        self.update_page_label()

    def update_page_label(self):
        """Update page label text"""
        shown_from = min(self.last_count, self.offset + 1) if self.last_count else 0
        shown_to = min(self.last_count, self.offset + self.limit)
        if shown_from and shown_to:
            self.page_label.config(text=f"{shown_from}-{shown_to} {i18n.t('of')} {self.last_count}")
        else:
            self.page_label.config(text="")
        self.update_nav_buttons()

    def update_nav_buttons(self):
        """Enable/disable paging buttons based on current result size and page."""
        total = int(self.last_count or 0)
        has_multiple_pages = total > self.limit
        is_first_page = self.offset <= 0
        is_last_page = (self.offset + self.limit) >= total

        first_prev_state = 'normal' if (has_multiple_pages and not is_first_page) else 'disabled'
        next_last_state = 'normal' if (has_multiple_pages and not is_last_page) else 'disabled'

        try:
            self.first_btn.config(state=first_prev_state)
            self.prev_btn.config(state=first_prev_state)
            self.next_btn.config(state=next_last_state)
            self.last_btn.config(state=next_last_state)
        except Exception:
            pass

    def reload_sets(self):
        """Reload sets from database"""
        rows = self.con.execute("SELECT name FROM sets ORDER BY updated_at DESC;").fetchall()
        values = [i18n.t('set_all')] + [r["name"] for r in rows]
        self.set_combo["values"] = values
        if self.set_var.get() not in values:
            self.set_var.set(i18n.t('set_all'))
        if self.set_var.get() == i18n.t('set_all'):
            self.status_var.set(i18n.t('set_all'))

    def format_size(self, n: int) -> str:
        """Format file size"""
        if n is None:
            return ""
        n = int(n)
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if n < 1024:
                return f"{n} {unit}"
            n = n // 1024
        return f"{n} PB"

    def format_mtime(self, ts: int) -> str:
        """Format modification time"""
        if ts is None:
            return ""
        try:
            return time.strftime("%Y-%m-%d %H:%M", time.localtime(int(ts)))
        except Exception:
            return ""

    def clear(self):
        """Clear treeview safely even if the window is closing."""
        if not self._ui_alive():
            return
        try:
            for i in self.tree.get_children():
                self.tree.delete(i)
        except Exception:
            return
        self.row_meta.clear()

    def _selected_set_id(self) -> int | None:
        """Get selected set ID"""
        name = self.set_var.get()
        if name == i18n.t('set_all'):
            return None
        row = self.con.execute("SELECT id FROM sets WHERE name=?;", (name,)).fetchone()
        return int(row["id"]) if row else None

    def _present_filter_sql(self) -> str:
        """Get SQL for present filter"""
        return " AND f.is_present=1 " if self.only_present.get() else ""

    def _status_filter_sql_for_set_items(self) -> tuple[str, tuple]:
        """Get SQL for status filter"""
        if self.set_var.get() == i18n.t('set_all'):
            return "", ()
        st_disp = self.status_var.get()
        code = None
        try:
            code = self._status_display_to_code.get(st_disp)
        except Exception:
            code = None
        if code:
            return " AND si.status=? ", (code,)
        return "", ()

    def _base_sql(self) -> tuple[str, tuple]:
        """Get base SQL query"""
        set_id = self._selected_set_id()

        if set_id is None:
            sql = (
                "SELECT f.name, f.relpath, f.fullpath, f.size_bytes, f.mtime, f.is_present, '' AS status, NULL AS set_item_id, NULL AS raw_path "
                "FROM files f WHERE 1=1"
                + self._present_filter_sql() +
                " ORDER BY f.relpath"
            )
            return sql, ()

        status_sql, status_params = self._status_filter_sql_for_set_items()

        sql = (
            "SELECT "
            "COALESCE(f.name, '') AS name, "
            "COALESCE(f.relpath, si.raw_path) AS relpath, "
            "COALESCE(f.fullpath, si.resolved_path, si.raw_path) AS fullpath, "
            "f.size_bytes AS size_bytes, "
            "f.mtime AS mtime, "
            "COALESCE(f.is_present, 0) AS is_present, "
            "si.status AS status, "
            "si.id AS set_item_id, "
            "si.raw_path AS raw_path "
            "FROM set_items si "
            "LEFT JOIN files f ON f.id = si.file_id "
            "WHERE si.set_id=?"
            + status_sql
            + ("" if not self.only_present.get() else " AND COALESCE(f.is_present, 0)=1 ") +
            " ORDER BY relpath"
        )
        return sql, (set_id,) + status_params

    def load_rows(self, sql: str, params: tuple, reset_offset: bool):
        """Load rows into treeview"""
        if reset_offset:
            self.offset = 0

        sql_paged = sql + " LIMIT ? OFFSET ?"
        params_paged = params + (self.limit, self.offset)

        self.clear()
        cur = self.con.cursor()
        rows = cur.execute(sql_paged, params_paged).fetchall()

        for r in rows:
            size = self.format_size(r["size_bytes"])
            mtime = self.format_mtime(r["mtime"])
            present = "✓" if int(r["is_present"] or 0) == 1 else ""
            st_code = r["status"] or ""
            st = self._status_code_to_display.get(st_code, st_code)
            iid = self.tree.insert("", "end", values=(r["name"], r["relpath"], size, mtime, present, st, r["fullpath"]))
            self.row_meta[iid] = {
                "status": st_code,
                "fullpath": r["fullpath"],
                "set_item_id": r["set_item_id"],
                "raw_path": r["raw_path"],
            }

        count_sql = "SELECT COUNT(*) FROM (" + sql + ")"
        total = cur.execute(count_sql, params).fetchone()[0]
        self.last_count = total

        self.update_page_label()

        self.last_query = (sql, params)

    def reset(self):
        """Reset to default view"""
        self.q.set("")
        self.reload_sets()
        sql, params = self._base_sql()
        self.load_rows(sql, params, reset_offset=True)



    # ---------------------------
    # Filters & Help
    # ---------------------------
    def _on_only_present_toggle(self):
        """Warn once when enabling 'only existing on disk'."""
        try:
            enabled = bool(self.only_present.get())
        except Exception:
            enabled = True

        # warn once per Viewer lifetime when enabling
        if enabled and not getattr(self, "_warned_only_existing_on", False):
            self._warned_only_existing_on = True
            msg = i18n.t('warn_only_existing_on')
            if not Messagebox.yesno(msg, i18n.t('warning_title'), parent=self):
                self.only_present.set(False)
                enabled = False

        self.refresh_view()

    def _show_only_present_help(self):
        Messagebox.show_info(i18n.t('help_only_existing_text'), i18n.t('help_only_existing_title'), parent=self)

    def _show_status_help(self):
        dialog = ttk.Toplevel(self)
        try:
            dialog.withdraw()
        except Exception:
            pass
        apply_app_icon(dialog)
        dialog.title(i18n.t('help_status_title'))
        dialog.geometry("820x340")
        dialog.resizable(True, True)
        try:
            dialog.transient(self)
        except Exception:
            pass
        dialog.grab_set()

        try:
            dialog.update_idletasks()
            x = self.winfo_rootx() + (self.winfo_width() // 2) - (760 // 2)
            y = self.winfo_rooty() + (self.winfo_height() // 2) - (260 // 2)
            dialog.geometry(f"820x340+{max(0, x)}+{max(0, y)}")
        except Exception:
            pass

        main = ttk.Frame(dialog, padding=15)
        main.pack(fill="both", expand=True)

        ttk.Label(
            main,
            text=i18n.t('help_status_title'),
            bootstyle="info",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", pady=(0, 10))

        msg = ttk.Label(
            main,
            text=i18n.t('help_status_text'),
            justify="left",
            anchor="w"
        )
        msg.pack(fill="both", expand=True, anchor="w")

        def _update_wrap(_event=None):
            try:
                msg.configure(wraplength=max(320, main.winfo_width() - 24))
            except Exception:
                pass

        main.bind("<Configure>", _update_wrap, add="+")
        _update_wrap()

        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill="x", pady=(12, 0))

        ttk.Button(
            btn_frame,
            text=i18n.t('ok') or 'Понятно',
            command=dialog.destroy,
            bootstyle="secondary"
        ).pack(side="right")

        dialog.bind("<Return>", lambda e: dialog.destroy())
        dialog.bind("<Escape>", lambda e: dialog.destroy())

        try:
            dialog.deiconify()
            dialog.lift()
            dialog.focus_force()
        except Exception:
            try:
                dialog.deiconify()
            except Exception:
                pass

        self.wait_window(dialog)

    def refresh_view(self, reset_offset: bool = True):
        """Reload view applying current filters without clearing search text."""
        try:
            q_raw = (self.q.get() or "").strip()
        except Exception:
            q_raw = ""

        if q_raw:
            # re-run search keeping query
            self.search(reset=reset_offset)
            return

        sql, params = self._base_sql()
        self.load_rows(sql, params, reset_offset=reset_offset)

    def search(self, reset: bool):
        """Search by query (max-forgiving) with progress indicator (runs in worker thread)."""
        q_raw = (self.q.get() or "").strip()
        if not q_raw:
            self.reset()
            return

        # Keep paging state consistent
        if reset:
            self.offset = 0

        base_sql, base_params = self._base_sql()

        # IMPORTANT:
        # _base_sql() already ends with ORDER BY for the normal list view.
        # If we append conditions after that, SQLite raises: near "ORDER": syntax error.
        # So for search we wrap the base query into a subquery (and strip trailing ORDER BY just in case).
        base_sql_no_order = re.sub(r"\s+ORDER\s+BY\s+[\s\S]*$", "", base_sql, flags=re.IGNORECASE)

        # Build scoring query (relevance)
        q_escaped = self._escape_like(q_raw)
        like_raw = f"%{q_escaped}%"

        q_norm = self._norm_for_search(q_raw)
        like_norm = f"%{self._escape_like(q_norm)}%" if q_norm else like_raw

        n_name = "PY_NORM(name)"
        n_rel  = "PY_NORM(relpath)"
        n_full = "PY_NORM(fullpath)"

        # Higher score = higher in list
        score_expr = (
            " (CASE WHEN name LIKE ? ESCAPE '!' COLLATE NOCASE THEN 30 ELSE 0 END) + "
            " (CASE WHEN relpath LIKE ? ESCAPE '!' COLLATE NOCASE THEN 20 ELSE 0 END) + "
            " (CASE WHEN fullpath LIKE ? ESCAPE '!' COLLATE NOCASE THEN 10 ELSE 0 END) + "
            f" (CASE WHEN {n_name} LIKE ? ESCAPE '!' THEN 8 ELSE 0 END) + "
            f" (CASE WHEN {n_rel}  LIKE ? ESCAPE '!' THEN 6 ELSE 0 END) + "
            f" (CASE WHEN {n_full} LIKE ? ESCAPE '!' THEN 4 ELSE 0 END) "
        )

        where_clause = (
            "("
            " name    LIKE ? ESCAPE '!' COLLATE NOCASE OR"
            " relpath LIKE ? ESCAPE '!' COLLATE NOCASE OR"
            " fullpath LIKE ? ESCAPE '!' COLLATE NOCASE OR"
            f" {n_name} LIKE ? ESCAPE '!' OR"
            f" {n_rel}  LIKE ? ESCAPE '!' OR"
            f" {n_full} LIKE ? ESCAPE '!' "
            ")"
        )

        # NOTE: parameter order matters in SQLite:
        # 1) params in SELECT (score_expr)
        # 2) params in subquery (base_sql_no_order)
        # 3) params in WHERE (where_clause)
        sql = f"SELECT *, ({score_expr}) AS _score FROM ({base_sql_no_order}) WHERE {where_clause} ORDER BY _score DESC, name COLLATE NOCASE ASC"
        params = [
            # score
            like_raw, like_raw, like_raw, like_norm, like_norm, like_norm,
        ] + list(base_params) + [
            # where
            like_raw, like_raw, like_raw, like_norm, like_norm, like_norm,
        ]

        # Run in background so spinner animates
        self.show_search_progress()
        self.update_idletasks()

        def _worker():
            try:
                con = sqlite3.connect(self.db_path)
                con.row_factory = sqlite3.Row
                con.create_function('PY_NORM', 1, Viewer._py_norm_sql)

                cur = con.cursor()

                # Total count
                count_sql = f"SELECT COUNT(1) AS c FROM ({sql})"
                total = cur.execute(count_sql, params).fetchone()["c"]

                # Page
                sql_paged = sql + " LIMIT ? OFFSET ?"
                params_paged = list(params) + [self.limit, self.offset]
                rows = cur.execute(sql_paged, params_paged).fetchall()

                con.close()

                def _deliver_success():
                    if not self._ui_alive():
                        return
                    self._apply_rows(sql, params, rows, total)
                self._safe_after(0, _deliver_success)
            except Exception as e:
                def _deliver_error(err=e):
                    if not self.winfo_exists() or getattr(self, "_closing", False):
                        return
                    self._search_failed(err)
                try:
                    self._safe_after(0, _deliver_error)
                except Exception:
                    pass

        threading.Thread(target=_worker, daemon=True).start()

    def _apply_rows(self, sql: str, params: list, rows: list, total: int):
        """Apply pre-fetched rows to UI (runs on UI thread)."""
        if not self._ui_alive():
            try:
                self.hide_search_progress()
            except Exception:
                pass
            return
        try:
            self.hide_search_progress()
        except Exception:
            pass

        if not self._ui_alive():
            return
        self.clear()
        if not self._ui_alive():
            return

        self.last_query = (sql, tuple(params))
        self.last_count = int(total or 0)

        for r in rows:
            size = self.format_size(r["size_bytes"])
            mtime = self.format_mtime(r["mtime"])
            present = "✓" if int(r["is_present"] or 0) == 1 else ""
            st_code = r["status"] or ""
            st = self._status_code_to_display.get(st_code, st_code)
            iid = self.tree.insert("", "end", values=(r["name"], r["relpath"], size, mtime, present, st, r["fullpath"]))
            self.row_meta[iid] = {
                "status": st_code,
                "fullpath": r["fullpath"],
                "set_item_id": r["set_item_id"],
                "raw_path": r["raw_path"],
            }

        self.update_page_label()

    def _search_failed(self, err: Exception):
        try:
            self.hide_search_progress()
        except Exception:
            pass
        if not self.winfo_exists() or getattr(self, "_closing", False):
            return
        Messagebox.show_error(i18n.t('search_failed_generic'), i18n.t('error_title'), parent=self)


    def next_page(self):
        """Go to next page"""
        if self.offset + self.limit >= self.last_count:
            return
        self.offset += self.limit
        if self.last_query:
            sql, params = self.last_query
        else:
            sql, params = self._base_sql()
        self.load_rows(sql, params, reset_offset=False)

    def prev_page(self):
        """Go to previous page"""
        self.offset = max(0, self.offset - self.limit)
        if self.last_query:
            sql, params = self.last_query
        else:
            sql, params = self._base_sql()
        self.load_rows(sql, params, reset_offset=False)

    def first_page(self):
        """Go to first page"""
        self.offset = 0
        if self.last_query:
            sql, params = self.last_query
        else:
            sql, params = self._base_sql()
        self.load_rows(sql, params, reset_offset=False)

    def last_page(self):
        """Go to last page"""
        if self.last_count <= 0:
            return
        self.offset = ((self.last_count - 1) // self.limit) * self.limit
        if self.last_query:
            sql, params = self.last_query
        else:
            sql, params = self._base_sql()
        self.load_rows(sql, params, reset_offset=False)

    def selected_row_id(self):
        """Get selected row ID"""
        sel = self.tree.selection()
        return sel[0] if sel else None

    def reveal_selected(self):
        """Show selected file in folder"""
        iid = self.selected_row_id()
        if not iid:
            return
        meta = self.row_meta.get(iid, {})
        fullpath = meta.get("fullpath") or self.tree.item(iid, "values")[6]
        reveal_in_folder(fullpath, parent=self)

    def resolve_selected(self):
        """Resolve selected AMBIGUOUS item"""
        iid = self.selected_row_id()
        if not iid:
            return
        meta = self.row_meta.get(iid, {})
        if self.set_var.get() == i18n.t('set_all'):
            Messagebox.show_info(i18n.t('resolve_need_specific_set'), i18n.t('info'))
            return
        if meta.get("status") != "AMBIGUOUS":
            Messagebox.show_info(i18n.t('resolve_row_not_ambiguous'), i18n.t('info'))
            return
        set_item_id = meta.get("set_item_id")
        raw_path = meta.get("raw_path")
        if not set_item_id or not raw_path:
            Messagebox.show_error(i18n.t('resolve_no_service_data'), i18n.t('error'))
            return

        dlg = ResolveDialog(self, self.con, int(set_item_id), str(raw_path))
        self.wait_window(dlg)
        if dlg.choice:
            self.reset()

    def on_double_click(self, event=None):
        """Handle double click"""
        iid = self.selected_row_id()
        if not iid:
            return
        meta = self.row_meta.get(iid, {})
        if self.set_var.get() != i18n.t('set_all') and meta.get("status") == "AMBIGUOUS":
            self.resolve_selected()
        else:
            self.reveal_selected()

    def _set_export_state(self, enabled: bool):
        self.export_running = not enabled
        try:
            self.export_btn.config(state=("normal" if enabled else "disabled"))
        except Exception:
            pass

    def export_csv(self):
        """Export current view to CSV in background thread."""
        if self.export_running:
            return
        out = filedialog.asksaveasfilename(
            title=i18n.t('export_csv'),
            defaultextension=".csv",
            filetypes=[(i18n.t('csv_filetype'), "*.csv"), (i18n.t('filetype_all'), "*.*")]
        )
        if not out:
            return

        if self.last_query:
            sql, params = self.last_query
        else:
            sql, params = self._base_sql()

        self._set_export_state(False)
        self.master.set_status(i18n.t('export_csv_running'))

        def _worker():
            con = None
            try:
                con = sqlite3.connect(self.db_path)
                con.row_factory = sqlite3.Row
                con.create_function('PY_NORM', 1, Viewer._py_norm_sql)
                rows = con.execute(sql, params).fetchall()
                with open(out, "w", newline="", encoding="utf-8") as f:
                    w = csv.writer(f, delimiter=";")
                    w.writerow([i18n.t('header_name'), i18n.t('header_relpath'), i18n.t('header_fullpath'), 
                               i18n.t('header_size'), i18n.t('header_mtime'), i18n.t('header_present'), i18n.t('header_status')])
                    for r in rows:
                        w.writerow([
                            r["name"], r["relpath"], r["fullpath"],
                            r["size_bytes"] if r["size_bytes"] is not None else "",
                            r["mtime"] if r["mtime"] is not None else "",
                            int(r["is_present"] or 0),
                            r["status"] or ""
                        ])
                self._safe_after(0, self._show_info_safe, i18n.t('csv_saved_msg').format(n=len(rows), path=out), i18n.t('done'))
                self._safe_after(0, self.master.set_status, i18n.t('export_csv_done').format(n=len(rows)))
            except Exception as e:
                self.logger.exception("CSV export failed", exc_info=e)
                self._safe_after(0, self._show_error_safe, i18n.t('report_save_failed_generic'), i18n.t('error'))
                self._safe_after(0, self.master.set_status, i18n.t('error'))
            finally:
                try:
                    if con is not None:
                        con.close()
                except Exception:
                    pass
                self._safe_after(0, self._set_export_state, True)

        threading.Thread(target=_worker, daemon=True).start()

    def _show_info_safe(self, message, title):
        if self._ui_alive():
            Messagebox.show_info(message, title, parent=self)

    def _show_error_safe(self, message, title):
        if self.winfo_exists() and not getattr(self, "_closing", False):
            Messagebox.show_error(message, title, parent=self)

    def destroy(self):
        """Close database connection and destroy window safely."""
        self._closing = True
        try:
            self._cancel_all_afters()
        except Exception:
            pass
        try:
            self.hide_search_progress()
        except Exception:
            pass
        try:
            self.con.close()
        except Exception:
            pass
        super().destroy()
