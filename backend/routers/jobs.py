from __future__ import annotations

import math
from datetime import datetime
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query

from backend.dependencies import get_config, get_job_service
from backend.schemas import JobDetail, JobListResponse, JobSummary, StatusUpdateRequest
from backend.services.jobs import JobDataService
from core.config import AppConfig
from core.storage import get_db_connection

router = APIRouter()


def _series_to_schema(row: pd.Series, schema_cls):
    """Convert a pandas Series to a Pydantic schema, coercing NaN → None."""
    data: dict = {}
    for field in schema_cls.model_fields:
        if field not in row.index:
            continue
        v = row[field]
        if isinstance(v, float) and math.isnan(v):
            data[field] = None
        elif isinstance(v, pd.Timestamp):
            data[field] = None if pd.isnull(v) else v.date()
        elif hasattr(v, "item"):  # numpy scalar → Python scalar
            data[field] = v.item()
        else:
            data[field] = v
    return schema_cls(**data)


@router.get("", response_model=JobListResponse)
async def list_jobs(
    country: Optional[str] = Query(None, description="Filter by country name"),
    city: Optional[str] = Query(None, description="Filter by city name"),
    site: Optional[str] = Query(None, description="linkedin | indeed | naukri"),
    status: Optional[str] = Query(None, description="new | interesting | applied"),
    min_score: Optional[float] = Query(None, ge=0, le=10),
    search: Optional[str] = Query(None, description="Substring match on title or company"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    service: JobDataService = Depends(get_job_service),
    cfg: AppConfig = Depends(get_config),
):
    df = service.jobs_with_status()
    if df.empty:
        return JobListResponse(jobs=[], total=0, page=page, page_size=page_size)

    if country:
        df = df[df["country"].str.lower() == country.lower()]
    if city:
        df = df[df["city"].str.lower() == city.lower()]
    if site:
        df = df[df["site"].str.lower() == site.lower()]
    if status:
        valid = {"new", "interesting", "applied"}
        if status not in valid:
            raise HTTPException(422, detail=f"status must be one of {sorted(valid)}")
        df = df[df["status"] == status]

    # Default minimum score equals the configured threshold
    effective_min = min_score if min_score is not None else cfg.llm.relevance_score_threshold
    if "relevance_score" in df.columns:
        df = df[df["relevance_score"].fillna(0) >= effective_min]

    if search:
        mask = df["title"].str.contains(search, case=False, na=False) | df[
            "company"
        ].str.contains(search, case=False, na=False)
        df = df[mask]

    sort_cols = [c for c in ("relevance_score", "date_posted") if c in df.columns]
    if sort_cols:
        df = df.sort_values(sort_cols, ascending=[False] * len(sort_cols))

    total = len(df)
    start_idx = (page - 1) * page_size
    page_df = df.iloc[start_idx : start_idx + page_size]

    jobs = [_series_to_schema(row, JobSummary) for _, row in page_df.iterrows()]
    return JobListResponse(jobs=jobs, total=total, page=page, page_size=page_size)


@router.get("/{job_id}", response_model=JobDetail)
async def get_job(
    job_id: str,
    service: JobDataService = Depends(get_job_service),
):
    row = service.get_by_id(job_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Job not found")
    detail = _series_to_schema(row, JobDetail)
    detail.status = service.get_status(job_id)
    return detail


@router.patch("/{job_id}/status")
async def update_job_status(
    job_id: str,
    body: StatusUpdateRequest,
    service: JobDataService = Depends(get_job_service),
    cfg: AppConfig = Depends(get_config),
):
    valid = {"new", "interesting", "applied"}
    if body.status not in valid:
        raise HTTPException(422, detail=f"status must be one of {sorted(valid)}")
    if service.get_by_id(job_id) is None:
        raise HTTPException(404, detail="Job not found")

    now = datetime.utcnow().isoformat()
    with get_db_connection(cfg.storage) as conn:
        conn.execute(
            """
            INSERT INTO job_status (uuid, status, notes, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(uuid) DO UPDATE SET
                status     = excluded.status,
                notes      = excluded.notes,
                updated_at = excluded.updated_at
            """,
            (job_id, body.status, body.notes, now),
        )
        conn.commit()

    return {"uuid": job_id, "status": body.status, "updated_at": now}
