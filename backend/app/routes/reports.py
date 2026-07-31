from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from app.config import settings
from app.filters import AnalyticsFilters, build_filters
from app.services.report_service import executive_summary, executive_summary_html


router = APIRouter(prefix=f"{settings.api_prefix}/reports", tags=["reports"])


@router.get("/executive-summary")
def executive_summary_report(filters: AnalyticsFilters = Depends(build_filters)) -> dict[str, object]:
    return executive_summary(filters=filters)


@router.get("/executive-summary.html", response_class=HTMLResponse)
def executive_summary_html_report(filters: AnalyticsFilters = Depends(build_filters)) -> str:
    return executive_summary_html(filters=filters)
