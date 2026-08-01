from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def _message_from_detail(detail: object) -> str:
    if isinstance(detail, str):
        if "start_date must be before or equal to end_date" in detail:
            return "start_date must be before or equal to end_date"
        return detail
    if isinstance(detail, list):
        return "Request validation failed"
    if isinstance(detail, dict) and "message" in detail:
        return str(detail["message"])
    return "Request failed"


def _code_for_status(status_code: int) -> str:
    if status_code == 400:
        return "bad_request"
    if status_code == 401:
        return "auth_failed"
    if status_code == 403:
        return "permission_denied"
    if status_code == 404:
        return "not_found"
    if status_code == 422:
        return "validation_error"
    return "request_failed"


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        message = _message_from_detail(exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "error": {
                    "code": _code_for_status(exc.status_code),
                    "message": message,
                    "status_code": exc.status_code,
                },
            },
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "detail": exc.errors(),
                "error": {
                    "code": "validation_error",
                    "message": "Request validation failed",
                    "status_code": 422,
                },
            },
        )
