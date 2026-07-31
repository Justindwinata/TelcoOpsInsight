from datetime import date

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.filters import AnalyticsFilters, build_filters


def test_filter_model_accepts_supported_values() -> None:
    filters = AnalyticsFilters(
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
        region="Jakarta",
        service_type="Fiber Internet",
        severity="High",
        status="Resolved",
        team="NOC Core",
    )

    assert filters.active_dict()["region"] == "Jakarta"
    assert filters.active_dict()["start_date"] == "2026-01-01"


def test_filter_model_rejects_invalid_region() -> None:
    with pytest.raises(ValidationError, match="Unsupported region"):
        AnalyticsFilters(region="Gotham")


def test_filter_model_rejects_invalid_date_range() -> None:
    with pytest.raises(ValidationError, match="start_date must be before"):
        AnalyticsFilters(start_date=date(2026, 2, 1), end_date=date(2026, 1, 1))


def test_filter_model_rejects_month_mixed_with_date_range() -> None:
    with pytest.raises(ValidationError, match="Use either month"):
        AnalyticsFilters(month="2026-01", start_date=date(2026, 1, 1))


def test_build_filters_returns_readable_http_error() -> None:
    with pytest.raises(HTTPException) as exc:
        build_filters(region="Invalid Region")

    assert exc.value.status_code == 422
    assert "Unsupported region" in str(exc.value.detail)
