from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.config import settings
from app.services.auth_service import DemoUser, get_current_user
from app.services.alarm_service import acknowledge_alarm, alarm_summary, assign_alarm, create_alarm, list_alarms, resolve_alarm, ALARM_SEVERITIES, ALARM_CATEGORIES

router = APIRouter(prefix=f"{settings.api_prefix}/alarms", tags=["alarms"])

class AlarmCreateRequest(BaseModel):
    severity: str
    category: str
    site_id: str = ""
    service_type: str = ""
    description: str = ""

@router.get("/summary")
def alarm_summary_endpoint(_: DemoUser = Depends(get_current_user)) -> dict[str, object]:
    return alarm_summary()

@router.get("")
def list_alarms_endpoint(status: str | None = None, severity: str | None = None, _: DemoUser = Depends(get_current_user)) -> list[dict[str, object]]:
    return list_alarms(status=status, severity=severity)

@router.post("")
def create_alarm_endpoint(payload: AlarmCreateRequest, _: DemoUser = Depends(get_current_user)) -> dict[str, object]:
    if payload.severity not in ALARM_SEVERITIES:
        raise HTTPException(status_code=422, detail=f"Invalid severity: {payload.severity}")
    if payload.category not in ALARM_CATEGORIES:
        raise HTTPException(status_code=422, detail=f"Invalid category: {payload.category}")
    return create_alarm(payload.model_dump())

@router.post("/{alarm_id}/acknowledge")
def acknowledge_alarm_endpoint(alarm_id: str, user: DemoUser = Depends(get_current_user)) -> dict[str, object]:
    return acknowledge_alarm(alarm_id, user.username)

@router.post("/{alarm_id}/assign")
def assign_alarm_endpoint(alarm_id: str, assigned_to: str, _: DemoUser = Depends(get_current_user)) -> dict[str, object]:
    return assign_alarm(alarm_id, assigned_to)

@router.post("/{alarm_id}/resolve")
def resolve_alarm_endpoint(alarm_id: str, user: DemoUser = Depends(get_current_user), notes: str = "") -> dict[str, object]:
    return resolve_alarm(alarm_id, user.username, notes)
