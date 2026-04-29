from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_tenant_id
from app.api.schemas import BriefCreate, BriefOut
from app.models.brief import ContentBrief
from app.models.campaign import Campaign


router = APIRouter()


@router.post("", response_model=BriefOut)
def create_brief(payload: BriefCreate, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    camp = db.query(Campaign).filter(Campaign.tenant_id == tenant_id, Campaign.id == payload.campaign_id).first()
    if not camp:
        raise HTTPException(status_code=404, detail="Campaign not found")
    brief = ContentBrief(
        tenant_id=tenant_id,
        campaign_id=payload.campaign_id,
        title=payload.title,
        audience=payload.audience,
        product_info=payload.product_info,
        constraints=payload.constraints,
        references=payload.references,
    )
    db.add(brief)
    db.commit()
    db.refresh(brief)
    return brief


@router.get("", response_model=list[BriefOut])
def list_briefs(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id), campaign_id: str | None = None):
    q = db.query(ContentBrief).filter(ContentBrief.tenant_id == tenant_id)
    if campaign_id:
        q = q.filter(ContentBrief.campaign_id == campaign_id)
    return q.order_by(ContentBrief.created_at.desc()).all()

