from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import AuditMixin, Base, TenantMixin, UUIDPrimaryKeyMixin


class Workspace(Base, UUIDPrimaryKeyMixin, TenantMixin, AuditMixin):
    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    campaigns: Mapped[list["Campaign"]] = relationship(back_populates="workspace", cascade="all, delete-orphan")


from app.models.campaign import Campaign  # noqa: E402

