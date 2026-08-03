from __future__ import annotations

import csv
import json
import sqlite3
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import BinaryIO
from hashlib import md5

from app.config import settings
from app.database import get_connection

import sys

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.validate_telco_dataset import detect_dataset_type, read_csv, validate_single_file  # noqa: E402


CSV_TO_TABLE = {
    "network_sites.csv": "network_sites",
    "network_incidents.csv": "network_incidents",
    "customer_tickets.csv": "customer_tickets",
    "sla_metrics.csv": "sla_metrics",
    "field_technician_jobs.csv": "field_technician_jobs",
    "region_performance.csv": "region_performance",
    "service_quality_metrics.csv": "service_quality_metrics",
    "recommendation_rules.csv": "recommendation_rules",
    "network_assets.csv": "network_assets",
}
DATASET_TYPE_TO_FILE = {table_name: file_name for file_name, table_name in CSV_TO_TABLE.items()}


def table_for_file(file_name: str) -> str:
    return CSV_TO_TABLE[file_name]


def compute_row_hash(row: dict[str, str]) -> str:
    """Compute MD5 hash of row for duplicate detection."""
    row_str = json.dumps(row, sort_keys=True, ensure_ascii=True)
    return md5(row_str.encode()).hexdigest()


def detect_duplicate_rows(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], int]:
    """Filter out duplicate rows, returning unique rows and duplicate count."""
    seen_hashes = set()
    unique_rows = []
    duplicate_count = 0
    for row in rows:
        row_hash = compute_row_hash(row)
        if row_hash not in seen_hashes:
            seen_hashes.add(row_hash)
            unique_rows.append(row)
        else:
            duplicate_count += 1
    return unique_rows, duplicate_count


def preview_dataset(rows: list[dict[str, str]], limit: int = 5) -> dict[str, object]:
    """Generate preview summary of dataset."""
    if not rows:
        return {
            "row_count": 0,
            "columns": [],
            "preview_rows": [],
            "sample_columns": [],
        }
    columns = list(rows[0].keys())
    return {
        "row_count": len(rows),
        "columns": columns,
        "column_count": len(columns),
        "preview_rows": rows[:limit],
        "sample_columns": columns[:5],
    }


def create_table(connection: sqlite3.Connection, table_name: str, columns: list[str]) -> None:
    quoted_columns = ", ".join(f'"{column}" TEXT' for column in columns)
    connection.execute(f'DROP TABLE IF EXISTS "{table_name}"')
    connection.execute(f'CREATE TABLE "{table_name}" ({quoted_columns})')


def insert_rows(connection: sqlite3.Connection, table_name: str, rows: list[dict[str, str]], columns: list[str]) -> None:
    placeholders = ", ".join(["?"] * len(columns))
    column_list = ", ".join(f'"{column}"' for column in columns)
    values = [[row.get(column, "") for column in columns] for row in rows]
    connection.executemany(f'INSERT INTO "{table_name}" ({column_list}) VALUES ({placeholders})', values)


def table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
    row = connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name = ?", (table_name,)).fetchone()
    return row is not None


def read_table_snapshot(connection: sqlite3.Connection, table_name: str) -> dict[str, object]:
    if not table_exists(connection, table_name):
        return {"table_exists": False, "columns": [], "rows": []}
    columns = [row["name"] for row in connection.execute(f'PRAGMA table_info("{table_name}")').fetchall()]
    rows = [dict(row) for row in connection.execute(f'SELECT * FROM "{table_name}"').fetchall()]
    return {"table_exists": True, "columns": columns, "rows": rows}


def restore_table_snapshot(connection: sqlite3.Connection, table_name: str, snapshot: dict[str, object]) -> None:
    if not snapshot.get("table_exists"):
        connection.execute(f'DROP TABLE IF EXISTS "{table_name}"')
        return
    columns = [str(column) for column in snapshot.get("columns", [])]
    rows = [{str(key): str(value) for key, value in row.items()} for row in snapshot.get("rows", [])]  # type: ignore[union-attr]
    create_table(connection, table_name, columns)
    if rows:
        insert_rows(connection, table_name, rows, columns)


def replace_dataset_table(connection: sqlite3.Connection, dataset_type: str, rows: list[dict[str, str]]) -> None:
    if dataset_type not in DATASET_TYPE_TO_FILE:
        raise ValueError(f"Unsupported dataset type: {dataset_type}")
    columns = list(rows[0].keys()) if rows else []
    create_table(connection, dataset_type, columns)
    if rows:
        insert_rows(connection, dataset_type, rows, columns)


def ensure_import_history_table(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS import_history (
            import_id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            dataset_type TEXT,
            uploaded_at TEXT NOT NULL,
            row_count INTEGER NOT NULL,
            valid_row_count INTEGER NOT NULL,
            invalid_row_count INTEGER NOT NULL,
            status TEXT NOT NULL,
            validation_summary TEXT NOT NULL,
            actor TEXT
        )
        """
        )


def ensure_import_snapshot_table(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS import_snapshots (
            import_id TEXT PRIMARY KEY,
            dataset_type TEXT NOT NULL,
            created_at TEXT NOT NULL,
            snapshot_json TEXT NOT NULL
        )
        """
    )


def record_import_snapshot(
    connection: sqlite3.Connection,
    *,
    import_id: str,
    dataset_type: str,
    snapshot: dict[str, object],
) -> None:
    ensure_import_snapshot_table(connection)
    connection.execute(
        """
        INSERT INTO import_snapshots (import_id, dataset_type, created_at, snapshot_json)
        VALUES (?, ?, ?, ?)
        """,
        (
            import_id,
            dataset_type,
            datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            json.dumps(snapshot, ensure_ascii=True),
        ),
    )


def record_import_history(
    connection: sqlite3.Connection,
    *,
    filename: str,
    dataset_type: str | None,
    row_count: int,
    errors: list[str],
    warnings: list[str],
    status: str,
    actor: str | None = None,
) -> str:
    ensure_import_history_table(connection)
    import_id = f"IMP-{uuid.uuid4().hex[:12].upper()}"
    invalid_row_count = row_count if errors else 0
    valid_row_count = 0 if errors else row_count
    validation_summary = json.dumps({"errors": errors, "warnings": warnings}, ensure_ascii=True)
    connection.execute(
        """
        INSERT INTO import_history (
            import_id, filename, dataset_type, uploaded_at, row_count, valid_row_count,
            invalid_row_count, status, validation_summary, actor
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            import_id,
            filename,
            dataset_type,
            datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            row_count,
            valid_row_count,
            invalid_row_count,
            status,
            validation_summary,
            actor,
        ),
    )
    return import_id


def update_import_status(connection: sqlite3.Connection, import_id: str, status: str) -> None:
    ensure_import_history_table(connection)
    connection.execute("UPDATE import_history SET status = ? WHERE import_id = ?", (status, import_id))


def list_import_history() -> list[dict[str, object]]:
    with get_connection() as connection:
        ensure_import_history_table(connection)
        rows = connection.execute("SELECT * FROM import_history ORDER BY uploaded_at DESC").fetchall()
        return [dict(row) for row in rows]


def get_import_history(import_id: str) -> dict[str, object] | None:
    with get_connection() as connection:
        ensure_import_history_table(connection)
        row = connection.execute("SELECT * FROM import_history WHERE import_id = ?", (import_id,)).fetchone()
        return dict(row) if row else None


def seed_sample_dataset(dataset_dir: Path | None = None) -> dict[str, object]:
    source_dir = dataset_dir or settings.dataset_dir
    row_counts: dict[str, int] = {}
    with get_connection() as connection:
        for file_name, table_name in CSV_TO_TABLE.items():
            path = source_dir / file_name
            rows = load_csv(path)
            columns = list(rows[0].keys()) if rows else []
            create_table(connection, table_name, columns)
            if rows:
                insert_rows(connection, table_name, rows, columns)
            row_counts[table_name] = len(rows)
    return {
        "seeded": True,
        "database_path": str(settings.database_path),
        "row_counts": row_counts,
    }


def database_has_seed_data() -> bool:
    if not settings.database_path.exists():
        return False
    with get_connection() as connection:
        row = connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='network_sites'").fetchone()
        return row is not None


def build_validation_context(dataset_dir: Path | None = None) -> dict[str, set[str]]:
    source_dir = dataset_dir or settings.dataset_dir
    context: dict[str, set[str]] = {}
    sites_path = source_dir / "network_sites.csv"
    incidents_path = source_dir / "network_incidents.csv"
    if sites_path.exists():
        context["site_ids"] = {row["site_id"] for row in read_csv(sites_path)}
    if incidents_path.exists():
        context["incident_ids"] = {row["incident_id"] for row in read_csv(incidents_path)}
    return context


def validate_uploaded_csv(file_name: str, file_stream: BinaryIO, persist: bool = False, actor: str | None = None) -> dict[str, object]:
    content = file_stream.read()
    if not content:
        with get_connection() as connection:
            import_id = record_import_history(
                connection,
                filename=file_name,
                dataset_type=None,
                row_count=0,
                errors=["Uploaded file is empty"],
                warnings=[],
                status="rejected",
                actor=actor,
            )
        return {
            "accepted": False,
            "dataset_type": None,
            "rows": 0,
            "errors": ["Uploaded file is empty"],
            "warnings": [],
            "imported": False,
            "import_id": import_id,
        }

    with tempfile.NamedTemporaryFile(prefix="telco-upload-", suffix=".csv", delete=False) as temp_file:
        temp_file.write(content)
        temp_path = Path(temp_file.name)

    try:
        rows = read_csv(temp_path)
        dataset_name = detect_dataset_type(list(rows[0].keys()) if rows else [])
        if dataset_name is None:
            errors = [f"{file_name} does not match any supported TelcoOps dataset schema"]
            with get_connection() as connection:
                import_id = record_import_history(
                    connection,
                    filename=file_name,
                    dataset_type=None,
                    row_count=len(rows),
                    errors=errors,
                    warnings=[],
                    status="rejected",
                    actor=actor,
                )
            return {
                "accepted": False,
                "dataset_type": None,
                "rows": len(rows),
                "errors": errors,
                "warnings": [],
                "imported": False,
                "import_id": import_id,
            }
        result = validate_single_file(temp_path, build_validation_context(), expected_name=dataset_name)
        imported = False
        status = "validated" if result.passed else "rejected"
        if persist and result.passed:
            with get_connection() as connection:
                import_id = record_import_history(
                    connection,
                    filename=file_name,
                    dataset_type=result.dataset_type,
                    row_count=result.rows,
                    errors=result.errors,
                    warnings=result.warnings,
                    status="imported",
                    actor=actor,
                )
                record_import_snapshot(
                    connection,
                    import_id=import_id,
                    dataset_type=result.dataset_type,
                    snapshot=read_table_snapshot(connection, result.dataset_type),
                )
                replace_dataset_table(connection, result.dataset_type, rows)
            imported = True
        else:
            with get_connection() as connection:
                import_id = record_import_history(
                    connection,
                    filename=file_name,
                    dataset_type=result.dataset_type,
                    row_count=result.rows,
                    errors=result.errors,
                    warnings=result.warnings,
                    status=status,
                    actor=actor,
                )
        return {
            "accepted": result.passed,
            "dataset_type": result.dataset_type,
            "rows": result.rows,
            "errors": result.errors,
            "warnings": result.warnings,
            "imported": imported,
            "import_id": import_id,
        }
    finally:
        temp_path.unlink(missing_ok=True)


def rollback_import(import_id: str) -> dict[str, object]:
    with get_connection() as connection:
        ensure_import_history_table(connection)
        ensure_import_snapshot_table(connection)
        import_row = connection.execute("SELECT * FROM import_history WHERE import_id = ?", (import_id,)).fetchone()
        if import_row is None:
            raise ValueError("Import history record not found")
        if import_row["status"] != "imported":
            raise ValueError("Only imports with status 'imported' can be rolled back")
        snapshot_row = connection.execute("SELECT * FROM import_snapshots WHERE import_id = ?", (import_id,)).fetchone()
        if snapshot_row is None:
            raise ValueError("Rollback snapshot not found for import")
        snapshot = json.loads(snapshot_row["snapshot_json"])
        restore_table_snapshot(connection, snapshot_row["dataset_type"], snapshot)
        update_import_status(connection, import_id, "rolled_back")
        return {
            "rolled_back": True,
            "import_id": import_id,
            "dataset_type": snapshot_row["dataset_type"],
            "restored_rows": len(snapshot.get("rows", [])),
        }
