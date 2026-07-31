from __future__ import annotations

from fastapi import APIRouter

from app.config import settings


router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "company": settings.company_name,
        "synthetic_data_only": True,
    }
