from fastapi.testclient import TestClient

from app.main import app
from tests.auth_helpers import auth_headers


client = TestClient(app)


def test_viewer_denied_dataset_import_permission() -> None:
    response = client.post(
        "/api/datasets/upload",
        headers=auth_headers(client, "viewer"),
        files={"file": ("bad.csv", b"wrong,column\n1,2\n", "text/csv")},
    )

    assert response.status_code == 403
    assert "datasets:validate" in response.text


def test_noc_manager_has_full_prototype_permissions() -> None:
    response = client.get("/api/auth/me", headers=auth_headers(client, "noc_manager"))

    assert response.status_code == 200
    permissions = response.json()["permissions"]
    assert "datasets:seed" in permissions
    assert "datasets:import" in permissions
    assert "imports:read" in permissions


def test_role_permission_matrix_for_protected_actions() -> None:
    roles = {
        "noc_manager": {
            "seed": 200,
            "validate": 200,
            "import": 200,
            "history": 200,
            "report": 200,
            "report_html": 200,
        },
        "service_assurance": {
            "seed": 403,
            "validate": 403,
            "import": 403,
            "history": 200,
            "report": 200,
            "report_html": 200,
        },
        "field_ops": {
            "seed": 403,
            "validate": 403,
            "import": 403,
            "history": 403,
            "report": 200,
            "report_html": 200,
        },
        "analyst": {
            "seed": 403,
            "validate": 200,
            "import": 403,
            "history": 403,
            "report": 200,
            "report_html": 200,
        },
        "viewer": {
            "seed": 403,
            "validate": 403,
            "import": 403,
            "history": 403,
            "report": 200,
            "report_html": 200,
        },
    }

    for username, expected in roles.items():
        headers = auth_headers(client, username)
        validate_files = {"file": ("bad.csv", b"wrong,column\n1,2\n", "text/csv")}
        import_files = {"file": ("bad.csv", b"wrong,column\n1,2\n", "text/csv")}
        responses = {
            "seed": client.post("/api/datasets/seed", headers=headers),
            "validate": client.post("/api/datasets/upload", headers=headers, files=validate_files),
            "import": client.post("/api/datasets/upload", params={"persist": "true"}, headers=headers, files=import_files),
            "history": client.get("/api/datasets/import-history", headers=headers),
            "report": client.get("/api/reports/executive-summary", headers=headers),
            "report_html": client.get("/api/reports/executive-summary.html", headers=headers),
        }

        for action, response in responses.items():
            assert response.status_code == expected[action], f"{username} {action}"
            if expected[action] == 403:
                assert "Permission denied" in response.text
