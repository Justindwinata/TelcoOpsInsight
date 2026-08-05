from __future__ import annotations
import time
from typing import Any

_cache_store: dict[str, dict[str, Any]] = {}
DEFAULT_TTL = 300

def get_cached(key: str, ttl: int = DEFAULT_TTL) -> Any | None:
    if key in _cache_store:
        entry = _cache_store[key]
        if time.time() - entry["timestamp"] < ttl:
            return entry["value"]
        del _cache_store[key]
    return None

def set_cached(key: str, value: Any) -> None:
    _cache_store[key] = {"value": value, "timestamp": time.time()}

def invalidate_cache(pattern: str = "") -> int:
    keys_to_delete = [k for k in _cache_store if pattern in k or not pattern]
    for key in keys_to_delete:
        del _cache_store[key]
    return len(keys_to_delete)
