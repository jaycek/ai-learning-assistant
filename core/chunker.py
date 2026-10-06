import config


def chunk_pages(pages: list[dict], chunk_words: int = config.CHUNK_WORDS,
                overlap: int = config.CHUNK_OVERLAP) -> list[dict]:
    """Split each page into overlapping word windows, keeping the page number."""
    step = max(1, chunk_words - overlap)
    chunks = []
    for p in pages:
        words = p["text"].split()
        for start in range(0, len(words), step):
            chunks.append({"text": " ".join(words[start:start + chunk_words]), "page": p["page"]})
            if start + chunk_words >= len(words):
                break
    return chunks
