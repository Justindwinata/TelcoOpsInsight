from __future__ import annotations

from fastapi import APIRouter, Depends, Query

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
