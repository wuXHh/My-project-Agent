from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable
from uuid import UUID

from sqlalchemy.orm import Session
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.api.utils import dumps, loads
from app.agents.contracts import STAGE_OUTPUT_MODELS
from app.models.enums import RunStage, RunStatus
from app.models.knowledge import KnowledgeChunk
from app.models.run import Run, RunLog
from app.worker import celery_app


class StageError(RuntimeError):
    pass


@dataclass(frozen=True)
class StageResult:
    stage: RunStage
    output: dict[str, Any]


def _log(db: Session, *, tenant_id: str, run_id: UUID, stage: RunStage, level: str, message: str, payload: Any = None):
    entry = RunLog(
        tenant_id=tenant_id,
        run_id=run_id,
        stage=stage.value,
        level=level,
        message=message,
        payload_json=dumps(payload) if payload is not None else None,
    )
    db.add(entry)
    db.commit()


def _set_run(db: Session, run: Run, *, status: RunStatus | None = None, current_stage: RunStage | None = None, error: str | None = None):
    if status is not None:
        run.status = status.value
    if current_stage is not None:
        run.current_stage = current_stage.value
    if error is not None:
        run.error = error
    db.add(run)
    db.commit()


def start_run(db: Session, *, tenant_id: str, brief_id: UUID, mode: str = "sync") -> Run:
    run = Run(tenant_id=tenant_id, brief_id=brief_id, status=RunStatus.queued.value, current_stage=None, attempt=1)
    db.add(run)
    db.commit()
    db.refresh(run)

    if mode == "async":
        execute_run.delay(str(run.id), tenant_id)
        return run

    _execute_run_sync(db=db, tenant_id=tenant_id, run_id=run.id)
    db.refresh(run)
    return run


def _load_run(db: Session, *, tenant_id: str, run_id: UUID) -> Run:
    run = db.query(Run).filter(Run.tenant_id == tenant_id, Run.id == run_id).first()
    if not run:
        raise StageError("Run not found")
    return run


def _idempotency_key(stage: RunStage) -> str:
    return f"stage:{stage.value}:done"


def _get_context(run: Run) -> dict[str, Any]:
    ctx = loads(run.result_json) or {}
    ctx.setdefault("_meta", {})
    ctx["_meta"].setdefault("stage_durations_ms", {})
    ctx["_meta"].setdefault("llm_usage", {"input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0})
    return ctx


def _save_context(db: Session, run: Run, ctx: dict[str, Any]) -> None:
    run.result_json = dumps(ctx)
    db.add(run)
    db.commit()


def _stage_sequence() -> list[RunStage]:
    return [
        RunStage.strategy,
        RunStage.research,
        RunStage.outline,
        RunStage.writing,
        RunStage.editing,
        RunStage.compliance,
        RunStage.human_review,
        RunStage.packaging,
        RunStage.memory,
        RunStage.export,
    ]


def _run_stage_impl(stage: RunStage, *, db: Session, tenant_id: str, run: Run) -> Callable[[dict[str, Any]], dict[str, Any]]:
    # MVP：真正的 Agent 实现会在后续 todo 里接入；这里先构造满足“结构化契约”的占位输出。
    def _impl(ctx: dict[str, Any]) -> dict[str, Any]:
        if stage == RunStage.strategy:
            return {"stage": stage.value, "audience": None, "value_props": [], "channel_strategy": {}}
        if stage == RunStage.research:
            rows = (
                db.query(KnowledgeChunk)
                .filter(KnowledgeChunk.tenant_id == tenant_id, KnowledgeChunk.brief_id == run.brief_id)
                .order_by(KnowledgeChunk.created_at.desc())
                .limit(8)
                .all()
            )
            fact_cards = []
            for r in rows:
                claim = (r.text.splitlines()[0] if r.text else "").strip()
                claim = claim[:240] if claim else "（资料要点）"
                evidence = r.text[:600]
                fact_cards.append(
                    {
                        "id": f"fc_{r.id}",
                        "claim": claim,
                        "evidence": evidence,
                        "source_asset_ids": [str(r.source_asset_id)] if r.source_asset_id else [],
                    }
                )
            return {"stage": stage.value, "fact_cards": fact_cards}
        if stage == RunStage.outline:
            return {
                "stage": stage.value,
                "outlines_by_channel": {
                    "wecom": [{"heading": "话术结构", "bullets": ["开场", "价值点", "异议处理", "行动号召"]}],
                    "douyin": [{"heading": "分镜", "bullets": ["3秒钩子", "痛点", "解决方案", "CTA"]}],
                    "xiaohongshu": [{"heading": "笔记结构", "bullets": ["种草点", "体验/方法", "避坑", "总结"]}],
                    "wechat_official": [{"heading": "文章结构", "bullets": ["引子", "论点", "案例", "结尾CTA"]}],
                },
            }
        if stage == RunStage.writing:
            fc_ids = [fc["id"] for fc in ctx.get(RunStage.research.value, {}).get("fact_cards", [])]
            citations = fc_ids[:2]
            return {
                "stage": stage.value,
                "drafts": [
                    {"channel": "wecom", "title": "私域触达话术", "content": "（占位）开场…价值点…CTA…", "citations": citations},
                    {"channel": "douyin", "title": "短视频脚本", "content": "（占位）镜头1…镜头2…", "citations": citations},
                    {"channel": "xiaohongshu", "title": "小红书笔记", "content": "（占位）标题…正文…", "citations": citations},
                    {"channel": "wechat_official", "title": "公众号文章", "content": "（占位）引言…正文…结尾…", "citations": citations},
                ],
            }
        if stage == RunStage.editing:
            return {"stage": stage.value, "drafts": ctx.get(RunStage.writing.value, {}).get("drafts", []), "change_notes": []}
        if stage == RunStage.compliance:
            fact_cards = ctx.get(RunStage.research.value, {}).get("fact_cards", [])
            drafts = ctx.get(RunStage.editing.value, {}).get("drafts", []) or ctx.get(RunStage.writing.value, {}).get("drafts", [])
            issues_by_channel: dict[str, list[dict[str, Any]]] = {}
            risk = "green"
            if fact_cards:
                for d in drafts or []:
                    if not d.get("citations"):
                        issues_by_channel.setdefault(d.get("channel", "unknown"), []).append(
                            {
                                "severity": "high",
                                "rule": "FactCardCitationRequired",
                                "excerpt": (d.get("content") or "")[:120],
                                "suggestion": "请基于已索引资料生成 FactCards 并在正文引用对应 FactCard id。",
                            }
                        )
                        risk = "red"
            return {"stage": stage.value, "issues_by_channel": issues_by_channel, "risk_level": risk}
        if stage == RunStage.human_review:
            return {"stage": stage.value, "gate": "needs_human_review"}
        if stage == RunStage.packaging:
            return {
                "stage": stage.value,
                "packages": [
                    {"channel": "wecom", "titles": ["私域触达话术（备选）"], "hashtags": [], "cta": "回复“资料”领取", "script_shots": []},
                    {"channel": "douyin", "titles": ["3秒抓住痛点脚本"], "hashtags": ["#干货"], "cta": "评论区见", "script_shots": ["镜头1：钩子", "镜头2：痛点", "镜头3：解决方案"]},
                    {"channel": "xiaohongshu", "titles": ["我把这个方法用了7天…"], "hashtags": ["#好物分享"], "cta": "收藏+关注", "script_shots": []},
                    {"channel": "wechat_official", "titles": ["从0到1的增长复盘"], "hashtags": [], "cta": "点击阅读原文", "script_shots": []},
                ],
            }
        if stage == RunStage.memory:
            return {"stage": stage.value, "stored_items": 0}
        if stage == RunStage.export:
            return {"stage": stage.value, "export_bundle_id": None}
        return {"stage": stage.value}

    return _impl


@retry(
    retry=retry_if_exception_type(StageError),
    wait=wait_exponential(multiplier=0.5, min=1, max=10),
    stop=stop_after_attempt(3),
)
def _execute_one_stage(db: Session, *, tenant_id: str, run_id: UUID, stage: RunStage) -> None:
    run = _load_run(db, tenant_id=tenant_id, run_id=run_id)
    ctx = _get_context(run)
    meta = ctx["_meta"]

    done_key = _idempotency_key(stage)
    if meta.get(done_key) is True:
        _log(db, tenant_id=tenant_id, run_id=run_id, stage=stage, level="INFO", message="Stage already done; skip")
        return

    _set_run(db, run, status=RunStatus.running, current_stage=stage, error=None)
    _log(db, tenant_id=tenant_id, run_id=run_id, stage=stage, level="INFO", message="Stage start")

    try:
        t0 = datetime.utcnow()
        raw_out = _run_stage_impl(stage, db=db, tenant_id=tenant_id, run=run)(ctx)
        model = STAGE_OUTPUT_MODELS[stage]
        out = model.model_validate(raw_out).model_dump()
        t1 = datetime.utcnow()
        dur_ms = int((t1 - t0).total_seconds() * 1000)
        meta["stage_durations_ms"][stage.value] = dur_ms
    except Exception as e:  # noqa: BLE001
        _log(db, tenant_id=tenant_id, run_id=run_id, stage=stage, level="ERROR", message="Stage error", payload={"error": str(e)})
        raise StageError(str(e)) from e

    ctx[stage.value] = out
    meta[done_key] = True
    _save_context(db, run, ctx)
    _log(
        db,
        tenant_id=tenant_id,
        run_id=run_id,
        stage=stage,
        level="INFO",
        message="Stage done",
        payload={"output_keys": list(out.keys()), "duration_ms": meta["stage_durations_ms"].get(stage.value)},
    )


def _execute_run_sync(db: Session, *, tenant_id: str, run_id: UUID) -> None:
    run = _load_run(db, tenant_id=tenant_id, run_id=run_id)
    _set_run(db, run, status=RunStatus.running, current_stage=None, error=None)

    try:
        for stage in _stage_sequence():
            _execute_one_stage(db, tenant_id=tenant_id, run_id=run_id, stage=stage)
        run = _load_run(db, tenant_id=tenant_id, run_id=run_id)
        _set_run(db, run, status=RunStatus.succeeded, current_stage=None, error=None)
    except Exception as e:  # noqa: BLE001
        run = _load_run(db, tenant_id=tenant_id, run_id=run_id)
        _set_run(db, run, status=RunStatus.failed, error=str(e))


@celery_app.task(name="workflow.execute_run")
def execute_run(run_id: str, tenant_id: str) -> None:
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        _execute_run_sync(db=db, tenant_id=tenant_id, run_id=UUID(run_id))
    finally:
        db.close()

