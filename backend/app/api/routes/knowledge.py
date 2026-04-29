from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_tenant_id
from app.models.asset import Asset
from app.models.brief import ContentBrief
from app.services.rag import index_text, search


router = APIRouter()


class IndexAssetIn(BaseModel):
    asset_id: UUID


class SearchIn(BaseModel):
    brief_id: UUID | None = None
    query: str = Field(min_length=1)
    top_k: int = 5


@router.post("/index_asset")
def index_asset(payload: IndexAssetIn, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    asset = db.query(Asset).filter(Asset.tenant_id == tenant_id, Asset.id == payload.asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    if not asset.text_extracted:
        raise HTTPException(status_code=400, detail="Asset has no extracted text (upload text/*.txt/*.md for MVP)")
    n = index_text(
        db,
        tenant_id=tenant_id,
        brief_id=asset.brief_id,
        source_asset_id=asset.id,
        kind="asset",
        text=asset.text_extracted,
    )
    return {"indexed_chunks": n}


@router.post("/search")
def search_knowledge(payload: SearchIn, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    hits = search(db, tenant_id=tenant_id, brief_id=payload.brief_id, query=payload.query, top_k=payload.top_k)
    return {
        "hits": [
            {"chunk_id": h.chunk_id, "score": h.score, "text": h.text, "source_asset_id": h.source_asset_id}
            for h in hits
        ]
    }

