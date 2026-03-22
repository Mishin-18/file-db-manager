import os
import sqlite3
from pathlib import Path
import time
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog

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

        ttk.Label(header, text=i18n.t('original_path'), font=("Segoe UI", 10, "bold")).pack(anchor="w")
        
        path_entry = ttk.Entry(header, width=120, state="readonly")
        path_entry.pack(fill="x", pady=(4, 10))
        path_entry.insert(0, raw_path)

        ttk.Label(header, text=f"{i18n.t('candidates')}{filename}", 
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")

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
            for unit in ("B", "KB", "MB", "GB", "TB"):
                if n < 1024:
                    return f"{n} {unit}"
                n //= 1024
            return f"{n} PB"

        def fmt_mtime(ts):
            if ts is None:
                return ""
            try:
                return time.strftime("%Y-%m-%d %H:%M", time.localtime(int(ts)))
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

        ttk.Button(btn_frame, text=i18n.t('show_in_folder'), 
                  command=self.reveal_selected,
                  bootstyle="info-outline").pack(side="left")
        
        ttk.Button(btn_frame, text=i18n.t('select_save'), 
                  command=self.save_selected,
                  bootstyle="success").pack(side="left", padx=8)
        
        ttk.Button(btn_frame, text=i18n.t('cancel'), 
                  command=self.destroy,
                  bootstyle="secondary").pack(side="right")

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
    
    save_text = 'Сохранить' if getattr(i18n, 'current_lang', 'ru') == 'ru' else 'Save'
    ttk.Button(btn_frame, text=save_text, command=ok, bootstyle="success").pack(side="left")
    ttk.Button(btn_frame, text=i18n.t('cancel'), command=cancel, bootstyle="secondary").pack(side="left", padx=8)

    dialog.bind("<Return>", lambda e: ok())
    dialog.bind("<Escape>", lambda e: cancel())

    parent.wait_window(dialog)
    return result["value"]
