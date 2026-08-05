from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.services.auth_service import DemoUser, get_current_user
from app.services.dispatch_service import (
    DISPATCH_PRIORITIES,
    DISPATCH_STATUSES,
    acknowledge_assignment,
    assign_technician,
    complete_job,
    create_route,
    create_work_order,
    dispatch_summary,
    get_route,
    get_work_order,
    list_assignments,
    list_work_orders,
    start_job,
    technician_workload,
    update_route_status,
    update_work_order,
)


router = APIRouter(prefix=f"{settings.api_prefix}/dispatch", tags=["dispatch"])


class WorkOrderCreateRequest(BaseModel):
    job_type: str = "Installation"
    priority: str = "Normal"
    region: str = ""
    service_type: str = ""
    site_id: str = ""
    site_name: str = ""
    customer_id: str = ""
    customer_name: str = ""
    description: str = ""
    related_incident_id: str = ""
    required_skills: str = ""
    estimated_duration_minutes: int = 60
    scheduled_start: str = ""
    scheduled_end: str = ""


class WorkOrderUpdateRequest(BaseModel):
    priority: str | None = None
    status: str | None = None
    assigned_technician_id: str | None = None
    assigned_team: str | None = None
    scheduled_start: str | None = None
    dispatch_date: str | None = None


class AssignmentRequest(BaseModel):
    technician_id: str
    notes: str = ""


class RouteCreateRequest(BaseModel):
    route_json: str = ""
    distance_km: float = 0
    estimated_duration_minutes: int = 0
    eta_timestamp: str = ""
    route_status: str = "Active"


@router.get("/summary")
def dispatch_summary_endpoint(_: DemoUser = Depends(get_current_user)) -> dict[str, object]:
    return dispatch_summary()


@router.get("/work-orders")
def list_work_orders_endpoint(
    status: str | None = None,
    priority: str | None = None,
    region: str | None = None,
    technician_id: str | None = None,
    _: DemoUser = Depends(get_current_user),
) -> list[dict[str, object]]:
    return list_work_orders(status=status, priority=priority, region=region, technician_id=technician_id)


@router.get("/work-orders/{work_order_id}")
def get_work_order_endpoint(
    work_order_id: str,
    _: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    work_order = get_work_order(work_order_id)
    if not work_order:
        raise HTTPException(status_code=404, detail=f"Work order not found: {work_order_id}")
    return work_order


@router.post("/work-orders")
def create_work_order_endpoint(
    payload: WorkOrderCreateRequest,
    _: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    if payload.priority not in DISPATCH_PRIORITIES:
        raise HTTPException(status_code=422, detail=f"Invalid priority: {payload.priority}")
    return create_work_order(payload.model_dump())


@router.put("/work-orders/{work_order_id}")
def update_work_order_endpoint(
    work_order_id: str,
    payload: WorkOrderUpdateRequest,
    _: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    work_order = get_work_order(work_order_id)
    if not work_order:
        raise HTTPException(status_code=404, detail=f"Work order not found: {work_order_id}")
    if payload.status and payload.status not in DISPATCH_STATUSES:
        raise HTTPException(status_code=422, detail=f"Invalid status: {payload.status}")
    return update_work_order(work_order_id, payload.model_dump(exclude_none=True))


@router.post("/work-orders/{work_order_id}/assign")
def assign_technician_endpoint(
    work_order_id: str,
    payload: AssignmentRequest,
    user: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    work_order = get_work_order(work_order_id)
    if not work_order:
        raise HTTPException(status_code=404, detail=f"Work order not found: {work_order_id}")
    return assign_technician(work_order_id, payload.technician_id, user.username)


@router.get("/assignments")
def list_assignments_endpoint(
    work_order_id: str | None = None,
    technician_id: str | None = None,
    status: str | None = None,
    _: DemoUser = Depends(get_current_user),
) -> list[dict[str, object]]:
    return list_assignments(work_order_id=work_order_id, technician_id=technician_id, status=status)


@router.post("/assignments/{assignment_id}/acknowledge")
def acknowledge_assignment_endpoint(
    assignment_id: str,
    user: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    try:
        return acknowledge_assignment(assignment_id, user.username)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/assignments/{assignment_id}/start")
def start_job_endpoint(
    assignment_id: str,
    user: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    try:
        return start_job(assignment_id, user.username)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/assignments/{assignment_id}/complete")
def complete_job_endpoint(
    assignment_id: str,
    user: DemoUser = Depends(get_current_user),
    notes: str = "",
) -> dict[str, object]:
    try:
        return complete_job(assignment_id, user.username, notes)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/work-orders/{work_order_id}/route")
def create_route_endpoint(
    work_order_id: str,
    payload: RouteCreateRequest,
    _: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    work_order = get_work_order(work_order_id)
    if not work_order:
        raise HTTPException(status_code=404, detail=f"Work order not found: {work_order_id}")
    return create_route(work_order_id, payload.model_dump())


@router.get("/work-orders/{work_order_id}/route")
def get_route_endpoint(
    work_order_id: str,
    _: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    route = get_route(work_order_id)
    if not route:
        raise HTTPException(status_code=404, detail=f"No route found for work order: {work_order_id}")
    return route


@router.post("/routes/{route_id}/status")
def update_route_status_endpoint(
    route_id: str,
    status: str | None = None,
    _: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    new_status = status or "Active"
    return update_route_status(route_id, new_status)


@router.get("/technician-workload")
def technician_workload_endpoint(
    technician_id: str | None = None,
    _: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    return technician_workload(technician_id=technician_id)