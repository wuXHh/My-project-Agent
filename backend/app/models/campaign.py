from __future__ import annotations

from uuid import UUID

from sqlalchemy import ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import AuditMixin, Base, TenantMixin, UUIDPrimaryKeyMixin


class Campaign(Base, UUIDPrimaryKeyMixin, TenantMixin, AuditMixin):
    __tablename__ = "campaigns"

    workspace_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(200))
    objective: Mapped[str | None] = mapped_column(Text, nullable=True)

    workspace: Mapped["Workspace"] = relationship(back_populates="campaigns")
    briefs: Mapped[list["ContentBrief"]] = relationship(back_populates="campaign", cascade="all, delete-orphan")


from app.models.workspace import Workspace  # noqa: E402
from app.models.brief import ContentBrief  # noqa: E402

