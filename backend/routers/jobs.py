from __future__ import annotations

from fastapi import APIRouter, Query
from typing import List, Optional

router = APIRouter()

# Full implementation in ticket #9 (FastAPI API design)


@router.get("")
async def list_jobs(
    country: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    min_score: Optional[float] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    return {"jobs": [], "total": 0, "page": page, "page_size": page_size}


@router.get("/{job_id}")
async def get_job(job_id: str):
    return {"uuid": job_id}


@router.patch("/{job_id}/status")
async def update_job_status(job_id: str, status: str):
    return {"uuid": job_id, "status": status}
