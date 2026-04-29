from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_tenant_id
from app.models.run import Run


router = APIRouter()


@router.get("/runs")
def runs_metrics(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    rows = (
        db.query(Run.status, func.count(Run.id))
        .filter(Run.tenant_id == tenant_id)
        .group_by(Run.status)
        .all()
    )
    by_status = {status: count for status, count in rows}
    latest = (
        db.query(Run)
        .filter(Run.tenant_id == tenant_id)
        .order_by(Run.created_at.desc())
        .limit(20)
        .all()
    )
    return {
        "by_status": by_status,
        "latest": [
            {"id": r.id, "brief_id": r.brief_id, "status": r.status, "current_stage": r.current_stage, "error": r.error}
            for r in latest
        ],
    }

