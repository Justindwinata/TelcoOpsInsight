from fastapi import APIRouter, Depends
from app.config import settings
from app.services.auth_service import DemoUser, get_current_user
from app.services.cache_service import clear_cache, cache_stats, invalidate_cache

router = APIRouter(prefix=f"{settings.api_prefix}/cache", tags=["cache"])

@router.get("/stats")
def cache_stats_endpoint(_: DemoUser = Depends(get_current_user)) -> dict:
    return cache_stats()

@router.post("/invalidate")
def cache_invalidate_endpoint(pattern: str = "", _: DemoUser = Depends(get_current_user)) -> dict:
    deleted = invalidate_cache(pattern)
    return {"invalidated": deleted, "pattern": pattern}

@router.post("/clear")
def cache_clear_endpoint(_: DemoUser = Depends(get_current_user)) -> dict:
    clear_cache()
    return {"cleared": True}
