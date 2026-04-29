from __future__ import annotations

import hashlib
from pathlib import Path
from typing import BinaryIO

from app.core.config import settings


def _local_base() -> Path:
    return Path(settings.local_storage_dir)


def put_bytes(*, tenant_id: str, key: str, data: bytes) -> str:
    base = _local_base() / tenant_id
    path = base / key
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return str(path)


def sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()

