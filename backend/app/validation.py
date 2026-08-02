from __future__ import annotations

from typing import Any


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to int with fallback."""
    if value is None or value == "":
        return default
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def safe_str(value: Any, default: str = "") -> str:
    """Safely convert value to string with fallback."""
    if value is None:
        return default
    return str(value).strip()


def validate_date_range(start_date: str | None, end_date: str | None) -> tuple[bool, str | None]:
    """Validate date range inputs."""
    if not start_date and not end_date:
        return True, None
    if start_date and end_date:
        if start_date > end_date:
            return False, "start_date must be before or equal to end_date"
    return True, None


def validate_positive_number(value: Any, field_name: str) -> tuple[bool, str | None]:
    """Validate that a value is a positive number."""
    try:
        num = float(value)
        if num < 0:
            return False, f"{field_name} must be non-negative"
        return True, None
    except (TypeError, ValueError):
        return False, f"{field_name} must be a valid number"


def sanitize_sql_identifier(identifier: str) -> str:
    """Sanitize SQL identifier to prevent injection."""
    return "".join(c for c in identifier if c.isalnum() or c == "_")


def validate_enum(value: str, allowed: set[str], field_name: str) -> tuple[bool, str | None]:
    """Validate that value is in allowed set."""
    if value not in allowed:
        return False, f"{field_name} must be one of: {', '.join(sorted(allowed))}"
    return True, None
