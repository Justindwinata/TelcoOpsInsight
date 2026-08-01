#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE = ROOT / "backend" / "telco_ops.db"
DEFAULT_BACKUP_DIR = ROOT / "backups"


def timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y%m%dT%H%M%SZ")


def backup_database(database_path: Path, backup_dir: Path) -> dict[str, str]:
    if not database_path.exists():
        raise FileNotFoundError(f"Database file not found: {database_path}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = timestamp()
    backup_path = backup_dir / f"telco_ops_{stamp}.db"
    manifest_path = backup_dir / f"telco_ops_{stamp}.manifest.json"
    shutil.copy2(database_path, backup_path)
    manifest = {
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "database_path": str(database_path),
        "backup_path": str(backup_path),
        "manifest_path": str(manifest_path),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Back up the local TelcoOps Insight SQLite database.")
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--backup-dir", type=Path, default=DEFAULT_BACKUP_DIR)
    args = parser.parse_args()
    manifest = backup_database(args.database.resolve(), args.backup_dir.resolve())
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
