from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.config import settings
from app.filters import AnalyticsFilters, build_filters
from app.services.timeline_service import incident_timeline


router = APIRouter(prefix=f"{settings.api_prefix}/timeline", tags=["timeline"])


def with_filter_metadata(payload: dict[str, object], filters: AnalyticsFilters) -> dict[str, object]:
    return {**payload, "filter_metadata": filters.metadata()}


@router.get("/incidents")
def incident_timelines(
    filters: AnalyticsFilters = Depends(build_filters),
    incident_id: str | None = Query(default=None, description="Filter to a specific incident_id"),
) -> dict[str, object]:
    return with_filter_metadata(incident_timeline(filters=filters, incident_id=incident_id), filters)
