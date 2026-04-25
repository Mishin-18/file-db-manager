from __future__ import annotations
from pathlib import Path
import os
import sys

def get_app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]

def get_content_runtime_dir() -> Path:
    root = get_app_root()
    return root / "content_runtime"

def get_tesseract_exe() -> Path:
    return get_content_runtime_dir() / "tesseract" / "tesseract.exe"

def get_tessdata_dir() -> Path:
    return get_content_runtime_dir() / "tesseract" / "tessdata"

def get_poppler_bin_dir() -> Path:
    return get_content_runtime_dir() / "poppler" / "bin"

def runtime_summary() -> dict:
    tesseract = get_tesseract_exe()
    tessdata = get_tessdata_dir()
    poppler = get_poppler_bin_dir()
    return {
        "content_runtime": str(get_content_runtime_dir()),
        "tesseract": str(tesseract),
        "tesseract_exists": tesseract.exists(),
        "tessdata": str(tessdata),
        "tessdata_exists": tessdata.exists(),
        "poppler_bin": str(poppler),
        "poppler_exists": poppler.exists(),
    }
