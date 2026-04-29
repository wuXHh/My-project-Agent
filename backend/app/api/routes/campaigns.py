from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_tenant_id
from app.api.schemas import CampaignCreate, CampaignOut
from app.models.campaign import Campaign
from app.models.workspace import Workspace


router = APIRouter()


@router.post("", response_model=CampaignOut)
def create_campaign(
    payload: CampaignCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    ws = db.query(Workspace).filter(Workspace.tenant_id == tenant_id, Workspace.id == payload.workspace_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    camp = Campaign(tenant_id=tenant_id, workspace_id=payload.workspace_id, name=payload.name, objective=payload.objective)
    db.add(camp)
    db.commit()
    db.refresh(camp)
    return camp


@router.get("", response_model=list[CampaignOut])
def list_campaigns(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id), workspace_id: str | None = None):
    q = db.query(Campaign).filter(Campaign.tenant_id == tenant_id)
    if workspace_id:
        q = q.filter(Campaign.workspace_id == workspace_id)
    return q.order_by(Campaign.created_at.desc()).all()

