from __future__ import annotations

import asyncio
import json
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from app.config import settings
from app.services.auth_service import DemoUser, get_current_user
from app.services.event_service import (
    EVENT_TYPES,
    SEVERITY_LEVELS,
    acknowledge_event,
    event_stats,
    event_summary_by_severity,
    event_summary_by_type,
    get_event_history,
    get_recent_events,
    publish_event,
    resolve_event,
    subscribe,
    unsubscribe,
)


router = APIRouter(prefix=f"{settings.api_prefix}/events", tags=["events"])


@router.get("/stats")
def events_stats(_: DemoUser = Depends(get_current_user)) -> dict:
    return event_stats()


@router.get("/summary/type")
def events_summary_by_type(_: DemoUser = Depends(get_current_user)) -> dict:
    return event_summary_by_type()


@router.get("/summary/severity")
def events_summary_by_severity_endpoint(_: DemoUser = Depends(get_current_user)) -> dict:
    return event_summary_by_severity()


@router.get("/recent")
def events_recent(
    limit: int = 50,
    event_type: str | None = None,
    severity: str | None = None,
    _: DemoUser = Depends(get_current_user),
) -> list[dict]:
    return get_recent_events(limit=limit, event_type=event_type, severity=severity)


@router.get("/history")
def events_history(
    limit: int = 200,
    event_type: str | None = None,
    _: DemoUser = Depends(get_current_user),
) -> list[dict]:
    return get_event_history(limit=limit, event_type=event_type)


@router.post("/publish")
def publish_event_endpoint(
    event_type: str,
    severity: str,
    title: str,
    detail: str = "",
    region: str = "",
    service_type: str = "",
    site_id: str = "",
    related_incident_id: str = "",
    related_alarm_id: str = "",
    _: DemoUser = Depends(get_current_user),
) -> dict:
    if event_type not in EVENT_TYPES:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail=f"Invalid event_type: {event_type}")
    if severity not in ["Info", "Warning", "Minor", "Major", "Critical"]:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail=f"Invalid severity: {severity}")

    return publish_event(
        event_type=event_type,
        severity=severity,
        title=title,
        detail=detail,
        region=region,
        service_type=service_type,
        site_id=site_id,
        related_incident_id=related_incident_id,
        related_alarm_id=related_alarm_id,
    )


@router.post("/{event_id}/acknowledge")
def acknowledge_event_endpoint(
    event_id: str,
    user: DemoUser = Depends(get_current_user),
) -> dict:
    result = acknowledge_event(event_id, user.username)
    if not result:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Event not found: {event_id}")
    return result


@router.post("/{event_id}/resolve")
def resolve_event_endpoint(
    event_id: str,
    user: DemoUser = Depends(get_current_user),
) -> dict:
    result = resolve_event(event_id, user.username)
    if not result:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Event not found: {event_id}")
    return result


# SSE Stream endpoint
async def event_stream(request: Request, user: DemoUser) -> StreamingResponse:
    """Server-Sent Events stream for real-time events."""
    queue = subscribe()

    async def event_generator():
        try:
            # Send initial connection event
            yield {
                "event": "connected",
                "data": json.dumps({"message": "Connected to event stream"}),
            }

            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    break

                try:
                    # Wait for event with timeout
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield {
                        "event": "event",
                        "data": json.dumps(event),
                    }
                except asyncio.TimeoutError:
                    # Send heartbeat
                    yield {
                        "event": "heartbeat",
                        "data": json.dumps({"timestamp": ""}),
                    }

        except asyncio.CancelledError:
            pass
        finally:
            unsubscribe(queue)

    return EventSourceResponse(
        event_generator(),
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/stream")
async def events_stream(
    request: Request,
    user: DemoUser = Depends(get_current_user),
) -> StreamingResponse:
    return await event_stream(request, user)