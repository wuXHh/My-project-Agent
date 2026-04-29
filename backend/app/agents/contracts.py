from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.models.enums import ChannelType, RunStage


class FactCard(BaseModel):
    id: str = Field(description="Stable id for citation")
    claim: str
    evidence: str = Field(description="Quoted evidence from uploaded assets/knowledge")
    source_asset_ids: list[str] = Field(default_factory=list)


class StrategyOutput(BaseModel):
    stage: Literal[RunStage.strategy.value] = RunStage.strategy.value
    audience: str | None = None
    value_props: list[str] = Field(default_factory=list)
    channel_strategy: dict[str, Any] = Field(default_factory=dict)


class ResearchOutput(BaseModel):
    stage: Literal[RunStage.research.value] = RunStage.research.value
    fact_cards: list[FactCard] = Field(default_factory=list)


class OutlineSection(BaseModel):
    heading: str
    bullets: list[str] = Field(default_factory=list)


class OutlineOutput(BaseModel):
    stage: Literal[RunStage.outline.value] = RunStage.outline.value
    outlines_by_channel: dict[str, list[OutlineSection]] = Field(default_factory=dict)


class DraftItem(BaseModel):
    channel: str
    title: str | None = None
    content: str
    citations: list[str] = Field(default_factory=list, description="FactCard ids used in this draft")


class WritingOutput(BaseModel):
    stage: Literal[RunStage.writing.value] = RunStage.writing.value
    drafts: list[DraftItem] = Field(default_factory=list)


class EditingOutput(BaseModel):
    stage: Literal[RunStage.editing.value] = RunStage.editing.value
    drafts: list[DraftItem] = Field(default_factory=list)
    change_notes: list[str] = Field(default_factory=list)


class ComplianceIssue(BaseModel):
    severity: Literal["low", "medium", "high"]
    rule: str
    excerpt: str
    suggestion: str | None = None


class ComplianceOutput(BaseModel):
    stage: Literal[RunStage.compliance.value] = RunStage.compliance.value
    issues_by_channel: dict[str, list[ComplianceIssue]] = Field(default_factory=dict)
    risk_level: Literal["green", "yellow", "red"] = "green"


class HumanReviewOutput(BaseModel):
    stage: Literal[RunStage.human_review.value] = RunStage.human_review.value
    gate: Literal["needs_human_review"] = "needs_human_review"


class PackagingItem(BaseModel):
    channel: str
    titles: list[str] = Field(default_factory=list)
    hashtags: list[str] = Field(default_factory=list)
    cta: str | None = None
    script_shots: list[str] = Field(default_factory=list, description="For short video channels")


class PackagingOutput(BaseModel):
    stage: Literal[RunStage.packaging.value] = RunStage.packaging.value
    packages: list[PackagingItem] = Field(default_factory=list)


class MemoryOutput(BaseModel):
    stage: Literal[RunStage.memory.value] = RunStage.memory.value
    stored_items: int = 0


class ExportOutput(BaseModel):
    stage: Literal[RunStage.export.value] = RunStage.export.value
    export_bundle_id: str | None = None


StageOutputModel = (
    StrategyOutput
    | ResearchOutput
    | OutlineOutput
    | WritingOutput
    | EditingOutput
    | ComplianceOutput
    | HumanReviewOutput
    | PackagingOutput
    | MemoryOutput
    | ExportOutput
)


STAGE_OUTPUT_MODELS: dict[RunStage, type[BaseModel]] = {
    RunStage.strategy: StrategyOutput,
    RunStage.research: ResearchOutput,
    RunStage.outline: OutlineOutput,
    RunStage.writing: WritingOutput,
    RunStage.editing: EditingOutput,
    RunStage.compliance: ComplianceOutput,
    RunStage.human_review: HumanReviewOutput,
    RunStage.packaging: PackagingOutput,
    RunStage.memory: MemoryOutput,
    RunStage.export: ExportOutput,
}


def json_schemas() -> dict[str, Any]:
    return {stage.value: model.model_json_schema() for stage, model in STAGE_OUTPUT_MODELS.items()}

