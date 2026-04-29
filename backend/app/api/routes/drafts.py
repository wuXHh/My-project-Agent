from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_tenant_id
from app.api.schemas import DraftCreate, DraftOut
from app.api.utils import dumps, loads
from app.models.brief import ContentBrief
from app.models.draft import Draft


router = APIRouter()


@router.post("", response_model=DraftOut)
def create_draft(payload: DraftCreate, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    brief = db.query(ContentBrief).filter(ContentBrief.tenant_id == tenant_id, ContentBrief.id == payload.brief_id).first()
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    last = (
        db.query(Draft)
        .filter(Draft.tenant_id == tenant_id, Draft.brief_id == payload.brief_id, Draft.channel == payload.channel)
        .order_by(Draft.version.desc())
        .first()
    )
    version = (last.version + 1) if last else 1
    draft = Draft(
        tenant_id=tenant_id,
        brief_id=payload.brief_id,
        channel=payload.channel,
        version=version,
        title=payload.title,
        content=payload.content,
        metadata_json=dumps(payload.metadata) if payload.metadata else None,
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return DraftOut(
        id=draft.id,
        brief_id=payload.brief_id,
        channel=draft.channel,
        version=draft.version,
        status=draft.status,
        title=draft.title,
        content=draft.content,
        metadata=loads(draft.metadata_json),
        created_at=draft.created_at,
        updated_at=draft.updated_at,
        created_by=draft.created_by,
        updated_by=draft.updated_by,
    )


@router.get("", response_model=list[DraftOut])
def list_drafts(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id), brief_id: str | None = None):
    q = db.query(Draft).filter(Draft.tenant_id == tenant_id)
    if brief_id:
        q = q.filter(Draft.brief_id == brief_id)
    drafts = q.order_by(Draft.created_at.desc()).all()
    return [
        DraftOut(
            id=d.id,
            brief_id=d.brief_id,
            channel=d.channel,
            version=d.version,
            status=d.status,
            title=d.title,
            content=d.content,
            metadata=loads(d.metadata_json),
            created_at=d.created_at,
            updated_at=d.updated_at,
            created_by=d.created_by,
            updated_by=d.updated_by,
        )
        for d in drafts
    ]


@router.get("/{draft_id}/diff")
def diff_drafts(
    draft_id: UUID,
    other_id: UUID,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    import difflib

    a = db.query(Draft).filter(Draft.tenant_id == tenant_id, Draft.id == draft_id).first()
    b = db.query(Draft).filter(Draft.tenant_id == tenant_id, Draft.id == other_id).first()
    if not a or not b:
        raise HTTPException(status_code=404, detail="Draft not found")
    if a.brief_id != b.brief_id:
        raise HTTPException(status_code=400, detail="Drafts must belong to same brief")

    diff = difflib.unified_diff(
        (a.content or "").splitlines(),
        (b.content or "").splitlines(),
        fromfile=f"{a.channel}@v{a.version}",
        tofile=f"{b.channel}@v{b.version}",
        lineterm="",
    )
    return {"diff": "\n".join(diff)}

