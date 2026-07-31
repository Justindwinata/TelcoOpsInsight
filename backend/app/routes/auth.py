from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials

from app.config import settings
from app.schemas import LoginRequest, TokenResponse, UserProfile
from app.services.auth_service import DemoUser, get_current_user, login, logout, security, user_to_profile


router = APIRouter(prefix=f"{settings.api_prefix}/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login_route(payload: LoginRequest) -> dict[str, object]:
    return login(payload.username, payload.password)


@router.get("/me", response_model=UserProfile)
def current_user_route(user: DemoUser = Depends(get_current_user)) -> dict[str, object]:
    return user_to_profile(user)


@router.post("/logout")
def logout_route(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict[str, object]:
    if credentials is not None:
        logout(credentials.credentials)
    return {"logged_out": True}
