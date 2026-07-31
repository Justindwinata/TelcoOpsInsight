from __future__ import annotations

from pathlib import Path
from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "TelcoOps Insight API"
    company_name: str = "NusaTel Digital Network"
    api_prefix: str = "/api"
    root_dir: Path = Path(__file__).resolve().parents[2]
    dataset_dir: Path = root_dir / "datasets" / "sample"
    database_path: Path = root_dir / "backend" / "telco_ops.db"


settings = Settings()
