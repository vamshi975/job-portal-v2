from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path

import pandas as pd

from core.config import StorageConfig


def daily_parquet_path(storage: StorageConfig, country: str, run_date: date) -> Path:
    country_slug = country.lower().replace(" ", "_")
    country_dir = Path(storage.daily_data_dir) / country_slug
    country_dir.mkdir(parents=True, exist_ok=True)
    return country_dir / f"{run_date.isoformat()}.parquet"


def processed_parquet_path(storage: StorageConfig) -> Path:
    return Path(storage.processed_data_dir) / storage.processed_filename


def read_daily_parquets(
    storage: StorageConfig, country: str, since_days: int
) -> pd.DataFrame:
    today = date.today()
    country_slug = country.lower().replace(" ", "_")
    country_dir = Path(storage.daily_data_dir) / country_slug
    if not country_dir.exists():
        return pd.DataFrame()

    frames = []
    for i in range(since_days):
        d = date.fromordinal(today.toordinal() - i)
        p = country_dir / f"{d.isoformat()}.parquet"
        if p.exists():
            df = pd.read_parquet(p)
            df["first_seen_date"] = d
            frames.append(df)

    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def delete_old_daily_files(storage: StorageConfig, max_days: int) -> None:
    today = date.today()
    for parquet in Path(storage.daily_data_dir).rglob("*.parquet"):
        try:
            file_date = date.fromisoformat(parquet.stem)
            if (today - file_date).days > max_days:
                parquet.unlink()
        except ValueError:
            pass


def get_db_connection(storage: StorageConfig) -> sqlite3.Connection:
    db_path = Path(storage.db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def ensure_db_schema(storage: StorageConfig) -> None:
    with get_db_connection(storage) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS job_status (
                uuid        TEXT PRIMARY KEY,
                status      TEXT NOT NULL DEFAULT 'new'
                                CHECK (status IN ('new', 'interesting', 'applied')),
                notes       TEXT,
                updated_at  TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                job_uuid      TEXT NOT NULL,
                doc_type      TEXT NOT NULL
                                  CHECK (doc_type IN ('cv', 'cover_letter')),
                file_path     TEXT NOT NULL,
                country_style TEXT NOT NULL,
                created_at    TEXT NOT NULL,
                FOREIGN KEY (job_uuid) REFERENCES job_status(uuid)
            )
        """)
        # Indexes for the API's primary query patterns
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_job_status_status
            ON job_status (status)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_documents_job_uuid
            ON documents (job_uuid)
        """)
