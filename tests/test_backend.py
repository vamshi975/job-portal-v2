"""
Integration tests for the FastAPI backend endpoints.
Uses TestClient against real in-memory SQLite + synthetic parquet data.
"""
from __future__ import annotations

import tempfile
from datetime import date
from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from core.config import AppConfig, BackendConfig, LLMConfig, StorageConfig
from core.storage import ensure_db_schema


@pytest.fixture
def tmp_storage(tmp_path: Path) -> StorageConfig:
    return StorageConfig(
        daily_data_dir=str(tmp_path / "daily_data"),
        processed_data_dir=str(tmp_path / "data"),
        documents_dir=str(tmp_path / "documents"),
        db_path=str(tmp_path / "data" / "jobs.db"),
        processed_filename="last_30_days.parquet",
    )


@pytest.fixture
def app_with_data(tmp_storage):
    """Create a test FastAPI app backed by synthetic data."""
    # Write a small parquet
    parquet_dir = Path(tmp_storage.processed_data_dir)
    parquet_dir.mkdir(parents=True, exist_ok=True)
    jobs = pd.DataFrame([
        {
            "uuid": "uuid-de-1",
            "title": "Data Scientist",
            "company": "Acme GmbH",
            "location": "Berlin, Germany",
            "city": "Berlin",
            "country": "Germany",
            "site": "linkedin",
            "job_url": "https://example.com/1",
            "description": "Python and ML required.",
            "date_posted": date(2026, 7, 20),
            "first_seen_date": date(2026, 7, 23),
            "search_term": "Data Scientist",
            "lang": "en",
            "relevance_score": 8.5,
        },
        {
            "uuid": "uuid-nl-1",
            "title": "ML Engineer",
            "company": "DataCo BV",
            "location": "Amsterdam, Netherlands",
            "city": "Amsterdam",
            "country": "Netherlands",
            "site": "indeed",
            "job_url": "https://example.com/2",
            "description": "We love PyTorch.",
            "date_posted": date(2026, 7, 19),
            "first_seen_date": date(2026, 7, 23),
            "search_term": "ML Engineer",
            "lang": "en",
            "relevance_score": 4.0,  # below threshold
        },
    ])
    jobs.to_parquet(parquet_dir / "last_30_days.parquet")

    # Bootstrap DB
    ensure_db_schema(tmp_storage)

    cfg = AppConfig(
        llm=LLMConfig(base_url="", model="", relevance_score_threshold=6.0),
        storage=tmp_storage,
        backend=BackendConfig(cors_origins=["*"]),
    )

    # Patch config + service used by the app
    from backend.services.jobs import JobDataService
    svc = JobDataService(tmp_storage)

    import backend.dependencies as deps
    original_cfg = deps._config
    original_svc = deps._job_service
    deps._config = cfg
    deps._job_service = svc

    # Import app AFTER patching so routers pick up patched deps
    from backend.main import app
    client = TestClient(app)

    yield client

    # Restore
    deps._config = original_cfg
    deps._job_service = original_svc


def test_list_jobs_default_min_score(app_with_data):
    """Default GET /jobs uses threshold=6.0 → only returns the 8.5-score job."""
    resp = app_with_data.get("/jobs")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["jobs"][0]["uuid"] == "uuid-de-1"


def test_list_jobs_lower_min_score(app_with_data):
    """min_score=0 returns all jobs."""
    resp = app_with_data.get("/jobs?min_score=0")
    assert resp.status_code == 200
    assert resp.json()["total"] == 2


def test_list_jobs_filter_country(app_with_data):
    """Country filter is case-insensitive."""
    resp = app_with_data.get("/jobs?min_score=0&country=netherlands")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["jobs"][0]["country"] == "Netherlands"


def test_list_jobs_search(app_with_data):
    resp = app_with_data.get("/jobs?min_score=0&search=Data+Sci")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1


def test_get_job_found(app_with_data):
    resp = app_with_data.get("/jobs/uuid-de-1")
    assert resp.status_code == 200
    body = resp.json()
    assert body["uuid"] == "uuid-de-1"
    assert body["status"] == "new"
    assert "description" in body


def test_get_job_not_found(app_with_data):
    resp = app_with_data.get("/jobs/does-not-exist")
    assert resp.status_code == 404


def test_update_status(app_with_data):
    resp = app_with_data.patch(
        "/jobs/uuid-de-1/status",
        json={"status": "interesting"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "interesting"

    # Verify it's reflected in GET
    resp2 = app_with_data.get("/jobs?status=interesting&min_score=0")
    assert resp2.json()["total"] == 1


def test_update_status_invalid(app_with_data):
    resp = app_with_data.patch(
        "/jobs/uuid-de-1/status",
        json={"status": "rejected"},  # not a valid status
    )
    assert resp.status_code == 422


def test_dashboard_counts(app_with_data):
    resp = app_with_data.get("/dashboard")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_jobs"] == 2
    countries = {item["label"] for item in body["jobs_by_country"]}
    assert "Germany" in countries
    assert "Netherlands" in countries


def test_list_documents_empty(app_with_data):
    resp = app_with_data.get("/jobs/uuid-de-1/documents")
    assert resp.status_code == 200
    assert resp.json()["documents"] == []


def test_generate_documents_accepted(app_with_data):
    resp = app_with_data.post(
        "/jobs/uuid-de-1/documents",
        json={"doc_type": "both"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "generating"
