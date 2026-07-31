from __future__ import annotations

from pydantic import BaseModel


class SeedResponse(BaseModel):
    seeded: bool
    database_path: str
    row_counts: dict[str, int]


class ValidationResponse(BaseModel):
    accepted: bool
    dataset_type: str | None
    rows: int
    errors: list[str]
    warnings: list[str]
    imported: bool = False
