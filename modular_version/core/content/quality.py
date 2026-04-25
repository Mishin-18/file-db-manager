from __future__ import annotations
import re

def score_text_quality(text: str, page_count: int = 1) -> float:
    if not text:
        return 0.0
    total = len(text)
    if total == 0:
        return 0.0
    good_chars = sum(ch.isalnum() or ch.isspace() or ch in ".,;:!?-()[]/%№\n\r\t" for ch in text)
    good_ratio = good_chars / total
    garbage_chars = sum(ch in "�ÐÑÃÆØ¤§±" for ch in text)
    garbage_ratio = garbage_chars / total
    tokens = re.findall(r'\S+', text)
    if not tokens:
        return 0.0
    word_like = [t for t in tokens if re.search(r'[A-Za-zА-Яа-яЁё]', t) and len(t) >= 2]
    word_ratio = len(word_like) / max(len(tokens), 1)
    avg_word_len = sum(len(t) for t in word_like) / len(word_like) if word_like else 0.0
    avg_word_score = min(avg_word_len / 5.0, 1.0)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    avg_line_len = (sum(len(line) for line in lines) / len(lines)) if lines else 0.0
    line_score = min(avg_line_len / 40.0, 1.0) if lines else 0.0
    chars_per_page = total / max(page_count, 1)
    volume_score = min(chars_per_page / 1000.0, 1.0)
    lang_chars = sum((('А' <= ch <= 'я') or ('A' <= ch <= 'Z') or ('a' <= ch <= 'z') or ch in 'Ёё') for ch in text)
    lang_ratio = lang_chars / total
    score = (0.25 * good_ratio + 0.20 * word_ratio + 0.15 * avg_word_score + 0.15 * line_score + 0.15 * volume_score + 0.10 * lang_ratio) - (0.30 * garbage_ratio)
    return max(0.0, min(score, 1.0))
