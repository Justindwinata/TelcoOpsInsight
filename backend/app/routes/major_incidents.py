from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.config import settings
from app.services.auth_service import DemoUser, get_current_user
from app.services.major_incident_service import (
    add_stakeholder, complete_major_incident, create_major_incident,
    get_mi_timeline, get_major_incident, get_stakeholders, list_major_incidents,
    MI_STATUSES, MI_SEVERITIES, update_mi_status,
)

router = APIRouter(prefix=f"{settings.api_prefix}/major-incidents", tags=["major-incidents"])

class MICreateRequest(BaseModel):
    incident_id: str = ""
    title: str = ""
    severity: str = "High"
    incident_commander: str = ""
    war_room_link: str = ""
    impact_services: str = ""
    impact_regions: str = ""
    impacted_customers: int = 0
    root_cause: str = ""

@router.get("")
def list_mis(status: str | None = None, _: DemoUser = Depends(get_current_user)) -> list:
    return list_major_incidents(status=status)

@router.post("")
def create_mi(payload: MICreateRequest, user: DemoUser = Depends(get_current_user)) -> dict:
    if payload.severity not in MI_SEVERITIES:
        raise HTTPException(status_code=422, detail=f"Invalid severity: {payload.severity}")
    return create_major_incident(payload.model_dump(), user.username)

@router.get("/{mi_id}")
def get_mi(mi_id: str, _: DemoUser = Depends(get_current_user)) -> dict:
    result = get_major_incident(mi_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Major incident not found: {mi_id}")
    return result

@router.put("/{mi_id}/status")
def update_mi_status_endpoint(mi_id: str, status: str, user: DemoUser = Depends(get_current_user)) -> dict:
    if status not in MI_STATUSES:
        raise HTTPException(status_code=422, detail=f"Invalid status: {status}")
    return update_mi_status(mi_id, status, user.username)

@router.post("/{mi_id}/stakeholders")
def add_stakeholder_endpoint(mi_id: str, name: str, role: str, contact: str, _: DemoUser = Depends(get_current_user)) -> dict:
    return add_stakeholder(mi_id, name, role, contact)

@router.get("/{mi_id}/stakeholders")
def get_stakeholders_endpoint(mi_id: str, _: DemoUser = Depends(get_current_user)) -> list:
    return get_stakeholders(mi_id)

@router.post("/{mi_id}/timeline")
def add_timeline_event_endpoint(mi_id: str, event_type: str, description: str, actor: str, _: DemoUser = Depends(get_current_user)) -> dict:
    return add_timeline_event(mi_id, event_type, description, actor)

@router.get("/{mi_id}/timeline")
def get_timeline_endpoint(mi_id: str, _: DemoUser = Depends(get_current_user)) -> list:
    return get_mi_timeline(mi_id)

@router.post("/{mi_id}/resolve")
def resolve_mi_endpoint(mi_id: str, commander: str, resolution_summary: str, root_cause: str, _: DemoUser = Depends(get_current_user)) -> dict:
    return complete_major_incident(mi_id, commander, resolution_summary, root_cause)