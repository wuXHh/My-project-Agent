from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_tenant_id
from app.api.utils import loads
from app.models.export_bundle import ExportBundle
from app.services.exporter import create_export_bundle


router = APIRouter()


class ExportCreateIn(BaseModel):
    brief_id: UUID


@router.post("")
def create_export(payload: ExportCreateIn, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    try:
        bundle = create_export_bundle(db, tenant_id=tenant_id, brief_id=payload.brief_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"export_bundle_id": bundle.id, "brief_id": bundle.brief_id, "manifest": loads(bundle.manifest_json)}


@router.get("/{bundle_id}/download")
def download_export(bundle_id: UUID, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    bundle = db.query(ExportBundle).filter(ExportBundle.tenant_id == tenant_id, ExportBundle.id == bundle_id).first()
    if not bundle:
        raise HTTPException(status_code=404, detail="Export bundle not found")
    return FileResponse(path=bundle.storage_key, filename=f"export_{bundle.id}.zip", media_type="application/zip")

