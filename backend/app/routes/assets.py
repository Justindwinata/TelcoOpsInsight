from __future__ import annotations

from fastapi import APIRouter, Depends

from app.config import settings
from app.filters import AnalyticsFilters, build_filters
from app.services.asset_service import asset_detail, asset_inventory


router = APIRouter(prefix=f"{settings.api_prefix}/assets", tags=["assets"])


def with_filter_metadata(payload: dict[str, object], filters: AnalyticsFilters) -> dict[str, object]:
    return {**payload, "filter_metadata": filters.metadata()}


@router.get("/inventory")
def asset_inventory_endpoint(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    return with_filter_metadata(asset_inventory(filters=filters), filters)


@router.get("/detail")
def asset_detail_endpoint(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    return with_filter_metadata(asset_detail(filters=filters), filters)
