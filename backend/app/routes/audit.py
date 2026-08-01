from __future__ import annotations

import csv
import io

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

from app.config import settings
from app.services.auth_service import DemoUser, require_permission
from app.services.audit_service import list_audit_logs


router = APIRouter(prefix=f"{settings.api_prefix}/audit-logs", tags=["audit"])


@router.get("")
def audit_logs(
    actor: str | None = Query(default=None),
    action: str | None = Query(default=None),
    status: str | None = Query(default=None),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    _: DemoUser = Depends(require_permission("audit:read")),
) -> dict[str, object]:
    logs = list_audit_logs(actor=actor, action=action, status=status, start_date=start_date, end_date=end_date)
    return {"audit_logs": logs, "count": len(logs)}


@router.get("/export.csv")
def audit_logs_export_csv(
    actor: str | None = Query(default=None),
    action: str | None = Query(default=None),
    status: str | None = Query(default=None),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    _: DemoUser = Depends(require_permission("audit:read")),
) -> Response:
    logs = list_audit_logs(actor=actor, action=action, status=status, start_date=start_date, end_date=end_date)
    output = io.StringIO()
    fieldnames = [
        "audit_id",
        "timestamp",
        "actor_username",
        "actor_role",
        "action",
        "entity_type",
        "entity_id",
        "summary",
        "status",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(logs)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="telco_audit_logs.csv"'},
    )
