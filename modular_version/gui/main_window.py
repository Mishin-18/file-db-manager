import os
import logging
import sqlite3
import threading
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import ToastNotification

from core.i18n import i18n
from core.env import HAS_OPENPYXL, IS_WIN
from core.ui_common import apply_app_icon
from core.tray import TrayIcon
from core.db import init_db, get_missing_required_tables, validate_db_path
from core.scanner import scan_folders_to_db
from core.content.indexer import index_document_contents
from core.shell import get_paths_from_clipboard_win
from core.resolver import (
    parse_paths_from_text,
    read_paths_from_txt,
    read_paths_from_xlsx,
    upsert_set,
    sync_set_items,
)
from gui.widgets import CustomMessagebox as Messagebox, ToolTip, Spinner, attach_help


class ActiveScanCloseController:
    """Single controller for all active-scan close/stop/cancel flows."""

    def __init__(self, app):
        self.app = app

    def _hide_progress_if_needed(self, hide_progress: bool):
        dlg = getattr(self.app, "scan_progress_dialog", None)
        hidden = False
        try:
            if hide_progress and dlg and dlg.winfo_exists():
                dlg.withdraw()
                dlg.update_idletasks()
                hidden = True
        except Exception:
            hidden = False
        return dlg, hidden

    def _show_progress_again(self, dlg=None):
        if dlg is None:
            dlg = getattr(self.app, "scan_progress_dialog", None)
        try:
            if dlg and dlg.winfo_exists():
                dlg.deiconify()
                dlg.update_idletasks()
                dlg.lift()
                try:
                    dlg.attributes("-topmost", True)
                    dlg.update_idletasks()
                    dlg.attributes("-topmost", False)
                except Exception:
                    pass
                try:
                    dlg.focus_force()
                except Exception:
                    try:
                        dlg.focus_set()
                    except Exception:
                        pass
        except Exception:
            pass

    def _show_close_action_dialog(self, title: str, message: str, hide_progress: bool):
        dlg, hidden = self._hide_progress_if_needed(hide_progress)
        self.app._restore_main_before_dialog()
        action = "cancel"
        try:
            action = Messagebox.ask_scan_close_action(message=message, title=title, parent=self.app)
            return action
        finally:
            if hidden and action not in ("background", "stop"):
                self._show_progress_again(dlg)

    def _confirm_stop_only(self):
        self.app._restore_main_before_dialog()
        action = self._show_close_action_dialog(
            title=i18n.t('scan_close_running_title'),
            message=i18n.t('scan_close_running_msg'),
            hide_progress=False,
        )
        if action == "background":
            self.app._background_scan()
            return False
        if action == "stop":
            return True
        self._show_progress_again()
        return False

    def request(self, source: str, *, title: str = None, message: str = None, hide_progress: bool = False):
        """Return one of: cancel, background, stop."""
        if source == "stop_button":
            return "stop" if self._confirm_stop_only() else "cancel"

        action = self._show_close_action_dialog(
            title=title or i18n.t('scan_close_running_title'),
            message=message or i18n.t('scan_close_running_msg'),
            hide_progress=hide_progress,
        )
        if action == "cancel":
            self._show_progress_again()
        return action
from gui.viewer import Viewer
from gui.dialogs import simple_input, askopenfilename_custom, asksaveasfilename_custom, askdirectory_custom, choose_multiple_folders

class App(ttk.Window):
    """Main application window with theme and language switching"""
    
    def __init__(self):
        # Default UI language
        i18n.set_language('ru')
        super().__init__(themename="darkly")
        # Hide window until icon is applied (prevents default icon flash on Windows)
        try:
            self.withdraw()
        except Exception:
            pass
        # Apply app icon as early as possible
        apply_app_icon(self)
        self.title(i18n.t('app_title'))
        self.geometry("950x550")
        self.protocol("WM_DELETE_WINDOW", self.exit_app)
        self.bind("<Map>", self._on_main_window_mapped, add="+")
        
        # Store available themes
        self.available_themes = self.style.theme_names()

        self.scan_running = False
        self.scan_progress_user_closed = False
        self.scan_backgrounded = False
        self.scan_progress_stop_btn = None
        self.scan_progress_bg_btn = None
        self._tray_tooltip_text = ""
        self._app_closing = False
        self._after_ids = set()
        self._tray_progress_phase = None
        self._tray_progress_processed = 0
        self._tray_progress_total = 0

        self.logger = logging.getLogger("FileDBManager")
        if IS_WIN:
            try:
                self.scan_tray = TrayIcon(self, self._restore_scan_from_background)
            except Exception:
                self.scan_tray = None
        self._schedule_tray_poll()

        # Main container
        main = ttk.Frame(self, padding=15)
        main.pack(fill="both", expand=True)

        # Header with theme and language selectors
        header = ttk.Frame(main)
        header.pack(fill="x", pady=(0, 15))

        # Title and selectors in same row
        title_frame = ttk.Frame(header)
        title_frame.pack(fill="x")

        self.title_label = ttk.Label(title_frame, text=i18n.t('app_title'), 
                                    font=("Segoe UI", 16, "bold"))
        self.title_label.pack(side="left")

        # Right side controls
        controls_frame = ttk.Frame(title_frame)
        controls_frame.pack(side="right")

        # Language selector
        lang_frame = ttk.Frame(controls_frame)
        lang_frame.pack(side="left", padx=(0, 15))

        self.lang_label = ttk.Label(lang_frame, text=i18n.t('language'), 
                                   font=("Segoe UI", 9))
        self.lang_label.pack(side="left", padx=(0, 5))

        self.lang_var = ttk.StringVar(value="ru")
        self.lang_combo = ttk.Combobox(
            lang_frame, 
            textvariable=self.lang_var,
            values=i18n.get_languages(),
            width=5,
            state="readonly"
        )
        self.lang_combo.pack(side="left")
        self.lang_combo.bind("<<ComboboxSelected>>", self.change_language)

        # Theme selector
        theme_frame = ttk.Frame(controls_frame)
        theme_frame.pack(side="left")

        self.theme_label = ttk.Label(theme_frame, text=i18n.t('theme'), 
                                    font=("Segoe UI", 9))
        self.theme_label.pack(side="left", padx=(0, 5))

        self.theme_var = ttk.StringVar(value="darkly")
        self.theme_combo = ttk.Combobox(
            theme_frame, 
            textvariable=self.theme_var,
            values=list(self.available_themes),
            width=12,
            state="readonly"
        )
        self.theme_combo.pack(side="left")
        self.theme_combo.bind("<<ComboboxSelected>>", self.change_theme)

        self.subtitle_label = ttk.Label(header, text=i18n.t('app_subtitle'),
                                       font=("Segoe UI", 10))
        self.subtitle_label.pack(anchor="w")

        # Info panel
        info_frame = ttk.Frame(main, bootstyle="info")
        info_frame.pack(fill="x", pady=(0, 15))
        
        self.info_label = ttk.Label(info_frame, text=i18n.t('info_text'), 
                                   font=("Segoe UI", 9))
        self.info_label.pack(padx=10, pady=10, anchor="w")

        # Quick start mini-block
        self.quick_start_visible = True
        self.quick_start_frame = ttk.LabelFrame(main, text=i18n.t('quick_start_title'))
        self.quick_start_frame.pack(fill="x", pady=(0, 15))

        self.quick_start_body = ttk.Label(
            self.quick_start_frame,
            text=i18n.t('quick_start_text'),
            justify="left",
            anchor="w",
            font=("Segoe UI", 9),
            wraplength=860
        )
        self.quick_start_body.pack(fill="x", padx=10, pady=(8, 6), anchor="w")

        self.quick_start_toggle_btn = ttk.Button(
            self.quick_start_frame,
            text=i18n.t('btn_hide'),
            width=10,
            command=self.toggle_quick_start,
            bootstyle="secondary-outline"
        )
        self.quick_start_toggle_btn.pack(anchor="w", padx=10, pady=(0, 10))

        # Options
        self.options_frame = ttk.LabelFrame(main, text=i18n.t('scan_options'))
        self.options_frame.pack(fill="x", pady=(0, 15))
        
        options_content = ttk.Frame(self.options_frame, padding=10)
        options_content.pack(fill="x")

        opt_row = ttk.Frame(options_content)
        opt_row.pack(fill="x")

        self.var_incremental = ttk.BooleanVar(value=False)
        self.var_sha1 = ttk.BooleanVar(value=False)
        self.var_recursive = ttk.BooleanVar(value=True)

        # One-time warnings per session
        self._warned_increment_off = False
        self._warned_sha1_on = False

        self.incremental_check = ttk.Checkbutton(opt_row, text=i18n.t('incremental'),
                                                variable=self.var_incremental,
                                                command=self._on_incremental_toggle,
                                                bootstyle="primary")
        self.incremental_check.pack(side="left")

        self.incremental_help_btn = ttk.Button(opt_row, text="ⓘ", width=3,
                                              command=self._show_incremental_help,
                                               bootstyle="secondary")
        self.incremental_help_btn.pack(side="left", padx=(6, 14))
        self.help_incremental = attach_help(
            self.incremental_help_btn,
            text_getter=lambda: i18n.t('help_incremental_text'),
            title_getter=lambda: i18n.t('help_incremental_title'),
            parent_getter=lambda: self,
        )
        self.sha1_check = ttk.Checkbutton(opt_row, text=i18n.t('calc_sha1'),
                                         variable=self.var_sha1,
                                         command=self._on_sha1_toggle,
                                         bootstyle="warning")
        self.sha1_check.pack(side="left")

        self.sha1_help_btn = ttk.Button(opt_row, text="ⓘ", width=3,
                                        command=self._show_sha1_help,
                                               bootstyle="secondary")
        self.sha1_help_btn.pack(side="left", padx=(6, 14))
        self.help_sha1 = attach_help(
            self.sha1_help_btn,
            text_getter=lambda: i18n.t('help_sha1_text'),
            title_getter=lambda: i18n.t('help_sha1_title'),
            parent_getter=lambda: self,
        )
        self.recursive_check = ttk.Checkbutton(opt_row, text=i18n.t('include_subfolders'), 
                                              variable=self.var_recursive,
                                              bootstyle="success")
        self.recursive_check.pack(side="left")

        # Tooltips
        self.tt_incremental = ToolTip(self.incremental_check, i18n.t('tt_incremental'))
        self.tt_sha1 = ToolTip(self.sha1_check, i18n.t('tt_sha1'))
        self.tt_recursive = ToolTip(self.recursive_check, i18n.t('tt_recursive'))


        # Action buttons
        actions = ttk.Frame(main)
        actions.pack(fill="x", pady=(0, 15))

        build_row = ttk.Frame(actions)
        build_row.pack(fill="x", pady=4)
        self.btn_build = ttk.Button(build_row, text=i18n.t('btn_build'), 
                                   command=self.build_db,
                                   bootstyle="success",
                                   width=40)
        self.btn_build.pack(side="left", fill="x", expand=True)
        self.btn_build_help = ttk.Button(build_row, text="ⓘ", width=3,
                                        command=self._show_build_help,
                                        bootstyle="secondary")
        self.btn_build_help.pack(side="left", padx=(6,0))
        self._refresh_build_button_text()

        set_row = ttk.Frame(actions)
        set_row.pack(fill="x", pady=4)
        self.btn_set = ttk.Button(set_row, text=i18n.t('btn_set'), 
                                 command=self.make_set,
                                 bootstyle="info",
                                 width=40)
        self.btn_set.pack(side="left", fill="x", expand=True)
        self.btn_set_help = ttk.Button(set_row, text="?", width=3,
                                      bootstyle="secondary")
        self.btn_set_help.pack(side="left", padx=(6,0))
        self.help_set = attach_help(
            self.btn_set_help,
            text_getter=lambda: i18n.t('help_btn_set_text'),
            title_getter=lambda: i18n.t('help_btn_set_title'),
            parent_getter=lambda: self,
            short_tooltip_text_getter=lambda: i18n.t('help_btn_set_text'),
        )

        view_row = ttk.Frame(actions)
        view_row.pack(fill="x", pady=4)
        self.btn_view = ttk.Button(view_row, text=i18n.t('btn_view'), 
                                  command=self.open_viewer,
                                  bootstyle="primary",
                                  width=40)
        self.btn_view.pack(side="left", fill="x", expand=True)
        self.btn_view_help = ttk.Button(view_row, text="?", width=3,
                                       bootstyle="secondary")
        self.btn_view_help.pack(side="left", padx=(6,0))
        self.help_view = attach_help(
            self.btn_view_help,
            text_getter=lambda: i18n.t('help_btn_view_text'),
            title_getter=lambda: i18n.t('help_btn_view_title'),
            parent_getter=lambda: self,
        )

        content_row = ttk.Frame(actions)
        content_row.pack(fill="x", pady=4)
        self.btn_index_content = ttk.Button(
            content_row,
            text=i18n.t('btn_index_content'),
            command=self.index_document_content,
            bootstyle="warning",
            width=40
        )
        self.btn_index_content.pack(side="left", fill="x", expand=True)
        self.btn_index_content_help = ttk.Button(content_row, text="ⓘ", width=3,
                                                command=self._show_index_content_help,
                                                bootstyle="secondary")
        self.btn_index_content_help.pack(side="left", padx=(6,0))

        exit_row = ttk.Frame(actions)
        exit_row.pack(fill="x", pady=(8, 0))
        self.btn_exit = ttk.Button(exit_row, text=i18n.t('btn_exit'),
                                  command=self.exit_app,
                                  bootstyle="danger-outline",
                                  width=14)
        self.btn_exit.pack(side="right")

        self.help_build = attach_help(
            self.btn_build_help,
            text_getter=lambda: i18n.t('help_btn_build_text'),
            title_getter=lambda: i18n.t('help_btn_build_title'),
            parent_getter=lambda: self,
        )
        self.help_index_content = attach_help(
            self.btn_index_content_help,
            text_getter=lambda: i18n.t('help_index_content_text'),
            title_getter=lambda: i18n.t('help_index_content_title'),
            parent_getter=lambda: self,
        )

        # Status bar
        status_frame = ttk.Frame(main)
        status_frame.pack(fill="x", pady=(10, 0))
        self.status_frame = status_frame

        status_text_frame = ttk.Frame(status_frame)
        status_text_frame.pack(side="left", fill="x", expand=True)

        self.status = ttk.Label(
            status_text_frame,
            text=i18n.t('status_ready'),
            font=("Segoe UI", 9),
            anchor="w",
            justify="left",
            wraplength=900,
        )
        self.status.pack(side="left", fill="x", expand=True)

        self.stop_flag = {"stop": False}
        self.scan_close_controller = ActiveScanCloseController(self)

        self.btn_stop = ttk.Button(
            status_frame,
            text=i18n.t('btn_stop'),
            command=self.stop_op,
            bootstyle="danger-outline"
        )
        self.btn_stop.pack(side="right", padx=(10, 0))
        self.btn_stop.config(state="disabled")

        try:
            self.status_frame.bind("<Configure>", self._on_status_frame_configure)
            self.btn_stop.bind("<Configure>", self._on_status_frame_configure)
        except Exception:
            pass

        self.xlsx_warn_label = None
        # XLSX warning
        if not HAS_OPENPYXL:
            warn_frame = ttk.Frame(main, bootstyle="warning")
            warn_frame.pack(fill="x", pady=(10, 0))
            
            self.xlsx_warn_label = ttk.Label(warn_frame, 
                     text=i18n.t('xlsx_disabled_warn'),
                     font=("Segoe UI", 9))
            self.xlsx_warn_label.pack(padx=10, pady=5, anchor="w")


    # ---------------------------
    # Option toggles & Help
        # Show window after UI is built and icon is set
        try:
            self.update_idletasks()
        except Exception:
            pass
        try:
            self.deiconify()
        except Exception:
            pass

    # ---------------------------
    def _refresh_build_button_text(self):
        key = 'btn_build_incremental' if self.var_incremental.get() else 'btn_build'
        try:
            self.btn_build.config(text=i18n.t(key))
        except Exception:
            pass

    def _on_incremental_toggle(self):
        """Warn once when user disables incremental mode and refresh button text."""
        if self.var_incremental.get():
            self._refresh_build_button_text()
            return
        if not getattr(self, "_warned_increment_off", False):
            self._warned_increment_off = True
            msg = i18n.t('warn_increment_off')
            # yes = continue disabling, no = revert
            if not Messagebox.yesno(msg, i18n.t('warning_title'), parent=self):
                self.var_incremental.set(True)
        self._refresh_build_button_text()

    def _on_sha1_toggle(self):
        """Warn once when user enables SHA1 calculation."""
        if not self.var_sha1.get():
            return
        if not getattr(self, "_warned_sha1_on", False):
            self._warned_sha1_on = True
            msg = i18n.t('warn_sha1_on')
            if not Messagebox.yesno(msg, i18n.t('warning_title'), parent=self):
                self.var_sha1.set(False)

    def _show_incremental_help(self):
        Messagebox.show_info(i18n.t('help_incremental_text'), i18n.t('help_incremental_title'), parent=self)









    def _show_sha1_help(self):
        Messagebox.show_info(i18n.t('help_sha1_text'), i18n.t('help_sha1_title'), parent=self)









    def _show_build_help(self):
        Messagebox.show_info(i18n.t('help_btn_build_text'), i18n.t('help_btn_build_title'), parent=self)

    def _show_set_help(self):
        return










    def _show_view_help(self):
        return





    def _show_index_content_help(self):
        title = i18n.t('help_index_content_title')
        text = i18n.t('help_index_content_text')
        Messagebox.show_info(text, title, parent=self)

    def _apply_quick_start_state(self):
        try:
            if self.quick_start_visible:
                if not self.quick_start_body.winfo_manager():
                    self.quick_start_body.pack(before=self.quick_start_toggle_btn, fill="x", padx=10, pady=(8, 6), anchor="w")
                self.quick_start_toggle_btn.config(text=i18n.t('btn_hide'))
            else:
                if self.quick_start_body.winfo_manager():
                    self.quick_start_body.pack_forget()
                self.quick_start_toggle_btn.config(text=i18n.t('btn_show'))
        except Exception:
            pass

    def toggle_quick_start(self):
        self.quick_start_visible = not self.quick_start_visible
        self._apply_quick_start_state()

    def _iter_ui_targets(self):
        """Yield all live descendant windows/widgets that can react to language updates."""
        stack = [self]
        seen = set()
        while stack:
            widget = stack.pop()
            marker = id(widget)
            if marker in seen:
                continue
            seen.add(marker)
            yield widget
            try:
                children = widget.winfo_children()
            except Exception:
                children = []
            stack.extend(children)

    def _refresh_scan_progress_language(self):
        """Refresh texts inside the shared scan progress dialog, if it is open."""
        dlg = getattr(self, 'scan_progress_dialog', None)
        try:
            if not dlg or not dlg.winfo_exists():
                return
        except Exception:
            return
        try:
            dlg.title(i18n.t('status_scan'))
        except Exception:
            pass
        try:
            if getattr(self, 'scan_progress_bg_btn', None):
                self.scan_progress_bg_btn.config(text=i18n.t('btn_background'))
            if getattr(self, 'scan_progress_stop_btn', None):
                self.scan_progress_stop_btn.config(text=i18n.t('btn_stop'))
        except Exception:
            pass
        try:
            if getattr(self, 'scan_progress_title_label', None):
                current = str(self.scan_progress_title_label.cget('text') or '')
                if not current.strip() or current == i18n.t('status_counting_title'):
                    self.scan_progress_title_label.config(text=i18n.t('status_counting_title'))
        except Exception:
            pass

    def _apply_language_to_self(self):
        """Update texts in the main window itself from the current language."""
        self.title(i18n.t('app_title'))
        self.title_label.config(text=i18n.t('app_title'))
        self.lang_label.config(text=i18n.t('language'))
        self.theme_label.config(text=i18n.t('theme'))
        self.subtitle_label.config(text=i18n.t('app_subtitle'))
        self.info_label.config(text=i18n.t('info_text'))
        self.quick_start_frame.config(text=i18n.t('quick_start_title'))
        self.quick_start_body.config(text=i18n.t('quick_start_text'))
        self._apply_quick_start_state()

        self.options_frame.config(text=i18n.t('scan_options'))
        self.incremental_check.config(text=i18n.t('incremental'))
        self.sha1_check.config(text=i18n.t('calc_sha1'))
        self.recursive_check.config(text=i18n.t('include_subfolders'))
        try:
            self.tt_incremental.text = i18n.t('tt_incremental')
            self.tt_sha1.text = i18n.t('tt_sha1')
            self.tt_recursive.text = i18n.t('tt_recursive')
            self.help_incremental.apply()
            self.help_sha1.apply()
            self.help_build.apply()
            self.help_set.apply()
            self.help_view.apply()
            self.help_index_content.apply()
        except Exception:
            pass

        self._refresh_build_button_text()
        self.btn_set.config(text=i18n.t('btn_set'))
        self.btn_view.config(text=i18n.t('btn_view'))
        self.btn_index_content.config(text=i18n.t('btn_index_content'))
        self.btn_exit.config(text=i18n.t('btn_exit'))
        try:
            if getattr(self, 'btn_stop', None):
                self.btn_stop.config(text=i18n.t('btn_stop'))
        except Exception:
            pass
        if getattr(self, 'xlsx_warn_label', None):
            self.xlsx_warn_label.config(text=i18n.t('xlsx_disabled_warn'))
        if not getattr(self, 'scan_running', False):
            self.status.config(text=i18n.t('status_ready'))
        self._refresh_scan_progress_language()

    def _notify_ui_change(self, change_kind: str):
        """Propagate a global UI change to all live child windows and widgets."""
        for widget in self._iter_ui_targets():
            if widget is self:
                continue
            handler = getattr(widget, 'on_ui_changed', None)
            if callable(handler):
                try:
                    handler(change_kind)
                    continue
                except Exception:
                    pass
            updater = None
            if change_kind == 'language':
                updater = getattr(widget, 'update_language', None)
            elif change_kind == 'theme':
                updater = getattr(widget, 'update_theme', None)
            if callable(updater):
                try:
                    updater()
                except Exception:
                    pass

    def change_language(self, event=None):
        """Change application language"""
        new_lang = self.lang_var.get()
        i18n.set_language(new_lang)

        self._apply_language_to_self()
        self._notify_ui_change('language')

        toast = ToastNotification(
            title=i18n.t('lang_changed'),
            message=f"{i18n.t('lang_changed_msg')}{new_lang.upper()}",
            duration=1500,
        )
        toast.show_toast()

    def change_theme(self, event=None):
        """Change application theme"""
        new_theme = self.theme_var.get()
        self.style.theme_use(new_theme)
        self._notify_ui_change('theme')

        toast = ToastNotification(
            title=i18n.t('theme_changed'),
            message=f"{i18n.t('theme_changed_msg')}{new_theme}",
            duration=1500,
        )
        toast.show_toast()

    def _on_status_frame_configure(self, event=None):
        try:
            frame_w = max(1, self.status_frame.winfo_width())
            btn_w = self.btn_stop.winfo_width() if getattr(self, 'btn_stop', None) else 0
            available = max(220, frame_w - btn_w - 30)
            self.status.configure(wraplength=available)
        except Exception:
            pass

    def set_status(self, text: str):
        """Update main-window status text only."""
        self.status.config(text=text)
        self._on_status_frame_configure()
        self._tray_tooltip_text = text or ""
        self._update_tray_tooltip()
        self.update_idletasks()

    def _build_tray_tooltip(self) -> str:
        title = i18n.t('app_title')
        phase = getattr(self, '_tray_progress_phase', None)
        if phase == 'scan' and self._tray_progress_total:
            pct = (self._tray_progress_processed / self._tray_progress_total) * 100.0 if self._tray_progress_total else 0.0
            return f"{title}\n{i18n.t('status_scan')}: {pct:.1f}%"[:127]
        if phase == 'count':
            return f"{title}\n{i18n.t('status_counting_title')}"[:127]
        if self._tray_tooltip_text:
            short = self._tray_tooltip_text.replace('\n', ' ')
            return f"{title}\n{short}"[:127]
        return title[:127]

    def _update_tray_tooltip(self):
        try:
            if self.scan_tray and self.scan_backgrounded:
                self.scan_tray.update_tooltip(self._build_tray_tooltip())
        except Exception:
            pass

    def _set_scan_dialog_status(self, text: str, *, log: bool = False):
        """Update only the scan dialog status/log without duplicating into the main window."""
        try:
            if getattr(self, 'scan_progress_label', None) and getattr(self, 'scan_progress_dialog', None) and self.scan_progress_dialog.winfo_exists():
                self.scan_progress_label.config(text=text)
        except Exception:
            pass
        if not log:
            return
        try:
            if getattr(self, 'scan_log_text', None) and getattr(self, 'scan_progress_dialog', None) and self.scan_progress_dialog.winfo_exists():
                last = getattr(self, '_last_scan_log_line', None)
                if text and text != last:
                    self._last_scan_log_line = text
                    self.scan_log_text.configure(state="normal")
                    self.scan_log_text.insert("end", text + "\n")
                    self.scan_log_text.see("end")
                    self.scan_log_text.configure(state="disabled")
        except Exception:
            pass

    def stop_op(self, *, confirm: bool = True):
        """Stop current operation through the unified close controller."""
        if confirm and self.scan_running:
            action = self.scan_close_controller.request("stop_button")
            if action != "stop":
                return
        self.stop_flag["stop"] = True
        self.set_status(i18n.t('status_stopping'))


    def _background_scan(self):
        """Hide scan UI and minimize app to system tray while keeping scan running."""
        self.scan_backgrounded = True
        try:
            if getattr(self, "scan_progress_dialog", None) and self.scan_progress_dialog.winfo_exists():
                self.scan_progress_dialog.grab_release()
                self.scan_progress_dialog.withdraw()
        except Exception:
            pass
        try:
            if self.scan_tray:
                self.scan_tray.show(self._build_tray_tooltip())
        except Exception:
            pass
        try:
            self._restore_state_after_background = self.state()
        except Exception:
            try:
                self._restore_state_after_background = self.wm_state()
            except Exception:
                self._restore_state_after_background = None
        try:
            self.withdraw()
        except Exception:
            try:
                self.iconify()
            except Exception:
                pass

    def _restore_main_before_dialog(self):
        """Raise and focus the main window before showing a dialog without breaking zoomed state."""
        try:
            if not self.winfo_exists():
                return
        except Exception:
            return

        state_before = None
        try:
            state_before = self.state()
        except Exception:
            try:
                state_before = self.wm_state()
            except Exception:
                state_before = None

        try:
            if state_before in ("withdrawn", "iconic"):
                self.deiconify()
        except Exception:
            pass
        try:
            self.update_idletasks()
        except Exception:
            pass
        try:
            self.lift()
        except Exception:
            pass
        try:
            self.attributes("-topmost", True)
            self.update_idletasks()
            self.update_idletasks()
            self.attributes("-topmost", False)
        except Exception:
            pass
        try:
            self.focus_force()
        except Exception:
            try:
                self.focus_set()
            except Exception:
                pass
        try:
            self.update_idletasks()
        except Exception:
            pass

    def _show_scan_close_action(self, message: str, title: str, *, parent=None, hide_progress: bool = False):
        """Backward-compatible wrapper over the unified close controller."""
        return self.scan_close_controller.request(
            "scan_close",
            title=title,
            message=message,
            hide_progress=hide_progress,
        )

    def _restore_scan_from_background(self):
        if not self.scan_running:
            try:
                if self.scan_tray:
                    self.scan_tray.hide()
            except Exception:
                pass
            return
        self.scan_backgrounded = False
        try:
            if self.scan_tray:
                self.scan_tray.hide()
        except Exception:
            pass
        prev_state = getattr(self, "_restore_state_after_background", None)
        try:
            self.deiconify()
            try:
                if prev_state == "zoomed":
                    self.state("zoomed")
            except Exception:
                pass
            self.update_idletasks()
            self.lift()
            try:
                self.attributes("-topmost", True)
                self.update_idletasks()
                self.attributes("-topmost", False)
            except Exception:
                pass
            self.focus_force()
        except Exception:
            pass
        try:
            if getattr(self, "scan_progress_dialog", None) and self.scan_progress_dialog.winfo_exists():
                self.scan_progress_dialog.deiconify()
                self.scan_progress_dialog.lift()
                try:
                    self.scan_progress_dialog.focus_force()
                except Exception:
                    pass
        except Exception:
            pass

    def _restore_progress_dialog(self):
        """Bring the scan progress dialog back to the front if it is still active."""
        dlg = getattr(self, "scan_progress_dialog", None)
        try:
            if dlg and dlg.winfo_exists():
                dlg.deiconify()
                dlg.update_idletasks()
                dlg.lift()
                try:
                    dlg.attributes("-topmost", True)
                    dlg.update_idletasks()
                    dlg.attributes("-topmost", False)
                except Exception:
                    pass
                try:
                    dlg.focus_force()
                except Exception:
                    try:
                        dlg.focus_set()
                    except Exception:
                        pass
        except Exception:
            pass

    def _safe_after(self, ms, callback, *args):
        if getattr(self, "_app_closing", False):
            return None
        holder = {"id": None}

        def _runner():
            aid = holder.get("id")
            if aid:
                self._after_ids.discard(aid)
            if getattr(self, "_app_closing", False):
                return
            try:
                if not self.winfo_exists():
                    return
            except Exception:
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
        try:
            self._after_ids.clear()
        except Exception:
            pass

    def _on_main_window_mapped(self, event=None):
        try:
            if event is not None and event.widget is not self:
                return
        except Exception:
            pass
        if self.scan_running and self.scan_backgrounded:
            self._safe_after(0, self._restore_scan_from_background)

    def _cancel_tray_poll(self):
        after_id = getattr(self, "_tray_poll_after_id", None)
        if after_id:
            try:
                self.after_cancel(after_id)
            except Exception:
                pass
        self._tray_poll_after_id = None

    def _schedule_tray_poll(self):
        if getattr(self, "_app_closing", False):
            return
        self._cancel_tray_poll()
        try:
            if self.winfo_exists():
                self._tray_poll_after_id = self._safe_after(500, self._poll_tray_events)
        except Exception:
            self._tray_poll_after_id = None

    def _poll_tray_events(self):
        try:
            if self.scan_tray and self.scan_backgrounded and self.scan_tray.has_restore_request():
                self._restore_scan_from_background()
        except Exception:
            pass
        finally:
            try:
                self._schedule_tray_poll()
            except Exception:
                pass

    def _handle_active_scan_close(self, *, title: str, message: str, hide_progress: bool = False):
        action = self.scan_close_controller.request(
            "scan_close",
            title=title,
            message=message,
            hide_progress=hide_progress,
        )
        if action == "background":
            self._background_scan()
            return True
        if action == "stop":
            if hide_progress:
                self._restore_main_before_dialog()
            self.stop_op(confirm=False)
            return True
        return False

    def exit_app(self):
        """Close the application from the main window."""
        try:
            scanning_active = bool(getattr(self, "scan_thread", None) and self.scan_thread.is_alive())
        except Exception:
            scanning_active = False

        if scanning_active:
            try:
                action = self.scan_close_controller.request(
                    "main_close",
                    hide_progress=False,
                )
            except Exception:
                return

            if action == "background":
                self._background_scan()
                return

            if action == "stop":
                try:
                    self.stop_op(confirm=False)
                except Exception:
                    pass
                try:
                    self._safe_after(250, self._finish_exit_after_stop)
                except Exception:
                    self._finish_exit_after_stop()
                return

            return

        self._app_closing = True
        self._cancel_tray_poll()
        try:
            if self.scan_tray:
                self.scan_tray.shutdown()
        except Exception:
            pass
        try:
            self.destroy()
        except Exception:
            try:
                self.quit()
            except Exception:
                pass

    def _finish_exit_after_stop(self):
        """Wait until the scan thread fully stops, then close the app."""
        try:
            scanning_active = bool(getattr(self, "scan_thread", None) and self.scan_thread.is_alive())
        except Exception:
            scanning_active = False

        if scanning_active:
            try:
                self._safe_after(250, self._finish_exit_after_stop)
            except Exception:
                pass
            return

        try:
            if self.scan_tray:
                self.scan_tray.shutdown()
        except Exception:
            pass
        try:
            self.destroy()
        except Exception:
            try:
                self.quit()
            except Exception:
                pass

    def _update_scan_progress_visuals(self, processed: int | None = None, total: int | None = None, *, show_pct: bool = True):
        try:
            if getattr(self, "scan_progress_bar", None) is None:
                return
            self.scan_progress_bar.stop()
            self.scan_progress_bar.configure(mode="determinate", maximum=100.0)
            if total and total > 0 and processed is not None:
                pct = max(0.0, min(100.0, (processed / total) * 100.0))
                self.scan_progress_bar.configure(value=pct)
                self.scan_progress_pct_label.config(text=f"{pct:.1f}%" if show_pct else "")
            else:
                self.scan_progress_bar.configure(value=0.0)
                self.scan_progress_pct_label.config(text="" if not show_pct else "0.0%")
        except Exception:
            pass

    def _fmt_num(self, value) -> str:
        try:
            return f"{int(value):,}".replace(',', "'")
        except Exception:
            return str(value)

    def _format_count_progress_text(self, counted: int) -> str:
        return i18n.t('status_counting_files').format(counted=self._fmt_num(counted))

    def _format_scan_progress_text(self, payload: dict) -> str:
        processed = int(payload.get('processed') or 0)
        total = int(payload.get('total') or 0)
        pct = ((processed / total) * 100.0) if total else 0.0
        return (
            f"{payload.get('mode') or i18n.t('status_scan')}: {self._fmt_num(processed)} / {self._fmt_num(total)} ({pct:.1f}%) | "
            f"{i18n.t('stat_new')} {self._fmt_num(payload.get('new') or 0)} | "
            f"{i18n.t('stat_updated')} {self._fmt_num(payload.get('updated') or 0)} | "
            f"{i18n.t('stat_skipped')} {self._fmt_num(payload.get('skipped') or 0)} | "
            f"{i18n.t('stat_errors')} {self._fmt_num(payload.get('errors') or 0)} | "
            f"{i18n.t('stat_sha1')} {self._fmt_num(payload.get('sha1') or 0)}"
        )

    def show_scan_progress(self):
        """Show progress dialog during database build"""
        try:
            if getattr(self, "btn_stop", None):
                self.btn_stop.config(state="normal")
        except Exception:
            pass
        try:
            if getattr(self, "scan_progress_dialog", None) and self.scan_progress_dialog.winfo_exists():
                return
        except Exception:
            pass

        self.scan_progress_dialog = ttk.Toplevel(self)
        try:
            self.scan_progress_dialog.withdraw()
        except Exception:
            pass
        apply_app_icon(self.scan_progress_dialog)
        self.scan_progress_dialog.title(i18n.t('status_scan'))
        self.scan_progress_dialog.geometry("760x360")
        self.scan_progress_dialog.transient(self)
        # Keep the progress window on top of the app, but do not grab input.
        # A global/local grab blocks the main window caption buttons after restore from tray.
        self.scan_progress_dialog.protocol("WM_DELETE_WINDOW", self._on_scan_dialog_close)

        # Center on parent
        self.scan_progress_dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (760 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (360 // 2)
        self.scan_progress_dialog.geometry(f"+{x}+{y}")

        def _scan_progress_update_language():
            try:
                self.scan_progress_dialog.title(i18n.t('status_scan'))
            except Exception:
                pass
            try:
                self.scan_progress_title_label.config(text=i18n.t('status_counting_title'))
            except Exception:
                pass
            try:
                self.scan_progress_bg_btn.config(text=i18n.t('btn_background'))
                self.scan_progress_stop_btn.config(text=i18n.t('btn_stop'))
            except Exception:
                pass

        self.scan_progress_dialog.update_language = _scan_progress_update_language
        self.scan_progress_dialog.on_ui_changed = lambda kind: _scan_progress_update_language() if kind == 'language' else None

        frame = ttk.Frame(self.scan_progress_dialog, padding=15)
        frame.pack(fill="both", expand=True)

        top = ttk.Frame(frame)
        top.pack(fill="x", pady=(0, 10))
        top.columnconfigure(0, weight=1)
        top.columnconfigure(1, weight=0)
        top.columnconfigure(2, weight=1)

        center_group = ttk.Frame(top)
        center_group.grid(row=0, column=1)

        self.scan_progress_title_label = ttk.Label(center_group, text=i18n.t('status_counting_title'), font=("Segoe UI", 10))
        self.scan_progress_title_label.pack(side="left", padx=(0, 10))

        self.scan_progress_spinner = Spinner(center_group, size=26, line_width=3, speed_ms=70, bootstyle='info')
        self.scan_progress_spinner.pack(side="left")
        self.scan_progress_spinner.start()

        action_btns = ttk.Frame(top)
        action_btns.grid(row=0, column=2, sticky="e")

        self.scan_progress_bg_btn = ttk.Button(
            action_btns,
            text=i18n.t('btn_background'),
            command=self._background_scan,
            bootstyle="secondary-outline"
        )
        self.scan_progress_bg_btn.pack(side="left", padx=(0, 8))

        self.scan_progress_stop_btn = ttk.Button(
            action_btns,
            text=i18n.t('btn_stop'),
            command=lambda: self.stop_op(confirm=True),
            bootstyle="danger-outline"
        )
        self.scan_progress_stop_btn.pack(side="left")

        progress_row = ttk.Frame(frame)
        progress_row.pack(fill="x", pady=(0, 8))
        progress_row.columnconfigure(0, weight=1)

        self.scan_progress_bar = ttk.Progressbar(progress_row, mode="determinate", maximum=100.0, value=0.0, bootstyle="info")
        self.scan_progress_bar.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.scan_progress_pct_label = ttk.Label(progress_row, text="", font=("Segoe UI", 9, "bold"))
        self.scan_progress_pct_label.grid(row=0, column=1, sticky="e")

        self.scan_progress_label = ttk.Label(frame, text="", font=("Segoe UI", 8), wraplength=700, justify="left")
        self.scan_progress_label.pack(anchor="w", pady=(0, 8), fill="x")

        self._last_scan_log_line = None
        self.scan_log_text = tk.Text(frame, height=12, wrap="word", state="disabled", font=("Consolas", 9))
        self.scan_log_text.pack(fill="both", expand=True)

        try:
            self.scan_progress_dialog.deiconify()
            self.scan_progress_dialog.lift()
        except Exception:
            try:
                self.scan_progress_dialog.deiconify()
            except Exception:
                pass

        self.scan_progress_dialog.update()

    
    def on_scan_progress_close(self):
        """Backward-compatible alias for unified progress-close handling."""
        self._on_scan_dialog_close()

    def hide_scan_progress(self):
        """Close scan progress dialog"""
        prev_state = getattr(self, "_restore_state_after_background", None)
        try:
            if getattr(self, "btn_stop", None):
                self.btn_stop.config(state="disabled")
        except Exception:
            pass
        try:
            if getattr(self, "scan_progress_spinner", None):
                self.scan_progress_spinner.stop()
        except Exception:
            pass
        try:
            if getattr(self, "scan_progress_bar", None):
                self.scan_progress_bar.stop()
        except Exception:
            pass
        try:
            if getattr(self, "scan_progress_dialog", None) and self.scan_progress_dialog.winfo_exists():
                try:
                    self.scan_progress_dialog.grab_release()
                except Exception:
                    pass
                try:
                    self.scan_progress_dialog.transient(None)
                except Exception:
                    pass
                self.scan_progress_dialog.destroy()
        except Exception:
            pass
        self.scan_running = False
        self.scan_progress_user_closed = False
        was_backgrounded = self.scan_backgrounded
        self.scan_backgrounded = False
        self._set_scan_controls_enabled(True)
        try:
            if getattr(self, "btn_stop", None):
                self.btn_stop.config(state="disabled")
        except Exception:
            pass
        try:
            if getattr(self, "scan_progress_stop_btn", None):
                self.scan_progress_stop_btn.config(state="disabled")
        except Exception:
            pass
        self.scan_progress_dialog = None
        self.scan_progress_bar = None
        self.scan_progress_label = None
        self.scan_progress_pct_label = None
        self.scan_log_text = None
        self.scan_progress_stop_btn = None
        self.scan_progress_bg_btn = None
        self._tray_tooltip_text = ""
        self._tray_progress_phase = None
        self._tray_progress_processed = 0
        self._tray_progress_total = 0
        self._last_scan_log_line = None
        try:
            if self.scan_tray:
                self.scan_tray.hide()
        except Exception:
            pass
        if was_backgrounded:
            def _restore_main():
                try:
                    self.deiconify()
                    if prev_state == "zoomed":
                        try:
                            self.state("zoomed")
                        except Exception:
                            pass
                    self.update_idletasks()
                    self.lift()
                    try:
                        self.attributes("-topmost", True)
                        self.update_idletasks()
                        self.attributes("-topmost", False)
                    except Exception:
                        pass
                    try:
                        self.focus_force()
                    except Exception:
                        try:
                            self.focus_set()
                        except Exception:
                            pass
                except Exception:
                    pass
            _restore_main()
            self._safe_after(50, _restore_main)


    def choose_set_source(self) -> str | None:
        """Ask user where to take paths from: clipboard or file.

        Returns:
            'paste' | 'file' | None
        """
        win = ttk.Toplevel(self)
        win.withdraw()
        apply_app_icon(win)
        win.title(i18n.t('choose_set_source_title'))
        win.geometry("520x220")
        win.transient(self)
        win.grab_set()

        # Center on parent
        win.update_idletasks()
        w, h = 520, 220
        x = self.winfo_x() + (self.winfo_width() // 2) - (w // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (h // 2)
        win.geometry(f"{w}x{h}+{x}+{y}")
        win.deiconify()
        win.lift()

        res = {'v': None}

        frame = ttk.Frame(win, padding=15)
        frame.pack(fill="both", expand=True)

        title_lbl = ttk.Label(frame, text=i18n.t('choose_set_source_title'), font=("Segoe UI", 10, "bold"))
        title_lbl.pack(anchor="w")
        body_lbl = ttk.Label(
            frame,
            text=i18n.t('source_text'),
            justify="left",
            font=("Segoe UI", 9),
        )
        body_lbl.pack(anchor="w", fill="x", pady=(8, 14))

        btns = ttk.Frame(frame)
        btns.pack(fill="x", pady=(10, 0))

        def choose(val):
            res['v'] = val
            try:
                win.destroy()
            except Exception:
                pass

        paste_btn = ttk.Button(btns, text=i18n.t('choose_set_source_paste'), command=lambda: choose('paste'), bootstyle="primary")
        paste_btn.pack(side="left")
        file_btn = ttk.Button(btns, text=i18n.t('choose_set_source_file'), command=lambda: choose('file'), bootstyle="secondary")
        file_btn.pack(side="left", padx=8)
        cancel_btn = ttk.Button(btns, text=i18n.t('choose_set_source_cancel'), command=lambda: choose(None), bootstyle="secondary")
        cancel_btn.pack(side="right")

        def _update_language():
            try:
                win.title(i18n.t('choose_set_source_title'))
                title_lbl.config(text=i18n.t('choose_set_source_title'))
                body_lbl.config(text=i18n.t('source_text'))
                paste_btn.config(text=i18n.t('choose_set_source_paste'))
                file_btn.config(text=i18n.t('choose_set_source_file'))
                cancel_btn.config(text=i18n.t('choose_set_source_cancel'))
            except Exception:
                pass

        win.update_language = _update_language
        win.on_ui_changed = lambda kind: _update_language() if kind == 'language' else None

        win.wait_window()
        return res['v']

    def show_text_report(self, title: str, text: str, *, suggested_name: str | None = None):
        """Show a scrollable text report in a dialog"""
        win = ttk.Toplevel(self)
        win.withdraw()
        apply_app_icon(win)
        win.title(title)
        win.geometry("820x600")
        win.transient(self)

        frame = ttk.Frame(win, padding=12)
        frame.pack(fill="both", expand=True)

        txt = ttk.Text(frame, wrap="none")
        vsb = ttk.Scrollbar(frame, orient="vertical", command=txt.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=txt.xview)
        txt.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        txt.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        txt.insert("1.0", text)
        txt.configure(state="disabled")

        btns = ttk.Frame(frame)
        btns.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        def copy_all():
            try:
                self.clipboard_clear()
                self.clipboard_append(text)
            except Exception:
                pass

        def save_report():
            try:
                # Default name: suggested_name or "report.txt"
                default = suggested_name or "report.txt"
                out = asksaveasfilename_custom(self, 
                    title=i18n.t('save_report_title'),
                    defaultextension=".txt",
                    initialfile=default,
                    filetypes=[(i18n.t('filetype_text'), "*.txt"), (i18n.t('filetype_all'), "*.*")],
                    parent=win,
                )
                if not out:
                    return
                with open(out, "w", encoding="utf-8") as f:
                    f.write(text)
                Messagebox.show_info(i18n.t('report_saved_msg').format(path=out), i18n.t('report_saved_title'), parent=win)
            except Exception as e:
                Messagebox.show_error(i18n.t('report_save_failed_generic'), i18n.t('error'), parent=win)

        save_btn = ttk.Button(btns, text=i18n.t('save_report_btn'), command=save_report, bootstyle="primary")
        save_btn.pack(side="left")

        copy_btn = ttk.Button(btns, text=i18n.t('copy'), command=copy_all, bootstyle="secondary")
        copy_btn.pack(side="left")
        close_btn = ttk.Button(btns, text=i18n.t('close'), command=win.destroy, bootstyle="secondary")
        close_btn.pack(side="right")

        def _update_language():
            try:
                save_btn.config(text=i18n.t('save_report_btn'))
                copy_btn.config(text=i18n.t('copy'))
                close_btn.config(text=i18n.t('close'))
            except Exception:
                pass

        win.update_language = _update_language
        win.on_ui_changed = lambda kind: _update_language() if kind == 'language' else None

        try:
            win.update_idletasks()
            w, h = 820, 600
            x = self.winfo_x() + (self.winfo_width() // 2) - (w // 2)
            y = self.winfo_y() + (self.winfo_height() // 2) - (h // 2)
            win.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            pass
        win.deiconify()
        win.lift()


    def _set_scan_controls_enabled(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        for name in ("btn_build", "btn_set", "btn_view", "btn_exit", "btn_stop"):
            try:
                widget = getattr(self, name, None)
                if widget is not None:
                    widget.config(state=state)
            except Exception:
                continue
        try:
            self.lang_combo.config(state="readonly" if enabled else "disabled")
        except Exception:
            pass
        try:
            self.theme_combo.config(state="readonly" if enabled else "disabled")
        except Exception:
            pass

    def _on_scan_dialog_close(self):
        dlg = getattr(self, "scan_progress_dialog", None)

        if not self.scan_running:
            try:
                if dlg and dlg.winfo_exists():
                    dlg.destroy()
            except Exception:
                pass
            self.scan_progress_dialog = None
            return

        self._handle_active_scan_close(
            title=i18n.t('scan_close_running_title'),
            message=i18n.t('scan_close_running_msg'),
            hide_progress=True,
        )

    def _build_scan_report_text(self, stats: dict) -> str:
        lines = [
            i18n.t('scan_report_summary').format(
                total=stats.get('files_total', 0),
                new=stats.get('new', 0),
                updated=stats.get('updated', 0),
                unchanged=stats.get('unchanged', 0),
                skipped=stats.get('skipped', 0),
                errors=stats.get('errors', 0),
                sha1=stats.get('sha1_computed', 0),
                missing=stats.get('missing', 0),
            ),
            "",
        ]
        roots = stats.get('roots') or []
        if roots:
            lines.append(i18n.t('scan_roots_label'))
            for root in roots:
                lines.append(str(root))
            lines.append("")
        lines.append(i18n.t('scan_report_folders'))
        per_folder = stats.get("per_folder") or {}
        folder_items = sorted(per_folder.items(), key=lambda kv: (0 if (kv[0] in ('', '.', './')) else 1, kv[0].lower()))
        for rel_dir, cnt in folder_items:
            lines.append(f"{cnt}\t{(rel_dir if rel_dir else '.')}" )
        return "\n".join(lines)

    def _is_valid_incremental_db(self, db_path: str):
        """Return (True, "") if db_path looks like an existing File DB Manager SQLite database."""
        try:
            if not db_path or not os.path.isfile(db_path):
                return False, i18n.t('incremental_db_reason_missing')
            con = sqlite3.connect(db_path)
            try:
                cur = con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('files', 'meta')")
                tables = {row[0] for row in cur.fetchall()}
                if not {'files', 'meta'}.issubset(tables):
                    return False, i18n.t('incremental_db_reason_structure')
            finally:
                con.close()
            return True, ""
        except sqlite3.Error:
            return False, i18n.t('incremental_db_reason_sqlite')
        except Exception:
            return False, i18n.t('incremental_db_reason_unknown')

    def build_db(self):
        """Build database from one or more selected folders (runs in background thread so spinner animates)"""
        folders = choose_multiple_folders(self)

        if not folders:
            Messagebox.show_warning(i18n.t('no_scan_folders_selected'), i18n.t('warning'), parent=self)
            return

        run_incremental = self.var_incremental.get()
        db_path = ""

        if run_incremental:
            while True:
                chosen = askopenfilename_custom(self, 
                    title=i18n.t('choose_db_open_title'),
                    filetypes=[(i18n.t('sqlite_db_filetype'), "*.db"), (i18n.t('filetype_all'), "*.*")],
                )
                if not chosen:
                    create_new = Messagebox.yesno(
                        i18n.t('incremental_no_db_selected_text'),
                        i18n.t('incremental_no_db_selected_title'),
                        parent=self,
                    )
                    if not create_new:
                        return
                    chosen = asksaveasfilename_custom(self, 
                        title=i18n.t('choose_db_save_title'),
                        defaultextension=".db",
                        filetypes=[(i18n.t('sqlite_db_filetype'), "*.db"), (i18n.t('filetype_all'), "*.*")],
                    )
                    if not chosen:
                        return
                    run_incremental = False
                    db_path = chosen
                    break

                valid, reason = self._is_valid_incremental_db(chosen)
                if valid:
                    db_path = chosen
                    break

                retry_existing = Messagebox.yesno(
                    i18n.t('incremental_invalid_db_text').format(reason=reason),
                    i18n.t('incremental_invalid_db_title'),
                    parent=self,
                )
                if retry_existing:
                    continue

                chosen = asksaveasfilename_custom(self, 
                    title=i18n.t('choose_db_save_title'),
                    defaultextension=".db",
                    filetypes=[(i18n.t('sqlite_db_filetype'), "*.db"), (i18n.t('filetype_all'), "*.*")],
                )
                if not chosen:
                    return
                run_incremental = False
                db_path = chosen
                break
        else:
            db_path = asksaveasfilename_custom(self, 
                title=i18n.t('choose_db_save_title'),
                defaultextension=".db",
                filetypes=[(i18n.t('sqlite_db_filetype'), "*.db"), (i18n.t('filetype_all'), "*.*")],
            )
            if not db_path:
                return

        self.stop_flag["stop"] = False
        self.scan_running = True
        self.scan_progress_user_closed = False
        self._set_scan_controls_enabled(False)
        self.show_scan_progress()

        # Thread-safe status callback (scan_folders_to_db may call from worker thread)
        def _status_cb(msg):
            # Throttle UI updates so spinner keeps animating
            try:
                import time as _time
                now = _time.monotonic()
                if isinstance(msg, dict) and msg.get('phase') == 'scan':
                    min_gap = 0.08
                else:
                    min_gap = 0.12
                if (now - _status_cb._last) < min_gap:
                    return
                _status_cb._last = now
            except Exception:
                pass

            def _apply_status_payload():
                if isinstance(msg, dict):
                    phase = msg.get('phase')
                    if phase == 'count':
                        count_text = self._format_count_progress_text(int(msg.get('counted') or 0))
                        try:
                            if getattr(self, 'scan_progress_title_label', None):
                                self.scan_progress_title_label.config(text=i18n.t('status_counting_title'))
                        except Exception:
                            pass
                        self._tray_progress_phase = 'count'
                        self._tray_progress_processed = int(msg.get('counted') or 0)
                        self._tray_progress_total = 0
                        self._update_scan_progress_visuals(None, None, show_pct=False)
                        self._set_scan_dialog_status(count_text, log=False)
                        self.set_status(count_text)
                        return
                    if phase == 'count_done':
                        total_count = int(msg.get('counted') or 0)
                        try:
                            if getattr(self, 'scan_progress_title_label', None):
                                self.scan_progress_title_label.config(text=i18n.t('status_scan'))
                        except Exception:
                            pass
                        ready_text = self._format_scan_progress_text({'mode': i18n.t('status_scan'), 'processed': 0, 'total': total_count, 'new': 0, 'updated': 0, 'skipped': 0, 'errors': 0, 'sha1': 0})
                        self._tray_progress_phase = 'scan'
                        self._tray_progress_processed = 0
                        self._tray_progress_total = total_count
                        self._update_scan_progress_visuals(0, total_count, show_pct=True)
                        try:
                            if getattr(self, 'scan_log_text', None):
                                self.scan_log_text.configure(state="normal")
                                self.scan_log_text.delete("1.0", "end")
                                self.scan_log_text.configure(state="disabled")
                            self._last_scan_log_line = None
                        except Exception:
                            pass
                        self._set_scan_dialog_status(ready_text, log=False)
                        self.set_status(ready_text)
                        return
                    if phase == 'scan':
                        try:
                            if getattr(self, 'scan_progress_title_label', None):
                                self.scan_progress_title_label.config(text=i18n.t('status_scan'))
                        except Exception:
                            pass
                        processed = int(msg.get('processed') or 0)
                        total = int(msg.get('total') or 0)
                        self._tray_progress_phase = 'scan'
                        self._tray_progress_processed = processed
                        self._tray_progress_total = total
                        scan_text = self._format_scan_progress_text(msg)
                        self._update_scan_progress_visuals(processed, total, show_pct=True)
                        self._set_scan_dialog_status(scan_text, log=True)
                        self.set_status(scan_text)
                        return
                self._set_scan_dialog_status(str(msg), log=True)
                self.set_status(str(msg))

            try:
                self._safe_after(0, _apply_status_payload)
            except Exception:
                pass
        _status_cb._last = 0.0

        def _done(stats: dict):
            try:
                if self.scan_backgrounded:
                    self._restore_scan_from_background()
                self._tray_progress_phase = None
                self._tray_progress_processed = 0
                self._tray_progress_total = 0
                if stats.get("stopped"):
                    self.set_status(i18n.t('status_scan_stopped'))
                    self._restore_main_before_dialog()
                    Messagebox.show_info(
                        i18n.t('scan_stopped_msg').format(total=self._fmt_num(stats.get('files_total', 0)), errors=self._fmt_num(stats.get('errors', 0))),
                        i18n.t('scan_stopped_title'),
                        parent=self,
                    )
                    self.set_status(i18n.t('status_ready'))
                else:
                    self._update_scan_progress_visuals(stats.get('files_total', 0), stats.get('files_planned', 0))
                    self.set_status(
                        f"{i18n.t('scan_complete')}: {self._fmt_num(stats.get('files_total', 0))} / {self._fmt_num(stats.get('files_planned', 0))} (100.0%) | {i18n.t('stat_new')} {self._fmt_num(stats.get('new', 0))} | {i18n.t('stat_updated')} {self._fmt_num(stats.get('updated', 0))} | {i18n.t('stat_skipped')} {self._fmt_num(stats.get('skipped', 0))} | {i18n.t('stat_errors')} {self._fmt_num(stats.get('errors', 0))}"
                    )

                    toast = ToastNotification(
                        title=i18n.t('scan_complete'),
                        message=f"{i18n.t('scan_complete_msg')}{self._fmt_num(stats.get('files_total', 0))}",
                        duration=3000,
                    )
                    toast.show_toast()

                base = os.path.splitext(os.path.basename(db_path))[0] if db_path else "report"
                report_title = i18n.t('scan_stopped_title') if stats.get('stopped') else i18n.t('scan_complete')
                self.show_text_report(report_title, self._build_scan_report_text(stats), suggested_name=f"report_{base}.txt")
            finally:
                self.hide_scan_progress()

        def _fail(err: Exception):
            try:
                if self.scan_backgrounded:
                    self._restore_scan_from_background()
                self.logger.exception("Scan failed", exc_info=err)
                self._tray_progress_phase = None
                self._tray_progress_processed = 0
                self._tray_progress_total = 0
                self.set_status(i18n.t('error'))
                self._restore_main_before_dialog()
                Messagebox.show_error(i18n.t('scan_failed_generic'), i18n.t('error'), parent=self)
            finally:
                self.hide_scan_progress()

        def _worker():
            try:
                self.logger.info("Starting scan: folders=%s db=%s incremental=%s sha1=%s recursive=%s", folders, db_path, run_incremental, self.var_sha1.get(), self.var_recursive.get())
                stats = scan_folders_to_db(
                    folders,
                    db_path,
                    incremental=run_incremental,
                    compute_sha1=self.var_sha1.get(),
                    recursive=self.var_recursive.get(),
                    status_cb=_status_cb,
                    stop_flag=self.stop_flag,
                )
                self.logger.info("Scan finished: %s", stats)
                self._safe_after(0, _done, stats)
            except Exception as e:
                self._safe_after(0, _fail, e)

        self.scan_thread = threading.Thread(target=_worker, daemon=True)
        self.scan_thread.start()

    def destroy(self):
        self._app_closing = True
        try:
            self._cancel_tray_poll()
        except Exception:
            pass
        try:
            self._cancel_all_afters()
        except Exception:
            pass
        try:
            if getattr(self, "scan_tray", None):
                self.scan_tray.shutdown()
        except Exception:
            pass
        try:
            super().destroy()
        except Exception:
            try:
                self.quit()
            except Exception:
                pass

    def make_set(self):
        """Create or update a set"""
        db_path = askopenfilename_custom(self, 
            title=i18n.t('choose_db_open_title'),
            filetypes=[(i18n.t('sqlite_db_filetype'), "*.db"), (i18n.t('filetype_all'), "*.*")]
        )
        if not db_path:
            return

        name = simple_input(self, i18n.t('set_name_title'), i18n.t('set_name_prompt'))
        if not name:
            return

        choice = self.choose_set_source()
        if choice is None:
            return

        paths: list[str] = []
        try:
            if choice == 'paste':
                # 1) Try Explorer-copied files/folders (Windows)
                paths = get_paths_from_clipboard_win() if IS_WIN else []
                # 2) Fallback to text clipboard (Copy as path, plain text)
                if not paths:
                    try:
                        clip_text = self.clipboard_get()
                    except Exception:
                        clip_text = ""
                    paths = parse_paths_from_text(clip_text)
            else:
                ft = [(i18n.t('text_files_filetype'), "*.txt")]
                if HAS_OPENPYXL:
                    ft = [
                        (i18n.t('text_excel_filetype'), "*.txt *.xlsx *.xlsm *.xltx *.xltm"),
                        (i18n.t('text_files_filetype'), "*.txt"),
                        (i18n.t('excel_files_filetype'), "*.xlsx *.xlsm *.xltx *.xltm"),
                        (i18n.t('filetype_all'), "*.*"),
                    ]
                in_path = askopenfilename_custom(self, title=i18n.t('choose_set_source_file'), filetypes=ft)
                if not in_path:
                    return
                ext = os.path.splitext(in_path)[1].lower()
                if ext == ".txt":
                    with open(in_path, "r", encoding="utf-8", errors="ignore") as f:
                        text = f.read()
                    paths = parse_paths_from_text(text)
                elif ext in (".xlsx", ".xlsm", ".xltx", ".xltm"):
                    paths = read_paths_from_xlsx(in_path)
                else:
                    raise ValueError(i18n.t('unsupported_set_source_filetype'))
        except Exception as e:
            Messagebox.show_error(i18n.t('err_read_paths_generic'), i18n.t('error'), parent=self)
            return

        if not paths:
            Messagebox.show_warning(i18n.t('empty_text'), i18n.t('warning'), parent=self)
            return

        replace = Messagebox.yesno(i18n.t('mode_text'), i18n.t('mode_title'))

        self.stop_flag["stop"] = False
        try:
            self.set_status(i18n.t('status_sync'))
            stats = sync_set_items(
                db_path=db_path,
                set_name=name,
                paths=paths,
                replace=replace,
                status_cb=self.set_status,
                stop_flag=self.stop_flag
            )
            msg = i18n.t('set_summary_full').format(name=name, total=stats['total'], found=stats['found'], missing=stats['missing'], ambiguous=stats['ambiguous'])
            self.set_status(i18n.t('set_status_updated').format(name=name, total=stats['total'], found=stats['found']))
            
            toast = ToastNotification(
                title=i18n.t('set_created'),
                message=i18n.t('set_toast_updated').format(name=name, total=stats['total'], found=stats['found'], ambiguous=stats['ambiguous']),
                duration=3500,
            )
            toast.show_toast()
            
            Messagebox.show_info(msg, i18n.t('info'), parent=self)
            
        except Exception as e:
            self.set_status(i18n.t('error'))
            Messagebox.show_error(i18n.t('set_sync_failed_generic'), i18n.t('error'), parent=self)

    def index_document_content(self):
        db_path = askopenfilename_custom(self, 
            title=i18n.t('choose_db_open_title'),
            filetypes=[(i18n.t('sqlite_db_filetype'), "*.db"), (i18n.t('filetype_all'), "*.*")]
        )
        if not db_path:
            return

        try:
            missing = validate_db_path(db_path)
        except Exception:
            Messagebox.show_error(i18n.t('err_open_db_generic'), i18n.t('error'), parent=self)
            return

        if missing:
            msg = i18n.t('old_db_message').format(tables=', '.join(missing))
            Messagebox.show_error(msg, i18n.t('old_db_title'), parent=self)
            return

        if self.scan_running:
            return

        self.stop_flag["stop"] = False
        self.scan_running = True
        self.scan_backgrounded = False
        self.scan_progress_user_closed = False
        self.show_scan_progress()
        try:
            if getattr(self, 'scan_progress_dialog', None) and self.scan_progress_dialog.winfo_exists():
                self.scan_progress_dialog.title(i18n.t('index_docs_title'))
        except Exception:
            pass
        try:
            if getattr(self, 'scan_progress_title_label', None):
                self.scan_progress_title_label.config(text=i18n.t('index_docs_title'))
        except Exception:
            pass
        try:
            if getattr(self, 'scan_progress_bg_btn', None):
                self.scan_progress_bg_btn.config(text=i18n.t('btn_background'))
        except Exception:
            pass
        try:
            if getattr(self, 'scan_progress_label', None):
                self.scan_progress_label.config(text=db_path)
        except Exception:
            pass
        try:
            if getattr(self, 'scan_progress_bar', None):
                self.scan_progress_bar.configure(mode='determinate', maximum=100.0, value=0.0)
        except Exception:
            pass
        try:
            if getattr(self, 'scan_progress_pct_label', None):
                self.scan_progress_pct_label.config(text='')
        except Exception:
            pass
        self._tray_progress_phase = 'scan'
        self._tray_progress_processed = 0
        self._tray_progress_total = 0
        self.set_status(f"{i18n.t('index_docs_title')}…")
        self._update_tray_tooltip()
        self._set_scan_dialog_status(db_path, log=False)

        def _status_cb(info):
            file = info.get('file') or ''
            processed = int(info.get('processed', 0) or 0)
            total = int(info.get('total', 0) or 0)
            msg = f"{processed}/{total}\n{os.path.basename(file)}" if file else f"{processed}/{total}"
            status_text = f"{i18n.t('index_docs_title')}: {processed}/{total}" if total else f"{i18n.t('index_docs_title')}…"
            def _update_ui():
                try:
                    self.set_status(status_text)
                except Exception:
                    pass
                try:
                    if getattr(self, 'scan_progress_label', None):
                        self.scan_progress_label.config(text=msg)
                except Exception:
                    pass
                try:
                    self._set_scan_dialog_status(msg, log=True)
                except Exception:
                    pass
                try:
                    self._tray_progress_phase = 'scan'
                    self._tray_progress_processed = processed
                    self._tray_progress_total = total
                    self._update_tray_tooltip()
                except Exception:
                    pass
                try:
                    if getattr(self, 'scan_progress_bar', None):
                        pct = (processed / total * 100.0) if total else 0.0
                        self.scan_progress_bar.configure(mode='determinate', maximum=100.0, value=pct)
                        self.scan_progress_pct_label.config(text=(f"{pct:.1f}%" if total else ''))
                except Exception:
                    pass
            self._safe_after(0, _update_ui)

        def _worker():
            try:
                stats = index_document_contents(db_path, status_cb=_status_cb, stop_flag=self.stop_flag)
                def _done():
                    was_backgrounded = self.scan_backgrounded
                    self.scan_running = False
                    self.hide_scan_progress()
                    if stats.get('stopped'):
                        msg = i18n.t('status_scan_stopped')
                        self.set_status(msg)
                        if was_backgrounded:
                            self._restore_main_before_dialog()
                            try:
                                self._append_scan_log(msg)
                            except Exception:
                                pass
                        return
                    if int(stats.get('queued', 0) or 0) == 0:
                        msg = i18n.t('index_docs_nothing_to_do')
                    else:
                        msg = i18n.t('index_docs_summary').format(processed=stats.get('processed',0), ok=stats.get('ok',0), errors=stats.get('errors',0))
                    self.set_status(msg)
                    if was_backgrounded:
                        self._restore_main_before_dialog()
                        try:
                            self._append_scan_log(msg)
                        except Exception:
                            pass
                    else:
                        Messagebox.show_info(msg, i18n.t('index_docs_title'), parent=self)
                self._safe_after(0, _done)
            except Exception as e:
                def _err(err=e):
                    was_backgrounded = self.scan_backgrounded
                    self.scan_running = False
                    self.hide_scan_progress()
                    if was_backgrounded:
                        self._restore_main_before_dialog()
                        self.set_status(str(err))
                        try:
                            self._append_scan_log(str(err))
                        except Exception:
                            pass
                        Messagebox.show_error(str(err), i18n.t('error'))
                    else:
                        Messagebox.show_error(str(err), i18n.t('error'), parent=self)
                self._safe_after(0, _err)
        self.scan_thread = threading.Thread(target=_worker, daemon=True)
        self.scan_thread.start()

    def _choose_viewer_db_path(self):
        """Ask the user for a database path for the viewer.

        This stays intentionally small: choose a file or return nothing.
        No validation and no viewer initialization should happen here.
        """
        return askopenfilename_custom(
            self,
            title=i18n.t('choose_db_open_title'),
            filetypes=[(i18n.t('sqlite_db_filetype'), "*.db"), (i18n.t('filetype_all'), "*.*")],
        )

    def _validate_viewer_db_path(self, db_path: str) -> bool:
        """Validate database structure before opening the viewer.

        Returns True only when the database is suitable for the viewer.
        All user-facing database errors are handled here so the caller can
        remain a straight-through "open viewer" flow.
        """
        try:
            missing = validate_db_path(db_path)
        except Exception:
            Messagebox.show_error(i18n.t('err_open_db_generic'), i18n.t('error'), parent=self)
            return False

        if missing:
            msg = i18n.t('old_db_message').format(tables=', '.join(missing))
            Messagebox.show_error(msg, i18n.t('old_db_title'), parent=self)
            return False

        return True

    def _create_viewer_window(self, db_path: str):
        """Create and initialize the viewer window.

        Viewer creation is separated from database validation so future
        viewer-related features do not complicate the simple "open DB"
        scenario and do not get reported as database-open failures.
        """
        viewer = Viewer(self, db_path)
        viewer.update_language()
        return viewer

    def open_viewer(self):
        """Open database viewer using a simple, linear flow."""
        db_path = self._choose_viewer_db_path()
        if not db_path:
            return

        if not self._validate_viewer_db_path(db_path):
            return

        try:
            self._create_viewer_window(db_path)
        except Exception as e:
            Messagebox.show_error(str(e), i18n.t('error'), parent=self)
