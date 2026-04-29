from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class AuditOut(BaseModel):
    created_at: datetime
    updated_at: datetime
    created_by: str | None = None
    updated_by: str | None = None


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None


class WorkspaceOut(WorkspaceCreate, AuditOut):
    id: UUID


class CampaignCreate(BaseModel):
    workspace_id: UUID
    name: str = Field(min_length=1, max_length=200)
    objective: str | None = None


class CampaignOut(CampaignCreate, AuditOut):
    id: UUID


class BriefCreate(BaseModel):
    campaign_id: UUID
    title: str = Field(min_length=1, max_length=200)
    audience: str | None = None
    product_info: str | None = None
    constraints: str | None = None
    references: str | None = None


class BriefOut(BriefCreate, AuditOut):
    id: UUID


class AssetOut(AuditOut):
    id: UUID
    brief_id: UUID
    filename: str
    content_type: str | None = None
    size_bytes: int | None = None
    storage_key: str
    sha256: str | None = None


class DraftCreate(BaseModel):
    brief_id: UUID
    channel: str
    title: str | None = None
    content: str
    metadata: dict[str, Any] | None = None


class DraftOut(AuditOut):
    id: UUID
    brief_id: UUID
    channel: str
    version: int
    status: str
    title: str | None = None
    content: str
    metadata: dict[str, Any] | None = None


class ReviewCreate(BaseModel):
    draft_id: UUID
    decision: str
    comment: str | None = None


class ReviewOut(ReviewCreate, AuditOut):
    id: UUID


class RunCreate(BaseModel):
    brief_id: UUID
    mode: str = Field(default="sync", description="sync | async")


class RunOut(AuditOut):
    id: UUID
    brief_id: UUID
    status: str
    current_stage: str | None = None
    attempt: int
    error: str | None = None
    result: dict[str, Any] | None = None


class RunLogOut(AuditOut):
    id: UUID
    run_id: UUID
    stage: str
    level: str
    message: str
    payload: dict[str, Any] | None = None

