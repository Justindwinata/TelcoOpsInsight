from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.error_handlers import register_error_handlers
from app.routes import audit, assets, auth, dashboard, datasets, health, maintenance, reports


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
    app.include_router(reports.router)
    return app


app = create_app()
