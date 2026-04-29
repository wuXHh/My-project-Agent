from __future__ import annotations

from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import AuditMixin, Base, TenantMixin, UUIDPrimaryKeyMixin


class KnowledgeChunk(Base, UUIDPrimaryKeyMixin, TenantMixin, AuditMixin):
    """
    MVP: 向量以 JSON 字符串存储，SQLite 可直接运行。
    未来切 Postgres + pgvector 时可将 vector_json 迁移为 vector 类型并加索引。
    """

    __tablename__ = "knowledge_chunks"

    brief_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("content_briefs.id", ondelete="CASCADE"), nullable=True, index=True
    )
    source_asset_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("assets.id", ondelete="SET NULL"), nullable=True, index=True
    )

    kind: Mapped[str] = mapped_column(String(40), default="asset")  # asset | approved_content | brand_guide
    chunk_index: Mapped[int] = mapped_column(Integer, default=0)
    text: Mapped[str] = mapped_column(Text)
    vector_json: Mapped[str] = mapped_column(Text)  # JSON list[float]

    asset: Mapped["Asset | None"] = relationship()


from app.models.asset import Asset  # noqa: E402

