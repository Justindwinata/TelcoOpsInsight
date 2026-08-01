from app.services.auth_service import ensure_auth_tables, get_user_by_username, hash_token, login
from app.database import fetch_one


def test_demo_users_are_persisted_to_sqlite() -> None:
    ensure_auth_tables()

    user = get_user_by_username("noc_manager")

    assert user is not None
    assert user.role == "NOC Manager"
    row = fetch_one("SELECT password_hash FROM users WHERE username = ?", ("noc_manager",))
    assert row is not None
    assert row["password_hash"] != "telco-demo-2026"


def test_login_persists_hashed_session_token() -> None:
    payload = login("viewer", "telco-demo-2026")
    token = str(payload["access_token"])

    row = fetch_one("SELECT token_hash, expires_at, revoked_at FROM sessions WHERE token_hash = ?", (hash_token(token),))

    assert row is not None
    assert row["token_hash"] != token
    assert row["expires_at"]
    assert row["revoked_at"] is None
