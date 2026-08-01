from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from app.config import settings
from app.schemas import ImportHistoryEntry, SeedResponse, ValidationResponse
from app.services.auth_service import DemoUser, ensure_permission, require_permission
from app.services.audit_service import record_audit
from app.services.dataset_service import (
    get_import_history,
    list_import_history,
    rollback_import,
    seed_sample_dataset,
    validate_uploaded_csv,
)


router = APIRouter(prefix=f"{settings.api_prefix}/datasets", tags=["datasets"])


@router.post("/seed", response_model=SeedResponse)
def seed_dataset(user: DemoUser = Depends(require_permission("datasets:seed"))) -> dict[str, object]:
    result = seed_sample_dataset()
    record_audit(
        actor_username=user.username,
        actor_role=user.role,
        action="datasets.seed",
        entity_type="dataset",
        summary="Seeded sample dataset into SQLite",
        status="success",
    )
    return result


@router.post("/upload", response_model=ValidationResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    persist: bool = Query(default=False),
    user: DemoUser = Depends(require_permission("datasets:validate")),
) -> dict[str, object]:
    if persist:
        ensure_permission(user, "datasets:import")
    result = validate_uploaded_csv(file.filename or "upload.csv", file.file, persist=persist, actor=user.username)
    record_audit(
        actor_username=user.username,
        actor_role=user.role,
        action="datasets.import" if result.get("imported") else "datasets.validate",
        entity_type="dataset",
        entity_id=str(result.get("import_id") or ""),
        summary=f"CSV upload {result.get('dataset_type') or 'unknown'} accepted={result.get('accepted')}",
        status="success" if result.get("accepted") else "rejected",
    )
    return result


@router.get("/import-history", response_model=list[ImportHistoryEntry])
def import_history(_: DemoUser = Depends(require_permission("imports:read"))) -> list[dict[str, object]]:
    return list_import_history()


@router.post("/import-history/{import_id}/rollback")
def rollback_import_history(
    import_id: str,
    user: DemoUser = Depends(require_permission("datasets:import")),
) -> dict[str, object]:
    try:
        result = rollback_import(import_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    record_audit(
        actor_username=user.username,
        actor_role=user.role,
        action="datasets.rollback",
        entity_type="import",
        entity_id=import_id,
        summary=f"Rolled back import for {result['dataset_type']}",
        status="success",
    )
    return result


@router.get("/import-history/{import_id}", response_model=ImportHistoryEntry)
def import_history_detail(import_id: str, _: DemoUser = Depends(require_permission("imports:read"))) -> dict[str, object]:
    row = get_import_history(import_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Import history record not found")
    return row
