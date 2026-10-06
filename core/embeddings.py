from functools import lru_cache

from sentence_transformers import SentenceTransformer

import config


@lru_cache(maxsize=1)
def _model() -> SentenceTransformer:
    return SentenceTransformer(config.EMBED_MODEL)


def embed(texts: list[str]) -> list[list[float]]:
    return _model().encode(texts, normalize_embeddings=True, show_progress_bar=False).tolist()
