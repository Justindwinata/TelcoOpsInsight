from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.services.auth_service import DemoUser, get_current_user
from app.services.workforce_service import (
    TECHNICIAN_STATUSES,
    SKILL_LEVELS,
    LEAVE_TYPES,
    LEAVE_STATUSES,
    add_certification,
    add_skill,
    approve_leave,
    assign_job,
    create_shift,
    create_technician,
    get_assignment_history,
    get_technician,
    get_technician_certifications,
    get_technician_skills,
    list_leave_requests,
    list_shifts,
    list_technicians,
    reject_leave,
    request_leave,
    update_technician,
    workforce_summary,
)


router = APIRouter(prefix=f"{settings.api_prefix}/workforce", tags=["workforce"])


class TechnicianCreateRequest(BaseModel):
    name: str
    employee_id: str
    region: str
    assigned_team: str
    status: str = "Available"
    phone: str = ""
    email: str = ""
    hire_date: str = ""
    years_experience: float = 0
    certifications: str = ""


class SkillAddRequest(BaseModel):
    skill_name: str
    skill_level: str = "Intermediate"
    certification_id: str = ""
    acquired_date: str = ""
    verified: bool = False
    verified_by: str = ""


class CertificationAddRequest(BaseModel):
    cert_name: str
    issuing_body: str
    issued_date: str
    expiry_date: str = ""
    status: str = "Active"
    renewal_required: bool = False


class ShiftCreateRequest(BaseModel):
    technician_id: str
    shift_type: str = "Day"
    start_time: str
    end_time: str
    shift_date: str
    region: str
    capacity_slots: int = 5


class LeaveRequestCreateRequest(BaseModel):
    technician_id: str
    leave_type: str
    start_date: str
    end_date: str
    days_requested: int
    reason: str = ""


class AssignmentCreateRequest(BaseModel):
    technician_id: str
    job_id: str
    priority: str = "Normal"
    estimated_duration_minutes: int = 0


@router.get("/summary")
def workforce_summary_endpoint(_: DemoUser = Depends(get_current_user)) -> dict[str, object]:
    return workforce_summary()


@router.get("/technicians")
def list_technicians_endpoint(
    region: str | None = None,
    team: str | None = None,
    status: str | None = None,
    _: DemoUser = Depends(get_current_user),
) -> list[dict[str, object]]:
    return list_technicians(region=region, team=team, status=status)


@router.get("/technicians/{tech_id}")
def get_technician_endpoint(
    tech_id: str,
    _: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    technician = get_technician(tech_id)
    if not technician:
        raise HTTPException(status_code=404, detail=f"Technician not found: {tech_id}")
    return technician


@router.post("/technicians")
def create_technician_endpoint(
    payload: TechnicianCreateRequest,
    user: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    if payload.status not in TECHNICIAN_STATUSES:
        raise HTTPException(status_code=422, detail=f"Invalid status: {payload.status}")
    return create_technician(payload.model_dump(), user.username)


@router.put("/technicians/{tech_id}")
def update_technician_endpoint(
    tech_id: str,
    payload: TechnicianCreateRequest,
    _: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    technician = get_technician(tech_id)
    if not technician:
        raise HTTPException(status_code=404, detail=f"Technician not found: {tech_id}")
    return update_technician(tech_id, payload.model_dump())


@router.get("/technicians/{tech_id}/skills")
def get_skills_endpoint(
    tech_id: str,
    _: DemoUser = Depends(get_current_user),
) -> list[dict[str, object]]:
    return get_technician_skills(tech_id)


@router.post("/technicians/{tech_id}/skills")
def add_skill_endpoint(
    tech_id: str,
    payload: SkillAddRequest,
    _: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    technician = get_technician(tech_id)
    if not technician:
        raise HTTPException(status_code=404, detail=f"Technician not found: {tech_id}")
    if payload.skill_level not in SKILL_LEVELS:
        raise HTTPException(status_code=422, detail=f"Invalid skill level: {payload.skill_level}")
    return add_skill(tech_id, payload.model_dump())


@router.get("/technicians/{tech_id}/certifications")
def get_certifications_endpoint(
    tech_id: str,
    _: DemoUser = Depends(get_current_user),
) -> list[dict[str, object]]:
    return get_technician_certifications(tech_id)


@router.post("/technicians/{tech_id}/certifications")
def add_certification_endpoint(
    tech_id: str,
    payload: CertificationAddRequest,
    _: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    technician = get_technician(tech_id)
    if not technician:
        raise HTTPException(status_code=404, detail=f"Technician not found: {tech_id}")
    return add_certification(tech_id, payload.model_dump())


@router.get("/shifts")
def list_shifts_endpoint(
    date_from: str | None = None,
    date_to: str | None = None,
    region: str | None = None,
    _: DemoUser = Depends(get_current_user),
) -> list[dict[str, object]]:
    return list_shifts(date_from=date_from, date_to=date_to, region=region)


@router.post("/shifts")
def create_shift_endpoint(
    payload: ShiftCreateRequest,
    _: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    technician = get_technician(payload.technician_id)
    if not technician:
        raise HTTPException(status_code=404, detail=f"Technician not found: {payload.technician_id}")
    return create_shift(payload.model_dump())


@router.get("/leave-requests")
def list_leave_requests_endpoint(
    tech_id: str | None = None,
    status: str | None = None,
    _: DemoUser = Depends(get_current_user),
) -> list[dict[str, object]]:
    if status and status not in LEAVE_STATUSES:
        raise HTTPException(status_code=422, detail=f"Invalid status: {status}")
    return list_leave_requests(tech_id=tech_id, status=status)


@router.post("/leave-requests")
def request_leave_endpoint(
    payload: LeaveRequestCreateRequest,
    user: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    technician = get_technician(payload.technician_id)
    if not technician:
        raise HTTPException(status_code=404, detail=f"Technician not found: {payload.technician_id}")
    if payload.leave_type not in LEAVE_TYPES:
        raise HTTPException(status_code=422, detail=f"Invalid leave type: {payload.leave_type}")
    return request_leave(payload.model_dump(), user.username)


@router.post("/leave-requests/{leave_id}/approve")
def approve_leave_endpoint(
    leave_id: str,
    user: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    leave = list_leave_requests(status="Pending")
    leave_record = next((l for l in leave if l.get("leave_id") == leave_id), None)
    if not leave_record:
        raise HTTPException(status_code=404, detail=f"Leave request not found: {leave_id}")
    return approve_leave(leave_id, user.username)


@router.post("/leave-requests/{leave_id}/reject")
def reject_leave_endpoint(
    leave_id: str,
    user: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    leave = list_leave_requests(status="Pending")
    leave_record = next((l for l in leave if l.get("leave_id") == leave_id), None)
    if not leave_record:
        raise HTTPException(status_code=404, detail=f"Leave request not found: {leave_id}")
    return reject_leave(leave_id, user.username)


@router.get("/assignments/{tech_id}")
def get_assignment_history_endpoint(
    tech_id: str,
    limit: int = 200,
    _: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    technician = get_technician(tech_id)
    if not technician:
        raise HTTPException(status_code=404, detail=f"Technician not found: {tech_id}")
    assignments = get_assignment_history(tech_id, limit=limit)
    return {
        "technician_id": tech_id,
        "assignments": assignments,
        "total": len(assignments),
    }


@router.post("/assignments")
def create_assignment_endpoint(
    payload: AssignmentCreateRequest,
    _: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    technician = get_technician(payload.technician_id)
    if not technician:
        raise HTTPException(status_code=404, detail=f"Technician not found: {payload.technician_id}")
    return assign_job(payload.model_dump())
