from __future__ import annotations

from uuid import UUID

from sqlalchemy import ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import AuditMixin, Base, TenantMixin, UUIDPrimaryKeyMixin
from app.models.enums import ReviewDecision


class Review(Base, UUIDPrimaryKeyMixin, TenantMixin, AuditMixin):
    __tablename__ = "reviews"

    draft_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("drafts.id", ondelete="CASCADE"), index=True)
    decision: Mapped[str] = mapped_column(String(40), index=True)  # ReviewDecision
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    draft: Mapped["Draft"] = relationship(back_populates="reviews")


from app.models.draft import Draft  # noqa: E402

