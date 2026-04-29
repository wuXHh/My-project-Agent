from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import agents, assets, campaigns, briefs, drafts, exports, knowledge, metrics, reviews, runs, workspaces


api_router = APIRouter()
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["workspaces"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(briefs.router, prefix="/briefs", tags=["briefs"])
api_router.include_router(drafts.router, prefix="/drafts", tags=["drafts"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
api_router.include_router(runs.router, prefix="/runs", tags=["runs"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(assets.router, prefix="/assets", tags=["assets"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(exports.router, prefix="/exports", tags=["exports"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])

