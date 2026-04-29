from __future__ import annotations

from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import AuditMixin, Base, TenantMixin, UUIDPrimaryKeyMixin
from app.models.enums import ChannelType, DraftStatus


class Draft(Base, UUIDPrimaryKeyMixin, TenantMixin, AuditMixin):
    __tablename__ = "drafts"

    brief_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("content_briefs.id", ondelete="CASCADE"), index=True
    )
    channel: Mapped[str] = mapped_column(String(40), index=True)  # ChannelType

    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(40), default=DraftStatus.draft.value, index=True)

    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string for structured add-ons

    brief: Mapped["ContentBrief"] = relationship(back_populates="drafts")
    reviews: Mapped[list["Review"]] = relationship(back_populates="draft", cascade="all, delete-orphan")


from app.models.brief import ContentBrief  # noqa: E402
from app.models.review import Review  # noqa: E402

