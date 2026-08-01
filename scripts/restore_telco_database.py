#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE = ROOT / "backend" / "telco_ops.db"


def restore_database(backup_path: Path, database_path: Path) -> dict[str, str]:
    if not backup_path.exists():
        raise FileNotFoundError(f"Backup file not found: {backup_path}")
    if backup_path.suffix != ".db":
        raise ValueError("Backup path must point to a .db file")
    database_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(backup_path, database_path)
    result = {"restored_from": str(backup_path), "database_path": str(database_path)}
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Restore the local TelcoOps Insight SQLite database from a backup.")
    parser.add_argument("backup", type=Path)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    args = parser.parse_args()
    result = restore_database(args.backup.resolve(), args.database.resolve())
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
