from __future__ import annotations
from fastapi import APIRouter, Depends
from app.config import settings
from app.services.auth_service import DemoUser, get_current_user
from app.services.maintenance_calendar_service import get_maintenance_calendar

router = APIRouter(prefix=f"{settings.api_prefix}/calendar", tags=["calendar"])

@router.get("")
def calendar_endpoint(start_date: str | None = None, end_date: str | None = None, _: DemoUser = Depends(get_current_user)) -> dict:
    return get_maintenance_calendar(start_date=start_date, end_date=end_date)
