from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class Job(BaseModel):
    uuid: str
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    site: Optional[str] = None
    job_url: Optional[str] = None
    description: Optional[str] = None
    date_posted: Optional[date] = None
    first_seen_date: date
    search_term: Optional[str] = None
    lang: Optional[str] = None
    relevance_score: Optional[float] = None


class JobStatus(BaseModel):
    uuid: str
    status: str  # "new" | "interesting" | "applied"
    updated_at: datetime


class Document(BaseModel):
    id: int
    job_uuid: str
    doc_type: str  # "cv" | "cover_letter"
    file_path: str
    country_style: str
    created_at: datetime
