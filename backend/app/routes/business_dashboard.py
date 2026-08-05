from fastapi import APIRouter, Depends
from app.config import settings
from app.services.auth_service import DemoUser, get_current_user
from app.services.business_dashboard_service import executive_business_dashboard

router = APIRouter(prefix=f"{settings.api_prefix}/business", tags=["business"])

@router.get("/dashboard")
def business_dashboard(_: DemoUser = Depends(get_current_user)) -> dict:
    return executive_business_dashboard()
