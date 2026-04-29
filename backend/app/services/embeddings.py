from __future__ import annotations

import json
from functools import lru_cache
from typing import Iterable

import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import settings


@lru_cache(maxsize=1)
def _model() -> SentenceTransformer:
    return SentenceTransformer(settings.embedding_model_name)


def embed_texts(texts: list[str]) -> list[list[float]]:
    m = _model()
    vecs = m.encode(texts, normalize_embeddings=True)
    return [v.astype(np.float32).tolist() for v in vecs]


def cosine_sim(a: list[float], b: list[float]) -> float:
    va = np.array(a, dtype=np.float32)
    vb = np.array(b, dtype=np.float32)
    denom = (np.linalg.norm(va) * np.linalg.norm(vb)) or 1.0
    return float(np.dot(va, vb) / denom)


def dumps_vector(v: list[float]) -> str:
    return json.dumps(v, separators=(",", ":"))


def loads_vector(s: str) -> list[float]:
    return json.loads(s)

