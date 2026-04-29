from __future__ import annotations

from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import AuditMixin, Base, TenantMixin, UUIDPrimaryKeyMixin
from app.models.enums import RunStage, RunStatus


class Run(Base, UUIDPrimaryKeyMixin, TenantMixin, AuditMixin):
    __tablename__ = "runs"

    brief_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("content_briefs.id", ondelete="CASCADE"), index=True)

    status: Mapped[str] = mapped_column(String(40), default=RunStatus.queued.value, index=True)
    current_stage: Mapped[str | None] = mapped_column(String(40), nullable=True, index=True)
    attempt: Mapped[int] = mapped_column(Integer, default=1)

    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string

    brief: Mapped["ContentBrief"] = relationship(back_populates="runs")
    logs: Mapped[list["RunLog"]] = relationship(back_populates="run", cascade="all, delete-orphan")


class RunLog(Base, UUIDPrimaryKeyMixin, TenantMixin, AuditMixin):
    __tablename__ = "run_logs"

    run_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("runs.id", ondelete="CASCADE"), index=True)
    stage: Mapped[str] = mapped_column(String(40), index=True)  # RunStage
    level: Mapped[str] = mapped_column(String(16), default="INFO", index=True)
    message: Mapped[str] = mapped_column(Text)
    payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    run: Mapped["Run"] = relationship(back_populates="logs")


from app.models.brief import ContentBrief  # noqa: E402

