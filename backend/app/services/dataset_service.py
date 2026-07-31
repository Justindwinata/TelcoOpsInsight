from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

from app.config import settings
from app.database import get_connection


CSV_TO_TABLE = {
    "network_sites.csv": "network_sites",
    "network_incidents.csv": "network_incidents",
    "customer_tickets.csv": "customer_tickets",
    "sla_metrics.csv": "sla_metrics",
    "field_technician_jobs.csv": "field_technician_jobs",
    "region_performance.csv": "region_performance",
    "service_quality_metrics.csv": "service_quality_metrics",
    "recommendation_rules.csv": "recommendation_rules",
}


def table_for_file(file_name: str) -> str:
    return CSV_TO_TABLE[file_name]


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def create_table(connection: sqlite3.Connection, table_name: str, columns: list[str]) -> None:
    quoted_columns = ", ".join(f'"{column}" TEXT' for column in columns)
    connection.execute(f'DROP TABLE IF EXISTS "{table_name}"')
    connection.execute(f'CREATE TABLE "{table_name}" ({quoted_columns})')


def insert_rows(connection: sqlite3.Connection, table_name: str, rows: list[dict[str, str]], columns: list[str]) -> None:
    placeholders = ", ".join(["?"] * len(columns))
    column_list = ", ".join(f'"{column}"' for column in columns)
    values = [[row.get(column, "") for column in columns] for row in rows]
    connection.executemany(f'INSERT INTO "{table_name}" ({column_list}) VALUES ({placeholders})', values)


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
