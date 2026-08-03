from __future__ import annotations

from typing import Any

from app.validation import safe_int, safe_str, validate_date_range, validate_positive_number, sanitize_sql_identifier, validate_enum


def validate_api_request(data: dict, required_fields: list[str]) -> tuple[bool, str | None]:
    """Validate API request data."""
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
        if safe_str(data[field]) == "":
            return False, f"Field cannot be empty: {field}"
    return True, None


def standardize_error_response(code: str, message: str, status_code: int) -> dict[str, object]:
    """Standardize error response format."""
    return {
        "error": {
            "code": code,
            "message": message,
            "status_code": status_code,
        },
        "detail": message,
    }


def standardize_success_response(data: dict | list, metadata: dict | None = None) -> dict[str, object]:
    """Standardize success response format with consistent envelope."""
    result: dict[str, Any] = {
        "data": data,
        "status": "success",
    }
    if metadata:
        result["metadata"] = metadata
    return result


def standardize_list_response(
    items: list,
    metadata: dict | None = None,
    page: int = 1,
    page_size: int = 50,
) -> dict[str, object]:
    """Standardize paginated list response."""
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = items[start:end]
    result: dict[str, Any] = {
        "data": paginated,
        "status": "success",
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size,
        },
    }
    if metadata:
        result["metadata"] = metadata
    return result


def paginate_data(data: list, page: int = 1, page_size: int = 50) -> dict[str, object]:
    """Paginate data with metadata."""
    total = len(data)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = data[start:end]
    return {
        "data": paginated,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size,
        },
    }


def extract_page_params(query_params: dict) -> tuple[int, int]:
    """Extract page and page_size from query params with safe defaults."""
    page = safe_int(query_params.get("page"), 1)
    page_size = safe_int(query_params.get("page_size"), 50)
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 500:
        page_size = 50
    return page, page_size


def api_response(data: Any, *, metadata: dict | None = None) -> dict[str, Any]:
    """Standard response envelope for all API endpoints."""
    result: dict[str, Any] = {
        "data": data,
        "status": "success",
    }
    if metadata:
        result["metadata"] = metadata
    return result


def api_error(code: str, message: str, *, status_code: int = 400, details: list | None = None) -> dict[str, Any]:
    """Standard error envelope for all API endpoints."""
    result: dict[str, Any] = {
        "error": {
            "code": code,
            "message": message,
            "status_code": status_code,
        },
    }
    if details:
        result["error"]["details"] = details
    return result
