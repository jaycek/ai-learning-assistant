from functools import lru_cache

import chromadb

import config
from core.embeddings import embed


@lru_cache(maxsize=1)
def _client():
    if config.PERSIST_DIR:
        return chromadb.PersistentClient(path=config.PERSIST_DIR)
    return chromadb.EphemeralClient()  # in-memory: nothing is saved


def add_document(doc_id: str, chunks: list[dict]) -> None:
    """One collection per document, so 'use only this PDF' is enforced structurally."""
    col = _client().get_or_create_collection(doc_id)
    if col.count() > 0:
        return
    for start in range(0, len(chunks), 256):
        batch = chunks[start:start + 256]
        col.add(
            ids=[f"{doc_id}-{start + i:06d}" for i in range(len(batch))],
            documents=[c["text"] for c in batch],
            embeddings=embed([c["text"] for c in batch]),
            metadatas=[{"page": c["page"], "idx": start + i} for i, c in enumerate(batch)],
        )


def query(doc_id: str, text: str, k: int = config.TOP_K) -> list[dict]:
    col = _client().get_collection(doc_id)
    n = min(k, col.count())
    if n == 0:
        return []
    res = col.query(query_embeddings=embed([text]), n_results=n, include=["documents", "metadatas"])
    return [{"text": d, "page": m["page"]} for d, m in zip(res["documents"][0], res["metadatas"][0])]


def get_all_chunks(doc_id: str) -> list[dict]:
    res = _client().get_collection(doc_id).get(include=["documents", "metadatas"])
    rows = sorted(zip(res["metadatas"], res["documents"]), key=lambda r: r[0]["idx"])
    return [{"text": d, "page": m["page"]} for m, d in rows]
