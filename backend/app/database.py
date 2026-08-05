from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from app.config import settings


@contextmanager
def get_connection(database_path: Path | None = None) -> Iterator[sqlite3.Connection]:
    path = database_path or settings.database_path
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA synchronous=NORMAL")
    connection.execute("PRAGMA cache_size=-20000")
    connection.execute("PRAGMA temp_store=MEMORY")
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def fetch_all(query: str, params: tuple[object, ...] = ()) -> list[dict[str, object]]:
    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def fetch_one(query: str, params: tuple[object, ...] = ()) -> dict[str, object] | None:
    with get_connection() as connection:
        row = connection.execute(query, params).fetchone()
        return dict(row) if row else None
