from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.knowledge import KnowledgeChunk
from app.services.embeddings import cosine_sim, dumps_vector, embed_texts, loads_vector


def chunk_text(text: str, *, max_chars: int = 800, overlap: int = 120) -> list[str]:
    text = (text or "").strip()
    if not text:
        return []
    chunks: list[str] = []
    i = 0
    while i < len(text):
        end = min(len(text), i + max_chars)
        chunk = text[i:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        i = max(0, end - overlap)
    return chunks


def index_text(
    db: Session,
    *,
    tenant_id: str,
    brief_id: UUID | None,
    source_asset_id: UUID | None,
    kind: str,
    text: str,
) -> int:
    chunks = chunk_text(text)
    if not chunks:
        return 0
    vectors = embed_texts(chunks)
    for idx, (chunk, vec) in enumerate(zip(chunks, vectors, strict=True)):
        db.add(
            KnowledgeChunk(
                tenant_id=tenant_id,
                brief_id=brief_id,
                source_asset_id=source_asset_id,
                kind=kind,
                chunk_index=idx,
                text=chunk,
                vector_json=dumps_vector(vec),
            )
        )
    db.commit()
    return len(chunks)


@dataclass(frozen=True)
class SearchHit:
    chunk_id: UUID
    score: float
    text: str
    source_asset_id: UUID | None


def search(
    db: Session,
    *,
    tenant_id: str,
    brief_id: UUID | None,
    query: str,
    top_k: int = 5,
) -> list[SearchHit]:
    qvec = embed_texts([query])[0]
    rows = db.query(KnowledgeChunk).filter(KnowledgeChunk.tenant_id == tenant_id)
    if brief_id:
        rows = rows.filter(KnowledgeChunk.brief_id == brief_id)
    rows = rows.limit(500).all()

    scored: list[SearchHit] = []
    for r in rows:
        vec = loads_vector(r.vector_json)
        score = cosine_sim(qvec, vec)
        scored.append(SearchHit(chunk_id=r.id, score=score, text=r.text, source_asset_id=r.source_asset_id))
    scored.sort(key=lambda x: x.score, reverse=True)
    return scored[:top_k]

