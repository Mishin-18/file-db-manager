from core.proc import popen_quiet, run_quiet
import os
import sys
import time
import subprocess
import ctypes
import tkinter as tk
import ttkbootstrap as ttk

from core.env import IS_WIN
from core.i18n import i18n
from core.ui_common import apply_app_icon
from gui.widgets import CustomMessagebox as Messagebox


def is_hidden_or_system(path: str) -> bool:
    if not IS_WIN:
        return False
    try:
        attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
        if attrs == -1:
            return False
        FILE_ATTRIBUTE_HIDDEN = 0x2
        FILE_ATTRIBUTE_SYSTEM = 0x4
        return bool(attrs & (FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM))
    except Exception:
        return False


def get_paths_from_clipboard_win(root=None):
    try:
        owns_root = False
        if root is None:
            root = tk.Tk()
            root.withdraw()
            owns_root = True
        try:
            text = root.clipboard_get()
        except Exception:
            text = ""
        finally:
            if owns_root:
                try:
                    root.destroy()
                except Exception:
                    pass
        return [line.strip() for line in str(text).splitlines() if line.strip()]
    except Exception:
        return []


def show_help_update_db(parent):
    dlg = ttk.Toplevel(parent)
    try:
        dlg.withdraw()
    except Exception:
        pass
    apply_app_icon(dlg)
    dlg.title(i18n.t('help_title'))
    dlg.geometry("820x380")
    dlg.minsize(640, 300)
    dlg.transient(parent)
    dlg.grab_set()

    try:
        dlg.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (820 // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (380 // 2)
        dlg.geometry(f"+{x}+{y}")
    except Exception:
        pass

    frame = ttk.Frame(dlg, padding=16)
    frame.pack(fill="both", expand=True)

    ttk.Label(
        frame,
        text=i18n.t('help_title'),
        font=("Segoe UI", 12, "bold")
    ).pack(anchor="w", pady=(0, 8))

    msg = ttk.Label(
        frame,
        text=i18n.t('help_update_db_text'),
        justify="left",
        anchor="w"
    )
    msg.pack(anchor="w", fill="x")

    def _update_wrap(_event=None):
        try:
            msg.configure(wraplength=max(320, frame.winfo_width() - 24))
        except Exception:
            pass

    frame.bind("<Configure>", _update_wrap, add="+")
    _update_wrap()

    btns = ttk.Frame(frame)
    btns.pack(fill="x", pady=(16, 0))
    close_text = i18n.t('close')
    ttk.Button(btns, text=close_text, command=dlg.destroy, bootstyle="primary").pack(side="right")

    dlg.bind("<Escape>", lambda e: dlg.destroy())

    try:
        dlg.deiconify()
        dlg.lift()
        dlg.focus_force()
    except Exception:
        try:
            dlg.deiconify()
        except Exception:
            pass


def show_file_not_found_dialog(parent, folder_path: str):
    dlg = ttk.Toplevel(parent)
    try:
        dlg.withdraw()
    except Exception:
        pass
    apply_app_icon(dlg)
    dlg.title(i18n.t('file_not_found'))
    dlg.geometry("820x300")
    dlg.minsize(640, 220)
    dlg.transient(parent)
    dlg.grab_set()

    try:
        dlg.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (820 // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (300 // 2)
        dlg.geometry(f"+{x}+{y}")
    except Exception:
        pass

    frame = ttk.Frame(dlg, padding=16)
    frame.pack(fill="both", expand=True)

    msg = ttk.Label(
        frame,
        text=f"{i18n.t('file_not_found_msg')}{folder_path}",
        justify="left",
        anchor="w"
    )
    msg.pack(anchor="w", fill="x")

    def _update_wrap(_event=None):
        try:
            msg.configure(wraplength=max(320, frame.winfo_width() - 24))
        except Exception:
            pass

    frame.bind("<Configure>", _update_wrap, add="+")
    _update_wrap()

    btns = ttk.Frame(frame)
    btns.pack(fill="x", pady=(16, 0))

    help_text = i18n.t('help')
    close_text = i18n.t('close')

    ttk.Button(btns, text=help_text, bootstyle="secondary", command=lambda: show_help_update_db(dlg)).pack(side="left")
    ttk.Button(btns, text=close_text, bootstyle="primary", command=dlg.destroy).pack(side="right")

    dlg.bind("<Escape>", lambda e: dlg.destroy())

    try:
        dlg.deiconify()
        dlg.lift()
        dlg.focus_force()
    except Exception:
        try:
            dlg.deiconify()
        except Exception:
            pass


def is_windows_11() -> bool:
    try:
        v = sys.getwindowsversion()
        return v.major == 10 and v.build >= 22000
    except Exception:
        return False


def _run_powershell_hidden(ps_script: str):
    cmd = [
        "powershell.exe",
        "-NoProfile",
        "-NonInteractive",
        "-WindowStyle", "Hidden",
        "-ExecutionPolicy", "Bypass",
        "-Command", ps_script
    ]
    popen_quiet(cmd)


def _open_folder_win(folder_path: str):
    popen_quiet(["explorer.exe", folder_path])


def _show_item_in_parent_win10(parent_folder: str, item_name: str):
    popen_quiet(["explorer.exe", "/select,", os.path.join(parent_folder, item_name)])

    time.sleep(0.5)

    folder_ps = parent_folder.replace('"', '""')
    item_ps = item_name.replace('"', '""')
    ps = f"""
$ErrorActionPreference = 'SilentlyContinue'
$folder = "{folder_ps}"
$itemName = "{item_ps}"

if ([string]::IsNullOrWhiteSpace($folder)) {{ exit 0 }}

Start-Sleep -Milliseconds 500

$shell = New-Object -ComObject Shell.Application
$targetWindow = $null

foreach ($w in $shell.Windows()) {{
    try {{
        if ($w.Document -and $w.Document.Folder -and $w.Document.Folder.Self) {{
            $loc = $w.Document.Folder.Self.Path
            if ($loc -and $loc -eq $folder) {{
                $targetWindow = $w
                break
            }}
        }}
    }} catch {{}}
}}

if ($targetWindow -ne $null) {{
    try {{
        $targetWindow.Visible = $true
        $folderObj = $targetWindow.Document.Folder
        $item = $folderObj.ParseName($itemName)

        if ($item -ne $null) {{
            $targetWindow.Document.SelectItem($null, 0)
            Start-Sleep -Milliseconds 50
            $targetWindow.Document.SelectItem($item, 1 + 8 + 16)

            $wshell = New-Object -ComObject wscript.shell
            $wshell.AppActivate($targetWindow.Title) | Out-Null
        }}
    }} catch {{}}
}}
"""
    _run_powershell_hidden(ps)


def _show_item_in_parent_win11(parent_folder: str, item_name: str):
    folder_ps = parent_folder.replace('"', '""')
    item_ps = item_name.replace('"', '""')
    ps = f"""
$ErrorActionPreference = 'SilentlyContinue'
$folder = "{folder_ps}"
$itemName = "{item_ps}"

if ([string]::IsNullOrWhiteSpace($folder)) {{ exit 0 }}

$shell = New-Object -ComObject Shell.Application
$shell.Open($folder)

Start-Sleep -Milliseconds 260

$windows = $shell.Windows()
foreach ($w in $windows) {{
  try {{
    if ($w.Document -and $w.Document.Folder -and $w.Document.Folder.Self -and ($w.Document.Folder.Self.Path -eq $folder)) {{
      $w.Visible = $true

      $folderObj = $w.Document.Folder
      $item = $folderObj.ParseName($itemName)

      if ($item -ne $null) {{
        $w.Document.SelectItem($item, 1 + 4 + 8 + 16)
        $wshell = New-Object -ComObject wscript.shell
        $wshell.AppActivate($w.Title) | Out-Null
      }}
      break
    }}
  }} catch {{}}
}}
"""
    _run_powershell_hidden(ps)


def _show_in_folder_win10(path_norm: str):
    parent_folder = os.path.dirname(path_norm)
    item_name = os.path.basename(path_norm)
    if not parent_folder or parent_folder == path_norm or not item_name:
        _open_folder_win(path_norm)
        return
    _show_item_in_parent_win10(parent_folder, item_name)


def _show_in_folder_win11(path_norm: str):
    parent_folder = os.path.dirname(path_norm)
    item_name = os.path.basename(path_norm)
    if not parent_folder or parent_folder == path_norm or not item_name:
        _open_folder_win(path_norm)
        return
    _show_item_in_parent_win11(parent_folder, item_name)


def reveal_in_folder(path: str, parent=None):
    path = (path or "").strip()
    if not path:
        Messagebox.show_warning(i18n.t('empty_path_msg'), i18n.t('warning'), parent=parent)
        return

    _parent = parent
    if _parent is None:
        try:
            _parent = tk._default_root
        except Exception:
            _parent = None

    try:
        if not IS_WIN:
            if sys.platform == "darwin":
                run_quiet(["open", "-R", path], check=False)
                return
            folder = os.path.dirname(path) if os.path.isfile(path) else path
            run_quiet(["xdg-open", folder], check=False)
            return

        path_norm = os.path.normpath(path.strip('"').strip())

        if not os.path.exists(path_norm):
            folder = os.path.dirname(path_norm)
            if folder and os.path.isdir(folder):
                subprocess.Popen(
                    ["explorer.exe", folder],
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
                )
                if _parent is not None:
                    show_file_not_found_dialog(_parent, str(folder))
            else:
                Messagebox.show_error(f"{i18n.t('not_found_msg')}{path_norm}", i18n.t('error'), parent=_parent)
            return

        if is_windows_11():
            _show_in_folder_win11(path_norm)
        else:
            _show_in_folder_win10(path_norm)

    except Exception:
        Messagebox.show_error(f"{i18n.t('show_in_folder_failed_generic')}\n\n{path}", i18n.t('error'), parent=_parent)
