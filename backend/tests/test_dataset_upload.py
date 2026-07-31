from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


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


def test_upload_invalid_dataset_csv() -> None:
    response = TestClient(app).post(
        "/api/datasets/upload",
        files={"file": ("bad.csv", b"wrong,column\n1,2\n", "text/csv")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["accepted"] is False
    assert payload["errors"]
