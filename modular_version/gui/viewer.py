import os
import logging
import re
import csv
import time
import threading
import sqlite3
import calendar
from datetime import datetime
from pathlib import Path
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import ToastNotification

from core.i18n import i18n
from core.ui_common import apply_app_icon
from core.shell import reveal_in_folder
from gui.widgets import CustomMessagebox as Messagebox, ToolTip, Spinner, attach_help
from gui.dialogs import ResolveDialog, askdirectory_custom, asksaveasfilename_custom
from core.search import search_fs, search_content, ContentSearchQueryError
from core.content.indexer import index_document_contents
from core.db import get_missing_required_tables

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

    def _search_modes(self):
        return [
            i18n.t('search_mode_fs'),
            i18n.t('search_mode_content'),
        ]

    def _mode_is_content(self) -> bool:
        try:
            return self.search_mode_var.get() == self._search_modes()[1]
        except Exception:
            return False

    def _visible_result_columns(self):
        if self._mode_is_content():
            return ("mark", "fullpath", "name", "relpath", "size", "mtime", "present", "status")
        return ("mark", "name", "relpath", "size", "mtime", "present", "status", "fullpath")

    def _apply_result_displaycolumns(self):
        try:
            self.tree.configure(displaycolumns=self._visible_result_columns())
        except Exception:
            pass

    def equalize_result_columns(self):
        try:
            visible = list(self._visible_result_columns())
            if not visible:
                return
            self.update_idletasks()
            total_width = max(int(self.tree.winfo_width() or 0), int(self.winfo_width() or 0) - 40, 640)
            per_col = max(80, total_width // max(1, len(visible)))
            for col in visible:
                self.tree.column(col, width=per_col, minwidth=80, stretch=True)
        except Exception:
            pass


    def _safe_widget_config(self, widget, **kwargs):
        try:
            widget.configure(**kwargs)
        except Exception:
            pass

    def _all_extensions_label(self):
        return i18n.t('filter_ext_all')

    def _load_extension_values(self):
        try:
            rows = self.con.execute(
                "SELECT DISTINCT lower(trim(ext)) AS ext FROM files WHERE trim(COALESCE(ext,'')) <> '' ORDER BY lower(trim(ext)) ASC"
            ).fetchall()
            return [self._all_extensions_label()] + [str(r['ext']).upper() for r in rows if r['ext']]
        except Exception:
            return [self._all_extensions_label()]

    def _refresh_extension_values(self):
        self._ext_all_values = self._load_extension_values()
        self._update_extension_popup()

    def _get_extension_candidates(self, typed: str):
        raw = (typed or '').strip()
        all_label = self._all_extensions_label()
        all_values = list(getattr(self, '_ext_all_values', []) or [all_label])
        if not raw or raw == all_label:
            return all_values
        needle = raw.lstrip('.').lower()
        return [v for v in all_values if v == all_label or needle in v.lstrip('.').lower()]

    def _hide_extension_popup(self):
        popup = getattr(self, '_ext_popup', None)
        if popup is not None:
            try:
                popup.withdraw()
            except Exception:
                pass

    def _ensure_extension_popup(self):
        popup = getattr(self, '_ext_popup', None)
        if popup is not None:
            return popup
        popup = tk.Toplevel(self)
        popup.withdraw()
        popup.overrideredirect(True)
        popup.transient(self)
        frame = ttk.Frame(popup, bootstyle='light')
        frame.pack(fill='both', expand=True)
        listbox = tk.Listbox(frame, activestyle='none', exportselection=False, height=8)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        listbox.bind('<<ListboxSelect>>', self._on_extension_listbox_select)
        listbox.bind('<ButtonRelease-1>', self._on_extension_listbox_click_apply)
        listbox.bind('<Return>', self._on_extension_listbox_confirm)
        listbox.bind('<Double-Button-1>', self._on_extension_listbox_confirm)
        listbox.bind('<Escape>', lambda e: self._hide_extension_popup() or 'break')
        popup.bind('<FocusOut>', lambda e: self._safe_after(100, self._hide_extension_popup))
        self._ext_popup = popup
        self._ext_listbox = listbox
        return popup

    def _update_extension_popup(self):
        popup = self._ensure_extension_popup()
        listbox = self._ext_listbox
        candidates = self._get_extension_candidates(self.ext_var.get())
        try:
            listbox.delete(0, tk.END)
            for value in candidates:
                listbox.insert(tk.END, value)
        except Exception:
            return
        if not candidates or self.ext_entry.instate(['disabled']):
            self._hide_extension_popup()
            return
        try:
            listbox.selection_clear(0, tk.END)
            listbox.selection_set(0)
            listbox.activate(0)
        except Exception:
            pass
        try:
            self.update_idletasks()
            x = self.ext_entry.winfo_rootx()
            y = self.ext_entry.winfo_rooty() + self.ext_entry.winfo_height()
            w = max(self.ext_entry.winfo_width() + self.ext_open_btn.winfo_width(), 180)
            rows = min(max(len(candidates), 1), 8)
            h = max(120, rows * 22)
            popup.geometry(f"{w}x{h}+{x}+{y}")
            popup.deiconify()
            popup.lift()
        except Exception:
            pass

    def _restore_extension_display_value(self):
        current = (self.ext_var.get() or '').strip()
        normalized = self._normalize_ext_value(current)
        if not normalized:
            self.ext_var.set(self._all_extensions_label())
            return
        for candidate in getattr(self, '_ext_all_values', []):
            if candidate != self._all_extensions_label() and candidate.lstrip('.').lower() == normalized:
                self.ext_var.set(candidate)
                return
        self.ext_var.set(current.upper().lstrip('.'))

    def _apply_extension_selection(self, value: str | None):
        selected = (value or '').strip()
        if not selected:
            selected = self._all_extensions_label()
        self.ext_var.set(selected)
        self._hide_extension_popup()
        self._on_ext_change()

    def _on_extension_listbox_select(self, event=None):
        try:
            selection = self._ext_listbox.curselection()
            if not selection:
                return
            value = self._ext_listbox.get(selection[0])
            self.ext_var.set(value)
        except Exception:
            return

    def _on_extension_listbox_click_apply(self, event=None):
        try:
            selection = self._ext_listbox.curselection()
            if selection:
                self._apply_extension_selection(self._ext_listbox.get(selection[0]))
                return 'break'
        except Exception:
            pass
        return None

    def _on_extension_listbox_confirm(self, event=None):
        try:
            selection = self._ext_listbox.curselection()
            if selection:
                self._apply_extension_selection(self._ext_listbox.get(selection[0]))
                return 'break'
        except Exception:
            pass
        self._on_ext_enter()
        return 'break'

    def _move_extension_popup_selection(self, delta: int):
        popup = getattr(self, '_ext_popup', None)
        if popup is None:
            return
        try:
            if str(popup.state()) == 'withdrawn':
                self._update_extension_popup()
            size = self._ext_listbox.size()
            if size <= 0:
                return
            selection = self._ext_listbox.curselection()
            idx = selection[0] if selection else 0
            idx = max(0, min(size - 1, idx + delta))
            self._ext_listbox.selection_clear(0, tk.END)
            self._ext_listbox.selection_set(idx)
            self._ext_listbox.activate(idx)
            self._ext_listbox.see(idx)
            self.ext_var.set(self._ext_listbox.get(idx))
        except Exception:
            pass

    def _toggle_extension_popup(self):
        popup = self._ensure_extension_popup()
        try:
            if str(popup.state()) == 'withdrawn':
                self._update_extension_popup()
                self.ext_entry.focus_set()
            else:
                self._hide_extension_popup()
        except Exception:
            self._update_extension_popup()

    def _on_ext_keyrelease(self, event=None):
        keysym = getattr(event, 'keysym', '') if event is not None else ''
        if keysym in {'Return', 'Escape', 'Tab', 'Up', 'Down', 'Prior', 'Next', 'Home', 'End'}:
            return
        self._update_extension_popup()

    def _on_ext_focus_in(self, event=None):
        if self.ext_entry.instate(['disabled']):
            return
        current = (self.ext_var.get() or '').strip()
        if current == self._all_extensions_label():
            self.ext_var.set('')
        self._update_extension_popup()

    def _on_ext_focus_out(self, event=None):
        self._safe_after(100, self._restore_extension_display_value)
        self._safe_after(120, self._hide_extension_popup)

    def _on_ext_enter(self, event=None):
        popup = getattr(self, '_ext_popup', None)
        try:
            popup_visible = popup is not None and str(popup.state()) != 'withdrawn'
        except Exception:
            popup_visible = False
        if popup_visible:
            try:
                selection = self._ext_listbox.curselection()
                if selection:
                    self._apply_extension_selection(self._ext_listbox.get(selection[0]))
                    return 'break'
            except Exception:
                pass
        self._restore_extension_display_value()
        self._hide_extension_popup()
        self._on_ext_change()
        return 'break'
    def _normalize_ext_value(self, value: str) -> str:
        raw = (value or '').strip()
        if not raw or raw == self._all_extensions_label():
            return ''
        return raw.lstrip('.').lower()

    def _sync_filter_states(self):
        is_content = self._mode_is_content()
        try:
            if self.kind_var.get() == i18n.t('item_kind_files'):
                self._kind_code = 'files'
            elif self.kind_var.get() == i18n.t('item_kind_folders'):
                self._kind_code = 'folders'
            else:
                self._kind_code = 'all'
        except Exception:
            self._kind_code = 'all'
        try:
            if is_content:
                self.kind_var.set(i18n.t('item_kind_files'))
                self.kind_combo.configure(state='disabled')
            else:
                self.kind_combo.configure(state='readonly')
        except Exception:
            pass
        try:
            kind_value = self.kind_var.get()
            ext_enabled = kind_value == i18n.t('item_kind_files')
            if not ext_enabled:
                self.ext_var.set(self._all_extensions_label())
                self.ext_entry.configure(state='disabled')
                self.ext_open_btn.configure(state='disabled')
                self._hide_extension_popup()
            else:
                self.ext_entry.configure(state='normal')
                self.ext_open_btn.configure(state='normal')
        except Exception:
            pass

    def _on_kind_change(self, event=None):
        self._sync_filter_states()
        self.refresh_view()

    def _on_ext_change(self, event=None):
        self._restore_extension_display_value()
        self.refresh_view()

    def _parse_entry_date(self, value: str | None):
        raw = (value or '').strip()
        if not raw:
            return None
        for fmt in ('%d.%m.%Y', '%Y-%m-%d', '%d-%m-%Y', '%Y.%m.%d', '%d/%m/%Y', '%Y/%m/%d'):
            try:
                return datetime.strptime(raw, fmt)
            except Exception:
                pass
        return None

    def _set_date_entry(self, var: ttk.StringVar, dt: datetime):
        var.set(dt.strftime('%d.%m.%Y'))
        self.refresh_view()

    def _show_calendar_popup(self, target_var: ttk.StringVar, anchor_widget):
        popup = ttk.Toplevel(self)
        popup.transient(self)
        popup.title(i18n.t('calendar_title'))
        popup.resizable(False, False)
        try:
            import sys
            if sys.platform.startswith('win'):
                popup.wm_attributes('-toolwindow', True)
        except Exception:
            pass
        selected = self._parse_entry_date(target_var.get()) or datetime.now()
        state = {'year': selected.year, 'month': selected.month}

        header = ttk.Frame(popup, padding=(10, 10, 10, 6))
        header.pack(fill='x')
        body = ttk.Frame(popup, padding=(10, 0, 10, 10))
        body.pack(fill='both', expand=True)

        month_label = ttk.Label(header, text='')
        month_label.pack(side='left', expand=True)

        def close_popup():
            try:
                popup.destroy()
            except Exception:
                pass

        def move_month(delta: int):
            month = state['month'] + delta
            year = state['year']
            while month < 1:
                month += 12
                year -= 1
            while month > 12:
                month -= 12
                year += 1
            state['year'] = year
            state['month'] = month
            render_calendar()

        prev_btn = ttk.Button(header, text=i18n.t('calendar_prev_month'), width=3, command=lambda: move_month(-1), bootstyle='secondary-outline')
        prev_btn.pack(side='left')
        next_btn = ttk.Button(header, text=i18n.t('calendar_next_month'), width=3, command=lambda: move_month(1), bootstyle='secondary-outline')
        next_btn.pack(side='right')

        def pick_day(day: int):
            self._set_date_entry(target_var, datetime(state['year'], state['month'], day))
            close_popup()

        def render_calendar():
            for child in body.winfo_children():
                child.destroy()
            month_names = (i18n.t('calendar_month_names') or '').split('|')
            month_name = month_names[state['month'] - 1] if len(month_names) >= 12 else str(state['month'])
            month_label.config(text=f"{month_name} {state['year']}")
            week_days = (i18n.t('calendar_weekday_names') or '').split('|')
            for idx, title in enumerate(week_days):
                ttk.Label(body, text=title, anchor='center').grid(row=0, column=idx, padx=2, pady=2, sticky='nsew')
            weeks = calendar.monthcalendar(state['year'], state['month'])
            for r, week in enumerate(weeks, start=1):
                for c, day in enumerate(week):
                    if day == 0:
                        ttk.Label(body, text='').grid(row=r, column=c, padx=2, pady=2, sticky='nsew')
                    else:
                        ttk.Button(body, text=str(day), width=3, command=lambda d=day: pick_day(d), bootstyle='light').grid(row=r, column=c, padx=2, pady=2, sticky='nsew')
            def pick_today():
                now = datetime.now()
                state['year'] = now.year
                state['month'] = now.month
                pick_day(now.day)

            today_btn = ttk.Button(body, text=i18n.t('calendar_today'), command=pick_today, bootstyle='info-link')
            today_btn.grid(row=len(weeks)+1, column=0, columnspan=7, pady=(8,0))

        def _popup_update_language():
            popup.title(i18n.t('calendar_title'))
            prev_btn.config(text=i18n.t('calendar_prev_month'))
            next_btn.config(text=i18n.t('calendar_next_month'))
            render_calendar()

        popup.update_language = _popup_update_language
        render_calendar()
        try:
            popup.update_idletasks()
            x = anchor_widget.winfo_rootx()
            y = anchor_widget.winfo_rooty() + anchor_widget.winfo_height() + 2
            popup.geometry(f'+{x}+{y}')
            popup.grab_set()
            popup.focus_force()
        except Exception:
            pass

    def _refresh_result_headers(self):
        try:
            headers = {
                "mark": i18n.t('header_mark'),
                "name": i18n.t('header_name'),
                "relpath": i18n.t('header_relpath'),
                "size": i18n.t('header_size'),
                "mtime": i18n.t('header_mtime'),
                "present": i18n.t('header_present'),
                "status": i18n.t('header_source') if self._mode_is_content() else i18n.t('header_status'),
                "fullpath": i18n.t('header_snippet') if self._mode_is_content() else i18n.t('header_fullpath'),
            }
            for c in self.tree['columns']:
                self.tree.heading(c, text=headers[c])
            self._apply_result_displaycolumns()
        except Exception:
            pass

    def _on_search_mode_change(self, event=None):
        self._refresh_result_headers()
        self._sync_filter_states()
        self._sync_status_filter_state()
        if not (self.q.get() or '').strip():
            self.refresh_view(reset_offset=True)

    def _has_indexed_content(self) -> bool:
        try:
            row = self.con.execute(
                """
                SELECT 1
                FROM file_content
                WHERE UPPER(COALESCE(status, '')) = 'OK'
                  AND LENGTH(TRIM(COALESCE(content_text, ''))) > 0
                LIMIT 1
                """
            ).fetchone()
            return bool(row)
        except Exception:
            return False

    def _refresh_search_mode_availability(self):
        values = [self._search_modes()[0]]
        if self._has_indexed_content():
            values.append(self._search_modes()[1])
        self.search_mode_combo['values'] = values
        if self.search_mode_var.get() not in values:
            self.search_mode_var.set(values[0])

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
        missing_tables = get_missing_required_tables(self.con)
        if missing_tables:
            self.con.close()
            msg = i18n.t('old_db_message').format(tables=', '.join(missing_tables))
            raise RuntimeError(msg)
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
        self.set_combo = ttk.Combobox(toolbar, textvariable=self.set_var, width=22, state="readonly")
        self.set_combo.pack(side="left", padx=6)
        self.set_combo.bind("<<ComboboxSelected>>", lambda e: self.reset())

        # Status filter
        self.status_label = ttk.Label(toolbar, text=i18n.t('status_label'), font=("Segoe UI", 9, "bold"))
        self.status_label.pack(side="left", padx=(12, 0))
        
        self.status_var = ttk.StringVar(value=i18n.t('set_all'))
        self.status_combo = ttk.Combobox(toolbar, textvariable=self.status_var, width=22, state="disabled")
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
            text="ⓘ",
            width=3,
            command=self._show_status_help,
                                               bootstyle="secondary",
        )
        self.status_help_btn.pack(side="left", padx=(0, 10))
        self.help_status = attach_help(
            self.status_help_btn,
            text_getter=lambda: i18n.t('help_status_text'),
            title_getter=lambda: i18n.t('help_status_title'),
            parent_getter=lambda: self,
        )

        self.search_mode_var = ttk.StringVar(value=self._search_modes()[0])
        self.search_mode_combo = ttk.Combobox(toolbar, textvariable=self.search_mode_var, width=22, state="readonly")
        self._refresh_search_mode_availability()
        self.search_mode_combo.pack(side="left", padx=(0, 4))
        self.search_mode_combo.bind("<<ComboboxSelected>>", self._on_search_mode_change)

        self.search_mode_help_btn = ttk.Button(
            toolbar,
            text="?",
            width=3,
            bootstyle="secondary",
        )
        self.search_mode_help_btn.pack(side="left", padx=(0, 10))
        self.help_search_mode_short = attach_help(
            self.search_mode_help_btn,
            text_getter=lambda: i18n.t('tt_search_mode_content_help'),
            parent_getter=lambda: self,
        )

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
        self.tt_search_btn = ToolTip(self.search_btn, i18n.t('tt_search_btn_filters'))
        
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
                                                bootstyle="secondary")
        self.only_present_help_btn.pack(side="left", padx=(0, 10))
        self.help_only_present = attach_help(
            self.only_present_help_btn,
            text_getter=lambda: i18n.t('help_only_existing_text'),
            title_getter=lambda: i18n.t('help_only_existing_title'),
            parent_getter=lambda: self,
        )

        self.tt_only_present_check = ToolTip(self.only_present_check, i18n.t('tt_only_existing'))


        # Advanced filters
        filters = ttk.Frame(self)
        filters.pack(fill="x", padx=10, pady=(0, 4))

        self.kind_var = ttk.StringVar(value=i18n.t('item_kind_all'))
        self.kind_combo = ttk.Combobox(filters, textvariable=self.kind_var, width=14, state="readonly")
        self.kind_combo["values"] = [i18n.t('item_kind_all'), i18n.t('item_kind_files'), i18n.t('item_kind_folders')]
        self.kind_combo.pack(side="left", padx=(0, 6))
        self.kind_combo.bind("<<ComboboxSelected>>", self._on_kind_change)

        self.filter_ext_label = ttk.Label(filters, text=i18n.t('filter_ext'))
        self.filter_ext_label.pack(side="left")
        self.ext_var = ttk.StringVar(value=self._all_extensions_label())
        self._ext_all_values = self._load_extension_values()
        self.ext_picker = ttk.Frame(filters)
        self.ext_picker.pack(side="left", padx=(4, 8))
        self.ext_entry = ttk.Entry(self.ext_picker, textvariable=self.ext_var, width=18)
        self.ext_entry.pack(side="left", fill="x", expand=True)
        self.ext_open_btn = ttk.Button(self.ext_picker, text="▼", width=3, command=self._toggle_extension_popup, bootstyle="secondary-outline")
        self.ext_open_btn.pack(side="left", padx=(2, 0))
        self.tt_ext_entry = ToolTip(self.ext_entry, i18n.t('tt_ext_filter_files_only'))
        self.tt_ext_open_btn = ToolTip(self.ext_open_btn, i18n.t('tt_ext_filter_files_only'))
        self.ext_entry.bind("<KeyRelease>", self._on_ext_keyrelease)
        self.ext_entry.bind("<FocusIn>", self._on_ext_focus_in)
        self.ext_entry.bind("<FocusOut>", self._on_ext_focus_out)
        self.ext_entry.bind("<Return>", self._on_ext_enter)
        self.ext_entry.bind("<Down>", lambda e: self._move_extension_popup_selection(1) or 'break')
        self.ext_entry.bind("<Up>", lambda e: self._move_extension_popup_selection(-1) or 'break')
        self.ext_entry.bind("<Escape>", lambda e: self._hide_extension_popup() or 'break')

        self.filter_size_from_label = ttk.Label(filters, text=i18n.t('filter_size_from'))
        self.filter_size_from_label.pack(side="left")
        self.size_min_var = ttk.StringVar()
        self.size_min_entry = ttk.Entry(filters, textvariable=self.size_min_var, width=10)
        self.size_min_entry.pack(side="left", padx=(4, 8))
        self.size_min_entry.bind("<Return>", lambda e: self.refresh_view())
        self.size_min_entry.bind("<FocusOut>", lambda e: self._schedule_size_filter_refresh(0))
        self.size_min_var.trace_add("write", self._on_size_filter_var_changed)
        self.tt_size_min_entry = ToolTip(self.size_min_entry, i18n.t('tt_size_filter_example'))

        self.filter_size_to_label = ttk.Label(filters, text=i18n.t('filter_to'))
        self.filter_size_to_label.pack(side="left")
        self.size_max_var = ttk.StringVar()
        self.size_max_entry = ttk.Entry(filters, textvariable=self.size_max_var, width=10)
        self.size_max_entry.pack(side="left", padx=(4, 8))
        self.size_max_entry.bind("<Return>", lambda e: self.refresh_view())
        self.size_max_entry.bind("<FocusOut>", lambda e: self._schedule_size_filter_refresh(0))
        self.size_max_var.trace_add("write", self._on_size_filter_var_changed)
        self.tt_size_max_entry = ToolTip(self.size_max_entry, i18n.t('tt_size_filter_example'))

        self.filter_date_from_label = ttk.Label(filters, text=i18n.t('filter_date_from'))
        self.filter_date_from_label.pack(side="left")
        self.date_from_var = ttk.StringVar()
        self.date_from_entry = ttk.Entry(filters, textvariable=self.date_from_var, width=12)
        self.date_from_entry.pack(side="left", padx=(4, 2))
        self.date_from_entry.bind("<Return>", lambda e: self.refresh_view())
        self.date_from_btn = ttk.Button(filters, text=i18n.t('calendar_btn'), width=3, command=lambda: self._show_calendar_popup(self.date_from_var, self.date_from_btn), bootstyle='secondary-outline')
        self.date_from_btn.pack(side="left", padx=(0, 8))

        self.filter_date_to_label = ttk.Label(filters, text=i18n.t('filter_to'))
        self.filter_date_to_label.pack(side="left")
        self.date_to_var = ttk.StringVar()
        self.date_to_entry = ttk.Entry(filters, textvariable=self.date_to_var, width=12)
        self.date_to_entry.pack(side="left", padx=(4, 2))
        self.date_to_entry.bind("<Return>", lambda e: self.refresh_view())
        self.date_to_btn = ttk.Button(filters, text=i18n.t('calendar_btn'), width=3, command=lambda: self._show_calendar_popup(self.date_to_var, self.date_to_btn), bootstyle='secondary-outline')
        self.date_to_btn.pack(side="left", padx=(0, 8))

        self.clear_filters_btn = ttk.Button(filters, text=i18n.t('filter_clear'), command=self.clear_filters, bootstyle="secondary-outline")
        self.clear_filters_btn.pack(side="right")
        self.equalize_cols_btn = ttk.Button(filters, text=i18n.t('btn_equalize_columns'), command=self.equalize_result_columns, bootstyle="secondary-outline")
        self.equalize_cols_btn.pack(side="right", padx=(0, 6))
        self.tt_equalize_cols_btn = ToolTip(self.equalize_cols_btn, i18n.t('tt_equalize_columns'))

        self.empty_state_var = tk.StringVar(value="")
        self.empty_state_label = None

        # Treeview
        cols = ("mark", "name", "relpath", "size", "mtime", "present", "status", "fullpath")

        # Make header column separators visible (some ttkbootstrap themes flatten headings too much).
        # We use a dedicated style for the search/result tree so only this window is affected.
        self._apply_tree_theme_style()
        try:
            self.tree = ttk.Treeview(
                self,
                columns=cols,
                show="headings",
                height=22,
                bootstyle="primary",
                style="ViewerSearch.Treeview",
                selectmode="extended",
            )
        except Exception:
            self.tree = ttk.Treeview(self, columns=cols, show="headings", height=22, bootstyle="primary", selectmode="extended")

        headers = {
            "mark": i18n.t('header_mark'),
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

        self.tree.column("mark", width=120, anchor="center", stretch=True)
        self.tree.column("name", width=120, anchor="w", stretch=True)
        self.tree.column("relpath", width=120, anchor="w", stretch=True)
        self.tree.column("size", width=120, anchor="e", stretch=True)
        self.tree.column("mtime", width=120, anchor="w", stretch=True)
        self.tree.column("present", width=120, anchor="center", stretch=True)
        self.tree.column("status", width=120, anchor="center", stretch=True)
        self.tree.column("fullpath", width=120, minwidth=120, stretch=True, anchor="w")
        self._apply_result_displaycolumns()

        # Scrollbars
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.pack(fill="both", expand=True, padx=10)
        vsb.place(in_=self.tree, relx=1.0, rely=0, relheight=1.0, anchor="ne")
        hsb.pack(fill="x", padx=10, pady=(0, 8))

        self.empty_state_bootstyle = 'secondary'
        self.empty_state_label = tk.Label(
            self.tree,
            textvariable=self.empty_state_var,
            anchor="center",
            justify="center",
            padx=12,
            pady=6,
            bd=1,
            relief="solid",
        )
        self.tree.bind("<Configure>", lambda e: self._update_empty_state_wrap(), add="+")
        self.empty_state_label.place_forget()

        self.row_meta = {}
        self.checked_items = set()
        self.checked_paths = set()
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Button-1>", self._on_tree_click, add="+")

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

        self.mark_all_btn = ttk.Button(bottom, text=i18n.t('btn_mark_page'), command=self.mark_all_visible, bootstyle="secondary-outline")
        self.mark_all_btn.pack(side="left", padx=8)
        self.mark_all_pages_btn = ttk.Button(bottom, text=i18n.t('btn_mark_all_pages'), command=self.mark_all_pages, bootstyle="secondary-outline")
        self.mark_all_pages_btn.pack(side="left", padx=8)
        self.unmark_all_btn = ttk.Button(bottom, text=i18n.t('btn_unmark_all'), command=self.unmark_all_visible, bootstyle="secondary-outline")
        self.unmark_all_btn.pack(side="left", padx=8)

        self.collect_btn = ttk.Button(bottom, text=i18n.t('btn_collect_checked'), command=self.collect_selected_files, bootstyle="warning")
        self.collect_btn.pack(side="left", padx=8)

        self.marked_count_label = ttk.Label(bottom, text="")
        self.marked_count_label.pack(side="left", padx=(12, 0))

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

        self._sync_filter_states()
        self._sync_status_filter_state()

        self.limit = 500
        self.offset = 0
        self.last_query = None
        self.last_count = 0

        self.reload_sets()
        self.reset()
        self._update_marked_count_label()

        # Finalize layout/position while still hidden, then show fully-built window.
        try:
            self.update_idletasks()
            self.lift()
            self.deiconify()
            self.focus_force()
            self._safe_after(50, self.equalize_result_columns)
        except Exception:
            try:
                self.deiconify()
                self._safe_after(50, self.equalize_result_columns)
            except Exception:
                pass

    def _apply_tree_theme_style(self):
        """Re-apply dedicated result tree styles after theme changes."""
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
            if getattr(self, 'tree', None) is not None:
                try:
                    self.tree.configure(style="ViewerSearch.Treeview")
                except Exception:
                    pass
        except Exception:
            pass

    def update_theme(self):
        self._apply_tree_theme_style()
        try:
            self._apply_empty_state_style(getattr(self, 'empty_state_bootstyle', 'secondary'))
        except Exception:
            pass
        try:
            self.equalize_result_columns()
        except Exception:
            pass

    def on_ui_changed(self, change_kind: str):
        if change_kind == 'language':
            self.update_language()
        elif change_kind == 'theme':
            self.update_theme()

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
        
        self.progress_title_label = ttk.Label(frame, text=i18n.t('searching'), 
                 font=("Segoe UI", 10))
        self.progress_title_label.pack(pady=(0, 10))
        
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
        self._size_filter_after_id = None

    def update_language(self):
        """Update viewer texts when language changes."""
        self.title(i18n.t('viewer_title') + Path(self.db_path).name)

        # Top toolbar labels
        self.set_label.config(text=i18n.t('set_label'))
        self.status_label.config(text=i18n.t('status_label'))
        self.search_label.config(text=i18n.t('search_label'))

        # Top toolbar comboboxes
        current_set = self.set_var.get()
        sets = [i18n.t('set_all')] + [r["name"] for r in self.con.execute("SELECT name FROM sets ORDER BY updated_at DESC;").fetchall()]
        self.set_combo['values'] = sets
        if current_set not in sets:
            self.set_var.set(i18n.t('set_all'))

        self._status_display_to_code = {
            i18n.t('status_found'): 'FOUND',
            i18n.t('status_missing'): 'MISSING',
            i18n.t('status_ambiguous'): 'AMBIGUOUS',
        }
        self._status_code_to_display = {v: k for k, v in self._status_display_to_code.items()}
        current_status_code = self._status_display_to_code.get(self.status_var.get(), None)
        self.status_combo['values'] = [
            i18n.t('set_all'),
            i18n.t('status_found'),
            i18n.t('status_missing'),
            i18n.t('status_ambiguous'),
        ]
        if current_status_code and current_status_code in self._status_code_to_display:
            self.status_var.set(self._status_code_to_display[current_status_code])
        elif self.status_var.get() not in self.status_combo['values']:
            self.status_var.set(i18n.t('set_all'))

        current_mode_is_content = self._mode_is_content()
        self._refresh_search_mode_availability()
        modes = self._search_modes()
        self.search_mode_combo['values'] = [m for m in self.search_mode_combo['values']]
        self.search_mode_var.set(modes[1] if current_mode_is_content and len(self.search_mode_combo['values']) > 1 else modes[0])

        # Advanced filter labels / values
        self.kind_combo['values'] = [i18n.t('item_kind_all'), i18n.t('item_kind_files'), i18n.t('item_kind_folders')]
        try:
            current_kind = getattr(self, '_kind_code', None)
            if current_kind == 'files':
                self.kind_var.set(i18n.t('item_kind_files'))
            elif current_kind == 'folders':
                self.kind_var.set(i18n.t('item_kind_folders'))
            elif current_kind == 'all':
                self.kind_var.set(i18n.t('item_kind_all'))
            elif self.kind_var.get() not in self.kind_combo['values']:
                self.kind_var.set(i18n.t('item_kind_all'))
        except Exception:
            if self.kind_var.get() not in self.kind_combo['values']:
                self.kind_var.set(i18n.t('item_kind_all'))
        self.filter_ext_label.config(text=i18n.t('filter_ext'))
        self.filter_size_from_label.config(text=i18n.t('filter_size_from'))
        self.filter_size_to_label.config(text=i18n.t('filter_to'))
        self.filter_date_from_label.config(text=i18n.t('filter_date_from'))
        self.filter_date_to_label.config(text=i18n.t('filter_to'))

        self.search_mode_help_btn.config(text="?")
        self.only_present_help_btn.config(text="?")

        self._refresh_extension_values()
        if self._normalize_ext_value(self.ext_var.get()) and self.ext_var.get() not in self._ext_all_values:
            self._restore_extension_display_value()
        elif self.ext_var.get() not in self._ext_all_values:
            self.ext_var.set(self._all_extensions_label())

        # Buttons / checkboxes / tooltips
        self.search_btn.config(text=i18n.t('search_btn'))
        try:
            self.tt_search_btn.text = i18n.t('tt_search_btn_filters')
        except Exception:
            pass
        self.reset_btn.config(text=i18n.t('reset_btn'))
        self.only_present_check.config(text=i18n.t('only_existing'))
        self.clear_filters_btn.config(text=i18n.t('filter_clear'))
        self.equalize_cols_btn.config(text=i18n.t('btn_equalize_columns'))
        self.show_btn.config(text=i18n.t('show_in_folder'))
        self.export_btn.config(text=i18n.t('export_csv'))
        self.mark_all_btn.config(text=i18n.t('btn_mark_page'))
        self.mark_all_pages_btn.config(text=i18n.t('btn_mark_all_pages'))
        self.unmark_all_btn.config(text=i18n.t('btn_unmark_all'))
        self.collect_btn.config(text=i18n.t('btn_collect_checked'))
        self.close_btn.config(text=i18n.t('close'))
        self.first_btn.config(text=i18n.t('first'))
        self.prev_btn.config(text=i18n.t('previous'))
        self.next_btn.config(text=i18n.t('next'))
        self.last_btn.config(text=i18n.t('last'))
        self.date_from_btn.config(text=i18n.t('calendar_btn'))
        self.date_to_btn.config(text=i18n.t('calendar_btn'))
        try:
            self.tt_only_present_check.text = i18n.t('tt_only_existing')
            self.tt_size_min_entry.text = i18n.t('tt_size_filter_example')
            self.tt_size_max_entry.text = i18n.t('tt_size_filter_example')
            self.tt_equalize_cols_btn.text = i18n.t('tt_equalize_columns')
            self.tt_ext_entry.text = i18n.t('tt_ext_filter_files_only')
            self.tt_ext_open_btn.text = i18n.t('tt_ext_filter_files_only')
            self.help_status.apply()
            self.help_only_present.apply()
            self.help_search_mode_short.apply()
        except Exception:
            pass

        self._refresh_result_headers()
        self._sync_filter_states()
        self._sync_status_filter_state()
        try:
            if getattr(self, 'progress_dialog', None) and self.progress_dialog.winfo_exists():
                self.progress_dialog.title(i18n.t('search_btn'))
                if getattr(self, 'progress_title_label', None):
                    self.progress_title_label.config(text=i18n.t('searching'))
        except Exception:
            pass

        self.update_page_label()
        self._update_marked_count_label()
        try:
            self.refresh_view()
        except Exception:
            pass

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
            self.mark_all_pages_btn.config(state='normal' if has_multiple_pages else 'disabled')
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
        self._sync_status_filter_state()

    def format_size(self, n: int) -> str:
        """Format file size"""
        if n is None:
            return ""
        n = int(n)
        for unit in (i18n.t('size_unit_b'), i18n.t('size_unit_kb'), i18n.t('size_unit_mb'), i18n.t('size_unit_gb'), i18n.t('size_unit_tb')):
            if n < 1024:
                return f"{n} {unit}"
            n = n // 1024
        return f"{n} {i18n.t('size_unit_pb')}"

    def format_mtime(self, ts: int) -> str:
        """Format modification time"""
        if ts is None:
            return ""
        try:
            return time.strftime(i18n.t('datetime_format'), time.localtime(int(ts)))
        except Exception:
            return ""


    def _translate_content_source(self, value: str) -> str:
        mapping = {
            'docx': i18n.t('content_source_docx'),
            'xlsx': i18n.t('content_source_xlsx'),
            'pdf_embedded': i18n.t('content_source_pdf_embedded'),
            'pdf_ocr': i18n.t('content_source_pdf_ocr'),
            'pdf_mixed': i18n.t('content_source_pdf_mixed'),
        }
        return mapping.get((value or '').strip().lower(), value or i18n.t('content_source_unknown'))

    def clear(self):
        """Clear treeview safely even if the window is closing."""
        if not self._ui_alive():
            return
        self._hide_empty_state()
        try:
            for i in self.tree.get_children():
                self.tree.delete(i)
        except Exception:
            return
        self.row_meta.clear()
        self.checked_items.clear()
        self._update_marked_count_label()

    def _selected_set_id(self) -> int | None:
        """Get selected set ID"""
        name = self.set_var.get()
        if name == i18n.t('set_all'):
            return None
        row = self.con.execute("SELECT id FROM sets WHERE name=?;", (name,)).fetchone()
        return int(row["id"]) if row else None

    def _sync_status_filter_state(self):
        has_set = self._selected_set_id() is not None
        try:
            if not has_set:
                self.status_var.set(i18n.t('set_all'))
            self.status_combo.configure(state=('readonly' if has_set else 'disabled'))
        except Exception:
            pass

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
            fullpath = r["fullpath"]
            is_marked = bool(fullpath and fullpath in self.checked_paths)
            iid = self.tree.insert("", "end", values=(self._mark_symbol(is_marked), r["name"], r["relpath"], size, mtime, present, st, fullpath))
            if is_marked:
                self.checked_items.add(iid)
            self.row_meta[iid] = {
                "status": st_code,
                "fullpath": fullpath,
                "set_item_id": r["set_item_id"],
                "raw_path": r["raw_path"],
            }

        count_sql = "SELECT COUNT(*) FROM (" + sql + ")"
        total = cur.execute(count_sql, params).fetchone()[0]
        self.last_count = total

        self.update_page_label()
        self._update_marked_count_label()

        self.last_query = (sql, params)

    def reset(self):
        """Reset to default view"""
        self.q.set("")
        self.reload_sets()
        self._sync_status_filter_state()
        self._refresh_search_mode_availability()
        self._refresh_result_headers()
        if self._mode_is_content():
            self.offset = 0
            self._apply_custom_rows([], 0, 'content', '')
            return
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
        return








    def _show_status_help(self):
        Messagebox.show_info(i18n.t('help_status_text'), i18n.t('help_status_title'), parent=self)








        def _update_wrap(_event=None):
            try:
                msg.configure(wraplength=max(320, main.winfo_width() - 24))
            except Exception:
                pass

        main.bind("<Configure>", _update_wrap, add="+")
        _update_wrap()

        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill="x", pady=(12, 0))

        ok_btn = ttk.Button(
            btn_frame,
            text=i18n.t('ok'),
            command=dialog.destroy,
            bootstyle="secondary"
        )
        ok_btn.pack(side="right")

        def _update_language():
            dialog.title(i18n.t('help_status_title'))
            title_lbl.config(text=i18n.t('help_status_title'))
            msg.config(text=i18n.t('help_status_text'))
            ok_btn.config(text=i18n.t('ok'))

        dialog.update_language = _update_language
        dialog.on_ui_changed = lambda kind: _update_language() if kind == 'language' else None

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

    def _current_query_text(self) -> str:
        try:
            return (self.q.get() or '').strip()
        except Exception:
            return ''

    def _visible_fullpaths(self) -> list[str]:
        paths = []
        seen = set()
        for iid in self.tree.get_children():
            meta = self.row_meta.get(iid, {})
            fullpath = meta.get('fullpath')
            if fullpath and fullpath not in seen:
                seen.add(fullpath)
                paths.append(fullpath)
        return paths

    def _apply_checked_state(self, paths, checked: bool):
        path_set = {p for p in (paths or []) if p}
        if not path_set:
            return
        if checked:
            self.checked_paths.update(path_set)
        else:
            self.checked_paths.difference_update(path_set)
        for iid in self.tree.get_children():
            meta = self.row_meta.get(iid, {})
            fullpath = meta.get('fullpath')
            if not fullpath or fullpath not in path_set:
                continue
            if checked:
                self.checked_items.add(iid)
            else:
                self.checked_items.discard(iid)
            self._set_mark_visual(iid, checked)


    def _show_content_search_help(self):
        dialog = ttk.Toplevel(self)
        try:
            dialog.withdraw()
        except Exception:
            pass
        apply_app_icon(dialog)
        dialog.title(i18n.t('help_content_search_title'))
        dialog.geometry("840x360")
        dialog.resizable(True, True)
        try:
            dialog.transient(self)
        except Exception:
            pass
        dialog.grab_set()

        try:
            dialog.update_idletasks()
            x = self.winfo_rootx() + (self.winfo_width() // 2) - (840 // 2)
            y = self.winfo_rooty() + (self.winfo_height() // 2) - (360 // 2)
            dialog.geometry(f"840x360+{max(0, x)}+{max(0, y)}")
        except Exception:
            pass

        main = ttk.Frame(dialog, padding=15)
        main.pack(fill="both", expand=True)

        title_lbl = ttk.Label(
            main,
            text=i18n.t('help_content_search_title'),
            bootstyle="info",
            font=("Segoe UI", 11, "bold")
        )
        title_lbl.pack(anchor="w", pady=(0, 10))

        msg = ttk.Label(
            main,
            text=i18n.t('help_content_search_text'),
            justify="left",
            anchor="w"
        )
        msg.pack(fill="both", expand=True, anchor="w")

        def _update_wrap(_event=None):
            try:
                msg.configure(wraplength=max(360, main.winfo_width() - 24))
            except Exception:
                pass

        main.bind("<Configure>", _update_wrap, add="+")
        _update_wrap()

        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill="x", pady=(12, 0))

        ok_btn = ttk.Button(btn_frame, text=i18n.t('ok'), command=dialog.destroy, bootstyle="secondary")
        ok_btn.pack(side="right")

        def _update_language():
            dialog.title(i18n.t('help_content_search_title'))
            title_lbl.config(text=i18n.t('help_content_search_title'))
            msg.config(text=i18n.t('help_content_search_text'))
            ok_btn.config(text=i18n.t('ok'))

        dialog.update_language = _update_language
        dialog.on_ui_changed = lambda kind: _update_language() if kind == 'language' else None
        dialog.bind("<Return>", lambda e: dialog.destroy())
        dialog.bind("<Escape>", lambda e: dialog.destroy())

        try:
            dialog.deiconify()
            dialog.lift()
            dialog.focus_force()
        except Exception:
            pass

    def _reload_current_page(self):
        q_raw = self._current_query_text()
        if q_raw:
            self.search(reset=False)
            return

        if isinstance(self.last_query, dict) and self.last_query.get('kind') == 'custom':
            mode = self.last_query.get('mode', 'fs')
            query = self.last_query.get('query', '') or ''
            filters = self.get_search_filters()
            only_present = self.only_present.get()
            if mode == 'content':
                rows, total = search_content(
                    self.con,
                    query,
                    only_present=only_present,
                    limit=self.limit,
                    offset=self.offset,
                    filters=filters,
                )
            else:
                rows, total = search_fs(
                    self.con,
                    query,
                    only_present=only_present,
                    limit=self.limit,
                    offset=self.offset,
                    filters=filters,
                )
            self._apply_custom_rows(rows, total, mode, query)
            return

        if self.last_query and not isinstance(self.last_query, dict):
            sql, params = self.last_query
        else:
            sql, params = self._base_sql()
        self.load_rows(sql, params, reset_offset=False)

    def _selected_fullpath(self):
        iid = self.selected_row_id()
        if not iid:
            return None
        meta = self.row_meta.get(iid, {})
        fullpath = meta.get('fullpath')
        if fullpath:
            return fullpath
        try:
            values = self.tree.item(iid, 'values')
            return values[7] if len(values) > 7 else values[6]
        except Exception:
            return None

    def _run_background_custom_search(self, mode: str, q_raw: str, deliver_rows):
        filters = self.get_search_filters()
        only_present = self.only_present.get()
        limit = self.limit
        offset = self.offset

        def _worker():
            con = None
            try:
                con = sqlite3.connect(self.db_path)
                con.row_factory = sqlite3.Row
                if mode == 'content':
                    rows, total = search_content(con, q_raw, only_present=only_present, limit=limit, offset=offset, filters=filters)
                else:
                    rows, total = search_fs(con, q_raw, only_present=only_present, limit=limit, offset=offset, filters=filters)

                def _deliver_success():
                    if not self._ui_alive():
                        return
                    deliver_rows(rows, total)

                self._safe_after(0, _deliver_success)
            except Exception as e:
                def _deliver_error(err=e):
                    if not self.winfo_exists() or getattr(self, '_closing', False):
                        return
                    self._search_failed(err)
                self._safe_after(0, _deliver_error)
            finally:
                try:
                    if con is not None:
                        con.close()
                except Exception:
                    pass

        threading.Thread(target=_worker, daemon=True).start()

    def _update_empty_state_wrap(self):
        try:
            if self.empty_state_label is not None:
                self.empty_state_label.configure(wraplength=max(280, self.tree.winfo_width() - 80))
        except Exception:
            pass

    def _apply_empty_state_style(self, bootstyle: str = 'secondary'):
        try:
            if self.empty_state_label is None:
                return

            def _hex_to_rgb(color: str):
                try:
                    r, g, b = self.winfo_rgb(color)
                    return (r // 256, g // 256, b // 256)
                except Exception:
                    return (43, 43, 43)

            def _rgb_to_hex(rgb):
                return '#%02x%02x%02x' % rgb

            def _mix(c1, c2, ratio: float):
                ratio = max(0.0, min(1.0, ratio))
                return tuple(int(round(c1[i] * (1.0 - ratio) + c2[i] * ratio)) for i in range(3))

            def _luminance(rgb):
                vals = []
                for c in rgb:
                    c = c / 255.0
                    vals.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
                return 0.2126 * vals[0] + 0.7152 * vals[1] + 0.0722 * vals[2]

            style = ttk.Style()
            tree_bg = style.lookup('ViewerSearch.Treeview', 'fieldbackground') or style.lookup('Treeview', 'fieldbackground') or self.tree.cget('background') or '#2b2b2b'
            base = _hex_to_rgb(tree_bg)
            is_dark = _luminance(base) < 0.45

            font = ("Segoe UI", 10)
            if bootstyle == 'danger':
                font = ("Segoe UI", 11, "bold")
            elif bootstyle == 'info':
                font = ("Segoe UI", 10, "bold")
            else:
                font = ("Segoe UI", 10, "bold")

            if is_dark:
                bg = _rgb_to_hex(_mix(base, (255, 255, 255), 0.12))
                border = _rgb_to_hex(_mix(base, (255, 255, 255), 0.32))
                fg = '#f8f9fa'
                if bootstyle == 'danger':
                    bg = _rgb_to_hex(_mix(base, (110, 20, 20), 0.55))
                    border = '#d67a7a'
                    fg = '#fff1f1'
                elif bootstyle == 'info':
                    bg = _rgb_to_hex(_mix(base, (25, 70, 120), 0.45))
                    border = '#8fc2ff'
                    fg = '#f3f9ff'
            else:
                bg = _rgb_to_hex(_mix(base, (0, 0, 0), 0.10))
                border = _rgb_to_hex(_mix(base, (0, 0, 0), 0.28))
                fg = '#111111'
                if bootstyle == 'danger':
                    bg = '#fdeaea'
                    border = '#c95c5c'
                    fg = '#5f1111'
                elif bootstyle == 'info':
                    bg = '#eaf4ff'
                    border = '#4f8ecf'
                    fg = '#12324d'

            self.empty_state_label.configure(
                font=font,
                bg=bg,
                fg=fg,
                bd=1,
                relief='solid',
                highlightthickness=1,
                highlightbackground=border,
                highlightcolor=border,
            )
        except Exception:
            pass

    def _show_empty_state(self, message: str, bootstyle: str = 'secondary'):
        try:
            self.empty_state_var.set(message or "")
            self.empty_state_bootstyle = bootstyle or 'secondary'
            if self.empty_state_label is not None:
                try:
                    self._apply_empty_state_style(self.empty_state_bootstyle)
                except Exception:
                    pass
                self._update_empty_state_wrap()
                self.empty_state_label.lift()
                self.empty_state_label.place(relx=0.5, rely=0.5, anchor="center")
        except Exception:
            pass

    def _hide_empty_state(self):
        try:
            self.empty_state_var.set("")
            if self.empty_state_label is not None:
                self.empty_state_label.place_forget()
        except Exception:
            pass

    def _schedule_size_filter_refresh(self, delay_ms: int = 350):
        try:
            pending = getattr(self, '_size_filter_after_id', None)
            if pending:
                self.after_cancel(pending)
        except Exception:
            pass

        def _run():
            self._size_filter_after_id = None
            try:
                if getattr(self, '_closing', False):
                    return
                self.refresh_view()
            except Exception:
                pass

        try:
            self._size_filter_after_id = self.after(delay_ms, _run)
        except Exception:
            self._size_filter_after_id = None

    def _on_size_filter_var_changed(self, *_args):
        self._schedule_size_filter_refresh()

    def get_search_filters(self) -> dict:
        kind = (self.kind_var.get() or '').strip()
        if kind == i18n.t('item_kind_files'):
            item_kind = 'files'
        elif kind == i18n.t('item_kind_folders'):
            item_kind = 'folders'
        else:
            item_kind = 'all'
        return {
            'item_kind': item_kind,
            'ext': self._normalize_ext_value(self.ext_var.get()),
            'size_min': (self.size_min_var.get() or '').strip(),
            'size_max': (self.size_max_var.get() or '').strip(),
            'date_from': (self.date_from_var.get() or '').strip(),
            'date_to': (self.date_to_var.get() or '').strip(),
        }

    def clear_filters(self):
        self.kind_var.set(i18n.t('item_kind_all'))
        self.ext_var.set(self._all_extensions_label())
        for var in (self.size_min_var, self.size_max_var, self.date_from_var, self.date_to_var):
            var.set('')
        self._sync_filter_states()
        self.refresh_view()

    def _mark_symbol(self, checked: bool) -> str:
        return "☑" if checked else "☐"

    def _set_mark_visual(self, iid: str, checked: bool):
        try:
            vals = list(self.tree.item(iid, "values"))
            if vals:
                vals[0] = self._mark_symbol(checked)
                self.tree.item(iid, values=vals)
        except Exception:
            pass

    def _toggle_mark(self, iid: str):
        if not iid:
            return
        meta = self.row_meta.get(iid, {})
        fullpath = meta.get('fullpath')
        if iid in self.checked_items:
            self.checked_items.discard(iid)
            if fullpath:
                self.checked_paths.discard(fullpath)
            self._set_mark_visual(iid, False)
        else:
            self.checked_items.add(iid)
            if fullpath:
                self.checked_paths.add(fullpath)
            self._set_mark_visual(iid, True)
        self._update_marked_count_label()

    def _on_tree_click(self, event=None):
        try:
            region = self.tree.identify("region", event.x, event.y)
            col = self.tree.identify_column(event.x)
            iid = self.tree.identify_row(event.y)
            if region == "cell" and col == "#1" and iid:
                self._toggle_mark(iid)
                return "break"
        except Exception:
            return None
        return None

    def _checked_or_selected_iids(self):
        visible_checked = [iid for iid in self.tree.get_children() if iid in self.checked_items]
        return visible_checked or list(self.tree.selection())

    def _marked_count(self) -> int:
        try:
            if self.checked_paths:
                return len(self.checked_paths)
            return len(self.checked_items)
        except Exception:
            return 0

    def _update_marked_count_label(self):
        try:
            self.marked_count_label.config(text=i18n.t('marked_count').format(count=self._marked_count()))
        except Exception:
            pass

    def _fetch_all_fullpaths_for_current_query(self):
        query = getattr(self, 'last_query', None)
        cur = self.con.cursor()
        paths = []
        seen = set()
        try:
            if isinstance(query, tuple) and len(query) == 2:
                sql, params = query
                rows = cur.execute(sql, params).fetchall()
            elif isinstance(query, dict) and query.get('kind') == 'custom':
                mode = query.get('mode', 'fs')
                q = query.get('query', '') or ''
                filters = self.get_search_filters()
                only_present = self.only_present.get()
                limit = max(int(getattr(self, 'last_count', 0) or 0), int(getattr(self, 'limit', 0) or 0), 1)
                if mode == 'content':
                    rows, _ = search_content(self.con, q, only_present=only_present, limit=limit, offset=0, filters=filters)
                else:
                    rows, _ = search_fs(self.con, q, only_present=only_present, limit=limit, offset=0, filters=filters)
            else:
                rows = []
        except Exception:
            rows = []
        for r in rows:
            try:
                fullpath = r['fullpath']
            except Exception:
                fullpath = None
            if fullpath and fullpath not in seen:
                seen.add(fullpath)
                paths.append(fullpath)
        return paths

    def mark_all_visible(self):
        self._apply_checked_state(self._visible_fullpaths(), True)
        self._update_marked_count_label()

    def mark_all_pages(self):
        self._apply_checked_state(self._fetch_all_fullpaths_for_current_query(), True)
        self._update_marked_count_label()

    def unmark_all_visible(self):
        paths = self._fetch_all_fullpaths_for_current_query()
        if not paths:
            paths = self._visible_fullpaths()
        self._apply_checked_state(paths, False)
        self._update_marked_count_label()

    def collect_selected_files(self):
        selected_paths = []
        if self.checked_paths:
            selected_paths = list(self.checked_paths)
        else:
            sels = self._checked_or_selected_iids()
            if not sels:
                Messagebox.show_info(i18n.t('collect_files_none_selected'), i18n.t('collect_files_title'), parent=self)
                return
            for iid in sels:
                meta = self.row_meta.get(iid, {})
                src = meta.get("fullpath")
                if src:
                    selected_paths.append(src)
        dst = askdirectory_custom(self, title=i18n.t('collect_files_choose_dir'))
        if not dst:
            return
        import shutil as _shutil
        copied = 0
        skipped = 0
        for src in selected_paths:
            if not src or not os.path.isfile(src):
                skipped += 1
                continue
            base_name = os.path.basename(src)
            target = os.path.join(dst, base_name)
            if os.path.exists(target):
                stem, ext = os.path.splitext(base_name)
                n = 1
                while True:
                    candidate = os.path.join(dst, f"{stem} ({n}){ext}")
                    if not os.path.exists(candidate):
                        target = candidate
                        break
                    n += 1
            try:
                _shutil.copy2(src, target)
                copied += 1
            except Exception:
                skipped += 1
        Messagebox.show_info(i18n.t('collect_files_result').format(copied=copied, skipped=skipped), i18n.t('collect_files_title'), parent=self)

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

        if self._mode_is_content():
            if reset_offset:
                self.offset = 0
            self._apply_custom_rows([], 0, 'content', '')
            return

        if self._selected_set_id() is None:
            if reset_offset:
                self.offset = 0
            rows, total = search_fs(self.con, '', only_present=self.only_present.get(), limit=self.limit, offset=self.offset, filters=self.get_search_filters())
            self._apply_custom_rows(rows, total, 'fs', '')
            return

        sql, params = self._base_sql()
        self.load_rows(sql, params, reset_offset=reset_offset)

    def search(self, reset: bool):
        """Run search in selected mode."""
        q_raw = self._current_query_text()
        if not q_raw:
            self.reset()
            return

        if reset:
            self.offset = 0

        mode = 'content' if self._mode_is_content() else 'fs'

        if mode == 'fs' and self._selected_set_id() is not None:
            return self._search_legacy_set(reset=False, q_raw=q_raw)

        self.show_search_progress()
        try:
            if mode == 'content':
                self._show_empty_state('Идёт поиск по содержимому...', bootstyle='info')
                self.progress_dialog.title('Поиск по содержимому')
                self.progress_title_label.config(text='Идёт поиск по содержимому...')
                self.progress_label.config(text=f"Обрабатываем запрос:\n'{q_raw}'\n\nЭто может занять немного времени.")
            else:
                self.progress_label.config(text=f"'{q_raw}'")
        except Exception:
            pass
        self.update_idletasks()

        self._run_background_custom_search(
            mode,
            q_raw,
            lambda rows, total: self._apply_custom_rows(rows, total, mode, q_raw),
        )

    def _search_legacy_set(self, reset: bool, q_raw: str):
        if reset:
            self.offset = 0
        base_sql, base_params = self._base_sql()
        base_sql_no_order = re.sub(r"\s+ORDER\s+BY\s+[\s\S]*$", "", base_sql, flags=re.IGNORECASE)
        q_escaped = self._escape_like(q_raw)
        like_raw = f"%{q_escaped}%"
        q_norm = self._norm_for_search(q_raw)
        like_norm = f"%{self._escape_like(q_norm)}%" if q_norm else like_raw
        n_name = "PY_NORM(name)"
        n_rel  = "PY_NORM(relpath)"
        n_full = "PY_NORM(fullpath)"
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
        sql = f"SELECT *, ({score_expr}) AS _score FROM ({base_sql_no_order}) WHERE {where_clause} ORDER BY _score DESC, name COLLATE NOCASE ASC"
        params = [like_raw, like_raw, like_raw, like_norm, like_norm, like_norm] + list(base_params) + [like_raw, like_raw, like_raw, like_norm, like_norm, like_norm]
        self.show_search_progress()
        try:
            self.progress_title_label.config(text='Идёт поиск...')
            self.progress_label.config(text=f"Обрабатываем запрос:\n'{q_raw}'")
        except Exception:
            pass
        self.update_idletasks()

        def _worker():
            try:
                con = sqlite3.connect(self.db_path)
                con.row_factory = sqlite3.Row
                con.create_function('PY_NORM', 1, Viewer._py_norm_sql)
                cur = con.cursor()
                count_sql = f"SELECT COUNT(1) AS c FROM ({sql})"
                total = cur.execute(count_sql, params).fetchone()["c"]
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
                self._safe_after(0, _deliver_error)

        threading.Thread(target=_worker, daemon=True).start()

    def _apply_custom_rows(self, rows: list, total: int, mode: str, query: str):
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
        self._refresh_result_headers()
        self.clear()
        self.last_query = {"kind": "custom", "mode": mode, "query": query}
        self.last_count = int(total or 0)

        self._show_empty_content_hint_if_needed(mode, query, total)

        for r in rows:
            keys = set(r.keys()) if hasattr(r, 'keys') else set()
            size = self.format_size(r["size_bytes"]) if "size_bytes" in keys else ""
            mtime = self.format_mtime(r["mtime"]) if "mtime" in keys else ""
            present = "✓" if int((r["is_present"] if "is_present" in keys else 0) or 0) == 1 else ""
            st_code = r["status"] if "status" in keys else ""
            if mode == 'content':
                st = self._translate_content_source((r["content_source"] if "content_source" in keys else "") or st_code or "")
                display_path = (r["snippet"] if "snippet" in keys else "") or ""
            else:
                item_type = (r["item_type"] if "item_type" in keys else "FILE")
                st = i18n.t('item_type_folder') if item_type == 'FOLDER' else i18n.t('item_type_file')
                display_path = r["fullpath"]
            fullpath = r["fullpath"]
            is_marked = bool(fullpath and fullpath in self.checked_paths)
            iid = self.tree.insert("", "end", values=(self._mark_symbol(is_marked), r["name"], r["relpath"], size, mtime, present, st, display_path))
            if is_marked:
                self.checked_items.add(iid)
            self.row_meta[iid] = {
                "status": st_code,
                "fullpath": fullpath,
                "set_item_id": r["set_item_id"] if "set_item_id" in keys else None,
                "raw_path": r["raw_path"] if "raw_path" in keys else None,
                "item_type": r["item_type"] if "item_type" in keys else "FILE",
            }
        self.update_page_label()

    def _show_empty_content_hint_if_needed(self, mode: str, query: str, total: int):
        if mode != 'content' or int(total or 0) != 0 or not (query or '').strip():
            return
        self._show_empty_state(i18n.t('content_search_no_results_message'), bootstyle='secondary')

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

        self._refresh_result_headers()
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
            fullpath = r["fullpath"]
            is_marked = bool(fullpath and fullpath in self.checked_paths)
            iid = self.tree.insert("", "end", values=(self._mark_symbol(is_marked), r["name"], r["relpath"], size, mtime, present, st, fullpath))
            if is_marked:
                self.checked_items.add(iid)
            self.row_meta[iid] = {
                "status": st_code,
                "fullpath": fullpath,
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
        if self._mode_is_content():
            key = 'search_failed_content_invalid' if isinstance(err, ContentSearchQueryError) else 'search_failed_content'
            msg = i18n.t(key)
            try:
                self.clear()
                self._show_empty_state(msg, bootstyle='danger')
            except Exception:
                pass
            return
        Messagebox.show_error(i18n.t('search_failed_generic'), i18n.t('error_title'), parent=self)


    def next_page(self):
        """Go to next page"""
        if self.offset + self.limit >= self.last_count:
            return
        self.offset += self.limit
        self._reload_current_page()

    def prev_page(self):
        """Go to previous page"""
        self.offset = max(0, self.offset - self.limit)
        self._reload_current_page()

    def first_page(self):
        """Go to first page"""
        self.offset = 0
        self._reload_current_page()

    def last_page(self):
        """Go to last page"""
        if self.last_count <= 0:
            return
        self.offset = ((self.last_count - 1) // self.limit) * self.limit
        self._reload_current_page()

    def selected_row_id(self):
        """Get selected row ID"""
        sel = self.tree.selection()
        return sel[0] if sel else None

    def reveal_selected(self):
        """Show selected file or folder in Explorer/Finder."""
        fullpath = self._selected_fullpath()
        if not fullpath:
            return
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

    def index_content(self):
        """Index document contents for current database."""
        if getattr(self, '_content_index_running', False):
            return
        self._content_index_running = True
        try:
            if hasattr(self.master, 'set_status'):
                self.master.set_status(f"{i18n.t('index_docs_title')}…")
        except Exception:
            pass
        self.show_search_progress()
        try:
            self.progress_dialog.title(i18n.t('index_docs_title'))
            self.progress_label.config(text=i18n.t('index_docs_prepare'))
        except Exception:
            pass

        def _status_cb(info):
            file = info.get('file') or ''
            processed = int(info.get('processed', 0) or 0)
            total = int(info.get('total', 0) or 0)
            text = f"{processed}/{total}\n{os.path.basename(file)}" if file else f"{processed}/{total}"
            status_text = f"{i18n.t('index_docs_title')}: {processed}/{total}" if total else f"{i18n.t('index_docs_title')}…"
            def _update_status(t=text, s=status_text):
                try:
                    if getattr(self, 'progress_label', None):
                        self.progress_label.config(text=t)
                except Exception:
                    pass
                try:
                    if hasattr(self.master, 'set_status'):
                        self.master.set_status(s)
                except Exception:
                    pass
            self._safe_after(0, _update_status)

        def _worker():
            try:
                mode_map = {i18n.t('index_mode_changed'): 'changed', i18n.t('index_mode_all'): 'all', i18n.t('index_mode_errors'): 'errors'}
                stats = index_document_contents(self.db_path, status_cb=_status_cb, mode=mode_map.get(self.reindex_mode_var.get(), 'changed'))
                def _done():
                    self._content_index_running = False
                    self.hide_search_progress()
                    self._refresh_search_mode_availability()
                    try:
                        if hasattr(self.master, 'set_status'):
                            self.master.set_status(i18n.t('status_ready'))
                    except Exception:
                        pass
                    Messagebox.show_info(
                        i18n.t('index_docs_summary').format(
                            processed=stats.get('processed', 0),
                            ok=stats.get('ok', 0),
                            errors=stats.get('errors', 0),
                        ),
                        i18n.t('index_docs_title'),
                        parent=self
                    )
                self._safe_after(0, _done)
            except Exception as e:
                def _err(err=e):
                    self._content_index_running = False
                    self.hide_search_progress()
                    try:
                        if hasattr(self.master, 'set_status'):
                            self.master.set_status(i18n.t('error'))
                    except Exception:
                        pass
                    Messagebox.show_error(str(err), i18n.t('error'), parent=self)
                self._safe_after(0, _err)

        threading.Thread(target=_worker, daemon=True).start()

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
        out = asksaveasfilename_custom(self, 
            title=i18n.t('export_csv'),
            defaultextension=".csv",
            filetypes=[(i18n.t('csv_filetype'), "*.csv"), (i18n.t('filetype_all'), "*.*")]
        )
        if not out:
            return

        export_mode = None
        export_query = None
        if isinstance(self.last_query, dict) and self.last_query.get('kind') == 'custom':
            export_mode = self.last_query.get('mode')
            export_query = self.last_query.get('query')
            sql = params = None
        elif self.last_query:
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
                if export_mode == 'content':
                    rows, _ = search_content(con, export_query or '', only_present=self.only_present.get(), limit=max(self.last_count, self.limit, 1), offset=0, filters=self.get_search_filters())
                elif export_mode == 'fs':
                    rows, _ = search_fs(con, export_query or '', only_present=self.only_present.get(), limit=max(self.last_count, self.limit, 1), offset=0, filters=self.get_search_filters())
                else:
                    rows = con.execute(sql, params).fetchall()
                with open(out, "w", newline="", encoding="utf-8") as f:
                    w = csv.writer(f, delimiter=";")
                    w.writerow([i18n.t('header_name'), i18n.t('header_relpath'), i18n.t('header_fullpath'), 
                               i18n.t('header_size'), i18n.t('header_mtime'), i18n.t('header_present'), i18n.t('header_status')])
                    for r in rows:
                        keys = set(r.keys()) if hasattr(r, 'keys') else set()
                        status_val = r["status"] if "status" in keys else ""
                        if export_mode == 'fs' and "item_type" in keys:
                            status_val = i18n.t('item_type_folder') if r['item_type'] == 'FOLDER' else i18n.t('item_type_file')
                        if export_mode == 'content' and "content_source" in keys:
                            status_val = self._translate_content_source(r['content_source'] or status_val)
                        full_display = r["fullpath"]
                        if export_mode == 'content' and "snippet" in keys and r["snippet"]:
                            full_display = r["snippet"]
                        w.writerow([
                            r["name"], r["relpath"], full_display,
                            r["size_bytes"] if ("size_bytes" in keys and r["size_bytes"] is not None) else "",
                            r["mtime"] if ("mtime" in keys and r["mtime"] is not None) else "",
                            int((r["is_present"] if "is_present" in keys else 0) or 0),
                            status_val or ""
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
            popup = getattr(self, '_ext_popup', None)
            if popup is not None:
                popup.destroy()
        except Exception:
            pass
        try:
            self.con.close()
        except Exception:
            pass
        super().destroy()
