from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.filters import AnalyticsFilters, build_filters
from app.services.auth_service import DemoUser, get_current_user
from app.services.sla_monitoring_service import (
    acknowledge_breach,
    create_sla_breach_alert,
    list_sla_breaches,
    resolve_breach,
    sla_monitoring_summary,
    sla_regional_heatmap,
)


router = APIRouter(prefix=f"{settings.api_prefix}/sla-monitoring", tags=["sla-monitoring"])


class SLABreachAlertRequest(BaseModel):
    incident_id: str = ""
    region: str
    service_type: str
    sla_target: float = 99.0
    sla_actual: float
    breach_gap: float = 0.0
    severity: str = "Medium"
    mttr_minutes: int = 0
    response_time_minutes: int = 0
    resolution_time_minutes: int = 0


@router.get("/summary")
def sla_monitoring_summary_endpoint(
    filters: AnalyticsFilters = Depends(build_filters),
    _: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    return sla_monitoring_summary(filters=filters)


@router.get("/breaches")
def list_breaches_endpoint(
    status: str | None = None,
    region: str | None = None,
    service_type: str | None = None,
    _: DemoUser = Depends(get_current_user),
) -> list[dict[str, object]]:
    return list_sla_breaches(status=status, region=region, service_type=service_type)


@router.post("/breaches")
def create_breach_alert_endpoint(
    payload: SLABreachAlertRequest,
    _: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    return create_sla_breach_alert(payload.model_dump())


@router.post("/breaches/{alert_id}/acknowledge")
def acknowledge_breach_endpoint(
    alert_id: str,
    user: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    return acknowledge_breach(alert_id, user.username)


@router.post("/breaches/{alert_id}/resolve")
def resolve_breach_endpoint(
    alert_id: str,
    _: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    return resolve_breach(alert_id)


@router.get("/heatmap")
def sla_heatmap_endpoint(
    filters: AnalyticsFilters = Depends(build_filters),
    _: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    return sla_regional_heatmap(filters=filters)
