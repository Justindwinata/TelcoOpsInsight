from __future__ import annotations

from fastapi import APIRouter, File, Query, UploadFile

from app.config import settings
from app.schemas import SeedResponse, ValidationResponse
from app.services.dataset_service import seed_sample_dataset, validate_uploaded_csv


router = APIRouter(prefix=f"{settings.api_prefix}/datasets", tags=["datasets"])


@router.post("/seed", response_model=SeedResponse)
def seed_dataset() -> dict[str, object]:
    return seed_sample_dataset()


@router.post("/upload", response_model=ValidationResponse)
async def upload_dataset(file: UploadFile = File(...), persist: bool = Query(default=False)) -> dict[str, object]:
    return validate_uploaded_csv(file.filename or "upload.csv", file.file, persist=persist)
