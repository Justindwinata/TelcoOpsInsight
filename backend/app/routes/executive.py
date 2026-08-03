from __future__ import annotations

from fastapi import APIRouter, Depends

from app.config import settings
from app.filters import AnalyticsFilters, build_filters
from app.services.executive_service import executive_summary


router = APIRouter(prefix=f"{settings.api_prefix}/reports/executive", tags=["reports"])


@router.get("/summary")
def executive_summary_endpoint(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    return executive_summary(filters=filters)


@router.get("/monthly")
def monthly_summary(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    summary = executive_summary(filters=filters)
    return {
        "summary": summary,
        "monthly_breakdown": summary.get("monthly_trend", {}),
        "region_comparison": summary.get("region_comparison", {}),
    }


@router.get("/weekly")
def weekly_summary(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    # Filter to last 7 days
    from datetime import date, timedelta
    end = date.today()
    start = end - timedelta(days=6)
    filtered_filters = AnalyticsFilters(start_date=start, end_date=end)
    summary = executive_summary(filters=filtered_filters)
    return {
        "period": {"start": start.isoformat(), "end": end.isoformat()},
        "summary": summary,
        "kpi_comparison": summary.get("kpi_comparison", {}),
    }


@router.get("/trend")
def trend_summary(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    summary = executive_summary(filters=filters)
    return {
        "service_trend": summary.get("service_trend", {}),
        "region_comparison": summary.get("region_comparison", {}),
        "monthly_trend": summary.get("monthly_trend", {}),
    }
