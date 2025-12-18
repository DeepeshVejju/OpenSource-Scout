from __future__ import annotations

import json
import time
import hashlib
from pathlib import Path
from typing import Any, Optional


CACHE_DIR = Path(".cache")
CACHE_DIR.mkdir(exist_ok=True)


def _key_to_path(key: str) -> Path:
    h = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return CACHE_DIR / f"{h}.json"


def get(key: str) -> Optional[Any]:
    path = _key_to_path(key)
    if not path.exists():
        return None

    try:
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        expires_at = payload.get("expires_at")
        if expires_at is not None and time.time() > expires_at:
            path.unlink(missing_ok=True)
            return None
        return payload.get("value")
    except Exception:
        return None


def set(key: str, value: Any, ttl_seconds: int = 3600) -> None:
    path = _key_to_path(key)
    payload = {
        "expires_at": time.time() + ttl_seconds if ttl_seconds else None,
        "value": value,
    }
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f)
