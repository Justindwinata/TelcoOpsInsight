from __future__ import annotations

from fastapi import APIRouter, Depends

from app.config import settings
from app.services.auth_service import DemoUser, get_current_user
from app.services.live_status_service import (
    active_operators,
    live_kpi_monitoring,
    live_regional_status,
    live_sla_status,
)

router = APIRouter(prefix=f"{settings.api_prefix}/live-status", tags=["live-status"])


@router.get("/regions")
def live_regional_status_endpoint(_: DemoUser = Depends(get_current_user)) -> dict:
    return live_regional_status()


@router.get("/kpi")
def live_kpi_endpoint(_: DemoUser = Depends(get_current_user)) -> dict:
    return live_kpi_monitoring()


@router.get("/sla")
def live_sla_endpoint(_: DemoUser = Depends(get_current_user)) -> dict:
    return live_sla_status()


@router.get("/operators")
def active_operators_endpoint(_: DemoUser = Depends(get_current_user)) -> dict:
    return active_operators()