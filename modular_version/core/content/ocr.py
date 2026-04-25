from __future__ import annotations
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
from typing import Optional

from .runtime_paths import get_tesseract_exe, get_tessdata_dir, get_poppler_bin_dir
from core.proc import run_quiet_interruptible

def _find_program(name: str) -> Optional[str]:
    return shutil.which(name)

def available_ocr_runtime() -> dict:
    tesseract = get_tesseract_exe()
    poppler_dir = get_poppler_bin_dir()
    return {
        "tesseract": str(tesseract if tesseract.exists() else (_find_program('tesseract') or '')),
        "poppler_dir": str(poppler_dir if poppler_dir.exists() else ''),
        "ok": bool((tesseract.exists() or _find_program('tesseract')) and poppler_dir.exists()),
    }

def ocr_pdf(path: str, *, lang: str = 'rus+eng', max_pages: int = 30, stop_flag=None) -> str:
    tesseract = get_tesseract_exe()
    tesseract_cmd = str(tesseract) if tesseract.exists() else (_find_program('tesseract') or '')
    poppler_dir = get_poppler_bin_dir()
    pdftoppm = poppler_dir / ('pdftoppm.exe' if os.name == 'nt' else 'pdftoppm')
    if not tesseract_cmd:
        raise RuntimeError('Tesseract not found in content_runtime or PATH')
    if not pdftoppm.exists():
        raise RuntimeError('pdftoppm not found in content_runtime/poppler/bin')
    tessdata_dir = get_tessdata_dir()
    env = os.environ.copy()
    if tessdata_dir.exists():
        env['TESSDATA_PREFIX'] = str(tessdata_dir)
    pages_text = []
    with tempfile.TemporaryDirectory(prefix='fdbm_pdfocr_') as td:
        td_path = Path(td)
        prefix = td_path / 'page'
        cmd = [str(pdftoppm), '-f', '1', '-l', str(max_pages), '-r', '200', '-png', path, str(prefix)]
        run_quiet_interruptible(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stop_flag=stop_flag)
        images = sorted(td_path.glob('page-*.png'))
        for img in images:
            if stop_flag and stop_flag.get('stop'):
                raise InterruptedError('Stopped by user')
            outbase = img.with_suffix('')
            cmd = [tesseract_cmd, str(img), str(outbase), '-l', lang]
            if stop_flag and stop_flag.get('stop'):
                raise InterruptedError('Stopped by user')
            run_quiet_interruptible(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, stop_flag=stop_flag)
            txt = outbase.with_suffix('.txt')
            if txt.exists():
                try:
                    pages_text.append(txt.read_text(encoding='utf-8', errors='ignore'))
                except Exception:
                    pages_text.append(txt.read_text(errors='ignore'))
    return '\n\n'.join(pages_text).strip()
