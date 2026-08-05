from __future__ import annotations

from fastapi import APIRouter, Depends

from app.config import settings
from app.filters import AnalyticsFilters, build_filters
from app.services.auth_service import DemoUser, get_current_user
from app.services.executive_decision_service import executive_decision_center


router = APIRouter(prefix=f"{settings.api_prefix}/executive", tags=["executive"])


@router.get("/decision-center")
def executive_decision_center_endpoint(
    filters: AnalyticsFilters = Depends(build_filters),
    _: DemoUser = Depends(get_current_user),
) -> dict[str, object]:
    return executive_decision_center(filters=filters)