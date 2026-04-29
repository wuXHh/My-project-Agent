from __future__ import annotations

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings


def create_app() -> FastAPI:
    settings.ensure_dirs()
    app = FastAPI(title=settings.app_name)
    app.include_router(api_router, prefix="/api")

    @app.get("/healthz")
    def healthz():
        return {"ok": True, "app": settings.app_name, "env": settings.app_env}

    return app


app = create_app()

