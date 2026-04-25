import tkinter as tk
from tkinter import Canvas
import math
import ttkbootstrap as ttk

from core.i18n import i18n
from core.ui_common import apply_app_icon


class CustomDialog(ttk.Toplevel):
    def __init__(self, parent=None, title=None, transient=True, **kwargs):
        super().__init__(parent, **kwargs)
        self.withdraw()
        self.title(title or i18n.t("app_title"))
        self.resizable(True, True)
        apply_app_icon(self)
        if transient and parent is not None:
            try:
                self.transient(parent)
            except Exception:
                pass
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def show(self):
        self.deiconify()
        self.lift()
        self.focus_force()
        self.grab_set()
        self.wait_window()


class CustomMessagebox:
    @staticmethod
    def _center_window(win, parent=None):
        try:
            win.update_idletasks()
            if parent is not None and parent.winfo_exists():
                x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (win.winfo_width() // 2)
                y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (win.winfo_height() // 2)
                win.geometry(f"+{max(0, x)}+{max(0, y)}")
        except Exception:
            pass

    @staticmethod
    def _prepare_parent(parent=None):
        host = parent
        if host is None:
            return None, None
        try:
            if not host.winfo_exists():
                return None, None
        except Exception:
            return None, None

        state_before = None
        try:
            state_before = host.state()
        except Exception:
            try:
                state_before = host.wm_state()
            except Exception:
                state_before = None

        try:
            if state_before in ("withdrawn", "iconic"):
                host.deiconify()
        except Exception:
            pass
        try:
            host.update_idletasks()
        except Exception:
            pass
        try:
            host.lift()
        except Exception:
            pass
        try:
            host.attributes("-topmost", True)
            host.update_idletasks()
            host.attributes("-topmost", False)
        except Exception:
            pass
        try:
            host.focus_force()
        except Exception:
            try:
                host.focus_set()
            except Exception:
                pass
        return host, state_before

    @staticmethod
    def _present_dialog(dlg, parent=None):
        host, host_state = CustomMessagebox._prepare_parent(parent)
        if host is not None:
            try:
                dlg.transient(host)
            except Exception:
                pass
        CustomMessagebox._center_window(dlg, host)
        try:
            dlg.deiconify()
            dlg.update_idletasks()
        except Exception:
            pass
        try:
            dlg.lift()
        except Exception:
            pass
        try:
            dlg.attributes("-topmost", True)
        except Exception:
            pass
        try:
            dlg.wait_visibility()
        except Exception:
            pass
        try:
            dlg.grab_set()
        except Exception:
            pass
        try:
            dlg.focus_force()
        except Exception:
            try:
                dlg.focus_set()
            except Exception:
                pass
        try:
            dlg.wait_window()
        finally:
            try:
                if host is not None and host.winfo_exists():
                    try:
                        if host_state in ("withdrawn", "iconic"):
                            host.deiconify()
                        elif host_state == "zoomed":
                            host.state("zoomed")
                    except Exception:
                        pass
                    host.lift()
                    host.attributes("-topmost", True)
                    host.update_idletasks()
                    host.attributes("-topmost", False)
                    try:
                        host.focus_force()
                    except Exception:
                        try:
                            host.focus_set()
                        except Exception:
                            pass
            except Exception:
                pass

    @staticmethod
    def _single_button_text():
        return i18n.t("ok")

    @staticmethod
    def _show(message, title, parent=None, kind="info", buttons=("ok",)):
        result = {"value": None}

        dlg = ttk.Toplevel(parent)
        try:
            dlg.withdraw()
        except Exception:
            pass

        apply_app_icon(dlg)
        dlg.title(title)
        dlg.resizable(False, False)
        dlg.minsize(720, 320)
        dlg.geometry("920x400")


        def close_with(value):
            result["value"] = value
            try:
                dlg.grab_release()
            except Exception:
                pass
            try:
                dlg.attributes("-topmost", False)
            except Exception:
                pass
            dlg.destroy()

        dlg.protocol(
            "WM_DELETE_WINDOW",
            lambda: close_with(False if "yes" in buttons or "no" in buttons else True)
        )

        container = ttk.Frame(dlg, padding=16)
        container.pack(fill="both", expand=True)

        head_style = {
            "info": "info",
            "warning": "warning",
            "error": "danger",
            "question": "primary",
        }.get(kind, "secondary")

        title_row = ttk.Frame(container)
        title_row.pack(fill="x", pady=(0, 10))

        ttk.Label(
            title_row,
            text=title,
            bootstyle=f"{head_style}",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w")

        msg = ttk.Label(
            container,
            text=message,
            justify="left",
            anchor="w"
        )
        msg.pack(anchor="w", fill="x")

        def _update_wrap(_event=None):
            try:
                msg.configure(wraplength=max(320, container.winfo_width() - 24))
            except Exception:
                pass

        container.bind("<Configure>", _update_wrap, add="+")
        _update_wrap()

        btns = ttk.Frame(container)
        btns.pack(fill="x", pady=(16, 0))

        if buttons == ("ok",):
            ok_text = CustomMessagebox._single_button_text()
            tk.Button(
                btns,
                text=ok_text,
                width=14,
                relief="raised",
                padx=10,
                pady=3,
                command=lambda: close_with(True)
            ).pack(side="right")
            dlg.bind("<Return>", lambda e: close_with(True))
            dlg.bind("<Escape>", lambda e: close_with(True))

        elif buttons == ("yes", "no"):
            ttk.Button(
                btns,
                text=i18n.t("yes"),
                bootstyle=head_style,
                command=lambda: close_with(True)
            ).pack(side="right")

            ttk.Button(
                btns,
                text=i18n.t("no"),
                bootstyle="secondary",
                command=lambda: close_with(False)
            ).pack(side="right", padx=(0, 8))

            dlg.bind("<Return>", lambda e: close_with(True))
            dlg.bind("<Escape>", lambda e: close_with(False))

        CustomMessagebox._present_dialog(dlg, parent)
        return result["value"]


    @staticmethod
    def ask_scan_close_action(message, title, parent=None):
        result = {"value": "cancel"}

        dlg = ttk.Toplevel(parent)
        try:
            dlg.withdraw()
        except Exception:
            pass

        apply_app_icon(dlg)
        dlg.title(title)
        dlg.resizable(False, False)
        dlg.minsize(760, 340)
        dlg.geometry("960x420")


        def close_with(value):
            result["value"] = value
            try:
                dlg.grab_release()
            except Exception:
                pass
            try:
                dlg.attributes("-topmost", False)
            except Exception:
                pass
            dlg.destroy()

        dlg.protocol("WM_DELETE_WINDOW", lambda: close_with("cancel"))

        container = ttk.Frame(dlg, padding=16)
        container.pack(fill="both", expand=True)

        title_row = ttk.Frame(container)
        title_row.pack(fill="x", pady=(0, 10))

        ttk.Label(
            title_row,
            text=title,
            bootstyle="primary",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w")

        msg = ttk.Label(container, text=message, justify="left", anchor="w")
        msg.pack(anchor="w", fill="x")

        def _update_wrap(_event=None):
            try:
                msg.configure(wraplength=max(340, container.winfo_width() - 24))
            except Exception:
                pass

        container.bind("<Configure>", _update_wrap, add="+")
        _update_wrap()

        btns = ttk.Frame(container)
        btns.pack(fill="x", pady=(16, 0))

        ttk.Button(
            btns,
            text=i18n.t("cancel"),
            bootstyle="secondary",
            command=lambda: close_with("cancel")
        ).pack(side="right")

        ttk.Button(
            btns,
            text=i18n.t("btn_stop"),
            bootstyle="danger-outline",
            command=lambda: close_with("stop")
        ).pack(side="right", padx=(0, 8))

        ttk.Button(
            btns,
            text=i18n.t("btn_background"),
            bootstyle="primary",
            command=lambda: close_with("background")
        ).pack(side="left")

        CustomMessagebox._present_dialog(dlg, parent)
        return result["value"]

    @staticmethod
    def show_info(message, title, parent=None):
        CustomMessagebox._show(message=message, title=title, parent=parent, kind="info", buttons=("ok",))

    @staticmethod
    def show_error(message, title, parent=None):
        CustomMessagebox._show(message=message, title=title, parent=parent, kind="error", buttons=("ok",))

    @staticmethod
    def show_warning(message, title, parent=None):
        CustomMessagebox._show(message=message, title=title, parent=parent, kind="warning", buttons=("ok",))

    @staticmethod
    def yesno(message, title, parent=None):
        return bool(
            CustomMessagebox._show(
                message=message,
                title=title,
                parent=parent,
                kind="question",
                buttons=("yes", "no"),
            )
        )


class ToolTip:
    def __init__(self, widget, text="", delay_ms=250):
        self.widget = widget
        self.text = text
        self.tip = None
        self._job = None
        self.delay_ms = int(delay_ms)
        widget.bind("<Enter>", self._schedule_show, add="+")
        widget.bind("<Leave>", self._leave, add="+")
        widget.bind("<ButtonPress>", self._leave, add="+")
        widget.bind("<Destroy>", self._leave, add="+")
        widget.bind("<Configure>", self._reposition, add="+")

    def _schedule_show(self, _event=None):
        self._cancel_job()
        if self.tip or not self.text:
            return
        try:
            self._job = self.widget.after(self.delay_ms, self._show)
        except Exception:
            self._show()

    def _cancel_job(self):
        if self._job is not None:
            try:
                self.widget.after_cancel(self._job)
            except Exception:
                pass
            self._job = None

    def _compute_geometry(self, tip_width: int, tip_height: int):
        try:
            screen_w = int(self.widget.winfo_screenwidth())
            screen_h = int(self.widget.winfo_screenheight())
            ptr_x = int(self.widget.winfo_pointerx())
            ptr_y = int(self.widget.winfo_pointery())
            root_x = int(self.widget.winfo_rootx())
            root_y = int(self.widget.winfo_rooty())
            w = int(self.widget.winfo_width())
            h = int(self.widget.winfo_height())
        except Exception:
            return 20, 20

        pad = 12
        cursor_dx = 18
        cursor_dy = 20

        x = ptr_x + cursor_dx
        y = ptr_y + cursor_dy

        if x + tip_width + pad > screen_w:
            x = ptr_x - tip_width - cursor_dx
        if y + tip_height + pad > screen_h:
            y = ptr_y - tip_height - cursor_dy

        # Fallback to widget-based placement when pointer-based placement still fails.
        if x < pad or x + tip_width + pad > screen_w:
            x = root_x + w - tip_width - 16
        if y < pad or y + tip_height + pad > screen_h:
            y = root_y - tip_height - 8
            if y < pad:
                y = root_y + h + 8

        max_x = max(pad, screen_w - tip_width - pad)
        max_y = max(pad, screen_h - tip_height - pad)
        x = max(pad, min(x, max_x))
        y = max(pad, min(y, max_y))
        return x, y

    def _show(self):
        self._cancel_job()
        if self.tip or not self.text:
            return
        self.tip = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        try:
            tw.attributes("-topmost", True)
        except Exception:
            pass
        lbl = ttk.Label(
            tw,
            text=self.text,
            bootstyle="inverse-secondary",
            padding=(8, 4),
            justify="left",
            wraplength=420,
        )
        lbl.pack()
        try:
            tw.update_idletasks()
            tip_w = int(tw.winfo_reqwidth())
            tip_h = int(tw.winfo_reqheight())
            x, y = self._compute_geometry(tip_w, tip_h)
            tw.wm_geometry(f"+{x}+{y}")
        except Exception:
            pass

    def _reposition(self, _event=None):
        if not self.tip:
            return
        try:
            self.tip.update_idletasks()
            tip_w = int(self.tip.winfo_reqwidth())
            tip_h = int(self.tip.winfo_reqheight())
            x, y = self._compute_geometry(tip_w, tip_h)
            self.tip.wm_geometry(f"+{x}+{y}")
        except Exception:
            pass

    def _leave(self, _event=None):
        self._cancel_job()
        if self.tip:
            try:
                self.tip.destroy()
            except Exception:
                pass
            self.tip = None


class HelpAffordance:
    SHORT_ICON = "?"
    LONG_ICON = "ⓘ"

    def __init__(self, button, text_getter, title_getter=None, parent_getter=None, short_tooltip_text_getter=None, width=3):
        self.button = button
        self.text_getter = text_getter
        self.title_getter = title_getter
        self.parent_getter = parent_getter or (lambda: None)
        self.short_tooltip_text_getter = short_tooltip_text_getter or text_getter
        self.width = int(width)
        self.tooltip = ToolTip(button, "")
        self.apply()

    @staticmethod
    def _line_count(text: str) -> int:
        normalized = (text or '').replace('\r\n', '\n').replace('\r', '\n').strip('\n')
        if not normalized.strip():
            return 0
        return len(normalized.split('\n'))

    def _is_short(self, text: str) -> bool:
        return self._line_count(text) <= 3

    def apply(self):
        text = self.text_getter() or ''
        title = self.title_getter() if callable(self.title_getter) else None
        is_short = self._is_short(text)

        if is_short:
            tooltip_text = self.short_tooltip_text_getter() or text
            self.tooltip.text = tooltip_text
            try:
                self.button.configure(text=self.SHORT_ICON, width=self.width, command=lambda: None)
            except Exception:
                pass
        else:
            self.tooltip.text = i18n.t('tt_help_btn')
            def _show_long_help():
                CustomMessagebox.show_info(text, title or i18n.t('help_title'), parent=self.parent_getter())
            try:
                self.button.configure(text=self.LONG_ICON, width=self.width, command=_show_long_help)
            except Exception:
                pass


def attach_help(button, text_getter, title_getter=None, parent_getter=None, short_tooltip_text_getter=None, width=3):
    return HelpAffordance(
        button=button,
        text_getter=text_getter,
        title_getter=title_getter,
        parent_getter=parent_getter,
        short_tooltip_text_getter=short_tooltip_text_getter,
        width=width,
    )


class Spinner(ttk.Frame):
    def __init__(self, parent, size=28, line_width=3, speed_ms=24, bootstyle='info', **kwargs):
        super().__init__(parent, **kwargs)
        self.size = int(size)
        self.line_width = int(line_width)
        self.speed_ms = int(speed_ms)
        self.bootstyle = bootstyle
        bg = None
        try:
            bg = self.cget("background")
        except Exception:
            bg = None
        self.canvas = Canvas(
            self,
            width=self.size,
            height=self.size,
            highlightthickness=0,
            bd=0,
            relief="flat",
            bg=bg,
        )
        self.canvas.pack(fill="both", expand=True)
        self._running = False
        self._job = None
        self._angle = 0.0
        self._phase = 0.0

    def _get_color(self):
        style_map = {
            "info": "#0dcaf0",
            "primary": "#0d6efd",
            "success": "#198754",
            "warning": "#ffc107",
            "danger": "#dc3545",
            "secondary": "#6c757d",
        }
        key = str(self.bootstyle).split("-")[0]
        return style_map.get(key, "#0d6efd")

    def _draw(self):
        self.canvas.delete("all")
        pad = self.line_width + 1
        x1 = pad
        y1 = pad
        x2 = self.size - pad
        y2 = self.size - pad
        extent = 35 + 210 * ((math.sin(self._phase) + 1) / 2)
        self.canvas.create_arc(
            x1, y1, x2, y2,
            start=self._angle,
            extent=extent,
            style="arc",
            width=self.line_width,
            outline=self._get_color(),
        )
        tail_extent = max(12, extent * 0.18)
        self.canvas.create_arc(
            x1, y1, x2, y2,
            start=self._angle - tail_extent - 8,
            extent=tail_extent,
            style="arc",
            width=max(1, self.line_width - 1),
            outline="#b9c2cc",
        )

    def _tick(self):
        if not self._running:
            self.canvas.delete("all")
            self._job = None
            return
        self._angle = (self._angle + 9) % 360
        self._phase += 0.16
        self._draw()
        self._job = self.after(self.speed_ms, self._tick)

    def start(self):
        if self._running:
            return
        self._running = True
        self._tick()

    def stop(self):
        self._running = False
        if self._job is not None:
            try:
                self.after_cancel(self._job)
            except Exception:
                pass
            self._job = None
        self.canvas.delete("all")
