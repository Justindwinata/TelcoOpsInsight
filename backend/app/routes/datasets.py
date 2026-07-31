from __future__ import annotations

from fastapi import APIRouter

from app.config import settings
from app.schemas import SeedResponse
from app.services.dataset_service import seed_sample_dataset


router = APIRouter(prefix=f"{settings.api_prefix}/datasets", tags=["datasets"])


@router.post("/seed", response_model=SeedResponse)
def seed_dataset() -> dict[str, object]:
    return seed_sample_dataset()
