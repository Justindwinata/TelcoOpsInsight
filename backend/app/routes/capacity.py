from __future__ import annotations

from fastapi import APIRouter, Depends

from app.config import settings
from app.filters import AnalyticsFilters, build_filters
from app.services.auth_service import DemoUser, get_current_user
from app.services.capacity_planning_service import (
    backbone_utilization,
    capacity_planning_by_site,
    capacity_planning_summary,
    capacity_utilization,
)


router = APIRouter(prefix=f"{settings.api_prefix}/capacity", tags=["capacity"])


@router.get("/summary")
def capacity_summary_endpoint(
    filters: AnalyticsFilters = Depends(build_filters),
    _: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    return capacity_planning_summary(filters=filters)


@router.get("/utilization")
def capacity_utilization_endpoint(
    filters: AnalyticsFilters = Depends(build_filters),
    _: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    return capacity_utilization(filters=filters)


@router.get("/backbone")
def backbone_utilization_endpoint(
    filters: AnalyticsFilters = Depends(build_filters),
    _: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    return backbone_utilization(filters=filters)


@router.get("/sites")
def capacity_planning_sites_endpoint(
    filters: AnalyticsFilters = Depends(build_filters),
    _: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    return capacity_planning_by_site(filters=filters)
