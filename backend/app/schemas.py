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
    import_id: str | None = None


class ImportHistoryEntry(BaseModel):
    import_id: str
    filename: str
    dataset_type: str | None
    uploaded_at: str
    row_count: int
    valid_row_count: int
    invalid_row_count: int
    status: str
    validation_summary: str
    actor: str | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class UserProfile(BaseModel):
    username: str
    display_name: str
    role: str
    permissions: list[str]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile
