from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.database import get_connection


ROLE_PERMISSIONS = {
    "NOC Manager": {
        "dashboard:read",
        "datasets:seed",
        "datasets:validate",
        "datasets:import",
        "imports:read",
        "reports:read",
        "recommendations:read",
        "audit:read",
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
SESSION_HOURS = 8


def hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000).hex()


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def ensure_auth_tables() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                role TEXT NOT NULL,
                salt TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                active INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                token_hash TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                revoked_at TEXT,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
            """
        )
        created_at = utc_now().isoformat()
        for user in DEMO_USERS.values():
            connection.execute(
                """
                INSERT OR IGNORE INTO users (
                    user_id, username, display_name, role, salt, password_hash, active, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f"USR-{user.username}",
                    user.username,
                    user.display_name,
                    user.role,
                    user.salt,
                    user.password_hash,
                    1,
                    created_at,
                ),
            )


def user_from_row(row) -> DemoUser:
    return DemoUser(
        username=row["username"],
        display_name=row["display_name"],
        role=row["role"],
        salt=row["salt"],
        password_hash=row["password_hash"],
    )


def get_user_by_username(username: str) -> DemoUser | None:
    ensure_auth_tables()
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM users WHERE username = ? AND active = 1", (username,)).fetchone()
        return user_from_row(row) if row else None


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
    user = get_user_by_username(username)
    if user is None or not verify_password(password, user):
        from app.services.audit_service import record_audit

        record_audit(
            actor_username=username,
            actor_role=None,
            action="auth.login",
            entity_type="session",
            summary="Login failed",
            status="failure",
        )
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = secrets.token_urlsafe(32)
    now = utc_now()
    expires_at = now + timedelta(hours=SESSION_HOURS)
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO sessions (session_id, token_hash, user_id, created_at, expires_at, revoked_at)
            VALUES (?, ?, ?, ?, ?, NULL)
            """,
            (
                f"SES-{secrets.token_hex(12).upper()}",
                hash_token(token),
                f"USR-{user.username}",
                now.isoformat(),
                expires_at.isoformat(),
            ),
        )
    from app.services.audit_service import record_audit

    record_audit(
        actor_username=user.username,
        actor_role=user.role,
        action="auth.login",
        entity_type="session",
        summary="Login succeeded",
        status="success",
    )
    return {"access_token": token, "token_type": "bearer", "expires_at": expires_at.isoformat(), "user": user_to_profile(user)}


def logout(token: str) -> None:
    ensure_auth_tables()
    user = None
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT users.username, users.role
            FROM sessions JOIN users ON users.user_id = sessions.user_id
            WHERE sessions.token_hash = ?
            """,
            (hash_token(token),),
        ).fetchone()
        if row:
            user = row
        connection.execute(
            "UPDATE sessions SET revoked_at = ? WHERE token_hash = ? AND revoked_at IS NULL",
            (utc_now().isoformat(), hash_token(token)),
        )
    from app.services.audit_service import record_audit

    record_audit(
        actor_username=user["username"] if user else None,
        actor_role=user["role"] if user else None,
        action="auth.logout",
        entity_type="session",
        summary="Logout requested",
        status="success",
    )


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> DemoUser:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    ensure_auth_tables()
    token_digest = hash_token(credentials.credentials)
    with get_connection() as connection:
        session = connection.execute(
            "SELECT session_id, expires_at FROM sessions WHERE token_hash = ? AND revoked_at IS NULL",
            (token_digest,),
        ).fetchone()
        if session is None:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        if datetime.fromisoformat(session["expires_at"]) <= utc_now():
            connection.execute(
                "UPDATE sessions SET revoked_at = ? WHERE session_id = ?",
                (utc_now().isoformat(), session["session_id"]),
            )
            raise HTTPException(status_code=401, detail="Session expired")
        row = connection.execute(
            """
            SELECT users.*
            FROM sessions
            JOIN users ON users.user_id = sessions.user_id
            WHERE sessions.token_hash = ?
              AND sessions.revoked_at IS NULL
              AND users.active = 1
            """,
            (token_digest,),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=401, detail="User is disabled or unavailable")
    return user_from_row(row)


def ensure_permission(user: DemoUser, permission: str) -> None:
    if permission not in user.permissions:
        from app.services.audit_service import record_audit

        record_audit(
            actor_username=user.username,
            actor_role=user.role,
            action="permission.denied",
            entity_type="permission",
            entity_id=permission,
            summary=f"Permission denied: {permission}",
            status="denied",
        )
        raise HTTPException(status_code=403, detail=f"Permission denied: {permission}")


def require_permission(permission: str):
    def dependency(user: DemoUser = Depends(get_current_user)) -> DemoUser:
        ensure_permission(user, permission)
        return user

    return dependency
