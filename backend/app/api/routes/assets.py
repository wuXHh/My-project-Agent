from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_tenant_id
from app.api.schemas import AssetOut
from app.models.asset import Asset
from app.models.brief import ContentBrief
from app.services.storage import put_bytes, sha256_bytes


router = APIRouter()


@router.post("/upload", response_model=AssetOut)
async def upload_asset(
    brief_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    brief = db.query(ContentBrief).filter(ContentBrief.tenant_id == tenant_id, ContentBrief.id == brief_id).first()
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")

    data = await file.read()
    digest = sha256_bytes(data)
    key = f"briefs/{brief_id}/assets/{digest}_{file.filename}"
    storage_path = put_bytes(tenant_id=tenant_id, key=key, data=data)

    text_extracted = None
    if (file.content_type or "").startswith("text/") or (file.filename or "").lower().endswith((".txt", ".md")):
        try:
            text_extracted = data.decode("utf-8", errors="ignore")
        except Exception:  # noqa: BLE001
            text_extracted = None

    asset = Asset(
        tenant_id=tenant_id,
        brief_id=brief_id,
        filename=file.filename or "upload.bin",
        content_type=file.content_type,
        size_bytes=len(data),
        storage_key=storage_path,
        sha256=digest,
        text_extracted=text_extracted,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@router.get("", response_model=list[AssetOut])
def list_assets(brief_id: UUID, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return (
        db.query(Asset)
        .filter(Asset.tenant_id == tenant_id, Asset.brief_id == brief_id)
        .order_by(Asset.created_at.desc())
        .all()
    )

