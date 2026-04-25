from dataclasses import dataclass
from typing import Optional

@dataclass
class ExtractResult:
    text: str
    status: str
    source: str
    quality_score: float = 0.0
    error_text: Optional[str] = None
    page_count: Optional[int] = None
    text_length: Optional[int] = None
    snippet: Optional[str] = None
