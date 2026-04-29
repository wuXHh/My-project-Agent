from __future__ import annotations

import json
from typing import Any


def dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def loads(s: str | None) -> Any:
    if not s:
        return None
    return json.loads(s)

