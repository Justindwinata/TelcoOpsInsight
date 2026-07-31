from __future__ import annotations

from fastapi import APIRouter, Query

from app.config import settings
from app.services.analytics_service import network_health, overview_metrics


router = APIRouter(prefix=f"{settings.api_prefix}/dashboard", tags=["dashboard"])


@router.get("/overview")
def dashboard_overview(
    region: str | None = Query(default=None),
    service_type: str | None = Query(default=None),
    severity: str | None = Query(default=None),
    month: str | None = Query(default=None),
) -> dict[str, object]:
    return overview_metrics(region=region, service_type=service_type, severity=severity, month=month)


@router.get("/network-health")
def dashboard_network_health(
    region: str | None = Query(default=None),
    service_type: str | None = Query(default=None),
    month: str | None = Query(default=None),
) -> dict[str, object]:
    return network_health(region=region, service_type=service_type, month=month)
