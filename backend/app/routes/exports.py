from __future__ import annotations
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from app.config import settings
from app.services.auth_service import DemoUser, get_current_user
from app.services.export_service import export_to_csv, export_to_json

router = APIRouter(prefix=f"{settings.api_prefix}/exports", tags=["exports"])

@router.get("/{data_type}/json")
def export_json(data_type: str, _: DemoUser = Depends(get_current_user)) -> Response:
    content = export_to_json(data_type)
    return Response(content=content, media_type="application/json", headers={"Content-Disposition": f"attachment; filename={data_type}.json"})

@router.get("/{data_type}/csv")
def export_csv(data_type: str, _: DemoUser = Depends(get_current_user)) -> Response:
    content = export_to_csv(data_type)
    return Response(content=content, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename={data_type}.csv"})
