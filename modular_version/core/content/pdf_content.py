from __future__ import annotations
from pathlib import Path

from .models import ExtractResult
from .limits import MAX_PDF_OCR_PAGES, PDF_EMBEDDED_SCORE_BAD, PDF_EMBEDDED_SCORE_OK, MAX_EXTRACTED_TEXT_CHARS
from .quality import score_text_quality

def _read_embedded_pdf(path: str, *, stop_flag=None) -> tuple[str, int]:
    try:
        from pypdf import PdfReader
    except Exception as e:
        raise RuntimeError(f'pypdf import failed: {e}')
    reader = PdfReader(path)
    parts = []
    page_count = len(reader.pages)
    for page in reader.pages:
        if stop_flag and stop_flag.get('stop'):
            raise InterruptedError('Stopped by user')
        try:
            txt = page.extract_text() or ''
        except Exception:
            txt = ''
        if txt:
            parts.append(txt.strip())
    text = '\n\n'.join(p for p in parts if p).strip()
    if len(text) > MAX_EXTRACTED_TEXT_CHARS:
        text = text[:MAX_EXTRACTED_TEXT_CHARS]
    return text, page_count

def extract_pdf_document(path: str, *, stop_flag=None) -> ExtractResult:
    from .ocr import ocr_pdf
    embedded_text, page_count = _read_embedded_pdf(path, stop_flag=stop_flag)
    score = score_text_quality(embedded_text, page_count=page_count)
    if embedded_text and score >= PDF_EMBEDDED_SCORE_OK:
        return ExtractResult(text=embedded_text, status='OK', source='pdf_embedded', quality_score=score, page_count=page_count, text_length=len(embedded_text))
    ocr_error = None
    ocr_text = ''
    try:
        ocr_text = ocr_pdf(path, max_pages=MAX_PDF_OCR_PAGES, stop_flag=stop_flag)
    except Exception as e:
        ocr_error = str(e)
    ocr_score = score_text_quality(ocr_text, page_count=page_count) if ocr_text else 0.0
    if ocr_text and ocr_score >= max(score, PDF_EMBEDDED_SCORE_BAD):
        source = 'pdf_ocr' if not embedded_text else 'pdf_mixed'
        return ExtractResult(text=ocr_text[:MAX_EXTRACTED_TEXT_CHARS], status='OK', source=source, quality_score=ocr_score, page_count=page_count, text_length=len(ocr_text))
    if embedded_text:
        status = 'LOW_QUALITY' if score < PDF_EMBEDDED_SCORE_BAD else 'OK'
        return ExtractResult(text=embedded_text, status=status, source='pdf_embedded', quality_score=score, page_count=page_count, text_length=len(embedded_text), error_text=ocr_error)
    return ExtractResult(text='', status='NO_TEXT' if not ocr_error else 'ERROR', source='pdf', quality_score=0.0, page_count=page_count, text_length=0, error_text=ocr_error)
