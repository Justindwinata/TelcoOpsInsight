from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.error_handlers import register_error_handlers
from app.routes import audit, alarms, assets, auth, cache, business_dashboard, calendar, capacity, changes, dashboard, datasets, dispatch, event_simulator, events, executive, executive_decision, exports, health, live_status, maintenance, major_incidents, noc, rca, reports, service_requests, sla_monitoring, timeline, workforce


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="Network Operations and Service Assurance Dashboard API for synthetic telecom operations data.",
        version="0.1.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_error_handlers(app)
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(audit.router)
    app.include_router(datasets.router)
    app.include_router(dashboard.router)
    app.include_router(assets.router)
    app.include_router(maintenance.router)
    app.include_router(changes.router)
    app.include_router(rca.router)
    app.include_router(reports.router)
    app.include_router(timeline.router)
    app.include_router(executive.router)
    app.include_router(workforce.router)
    app.include_router(dispatch.router)
    app.include_router(service_requests.router)
    app.include_router(sla_monitoring.router)
    app.include_router(capacity.router)
    app.include_router(executive_decision.router)
    app.include_router(noc.router)
    app.include_router(alarms.router)
    app.include_router(major_incidents.router)
    app.include_router(calendar.router)
    app.include_router(exports.router)
    app.include_router(business_dashboard.router)
    app.include_router(cache.router)
    app.include_router(events.router)
    app.include_router(event_simulator.router)
    app.include_router(live_status.router)
    return app


app = create_app()
