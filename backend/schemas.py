from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class JobSummary(BaseModel):
    uuid: str
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    site: Optional[str] = None
    job_url: Optional[str] = None
    date_posted: Optional[date] = None
    first_seen_date: Optional[date] = None
    search_term: Optional[str] = None
    lang: Optional[str] = None
    relevance_score: Optional[float] = None
    status: str = "new"
    notes: Optional[str] = None


class JobDetail(JobSummary):
    description: Optional[str] = None


class JobListResponse(BaseModel):
    jobs: List[JobSummary]
    total: int
    page: int
    page_size: int


class StatusUpdateRequest(BaseModel):
    status: str
    notes: Optional[str] = None


class CountItem(BaseModel):
    label: str
    count: int


class DateCount(BaseModel):
    date: str
    count: int


class FunnelStats(BaseModel):
    new: int = 0
    interesting: int = 0
    applied: int = 0


class DashboardResponse(BaseModel):
    total_jobs: int
    jobs_by_country: List[CountItem]
    jobs_by_role: List[CountItem]
    jobs_by_search_term: List[CountItem]
    application_funnel: FunnelStats
    top_companies: List[CountItem]
    jobs_over_time: List[DateCount]


class DocumentItem(BaseModel):
    id: int
    doc_type: str
    file_path: str
    country_style: str
    created_at: str


class DocumentListResponse(BaseModel):
    job_uuid: str
    documents: List[DocumentItem]


class DocumentGenerateRequest(BaseModel):
    doc_type: str = "both"  # "cv" | "cover_letter" | "both"
