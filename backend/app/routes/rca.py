from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.services.auth_service import DemoUser, get_current_user
from app.services.rca_service import RCA_CATEGORIES, RCA_METHODS, RCA_STATUSES, create_rca, list_rcas, rca_summary, update_rca


router = APIRouter(prefix=f"{settings.api_prefix}/rca", tags=["rca"])


class RcaCreateRequest(BaseModel):
    incident_id: str = ""
    title: str = ""
    root_cause_category: str = ""
    root_cause_description: str = ""
    resolution: str = ""
    lessons_learned: str = ""
    method: str = "5 Whys"
    status: str = "Draft"
    severity: str = "Medium"
    region: str = ""
    service_type: str = ""
    assigned_engineer: str = ""
    preventive_actions: str = ""


class RcaUpdateRequest(BaseModel):
    title: str | None = None
    root_cause_description: str | None = None
    resolution: str | None = None
    lessons_learned: str | None = None
    status: str | None = None
    assigned_engineer: str | None = None
    preventive_actions: str | None = None


@router.get("/summary")
def rca_summary_endpoint(_: DemoUser = Depends(get_current_user)) -> dict[str, object]:
    return rca_summary()


@router.get("")
def list_rca_records(
    status: str | None = None,
    category: str | None = None,
    engineer: str | None = None,
    _: DemoUser = Depends(get_current_user),
) -> list[dict[str, object]]:
    return list_rcas(status=status, category=category, engineer=engineer)


@router.post("")
def create_rca_record(payload: RcaCreateRequest, user: DemoUser = Depends(get_current_user)) -> dict[str, object]:
    if payload.root_cause_category and payload.root_cause_category not in RCA_CATEGORIES:
        raise HTTPException(status_code=422, detail=f"Invalid root_cause_category: {payload.root_cause_category}")
    if payload.method and payload.method not in RCA_METHODS:
        raise HTTPException(status_code=422, detail=f"Invalid method: {payload.method}")
    if payload.status and payload.status not in RCA_STATUSES:
        raise HTTPException(status_code=422, detail=f"Invalid status: {payload.status}")
    return create_rca(payload.model_dump(), user.username)


@router.put("/{rca_id}")
def update_rca_record(rca_id: str, payload: RcaUpdateRequest, user: DemoUser = Depends(get_current_user)) -> dict[str, object]:
    return update_rca(rca_id, payload.model_dump(exclude_none=True))