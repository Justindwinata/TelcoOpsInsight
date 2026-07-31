from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


ROLE_PERMISSIONS = {
    "NOC Manager": {
        "dashboard:read",
        "datasets:seed",
        "datasets:validate",
        "datasets:import",
        "imports:read",
        "reports:read",
        "recommendations:read",
    },
    "Service Assurance Lead": {"dashboard:read", "reports:read", "recommendations:read", "imports:read"},
    "Field Operations Lead": {"dashboard:read", "reports:read", "recommendations:read"},
    "Analyst": {"dashboard:read", "datasets:validate", "reports:read"},
    "Viewer": {"dashboard:read", "reports:read"},
}


@dataclass(frozen=True)
class DemoUser:
    username: str
    display_name: str
    role: str
    salt: str
    password_hash: str

    @property
    def permissions(self) -> list[str]:
        return sorted(ROLE_PERMISSIONS[self.role])


DEMO_USERS = {
    "noc_manager": DemoUser(
        "noc_manager",
        "NOC Manager Demo",
        "NOC Manager",
        "telcoops-noc_manager-2026",
        "56f7743eb13af2a74f492b3591c40f1d2a2d6cb50e04e00c1b1fa26b88440618",
    ),
    "service_assurance": DemoUser(
        "service_assurance",
        "Service Assurance Demo",
        "Service Assurance Lead",
        "telcoops-service_assurance-2026",
        "7a4f35d543b53fff6a2bdd44ee498616090a0c9078029a191b3bb72974ce0805",
    ),
    "field_ops": DemoUser(
        "field_ops",
        "Field Operations Demo",
        "Field Operations Lead",
        "telcoops-field_ops-2026",
        "7229d03888ba131f58edaafefe7b1b2f1ef2298e56d4b65104b3af3de1aca5f8",
    ),
    "analyst": DemoUser(
        "analyst",
        "Analyst Demo",
        "Analyst",
        "telcoops-analyst-2026",
        "8e2c377a96cd29f30559e55dd7180a7115b9c318f6f346d6bd4500d1e25fbb10",
    ),
    "viewer": DemoUser(
        "viewer",
        "Viewer Demo",
        "Viewer",
        "telcoops-viewer-2026",
        "8a5cb388c1566f3ed3c7e1e2d696938341501c42415c03f5254425627220afdb",
    ),
}

security = HTTPBearer(auto_error=False)
ACTIVE_TOKENS: dict[str, str] = {}


def hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000).hex()


def verify_password(password: str, user: DemoUser) -> bool:
    return hmac.compare_digest(hash_password(password, user.salt), user.password_hash)


def user_to_profile(user: DemoUser) -> dict[str, object]:
    return {
        "username": user.username,
        "display_name": user.display_name,
        "role": user.role,
        "permissions": user.permissions,
    }


def login(username: str, password: str) -> dict[str, object]:
    user = DEMO_USERS.get(username)
    if user is None or not verify_password(password, user):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = secrets.token_urlsafe(32)
    ACTIVE_TOKENS[token] = user.username
    return {"access_token": token, "token_type": "bearer", "user": user_to_profile(user)}


def logout(token: str) -> None:
    ACTIVE_TOKENS.pop(token, None)


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> DemoUser:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    username = ACTIVE_TOKENS.get(credentials.credentials)
    if username is None or username not in DEMO_USERS:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return DEMO_USERS[username]


def ensure_permission(user: DemoUser, permission: str) -> None:
    if permission not in user.permissions:
        raise HTTPException(status_code=403, detail=f"Permission denied: {permission}")


def require_permission(permission: str):
    def dependency(user: DemoUser = Depends(get_current_user)) -> DemoUser:
        ensure_permission(user, permission)
        return user

    return dependency
