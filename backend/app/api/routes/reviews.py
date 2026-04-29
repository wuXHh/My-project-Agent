from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_tenant_id
from app.api.schemas import ReviewCreate, ReviewOut
from app.models.draft import Draft
from app.models.enums import DraftStatus, ReviewDecision
from app.models.review import Review
from app.services.rag import index_text


router = APIRouter()


@router.post("", response_model=ReviewOut)
def create_review(payload: ReviewCreate, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    draft = db.query(Draft).filter(Draft.tenant_id == tenant_id, Draft.id == payload.draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    if payload.decision not in (ReviewDecision.approved.value, ReviewDecision.rejected.value):
        raise HTTPException(status_code=400, detail="Invalid decision")

    review = Review(tenant_id=tenant_id, draft_id=payload.draft_id, decision=payload.decision, comment=payload.comment)
    db.add(review)

    draft.status = DraftStatus.approved.value if payload.decision == ReviewDecision.approved.value else DraftStatus.rejected.value
    db.add(draft)
    db.commit()

    # 通过审核的内容自动沉淀到知识库（可复用）
    if payload.decision == ReviewDecision.approved.value:
        index_text(
            db,
            tenant_id=tenant_id,
            brief_id=draft.brief_id,
            source_asset_id=None,
            kind="approved_content",
            text=draft.content,
        )

    db.refresh(review)
    return review

