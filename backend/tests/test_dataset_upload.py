from pathlib import Path
from io import StringIO
import csv

from fastapi.testclient import TestClient

from app.database import fetch_one
from app.main import app
from app.services.dataset_service import load_csv, seed_sample_dataset


ROOT = Path(__file__).resolve().parents[2]


def test_upload_valid_dataset_csv() -> None:
    path = ROOT / "datasets" / "sample" / "network_sites.csv"
    response = TestClient(app).post(
        "/api/datasets/upload",
        files={"file": ("network_sites.csv", path.read_bytes(), "text/csv")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["accepted"] is True
    assert payload["dataset_type"] == "network_sites"
    assert payload["rows"] == 250
    assert payload["imported"] is False


def test_upload_invalid_dataset_csv() -> None:
    response = TestClient(app).post(
        "/api/datasets/upload",
        files={"file": ("bad.csv", b"wrong,column\n1,2\n", "text/csv")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["accepted"] is False
    assert payload["errors"]
    assert payload["imported"] is False


def test_upload_valid_dataset_can_replace_table_safely() -> None:
    seed_sample_dataset()
    path = ROOT / "datasets" / "sample" / "network_sites.csv"
    rows = load_csv(path)
    rows[0]["site_name"] = "Jakarta Import Governance Test Node"
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

    response = TestClient(app).post(
        "/api/datasets/upload",
        params={"persist": "true"},
        files={"file": ("network_sites.csv", buffer.getvalue().encode("utf-8"), "text/csv")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["accepted"] is True
    assert payload["imported"] is True
    stored = fetch_one("SELECT site_name FROM network_sites WHERE site_id = ?", ("SITE-0001",))
    assert stored is not None
    assert stored["site_name"] == "Jakarta Import Governance Test Node"


def test_invalid_persisted_import_does_not_replace_existing_table() -> None:
    seed_sample_dataset()
    before = fetch_one("SELECT COUNT(*) AS count FROM network_sites")

    response = TestClient(app).post(
        "/api/datasets/upload",
        params={"persist": "true"},
        files={"file": ("bad.csv", b"wrong,column\n1,2\n", "text/csv")},
    )

    after = fetch_one("SELECT COUNT(*) AS count FROM network_sites")
    assert response.status_code == 200
    assert response.json()["accepted"] is False
    assert response.json()["imported"] is False
    assert before == after
