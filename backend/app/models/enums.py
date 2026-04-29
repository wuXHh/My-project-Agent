from __future__ import annotations

import enum


class ChannelType(str, enum.Enum):
    wecom = "wecom"
    douyin = "douyin"
    xiaohongshu = "xiaohongshu"
    wechat_official = "wechat_official"


class DraftStatus(str, enum.Enum):
    draft = "draft"
    ready_for_review = "ready_for_review"
    approved = "approved"
    rejected = "rejected"


class ReviewDecision(str, enum.Enum):
    approved = "approved"
    rejected = "rejected"


class RunStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"
    cancelled = "cancelled"


class RunStage(str, enum.Enum):
    strategy = "strategy"
    research = "research"
    outline = "outline"
    writing = "writing"
    editing = "editing"
    compliance = "compliance"
    human_review = "human_review"
    packaging = "packaging"
    memory = "memory"
    export = "export"

