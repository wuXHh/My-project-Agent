from __future__ import annotations

from uuid import UUID

from sqlalchemy import ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import AuditMixin, Base, TenantMixin, UUIDPrimaryKeyMixin


class ContentBrief(Base, UUIDPrimaryKeyMixin, TenantMixin, AuditMixin):
    __tablename__ = "content_briefs"

    campaign_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(200))
    audience: Mapped[str | None] = mapped_column(String(400), nullable=True)
    product_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    constraints: Mapped[str | None] = mapped_column(Text, nullable=True)  # 禁用词/合规/口吻等
    references: Mapped[str | None] = mapped_column(Text, nullable=True)  # 链接或说明

    campaign: Mapped["Campaign"] = relationship(back_populates="briefs")
    assets: Mapped[list["Asset"]] = relationship(back_populates="brief", cascade="all, delete-orphan")
    drafts: Mapped[list["Draft"]] = relationship(back_populates="brief", cascade="all, delete-orphan")
    runs: Mapped[list["Run"]] = relationship(back_populates="brief", cascade="all, delete-orphan")


from app.models.campaign import Campaign  # noqa: E402
from app.models.asset import Asset  # noqa: E402
from app.models.draft import Draft  # noqa: E402
from app.models.run import Run  # noqa: E402

