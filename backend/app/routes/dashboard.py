from __future__ import annotations

from fastapi import APIRouter, Query

from app.config import settings
from app.services.analytics_service import incident_analytics, network_health, overview_metrics, sla_analytics, ticket_analytics


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


@router.get("/incidents")
def dashboard_incidents(
    region: str | None = Query(default=None),
    service_type: str | None = Query(default=None),
    severity: str | None = Query(default=None),
    month: str | None = Query(default=None),
) -> dict[str, object]:
    return incident_analytics(region=region, service_type=service_type, severity=severity, month=month)


@router.get("/tickets")
def dashboard_tickets(
    region: str | None = Query(default=None),
    service_type: str | None = Query(default=None),
    severity: str | None = Query(default=None),
    month: str | None = Query(default=None),
) -> dict[str, object]:
    return ticket_analytics(region=region, service_type=service_type, severity=severity, month=month)


@router.get("/sla")
def dashboard_sla(
    region: str | None = Query(default=None),
    service_type: str | None = Query(default=None),
    month: str | None = Query(default=None),
) -> dict[str, object]:
    return sla_analytics(region=region, service_type=service_type, month=month)
