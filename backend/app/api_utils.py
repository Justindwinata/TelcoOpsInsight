from __future__ import annotations

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


def standardize_success_response(data: dict, metadata: dict | None = None) -> dict[str, object]:
    """Standardize success response format."""
    result = {"data": data}
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
