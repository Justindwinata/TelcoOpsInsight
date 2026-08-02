from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.services.auth_service import DemoUser, get_current_user
from app.services.change_service import (
    CHANGE_STATUSES,
    CHANGE_TYPES,
    CHANGE_RISK,
    create_change,
    list_changes,
    transition_change,
    change_management_summary,
)


router = APIRouter(prefix=f"{settings.api_prefix}/changes", tags=["changes"])


class ChangeCreateRequest(BaseModel):
    title: str
    change_type: str = "Planned Change"
    risk_level: str = "Medium"
    region: str
    service_type: str
    description: str
    rollback_plan: str = ""
    scheduled_start: str = ""
    scheduled_end: str = ""
    related_incident_id: str = ""
    affected_sites: str = ""


class ChangeTransitionRequest(BaseModel):
    new_status: str
    approver: str | None = None


@router.get("/summary")
def change_summary(_: DemoUser = Depends(get_current_user)) -> dict[str, object]:
    return change_management_summary()


@router.get("")
def list_change_records(
    status: str | None = None,
    change_type: str | None = None,
    user: DemoUser = Depends(get_current_user),
) -> list[dict[str, object]]:
    return list_changes(status=status, change_type=change_type)


@router.post("")
def create_change_record(
    payload: ChangeCreateRequest,
    user: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    if payload.change_type not in CHANGE_TYPES:
        raise HTTPException(status_code=422, detail=f"Invalid change_type: {payload.change_type}")
    if payload.risk_level not in CHANGE_RISK:
        raise HTTPException(status_code=422, detail=f"Invalid risk_level: {payload.risk_level}")
    return create_change(payload.model_dump(), user.username)


@router.post("/{change_id}/transition")
def transition_change_record(
    change_id: str,
    payload: ChangeTransitionRequest,
    user: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    if payload.new_status not in CHANGE_STATUSES:
        raise HTTPException(status_code=422, detail=f"Invalid status: {payload.new_status}")
    try:
        return transition_change(change_id, payload.new_status, user.username, payload.approver)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc