import sys

IS_WIN = sys.platform.startswith("win")

try:
    import openpyxl  # type: ignore
    HAS_OPENPYXL = True
except Exception:
    HAS_OPENPYXL = False
