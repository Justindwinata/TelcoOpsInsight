from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from app.config import settings
from app.schemas import ImportHistoryEntry, SeedResponse, ValidationResponse
from app.services.auth_service import DemoUser, ensure_permission, require_permission
from app.services.dataset_service import get_import_history, list_import_history, seed_sample_dataset, validate_uploaded_csv


router = APIRouter(prefix=f"{settings.api_prefix}/datasets", tags=["datasets"])


@router.post("/seed", response_model=SeedResponse)
def seed_dataset(_: DemoUser = Depends(require_permission("datasets:seed"))) -> dict[str, object]:
    return seed_sample_dataset()


@router.post("/upload", response_model=ValidationResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    persist: bool = Query(default=False),
    user: DemoUser = Depends(require_permission("datasets:validate")),
) -> dict[str, object]:
    if persist:
        ensure_permission(user, "datasets:import")
    return validate_uploaded_csv(file.filename or "upload.csv", file.file, persist=persist, actor=user.username)


@router.get("/import-history", response_model=list[ImportHistoryEntry])
def import_history(_: DemoUser = Depends(require_permission("imports:read"))) -> list[dict[str, object]]:
    return list_import_history()


@router.get("/import-history/{import_id}", response_model=ImportHistoryEntry)
def import_history_detail(import_id: str, _: DemoUser = Depends(require_permission("imports:read"))) -> dict[str, object]:
    row = get_import_history(import_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Import history record not found")
    return row
