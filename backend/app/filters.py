from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


REGIONS = {
    "Jakarta",
    "Bandung",
    "Surabaya",
    "Medan",
    "Makassar",
    "Semarang",
    "Yogyakarta",
    "Denpasar",
    "Palembang",
    "Balikpapan",
}
SERVICE_TYPES = {
    "Fiber Internet",
    "Mobile Broadband",
    "Enterprise VPN",
    "IPTV",
    "Voice",
    "Cloud Connectivity",
}
SEVERITIES = {"Low", "Medium", "High", "Critical"}
STATUSES = {"Open", "Investigating", "Escalated", "Resolved", "Closed", "In Progress", "Waiting Customer"}
TEAMS = {"NOC Core", "Field Operations", "Customer Assurance", "Fiber Maintenance", "Enterprise Support"}


class AnalyticsFilters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    start_date: date | None = Field(default=None)
    end_date: date | None = Field(default=None)
    month: str | None = Field(default=None, pattern=r"^2026-(0[1-9]|1[0-2])$")
    region: str | None = None
    service_type: str | None = None
    severity: str | None = None
    status: str | None = None
    team: str | None = None

    @field_validator("region")
    @classmethod
    def validate_region(cls, value: str | None) -> str | None:
        if value is not None and value not in REGIONS:
            raise ValueError(f"Unsupported region: {value}")
        return value

    @field_validator("service_type")
    @classmethod
    def validate_service_type(cls, value: str | None) -> str | None:
        if value is not None and value not in SERVICE_TYPES:
            raise ValueError(f"Unsupported service_type: {value}")
        return value

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, value: str | None) -> str | None:
        if value is not None and value not in SEVERITIES:
            raise ValueError(f"Unsupported severity: {value}")
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        if value is not None and value not in STATUSES:
            raise ValueError(f"Unsupported status: {value}")
        return value

    @field_validator("team")
    @classmethod
    def validate_team(cls, value: str | None) -> str | None:
        if value is not None and value not in TEAMS:
            raise ValueError(f"Unsupported team: {value}")
        return value

    @model_validator(mode="after")
    def validate_date_range(self) -> "AnalyticsFilters":
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("start_date must be before or equal to end_date")
        if self.month and (self.start_date or self.end_date):
            raise ValueError("Use either month or start_date/end_date, not both")
        return self

    def active_dict(self) -> dict[str, str]:
        data = self.model_dump(exclude_none=True)
        return {key: value.isoformat() if isinstance(value, date) else str(value) for key, value in data.items()}

    def metadata(self) -> dict[str, object]:
        return {
            "applied_filters": self.active_dict(),
            "available_filters": {
                "regions": sorted(REGIONS),
                "service_types": sorted(SERVICE_TYPES),
                "severities": sorted(SEVERITIES),
                "statuses": sorted(STATUSES),
                "teams": sorted(TEAMS),
            },
        }


def build_filters(
    start_date: Annotated[date | None, Query(description="Inclusive YYYY-MM-DD start date")] = None,
    end_date: Annotated[date | None, Query(description="Inclusive YYYY-MM-DD end date")] = None,
    month: Annotated[str | None, Query(description="Month key in YYYY-MM format")] = None,
    region: Annotated[str | None, Query(description="Region name")] = None,
    service_type: Annotated[str | None, Query(description="Service type")] = None,
    severity: Annotated[str | None, Query(description="Severity or priority")] = None,
    status: Annotated[str | None, Query(description="Incident, ticket, or job status")] = None,
    team: Annotated[str | None, Query(description="Operational team")] = None,
) -> AnalyticsFilters:
    try:
        return AnalyticsFilters(
            start_date=start_date,
            end_date=end_date,
            month=month,
            region=region,
            service_type=service_type,
            severity=severity,
            status=status,
            team=team,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
