"""Coverage-oriented generation: spread flashcards/questions across the whole document."""
import math
from typing import Callable, Type

from pydantic import BaseModel

import config
from core import llm, vector_store

FOCUS_K = 12


def format_chunks(chunks: list[dict]) -> str:
    return "\n\n".join(f"[Page {c['page']}] {c['text']}" for c in chunks)


def select_chunks(doc_id: str, page_range=None, focus: str | None = None) -> list[dict]:
    if focus and focus.strip():
        chunks = vector_store.query(doc_id, focus.strip(), k=FOCUS_K)
        chunks.sort(key=lambda c: c["page"])
    else:
        chunks = vector_store.get_all_chunks(doc_id)
    if page_range:
        lo, hi = page_range
        chunks = [c for c in chunks if lo <= c["page"] <= hi]
    if not chunks:
        raise ValueError("No text found for that selection.")
    return chunks


def build_batches(chunks: list[dict], n_items: int,
                  group_size: int = config.GROUP_SIZE,
                  max_per_batch: int = config.MAX_ITEMS_PER_BATCH) -> list[tuple[list[dict], int]]:
    """Group chunks and decide how many items to request from each group."""
    groups = [chunks[i:i + group_size] for i in range(0, len(chunks), group_size)]
    needed = max(1, math.ceil(n_items / max_per_batch))
    if needed < len(groups):  # pick evenly spaced groups so the whole document is covered
        if needed == 1:
            idxs = [len(groups) // 2]
        else:
            idxs = [round(i * (len(groups) - 1) / (needed - 1)) for i in range(needed)]
        groups = [groups[i] for i in sorted(set(idxs))]
    base, extra = divmod(n_items, len(groups))
    return [(g, base + (1 if i < extra else 0)) for i, g in enumerate(groups)]


def generate_items(doc_id: str, n: int, model: str, schema: Type[BaseModel], system: str,
                   make_prompt: Callable[[str, int], str], items_attr: str,
                   page_range=None, focus=None,
                   on_progress: Callable[[float], None] | None = None) -> list[tuple]:
    """Run one LLM call per batch. Returns [(item, pages_in_batch), ...]."""
    batches = build_batches(select_chunks(doc_id, page_range, focus), n)
    out, errors = [], []
    for i, (group, count) in enumerate(batches):
        pages = sorted({c["page"] for c in group})
        try:
            result = llm.generate_structured(make_prompt(format_chunks(group), count),
                                             schema, model, system)
            out += [(item, pages) for item in getattr(result, items_attr)[:count]]
        except Exception as e:  # keep going; one bad batch shouldn't kill the run
            errors.append(str(e))
        if on_progress:
            on_progress((i + 1) / len(batches))
    if not out:
        raise RuntimeError("The model returned no usable output. " + (errors[0] if errors else ""))
    return out
