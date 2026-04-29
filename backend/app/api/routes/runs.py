from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_tenant_id
from app.api.schemas import RunCreate, RunLogOut, RunOut
from app.api.utils import loads
from app.models.brief import ContentBrief
from app.models.run import Run, RunLog
from app.services.workflow import start_run


router = APIRouter()


@router.post("", response_model=RunOut)
def create_run(payload: RunCreate, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    brief = db.query(ContentBrief).filter(ContentBrief.tenant_id == tenant_id, ContentBrief.id == payload.brief_id).first()
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    run = start_run(db=db, tenant_id=tenant_id, brief_id=payload.brief_id, mode=payload.mode)
    db.refresh(run)
    return RunOut(
        id=run.id,
        brief_id=run.brief_id,
        status=run.status,
        current_stage=run.current_stage,
        attempt=run.attempt,
        error=run.error,
        result=loads(run.result_json),
        created_at=run.created_at,
        updated_at=run.updated_at,
        created_by=run.created_by,
        updated_by=run.updated_by,
    )


@router.get("", response_model=list[RunOut])
def list_runs(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id), brief_id: str | None = None):
    q = db.query(Run).filter(Run.tenant_id == tenant_id)
    if brief_id:
        q = q.filter(Run.brief_id == brief_id)
    runs = q.order_by(Run.created_at.desc()).all()
    return [
        RunOut(
            id=r.id,
            brief_id=r.brief_id,
            status=r.status,
            current_stage=r.current_stage,
            attempt=r.attempt,
            error=r.error,
            result=loads(r.result_json),
            created_at=r.created_at,
            updated_at=r.updated_at,
            created_by=r.created_by,
            updated_by=r.updated_by,
        )
        for r in runs
    ]


@router.get("/{run_id}/logs", response_model=list[RunLogOut])
def list_run_logs(run_id: UUID, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    logs = (
        db.query(RunLog)
        .filter(RunLog.tenant_id == tenant_id, RunLog.run_id == run_id)
        .order_by(RunLog.created_at.asc())
        .all()
    )
    return [
        RunLogOut(
            id=l.id,
            run_id=l.run_id,
            stage=l.stage,
            level=l.level,
            message=l.message,
            payload=loads(l.payload_json),
            created_at=l.created_at,
            updated_at=l.updated_at,
            created_by=l.created_by,
            updated_by=l.updated_by,
        )
        for l in logs
    ]

