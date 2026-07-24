from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd

from core.config import StorageConfig
from core.storage import get_db_connection, processed_parquet_path


class JobDataService:
    """Loads job data from parquet and merges with SQLite status.

    The parquet file is reloaded only when its mtime changes, keeping
    repeated API calls cheap without serving stale data after a pipeline run.
    """

    def __init__(self, storage: StorageConfig) -> None:
        self._storage = storage
        self._df: Optional[pd.DataFrame] = None
        self._mtime: Optional[float] = None

    # ── internal ──────────────────────────────────────────────────────────────

    def _path(self) -> Path:
        return processed_parquet_path(self._storage)

    def _is_stale(self) -> bool:
        p = self._path()
        if not p.exists():
            return False
        return self._df is None or p.stat().st_mtime != self._mtime

    def _reload(self) -> None:
        p = self._path()
        if p.exists():
            self._df = pd.read_parquet(p)
            self._mtime = p.stat().st_mtime
        else:
            self._df = pd.DataFrame()

    # ── public API ────────────────────────────────────────────────────────────

    def all_jobs(self) -> pd.DataFrame:
        """Return raw job DataFrame (no status column)."""
        if self._is_stale():
            self._reload()
        return self._df.copy() if self._df is not None else pd.DataFrame()

    def jobs_with_status(self) -> pd.DataFrame:
        """Return job DataFrame left-joined with job_status from SQLite.

        Jobs with no status row default to 'new'.
        """
        df = self.all_jobs()
        if df.empty:
            return df
        with get_db_connection(self._storage) as conn:
            statuses = pd.read_sql_query(
                "SELECT uuid, status, notes FROM job_status", conn
            )
        df = df.merge(statuses, on="uuid", how="left")
        df["status"] = df["status"].fillna("new")
        # pandas fills string NaN as NaN (float); convert to None for JSON
        df["notes"] = df["notes"].where(df["notes"].notna(), other=None)
        return df

    def get_by_id(self, job_uuid: str) -> Optional[pd.Series]:
        """Return the raw parquet row for a single job, or None."""
        df = self.all_jobs()
        if df.empty or "uuid" not in df.columns:
            return None
        matches = df[df["uuid"] == job_uuid]
        return matches.iloc[0] if not matches.empty else None

    def get_status(self, job_uuid: str) -> str:
        """Return the current workflow status for a job (defaults to 'new')."""
        with get_db_connection(self._storage) as conn:
            row = conn.execute(
                "SELECT status FROM job_status WHERE uuid = ?", (job_uuid,)
            ).fetchone()
        return row["status"] if row else "new"
