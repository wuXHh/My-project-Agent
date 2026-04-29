from __future__ import annotations

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db


def get_tenant_id(x_tenant_id: str | None = Header(default="dev-tenant")) -> str:
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="Missing X-Tenant-Id header")
    return x_tenant_id


DbDep = Depends(get_db)
TenantDep = Depends(get_tenant_id)

