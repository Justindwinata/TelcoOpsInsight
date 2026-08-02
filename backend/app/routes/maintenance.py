from __future__ import annotations

from fastapi import APIRouter, Depends

from app.config import settings
from app.filters import AnalyticsFilters, build_filters
from app.services.maintenance_service import maintenance_schedule


router = APIRouter(prefix=f"{settings.api_prefix}/maintenance", tags=["maintenance"])


def with_filter_metadata(payload: dict[str, object], filters: AnalyticsFilters) -> dict[str, object]:
    return {**payload, "filter_metadata": filters.metadata()}


@router.get("/schedule")
def maintenance_schedule_endpoint(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    return with_filter_metadata(maintenance_schedule(filters=filters), filters)
