from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.services.auth_service import DemoUser, get_current_user
from app.services.service_request_service import (
    SERVICE_REQUEST_STATUSES,
    SERVICE_REQUEST_TYPES,
    PRIORITY_LEVELS,
    add_milestone,
    approve_request,
    create_service_request,
    get_request_history,
    get_request_milestones,
    get_service_request,
    list_service_requests,
    reject_request,
    service_request_summary,
    submit_for_approval,
    update_service_request,
)


router = APIRouter(prefix=f"{settings.api_prefix}/service-requests", tags=["service-requests"])


class ServiceRequestCreateRequest(BaseModel):
    customer_id: str
    customer_name: str
    service_type: str
    description: str = ""
    priority: str = "Normal"
    region: str = ""
    requested_date: str = ""
    target_completion_date: str = ""


class ServiceRequestUpdateRequest(BaseModel):
    priority: str | None = None
    status: str | None = None
    assigned_team: str | None = None
    assigned_technician_id: str | None = None
    progress_percentage: int | None = None
    target_completion_date: str | None = None


class MilestoneCreateRequest(BaseModel):
    milestone_name: str
    description: str = ""
    target_date: str = ""
    order_sequence: int = 0


class ApprovalRequest(BaseModel):
    comments: str = ""


class RejectionRequest(BaseModel):
    reason: str = ""


@router.get("/summary")
def service_request_summary_endpoint(_: DemoUser = Depends(get_current_user)) -> dict[str, object]:
    return service_request_summary()


@router.get("")
def list_service_requests_endpoint(
    status: str | None = None,
    priority: str | None = None,
    region: str | None = None,
    customer_id: str | None = None,
    _: DemoUser = Depends(get_current_user),
) -> list[dict[str, object]]:
    return list_service_requests(status=status, priority=priority, region=region, customer_id=customer_id)


@router.get("/{request_id}")
def get_service_request_endpoint(
    request_id: str,
    _: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    request = get_service_request(request_id)
    if not request:
        raise HTTPException(status_code=404, detail=f"Service request not found: {request_id}")
    return request


@router.post("")
def create_service_request_endpoint(
    payload: ServiceRequestCreateRequest,
    user: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    if payload.priority not in PRIORITY_LEVELS:
        raise HTTPException(status_code=422, detail=f"Invalid priority: {payload.priority}")
    if payload.service_type not in SERVICE_REQUEST_TYPES:
        raise HTTPException(status_code=422, detail=f"Invalid service type: {payload.service_type}")
    return create_service_request(payload.model_dump(), user.username)


@router.put("/{request_id}")
def update_service_request_endpoint(
    request_id: str,
    payload: ServiceRequestUpdateRequest,
    user: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    request = get_service_request(request_id)
    if not request:
        raise HTTPException(status_code=404, detail=f"Service request not found: {request_id}")
    if payload.status and payload.status not in SERVICE_REQUEST_STATUSES:
        raise HTTPException(status_code=422, detail=f"Invalid status: {payload.status}")
    return update_service_request(request_id, payload.model_dump(exclude_none=True), user.username)


@router.post("/{request_id}/submit")
def submit_for_approval_endpoint(
    request_id: str,
    user: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    request = get_service_request(request_id)
    if not request:
        raise HTTPException(status_code=404, detail=f"Service request not found: {request_id}")
    return submit_for_approval(request_id, user.username)


@router.post("/{request_id}/approve")
def approve_request_endpoint(
    request_id: str,
    payload: ApprovalRequest,
    user: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    request = get_service_request(request_id)
    if not request:
        raise HTTPException(status_code=404, detail=f"Service request not found: {request_id}")
    return approve_request(request_id, user.username, payload.comments)


@router.post("/{request_id}/reject")
def reject_request_endpoint(
    request_id: str,
    payload: RejectionRequest,
    user: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    request = get_service_request(request_id)
    if not request:
        raise HTTPException(status_code=404, detail=f"Service request not found: {request_id}")
    return reject_request(request_id, user.username, payload.reason)


@router.get("/{request_id}/milestones")
def get_milestones_endpoint(
    request_id: str,
    _: DemoUser = Depends(get_current_user),
) -> list[dict[str, object]]:
    request = get_service_request(request_id)
    if not request:
        raise HTTPException(status_code=404, detail=f"Service request not found: {request_id}")
    return get_request_milestones(request_id)


@router.post("/{request_id}/milestones")
def add_milestone_endpoint(
    request_id: str,
    payload: MilestoneCreateRequest,
    _: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    request = get_service_request(request_id)
    if not request:
        raise HTTPException(status_code=404, detail=f"Service request not found: {request_id}")
    return add_milestone(request_id, payload.model_dump())


@router.get("/{request_id}/history")
def get_history_endpoint(
    request_id: str,
    _: DemoUser = Depends(get_current_user),
) -> list[dict[str, object]]:
    request = get_service_request(request_id)
    if not request:
        raise HTTPException(status_code=404, detail=f"Service request not found: {request_id}")
    return get_request_history(request_id)
