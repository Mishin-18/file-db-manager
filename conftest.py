import importlib.util
import sys
import types
from pathlib import Path
import pytest


SCRIPT_CANDIDATES = [
    Path("file_db_manager.py"),
]


def _build_ttkbootstrap_stub():
    ttk = types.ModuleType("ttkbootstrap")

    class _Dummy:
        def __init__(self, *args, **kwargs):
            pass

        def __getattr__(self, name):
            def _noop(*args, **kwargs):
                return None
            return _noop

    # Common classes referenced in inheritance / construction
    for cls_name in [
        "Window", "Toplevel", "Frame", "Label", "Button", "Entry",
        "Labelframe", "Combobox", "Checkbutton", "Progressbar",
        "Scrollbar", "Treeview", "Panedwindow"
    ]:
        setattr(ttk, cls_name, type(cls_name, (), {}))

    ttk.Style = type("Style", (), {})
    ttk.StringVar = _Dummy
    ttk.BooleanVar = _Dummy
    ttk.IntVar = _Dummy

    constants = types.ModuleType("ttkbootstrap.constants")
    dialogs = types.ModuleType("ttkbootstrap.dialogs")
    widgets = types.ModuleType("ttkbootstrap.widgets")

    class _Messagebox:
        @staticmethod
        def show_error(*args, **kwargs):
            return None

        @staticmethod
        def show_info(*args, **kwargs):
            return None

        @staticmethod
        def yesno(*args, **kwargs):
            return "No"

    class _ToastNotification:
        def __init__(self, *args, **kwargs):
            pass
        def show_toast(self, *args, **kwargs):
            return None

    dialogs.Messagebox = _Messagebox
    widgets.ToastNotification = _ToastNotification

    return ttk, constants, dialogs, widgets


@pytest.fixture(scope="session")
def appmod():
    ttk, constants, dialogs, widgets = _build_ttkbootstrap_stub()
    sys.modules.setdefault("ttkbootstrap", ttk)
    sys.modules.setdefault("ttkbootstrap.constants", constants)
    sys.modules.setdefault("ttkbootstrap.dialogs", dialogs)
    sys.modules.setdefault("ttkbootstrap.widgets", widgets)

    for p in SCRIPT_CANDIDATES:
        if p.exists():
            spec = importlib.util.spec_from_file_location("file_db_manager_app", p)
            module = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(module)
            return module

    pytest.fail("Could not locate the File DB Manager .py script for testing.")
