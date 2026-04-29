from __future__ import annotations

from celery import Celery

from app.core.config import settings


celery_app = Celery(
    "multiagent_content_factory",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)
celery_app.conf.update(
    task_always_eager=settings.celery_always_eager,
    task_eager_propagates=True,
    task_track_started=True,
    worker_max_tasks_per_child=200,
)

