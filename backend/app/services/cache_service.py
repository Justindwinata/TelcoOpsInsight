from __future__ import annotations
import time
from typing import Any, Optional

_cache_store: dict[str, dict[str, Any]] = {}
DEFAULT_TTL = 300  # 5 minutes

def get_cached(key: str) -> Optional[Any]:
    """Get value from cache if not expired."""
    if key in _cache_store:
        entry = _cache_store[key]
        if time.time() - entry["timestamp"] < DEFAULT_TTL:
            return entry["value"]
        del _cache_store[key]
    return None

def set_cached(key: str, value: Any) -> None:
    """Store value in cache with timestamp."""
    _cache_store[key] = {"value": value, "timestamp": time.time()}

def invalidate_cache(pattern: str = "") -> int:
    """Invalidate cache entries matching pattern. Returns count deleted."""
    keys_to_delete = [k for k in _cache_store if pattern in k or not pattern]
    for key in keys_to_delete:
        del _cache_store[key]
    return len(keys_to_delete)

def clear_cache() -> None:
    """Clear all cache entries."""
    _cache_store.clear()

def cache_stats() -> dict[str, Any]:
    """Get cache statistics."""
    return {
        "total_entries": len(_cache_store),
        "default_ttl_seconds": DEFAULT_TTL,
    }
