from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()

# Full implementation in ticket #9 (FastAPI API design)


@router.get("")
async def get_dashboard():
    return {
        "jobs_by_country": [],
        "jobs_by_role": [],
        "jobs_by_skill": [],
        "application_funnel": {"new": 0, "interesting": 0, "applied": 0},
    }
