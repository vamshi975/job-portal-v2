from __future__ import annotations

from core.config import AppConfig, load_app
from backend.services.jobs import JobDataService

_config: AppConfig = load_app()
_job_service: JobDataService = JobDataService(_config.storage)


def get_config() -> AppConfig:
    return _config


def get_job_service() -> JobDataService:
    return _job_service
