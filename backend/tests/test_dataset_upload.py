from pathlib import Path
from io import StringIO
import csv

from fastapi.testclient import TestClient

from app.database import fetch_one
from app.main import app
from app.services.dataset_service import load_csv, seed_sample_dataset
from tests.auth_helpers import auth_headers


ROOT = Path(__file__).resolve().parents[2]
client = TestClient(app)


def test_upload_valid_dataset_csv() -> None:
    path = ROOT / "datasets" / "sample" / "network_sites.csv"
    response = client.post(
        "/api/datasets/upload",
        headers=auth_headers(client, "analyst"),
        files={"file": ("network_sites.csv", path.read_bytes(), "text/csv")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["accepted"] is True
    assert payload["dataset_type"] == "network_sites"
    assert payload["rows"] == 250
    assert payload["imported"] is False
    assert payload["import_id"].startswith("IMP-")


def test_upload_invalid_dataset_csv() -> None:
    response = client.post(
        "/api/datasets/upload",
        headers=auth_headers(client, "analyst"),
        files={"file": ("bad.csv", b"wrong,column\n1,2\n", "text/csv")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["accepted"] is False
    assert payload["errors"]
    assert payload["imported"] is False
    assert payload["import_id"].startswith("IMP-")


def test_upload_valid_dataset_can_replace_table_safely() -> None:
    seed_sample_dataset()
    path = ROOT / "datasets" / "sample" / "network_sites.csv"
    rows = load_csv(path)
    rows[0]["site_name"] = "Jakarta Import Governance Test Node"
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

    response = client.post(
        "/api/datasets/upload",
        params={"persist": "true"},
        headers=auth_headers(client, "noc_manager"),
        files={"file": ("network_sites.csv", buffer.getvalue().encode("utf-8"), "text/csv")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["accepted"] is True
    assert payload["imported"] is True
    assert payload["import_id"].startswith("IMP-")
    stored = fetch_one("SELECT site_name FROM network_sites WHERE site_id = ?", ("SITE-0001",))
    assert stored is not None
    assert stored["site_name"] == "Jakarta Import Governance Test Node"


def test_invalid_persisted_import_does_not_replace_existing_table() -> None:
    seed_sample_dataset()
    before = fetch_one("SELECT COUNT(*) AS count FROM network_sites")

    response = client.post(
        "/api/datasets/upload",
        params={"persist": "true"},
        headers=auth_headers(client, "noc_manager"),
        files={"file": ("bad.csv", b"wrong,column\n1,2\n", "text/csv")},
    )

    after = fetch_one("SELECT COUNT(*) AS count FROM network_sites")
    assert response.status_code == 200
    assert response.json()["accepted"] is False
    assert response.json()["imported"] is False
    assert before == after


def test_persisted_import_can_be_rolled_back() -> None:
    seed_sample_dataset()
    path = ROOT / "datasets" / "sample" / "network_sites.csv"
    rows = load_csv(path)
    original = rows[0]["site_name"]
    rows[0]["site_name"] = "Rollback Candidate Site"
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    headers = auth_headers(client, "noc_manager")

    import_response = client.post(
        "/api/datasets/upload",
        params={"persist": "true"},
        headers=headers,
        files={"file": ("network_sites.csv", buffer.getvalue().encode("utf-8"), "text/csv")},
    )
    import_id = import_response.json()["import_id"]
    changed = fetch_one("SELECT site_name FROM network_sites WHERE site_id = ?", ("SITE-0001",))

    rollback_response = client.post(f"/api/datasets/import-history/{import_id}/rollback", headers=headers)
    restored = fetch_one("SELECT site_name FROM network_sites WHERE site_id = ?", ("SITE-0001",))
    history = client.get(f"/api/datasets/import-history/{import_id}", headers=headers)

    assert import_response.status_code == 200
    assert changed is not None
    assert changed["site_name"] == "Rollback Candidate Site"
    assert rollback_response.status_code == 200
    assert rollback_response.json()["rolled_back"] is True
    assert restored is not None
    assert restored["site_name"] == original
    assert history.json()["status"] == "rolled_back"


def test_viewer_cannot_rollback_import() -> None:
    response = client.post("/api/datasets/import-history/IMP-NOPE/rollback", headers=auth_headers(client, "viewer"))

    assert response.status_code == 403


def test_analyst_can_validate_but_cannot_persist_import() -> None:
    path = ROOT / "datasets" / "sample" / "network_sites.csv"
    response = client.post(
        "/api/datasets/upload",
        params={"persist": "true"},
        headers=auth_headers(client, "analyst"),
        files={"file": ("network_sites.csv", path.read_bytes(), "text/csv")},
    )

    assert response.status_code == 403
