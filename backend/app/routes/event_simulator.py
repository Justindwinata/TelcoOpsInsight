from __future__ import annotations

from fastapi import APIRouter, Depends

from app.config import settings
from app.services.auth_service import DemoUser, get_current_user
from app.services.event_simulator import (
    generate_random_event,
    get_simulator_stats,
    set_interval,
    start_simulator,
    stop_simulator,
)

router = APIRouter(prefix=f"{settings.api_prefix}/events/simulator", tags=["events-simulator"])


@router.get("/status")
def simulator_status(_: DemoUser = Depends(get_current_user)) -> dict:
    return get_simulator_stats()


@router.post("/start")
async def simulator_start(
    interval_seconds: float = 5.0,
    _: DemoUser = Depends(get_current_user),
) -> dict:
    return await start_simulator(interval_seconds=interval_seconds)


@router.post("/stop")
async def simulator_stop(_: DemoUser = Depends(get_current_user)) -> dict:
    return await stop_simulator()


@router.post("/interval")
def simulator_interval(interval_seconds: float = 5.0, _: DemoUser = Depends(get_current_user)) -> dict:
    return set_interval(interval_seconds)


@router.post("/generate")
def simulator_generate(_: DemoUser = Depends(get_current_user)) -> dict:
    """Generate a single event manually (useful for testing)."""
    return generate_random_event()