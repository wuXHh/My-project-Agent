from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_tenant_id
from app.api.schemas import WorkspaceCreate, WorkspaceOut
from app.models.workspace import Workspace


router = APIRouter()


@router.post("", response_model=WorkspaceOut)
def create_workspace(
    payload: WorkspaceCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    ws = Workspace(tenant_id=tenant_id, name=payload.name, description=payload.description)
    db.add(ws)
    db.commit()
    db.refresh(ws)
    return ws


@router.get("", response_model=list[WorkspaceOut])
def list_workspaces(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return db.query(Workspace).filter(Workspace.tenant_id == tenant_id).order_by(Workspace.created_at.desc()).all()

