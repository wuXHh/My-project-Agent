from __future__ import annotations

from uuid import UUID

from sqlalchemy import ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import AuditMixin, Base, TenantMixin, UUIDPrimaryKeyMixin


class ExportBundle(Base, UUIDPrimaryKeyMixin, TenantMixin, AuditMixin):
    __tablename__ = "export_bundles"

    brief_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("content_briefs.id", ondelete="CASCADE"), index=True)
    storage_key: Mapped[str] = mapped_column(String(500))
    manifest_json: Mapped[str] = mapped_column(Text)  # JSON string

