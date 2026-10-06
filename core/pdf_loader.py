import re
from typing import BinaryIO

from pypdf import PdfReader


def _clean(text: str) -> str:
    text = re.sub(r"-\s*\n\s*(\w)", r"\1", text)  # re-join words hyphenated across lines
    return re.sub(r"\s+", " ", text).strip()


def extract_pages(file: BinaryIO) -> list[dict]:
    """Return [{'page': 1, 'text': '...'}, ...] for pages that contain text."""
    reader = PdfReader(file)
    pages = []
    for number, page in enumerate(reader.pages, start=1):
        text = _clean(page.extract_text() or "")
        if text:
            pages.append({"page": number, "text": text})
    return pages
