from __future__ import annotations

from fastapi import APIRouter

from app.agents.contracts import json_schemas


router = APIRouter()


@router.get("/schemas")
def get_agent_schemas():
    return json_schemas()

