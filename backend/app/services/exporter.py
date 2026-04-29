from __future__ import annotations

import io
import json
import zipfile
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.api.utils import dumps
from app.models.draft import Draft
from app.models.enums import DraftStatus
from app.models.export_bundle import ExportBundle
from app.services.storage import put_bytes


def _safe_filename(name: str) -> str:
    return "".join(ch for ch in name if ch.isalnum() or ch in ("-", "_", ".", " ")).strip() or "file"


def create_export_bundle(db: Session, *, tenant_id: str, brief_id: UUID) -> ExportBundle:
    drafts = (
        db.query(Draft)
        .filter(Draft.tenant_id == tenant_id, Draft.brief_id == brief_id, Draft.status == DraftStatus.approved.value)
        .order_by(Draft.channel.asc(), Draft.version.desc())
        .all()
    )
    if not drafts:
        raise ValueError("No approved drafts for this brief")

    # keep latest version per channel
    latest: dict[str, Draft] = {}
    for d in drafts:
        latest.setdefault(d.channel, d)

    manifest: dict[str, Any] = {
        "brief_id": str(brief_id),
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "channels": [],
    }

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for ch, d in latest.items():
            title = d.title or f"{ch}_draft"
            md_name = f"{ch}/{_safe_filename(title)}.md"
            md = f"# {title}\n\n{d.content}\n"
            zf.writestr(md_name, md)
            manifest["channels"].append(
                {
                    "channel": ch,
                    "draft_id": str(d.id),
                    "version": d.version,
                    "title": title,
                    "file": md_name,
                }
            )

        zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))

    bundle_id = uuid4()
    key = f"briefs/{brief_id}/exports/{bundle_id}.zip"
    storage_path = put_bytes(tenant_id=tenant_id, key=key, data=buf.getvalue())

    bundle = ExportBundle(tenant_id=tenant_id, brief_id=brief_id, storage_key=storage_path, manifest_json=dumps(manifest))
    db.add(bundle)
    db.commit()
    db.refresh(bundle)
    return bundle

