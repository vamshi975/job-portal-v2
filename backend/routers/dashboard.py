from __future__ import annotations

import pandas as pd
from fastapi import APIRouter, Depends

from backend.dependencies import get_config, get_job_service
from backend.schemas import CountItem, CountryStats, DateCount, DashboardResponse, FunnelStats
from backend.services.jobs import JobDataService
from core.config import AppConfig
from core.storage import get_db_connection

router = APIRouter()


def _top_counts(df: pd.DataFrame, col: str, n: int = 15) -> list[CountItem]:
    if col not in df.columns:
        return []
    return [
        CountItem(label=str(label), count=int(cnt))
        for label, cnt in df[col].dropna().value_counts().head(n).items()
    ]


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    service: JobDataService = Depends(get_job_service),
    cfg: AppConfig = Depends(get_config),
):
    df = service.all_jobs()

    if df.empty:
        return DashboardResponse(
            total_jobs=0,
            jobs_by_country=[],
            jobs_by_role=[],
            jobs_by_search_term=[],
            application_funnel=FunnelStats(),
            top_companies=[],
            jobs_over_time=[],
        )

    jobs_by_country = _top_counts(df, "country", n=20)
    jobs_by_search_term = _top_counts(df, "search_term", n=20)
    top_companies = _top_counts(df, "company", n=20)
    jobs_by_role = _top_counts(df, "title", n=15)

    jobs_over_time: list[DateCount] = []
    if "date_posted" in df.columns:
        by_date = (
            df["date_posted"]
            .dropna()
            .astype(str)
            .value_counts()
            .sort_index()
        )
        jobs_over_time = [
            DateCount(date=d, count=int(c)) for d, c in by_date.items()
        ]

    funnel = FunnelStats()
    try:
        with get_db_connection(cfg.storage) as conn:
            rows = conn.execute(
                "SELECT status, COUNT(*) AS cnt FROM job_status GROUP BY status"
            ).fetchall()
        for row in rows:
            if row["status"] == "new":
                funnel.new = row["cnt"]
            elif row["status"] == "interesting":
                funnel.interesting = row["cnt"]
            elif row["status"] == "applied":
                funnel.applied = row["cnt"]
    except Exception:
        pass

    return DashboardResponse(
        total_jobs=len(df),
        jobs_by_country=jobs_by_country,
        jobs_by_role=jobs_by_role,
        jobs_by_search_term=jobs_by_search_term,
        application_funnel=funnel,
        top_companies=top_companies,
        jobs_over_time=jobs_over_time,
    )


@router.get("/country/{country}", response_model=CountryStats)
async def get_country_stats(
    country: str,
    service: JobDataService = Depends(get_job_service),
):
    df = service.all_jobs()
    df = df[df["country"].str.lower() == country.lower()]

    if df.empty:
        return CountryStats(
            country=country,
            total_jobs=0,
            jobs_by_city=[],
            jobs_by_role=[],
            jobs_by_site=[],
            top_companies=[],
        )

    return CountryStats(
        country=country,
        total_jobs=len(df),
        jobs_by_city=_top_counts(df, "city", n=20),
        jobs_by_role=_top_counts(df, "search_term", n=15),
        jobs_by_site=_top_counts(df, "site", n=10),
        top_companies=_top_counts(df, "company", n=10),
    )
