import os
import sqlite3
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import time
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from core.i18n import i18n
from core.ui_common import apply_app_icon
from core.shell import reveal_in_folder
from gui.widgets import CustomDialog, CustomMessagebox as Messagebox, ToolTip, Spinner

class ResolveDialog(ttk.Toplevel):
    """Dialog for resolving ambiguous file matches"""
    
    def __init__(self, parent, con: sqlite3.Connection, set_item_id: int, raw_path: str):
        super().__init__(parent)
        try:
            self.withdraw()
        except Exception:
            pass
        apply_app_icon(self)
        self.title(i18n.t('resolve_title'))
        self.geometry("950x520")
        try:
            self.transient(parent)
        except Exception:
            pass
        self.grab_set()

        self.con = con
        self.set_item_id = set_item_id
        self.raw_path = raw_path
        self.choice = None  # (file_id, fullpath)

        filename = os.path.basename(raw_path)

        # Header
        header = ttk.Frame(self)
        header.pack(fill="x", padx=15, pady=15)

        self.original_path_label = ttk.Label(header, text=i18n.t('original_path'), font=("Segoe UI", 10, "bold"))
        self.original_path_label.pack(anchor="w")
        
        path_entry = ttk.Entry(header, width=120, state="readonly")
        path_entry.pack(fill="x", pady=(4, 10))
        path_entry.insert(0, raw_path)

        self.candidates_label = ttk.Label(header, text=f"{i18n.t('candidates')}{filename}", 
                 font=("Segoe UI", 10, "bold"))
        self.candidates_label.pack(anchor="w")

        # Treeview for candidates
        cols = ("fullpath", "size", "mtime")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=14, bootstyle="primary")
        
        self.tree.heading("fullpath", text=i18n.t("header_fullpath"))
        self.tree.heading("size", text=i18n.t("header_size"))
        self.tree.heading("mtime", text=i18n.t("header_mtime"))
        
        self.tree.column("fullpath", width=720, anchor="w")
        self.tree.column("size", width=90, anchor="e")
        self.tree.column("mtime", width=120, anchor="w")
        
        self.tree.pack(fill="both", expand=True, padx=15, pady=(6, 10))

        self._id_by_iid = {}

        def fmt_size(n):
            if n is None:
                return ""
            n = int(n)
            for unit in (i18n.t('size_unit_b'), i18n.t('size_unit_kb'), i18n.t('size_unit_mb'), i18n.t('size_unit_gb'), i18n.t('size_unit_tb')):
                if n < 1024:
                    return f"{n} {unit}"
                n //= 1024
            return f"{n} {i18n.t('size_unit_pb')}"

        def fmt_mtime(ts):
            if ts is None:
                return ""
            try:
                return time.strftime(i18n.t('datetime_format'), time.localtime(int(ts)))
            except Exception:
                return ""

        rows = self.con.execute(
            "SELECT id, fullpath, size_bytes, mtime FROM files WHERE name=? AND is_present=1 ORDER BY fullpath LIMIT 500;",
            (filename,)
        ).fetchall()

        for r in rows:
            iid = self.tree.insert("", "end", values=(r["fullpath"], fmt_size(r["size_bytes"]), fmt_mtime(r["mtime"])))
            self._id_by_iid[iid] = (int(r["id"]), str(r["fullpath"]))

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.reveal_btn = ttk.Button(btn_frame, text=i18n.t('show_in_folder'), 
                  command=self.reveal_selected,
                  bootstyle="info-outline")
        self.reveal_btn.pack(side="left")
        
        self.select_btn = ttk.Button(btn_frame, text=i18n.t('select_save'), 
                  command=self.save_selected,
                  bootstyle="success")
        self.select_btn.pack(side="left", padx=8)
        
        self.cancel_btn = ttk.Button(btn_frame, text=i18n.t('cancel'), 
                  command=self.destroy,
                  bootstyle="secondary")
        self.cancel_btn.pack(side="right")

        self.tree.bind("<Double-1>", lambda e: self.save_selected())

        try:
            self.update_idletasks()
            w, h = 950, 520
            x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (w // 2)
            y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (h // 2)
            self.geometry(f"{w}x{h}+{max(0, x)}+{max(0, y)}")
        except Exception:
            pass

        try:
            self.deiconify()
            self.lift()
            self.focus_force()
        except Exception:
            try:
                self.deiconify()
            except Exception:
                pass

        if not rows:
            Messagebox.show_warning(i18n.t('no_candidates_msg'), i18n.t('warning'))


    def update_language(self):
        """Refresh dialog texts after a live language switch."""
        filename = os.path.basename(self.raw_path)
        self.title(i18n.t('resolve_title'))
        self.original_path_label.config(text=i18n.t('original_path'))
        self.candidates_label.config(text=f"{i18n.t('candidates')}{filename}")
        self.tree.heading('fullpath', text=i18n.t('header_fullpath'))
        self.tree.heading('size', text=i18n.t('header_size'))
        self.tree.heading('mtime', text=i18n.t('header_mtime'))
        self.reveal_btn.config(text=i18n.t('show_in_folder'))
        self.select_btn.config(text=i18n.t('select_save'))
        self.cancel_btn.config(text=i18n.t('cancel'))

    def reveal_selected(self):
        """Show selected file in folder"""
        sel = self.tree.selection()
        if not sel:
            return
        _file_id, fullpath = self._id_by_iid.get(sel[0], (None, None))
        if fullpath:
            reveal_in_folder(fullpath, parent=self)

    def save_selected(self):
        """Save selected file as resolution"""
        sel = self.tree.selection()
        if not sel:
            Messagebox.show_warning(i18n.t('no_selection_msg'), i18n.t('warning'))
            return
        file_id, fullpath = self._id_by_iid.get(sel[0], (None, None))
        if file_id is None:
            return

        now = int(time.time())
        self.con.execute(
            "UPDATE set_items SET file_id=?, resolved_path=?, status='FOUND', note='manual_resolve', updated_at=? WHERE id=?;",
            (file_id, fullpath, now, self.set_item_id)
        )
        self.con.commit()
        self.choice = (file_id, fullpath)
        self.destroy()


class FolderSelectionDialog(ttk.Toplevel):
    """Single-window dialog for choosing multiple folders for indexing."""

    def __init__(self, parent, initial_folders=None):
        super().__init__(parent)
        try:
            self.withdraw()
        except Exception:
            pass
        apply_app_icon(self)
        self.parent = parent
        self.result = None
        self._seen = set()
        self._folders = []
        self.title(i18n.t('choose_scan_folders_title'))
        self.geometry('760x420')
        try:
            self.transient(parent)
        except Exception:
            pass
        self.grab_set()

        main = ttk.Frame(self, padding=15)
        main.pack(fill='both', expand=True)

        self.prompt_label = ttk.Label(main, text=i18n.t('multi_folder_prompt'), justify='left', anchor='w')
        self.prompt_label.pack(fill='x')

        list_frame = ttk.Frame(main)
        list_frame.pack(fill='both', expand=True, pady=(10, 12))

        self.folders_label = ttk.Label(list_frame, text=i18n.t('selected_folders_label'), font=('Segoe UI', 10, 'bold'))
        self.folders_label.pack(anchor='w', pady=(0, 6))

        body = ttk.Frame(list_frame)
        body.pack(fill='both', expand=True)

        self.listbox = tk.Listbox(body, activestyle='dotbox', exportselection=False)
        self.listbox.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(body, orient='vertical', command=self.listbox.yview)
        scrollbar.pack(side='left', fill='y', padx=(8, 0))
        self.listbox.configure(yscrollcommand=scrollbar.set)
        self.listbox.bind('<<ListboxSelect>>', lambda e: self._refresh_buttons())
        self.listbox.bind('<Delete>', lambda e: self.remove_selected())
        self.listbox.bind('<Double-1>', lambda e: self.remove_selected())

        buttons = ttk.Frame(main)
        buttons.pack(fill='x')

        self.btn_add = ttk.Button(buttons, text=i18n.t('btn_add_folder'), command=self.add_folder, bootstyle='primary')
        self.btn_add.pack(side='left')
        self.btn_remove = ttk.Button(buttons, text=i18n.t('btn_remove_selected_folder'), command=self.remove_selected, bootstyle='secondary')
        self.btn_remove.pack(side='left', padx=(8, 0))
        self.btn_clear = ttk.Button(buttons, text=i18n.t('btn_clear_folders'), command=self.clear_folders, bootstyle='secondary-outline')
        self.btn_clear.pack(side='left', padx=(8, 0))

        self.count_label = ttk.Label(buttons, text='')
        self.count_label.pack(side='right')

        actions = ttk.Frame(main)
        actions.pack(fill='x', pady=(14, 0))
        self.btn_ok = ttk.Button(actions, text=i18n.t('btn_start_scan'), command=self.confirm, bootstyle='success')
        self.btn_ok.pack(side='right')
        self.btn_cancel = ttk.Button(actions, text=i18n.t('cancel'), command=self.cancel, bootstyle='secondary')
        self.btn_cancel.pack(side='right', padx=(0, 8))

        for folder in initial_folders or []:
            self._add_folder(folder)
        self._refresh_buttons()

        try:
            self.update_idletasks()
            w, h = 760, 420
            x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (w // 2)
            y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (h // 2)
            self.geometry(f"{w}x{h}+{max(0, x)}+{max(0, y)}")
        except Exception:
            pass

        try:
            self.deiconify()
            self.lift()
            self.focus_force()
        except Exception:
            try:
                self.deiconify()
            except Exception:
                pass

        if not self._folders:
            self.after(50, self.add_folder)

    def _normalize(self, folder: str) -> str:
        return os.path.normcase(os.path.abspath(folder))

    def _add_folder(self, folder: str) -> bool:
        folder = (folder or '').strip()
        if not folder:
            return False
        abspath = os.path.abspath(folder)
        norm = self._normalize(abspath)
        if norm in self._seen:
            return False
        self._seen.add(norm)
        self._folders.append(abspath)
        self.listbox.insert('end', abspath)
        self._refresh_buttons()
        return True

    def _refresh_buttons(self):
        count = len(self._folders)
        selected = bool(self.listbox.curselection())
        try:
            self.count_label.config(text=i18n.t('selected_folders_count').format(count=count))
            self.btn_ok.config(state=('normal' if count else 'disabled'))
            self.btn_clear.config(state=('normal' if count else 'disabled'))
            self.btn_remove.config(state=('normal' if selected else 'disabled'))
        except Exception:
            pass

    def update_language(self):
        self.title(i18n.t('choose_scan_folders_title'))
        self.prompt_label.config(text=i18n.t('multi_folder_prompt'))
        self.folders_label.config(text=i18n.t('selected_folders_label'))
        self.btn_add.config(text=i18n.t('btn_add_folder'))
        self.btn_remove.config(text=i18n.t('btn_remove_selected_folder'))
        self.btn_clear.config(text=i18n.t('btn_clear_folders'))
        self.btn_ok.config(text=i18n.t('btn_start_scan'))
        self.btn_cancel.config(text=i18n.t('cancel'))
        self._refresh_buttons()

    def add_folder(self):
        folder = askdirectory_custom(self, title=i18n.t('choose_scan_folders_title'))
        if folder:
            added = self._add_folder(folder)
            if not added:
                Messagebox.show_info(i18n.t('folder_already_added'), i18n.t('choose_scan_folders_title'), parent=self)
            else:
                try:
                    idx = len(self._folders) - 1
                    self.listbox.selection_clear(0, 'end')
                    self.listbox.selection_set(idx)
                    self.listbox.see(idx)
                except Exception:
                    pass
        self._refresh_buttons()

    def remove_selected(self):
        sel = list(self.listbox.curselection())
        if not sel:
            self._refresh_buttons()
            return
        for idx in reversed(sel):
            folder = self._folders.pop(idx)
            self._seen.discard(self._normalize(folder))
            self.listbox.delete(idx)
        self._refresh_buttons()

    def clear_folders(self):
        self._folders.clear()
        self._seen.clear()
        self.listbox.delete(0, 'end')
        self._refresh_buttons()

    def confirm(self):
        if not self._folders:
            Messagebox.show_warning(i18n.t('no_scan_folders_selected'), i18n.t('warning'), parent=self)
            return
        self.result = list(self._folders)
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()


def choose_multiple_folders(parent, initial_folders=None):
    dialog = FolderSelectionDialog(parent, initial_folders=initial_folders)
    try:
        parent.wait_window(dialog)
    except Exception:
        pass
    return dialog.result or []


def simple_input(parent, title: str, prompt: str) -> str | None:
    """Simple input dialog"""
    dialog = ttk.Toplevel(parent)
    try:
        dialog.withdraw()
    except Exception:
        pass
    apply_app_icon(dialog)
    dialog.title(title)
    dialog.geometry("620x220")
    dialog.grab_set()

    # Center on parent
    dialog.transient(parent)
    dialog.update_idletasks()
    x = parent.winfo_x() + (parent.winfo_width() // 2) - (620 // 2)
    y = parent.winfo_y() + (parent.winfo_height() // 2) - (220 // 2)
    dialog.geometry(f"620x220+{max(0, x)}+{max(0, y)}")

    try:
        dialog.deiconify()
        dialog.lift()
        dialog.focus_force()
    except Exception:
        try:
            dialog.deiconify()
        except Exception:
            pass

    main = ttk.Frame(dialog, padding=15)
    main.pack(fill="both", expand=True)

    prompt_lbl = ttk.Label(main, text=prompt, font=("Segoe UI", 9), justify="left", anchor="w")
    prompt_lbl.pack(anchor="w", fill="x")
    try:
        prompt_lbl.configure(wraplength=560)
    except Exception:
        pass
    
    var = ttk.StringVar()
    entry = ttk.Entry(main, textvariable=var, width=60)
    entry.pack(fill="x", pady=(8, 15))
    entry.focus_set()

    result = {"value": None}

    def ok():
        v = var.get().strip()
        if not v:
            Messagebox.show_warning(i18n.t('set_name_empty'), i18n.t('set_name_title'), parent=dialog)
            try:
                entry.focus_set()
            except Exception:
                pass
            return
        result["value"] = v
        dialog.destroy()

    def cancel():
        result["value"] = None
        dialog.destroy()

    btn_frame = ttk.Frame(main)
    btn_frame.pack(fill="x")
    
    save_btn = ttk.Button(btn_frame, text=i18n.t('save'), command=ok, bootstyle="success")
    save_btn.pack(side="left")
    cancel_btn = ttk.Button(btn_frame, text=i18n.t('cancel'), command=cancel, bootstyle="secondary")
    cancel_btn.pack(side="left", padx=8)

    def _update_language():
        dialog.title(title)
        prompt_lbl.config(text=prompt)
        save_btn.config(text=i18n.t('save'))
        cancel_btn.config(text=i18n.t('cancel'))

    dialog.update_language = _update_language
    dialog.on_ui_changed = lambda kind: _update_language() if kind == 'language' else None

    dialog.bind("<Return>", lambda e: ok())
    dialog.bind("<Escape>", lambda e: cancel())

    parent.wait_window(dialog)
    return result["value"]


import fnmatch
from pathlib import Path as _Path


def _patterns_from_filetypes(filetypes):
    patterns = []
    for _label, spec in (filetypes or []):
        for part in str(spec).split():
            part = part.strip()
            if part:
                patterns.append(part)
    return patterns or ['*']


class PathChooserDialog(ttk.Toplevel):
    def __init__(self, parent, mode='open_file', title=None, initialdir=None, initialfile='', defaultextension='', filetypes=None):
        super().__init__(parent)
        try:
            self.withdraw()
        except Exception:
            pass
        apply_app_icon(self)
        self.parent = parent
        self.mode = mode
        self.result = None
        self.filetypes = filetypes or [(i18n.t('filetype_all'), '*.*')]
        self.patterns = _patterns_from_filetypes(self.filetypes)
        self.defaultextension = defaultextension or ''
        self.current_dir = _Path(initialdir or os.getcwd()).resolve()
        self.title(title or i18n.t('path_dialog_title'))
        self.geometry('860x560')
        try:
            self.transient(parent)
        except Exception:
            pass
        self.grab_set()

        main = ttk.Frame(self, padding=12)
        main.pack(fill='both', expand=True)
        
        top = ttk.Frame(main)
        top.pack(fill='x', pady=(0, 8))
        self.location_label = ttk.Label(top, text=i18n.t('path_dialog_location'))
        self.location_label.pack(side='left')
        self.path_var = ttk.StringVar(value=str(self.current_dir))
        self.path_entry = ttk.Entry(top, textvariable=self.path_var)
        self.path_entry.pack(side='left', fill='x', expand=True, padx=8)
        self.go_btn = ttk.Button(top, text=i18n.t('path_dialog_go'), command=self._go_to_path, bootstyle='secondary')
        self.go_btn.pack(side='left', padx=(0,6))
        self.up_btn = ttk.Button(top, text=i18n.t('path_dialog_up'), command=self._go_up, bootstyle='secondary')
        self.up_btn.pack(side='left')

        mid = ttk.Frame(main)
        mid.pack(fill='both', expand=True)
        cols = ('name','type')
        self.tree = ttk.Treeview(mid, columns=cols, show='headings', bootstyle='primary')
        self.tree.heading('name', text=i18n.t('path_dialog_name'))
        self.tree.heading('type', text=i18n.t('path_dialog_type'))
        self.tree.column('name', width=620, anchor='w')
        self.tree.column('type', width=120, anchor='w')
        ys = ttk.Scrollbar(mid, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=ys.set)
        self.tree.pack(side='left', fill='both', expand=True)
        ys.pack(side='right', fill='y')

        bottom = ttk.Frame(main)
        bottom.pack(fill='x', pady=(8,0))
        self.file_var = ttk.StringVar(value=initialfile or '')
        if self.mode != 'directory':
            self.bottom_label = ttk.Label(bottom, text=i18n.t('path_dialog_filename'))
            self.bottom_label.pack(side='left')
            self.file_entry = ttk.Entry(bottom, textvariable=self.file_var)
            self.file_entry.pack(side='left', fill='x', expand=True, padx=8)
        else:
            self.file_entry = None
            self.bottom_label = ttk.Label(bottom, text=i18n.t('path_dialog_current_folder'))
            self.bottom_label.pack(side='left')
            self.current_folder_value = ttk.Label(bottom, textvariable=self.path_var)
            self.current_folder_value.pack(side='left', fill='x', expand=True, padx=8)

        btns = ttk.Frame(main)
        btns.pack(fill='x', pady=(8,0))
        ok_text = i18n.t('open') if self.mode == 'open_file' else i18n.t('save') if self.mode == 'save_file' else i18n.t('select')
        self.ok_btn = ttk.Button(btns, text=ok_text, command=self._confirm, bootstyle='success')
        self.ok_btn.pack(side='left')
        self.cancel_btn = ttk.Button(btns, text=i18n.t('cancel'), command=self._cancel, bootstyle='secondary')
        self.cancel_btn.pack(side='right')

        self.tree.bind('<Double-1>', self._on_double)
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        self.path_entry.bind('<Return>', lambda e: self._go_to_path())
        if self.file_entry is not None:
            self.file_entry.bind('<Return>', lambda e: self._confirm())

        self._reload()
        try:
            self.update_idletasks()
            w, h = 860, 560
            x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (w // 2)
            y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (h // 2)
            self.geometry(f'{w}x{h}+{max(0,x)}+{max(0,y)}')
            self.deiconify(); self.lift(); self.focus_force()
        except Exception:
            try: self.deiconify()
            except Exception: pass


    def update_language(self):
        """Refresh chooser texts after a live language switch."""
        self.title(i18n.t('path_dialog_title'))
        self.location_label.config(text=i18n.t('path_dialog_location'))
        self.go_btn.config(text=i18n.t('path_dialog_go'))
        self.up_btn.config(text=i18n.t('path_dialog_up'))
        if getattr(self, 'bottom_label', None):
            if self.mode != 'directory':
                self.bottom_label.config(text=i18n.t('path_dialog_filename'))
            else:
                self.bottom_label.config(text=i18n.t('path_dialog_current_folder'))
        self.tree.heading('name', text=i18n.t('path_dialog_name'))
        self.tree.heading('type', text=i18n.t('path_dialog_type'))
        self.ok_btn.config(text=i18n.t('open') if self.mode == 'open_file' else i18n.t('save') if self.mode == 'save_file' else i18n.t('select'))
        self.cancel_btn.config(text=i18n.t('cancel'))
        self._reload()

    def _matches(self, name):
        return any(fnmatch.fnmatch(name.lower(), p.lower()) for p in self.patterns)

    def _reload(self):
        self.path_var.set(str(self.current_dir))
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        try:
            entries = sorted(self.current_dir.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        except Exception as e:
            Messagebox.show_error(str(e), i18n.t('error'), parent=self)
            return
        for item in entries:
            if item.is_dir():
                self.tree.insert('', 'end', values=(item.name, i18n.t('path_dialog_folder')), tags=('dir',))
            elif self.mode != 'directory' and self._matches(item.name):
                self.tree.insert('', 'end', values=(item.name, i18n.t('path_dialog_file')), tags=('file',))

    def _go_up(self):
        parent = self.current_dir.parent
        if parent != self.current_dir:
            self.current_dir = parent
            self._reload()

    def _go_to_path(self):
        p = _Path(self.path_var.get().strip())
        if p.exists() and p.is_dir():
            self.current_dir = p.resolve()
            self._reload()
        else:
            Messagebox.show_warning(i18n.t('path_dialog_invalid_folder'), i18n.t('warning'), parent=self)

    def _selected_name(self):
        sel = self.tree.selection()
        if not sel:
            return None, None
        iid = sel[0]
        vals = self.tree.item(iid, 'values')
        return (vals[0] if vals else None), set(self.tree.item(iid, 'tags'))

    def _on_select(self, _event=None):
        name, tags = self._selected_name()
        if not name:
            return
        if 'file' in tags and self.file_entry is not None:
            self.file_var.set(name)

    def _on_double(self, _event=None):
        name, tags = self._selected_name()
        if not name:
            return
        p = self.current_dir / name
        if 'dir' in tags:
            self.current_dir = p.resolve()
            self._reload()
        else:
            if self.mode == 'open_file':
                self.result = str(p)
                self.destroy()
            elif self.file_entry is not None:
                self.file_var.set(name)

    def _confirm(self):
        if self.mode == 'directory':
            self.result = str(self.current_dir)
            self.destroy()
            return
        name = (self.file_var.get() if self.file_entry is not None else '').strip()
        if not name:
            Messagebox.show_warning(i18n.t('path_dialog_no_file_name'), i18n.t('warning'), parent=self)
            return
        p = self.current_dir / name
        if self.mode == 'open_file':
            if not p.exists() or not p.is_file():
                Messagebox.show_warning(i18n.t('path_dialog_file_missing'), i18n.t('warning'), parent=self)
                return
            self.result = str(p)
            self.destroy()
            return
        if self.mode == 'save_file':
            if self.defaultextension and not p.suffix:
                p = p.with_suffix(self.defaultextension)
            self.result = str(p)
            self.destroy()
            return

    def _cancel(self):
        self.result = None
        self.destroy()


def _show_system_dialog_hint(parent, text, duration_ms=950):
    if not text:
        return
    try:
        host = parent if parent is not None and parent.winfo_exists() else None
    except Exception:
        host = None
    try:
        win = tk.Toplevel(host)
        win.withdraw()
        win.overrideredirect(True)
        try:
            win.transient(host)
        except Exception:
            pass
        try:
            win.attributes("-topmost", True)
        except Exception:
            pass

        frame = ttk.Frame(win, padding=(10, 8), bootstyle='info')
        frame.pack(fill='both', expand=True)
        lbl = ttk.Label(frame, text=text, justify='left', anchor='w')
        lbl.pack(fill='both', expand=True)

        win.update_idletasks()
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        ww = win.winfo_reqwidth()
        wh = win.winfo_reqheight()

        if host is not None:
            try:
                hx = host.winfo_rootx()
                hy = host.winfo_rooty()
                hw = max(1, host.winfo_width())
                x = hx + min(max(12, hw - ww - 24), 40)
                y = hy + 70
            except Exception:
                x = (sw - ww) // 2
                y = 80
        else:
            x = (sw - ww) // 2
            y = 80

        x = max(8, min(x, sw - ww - 8))
        y = max(8, min(y, sh - wh - 8))
        win.geometry(f"+{x}+{y}")
        win.deiconify()
        win.lift()
        win.update()
        time.sleep(max(0.15, duration_ms / 1000.0))
        try:
            win.destroy()
        except Exception:
            pass
    except Exception:
        pass


def _normalize_dialog_result(value):
    return value or ''


def askopenfilename_custom(parent, **kwargs):
    kwargs.pop('dialog_hint', None)
    result = filedialog.askopenfilename(parent=parent, **kwargs)
    return _normalize_dialog_result(result)


def asksaveasfilename_custom(parent, **kwargs):
    kwargs.pop('dialog_hint', None)
    result = filedialog.asksaveasfilename(parent=parent, **kwargs)
    return _normalize_dialog_result(result)


def askdirectory_custom(parent, **kwargs):
    kwargs.pop('dialog_hint', None)
    result = filedialog.askdirectory(parent=parent, **kwargs)
    return _normalize_dialog_result(result)
