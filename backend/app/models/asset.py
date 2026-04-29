from __future__ import annotations

from uuid import UUID

from sqlalchemy import ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import AuditMixin, Base, TenantMixin, UUIDPrimaryKeyMixin


class Asset(Base, UUIDPrimaryKeyMixin, TenantMixin, AuditMixin):
    __tablename__ = "assets"

    brief_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("content_briefs.id", ondelete="CASCADE"), index=True
    )

    filename: Mapped[str] = mapped_column(String(260))
    content_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(nullable=True)

    storage_key: Mapped[str] = mapped_column(String(500))  # local path key / s3 key
    sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    text_extracted: Mapped[str | None] = mapped_column(Text, nullable=True)

    brief: Mapped["ContentBrief"] = relationship(back_populates="assets")


from app.models.brief import ContentBrief  # noqa: E402

