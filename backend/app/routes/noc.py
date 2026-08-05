from __future__ import annotations

from fastapi import APIRouter, Depends

from app.config import settings
from app.filters import AnalyticsFilters, build_filters
from app.services.auth_service import DemoUser, get_current_user
from app.services.noc_service import noc_command_center


router = APIRouter(prefix=f"{settings.api_prefix}/noc", tags=["noc"])


@router.get("/command-center")
def noc_command_center_endpoint(
    filters: AnalyticsFilters = Depends(build_filters),
    _: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    return noc_command_center(filters=filters)