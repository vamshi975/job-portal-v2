from __future__ import annotations

from core.config import AppConfig, UserProfile, load_app, load_profile
from backend.services.documents import DocumentService
from backend.services.jobs import JobDataService

_config: AppConfig = load_app()
_profile: UserProfile = load_profile()
_job_service: JobDataService = JobDataService(_config.storage)
_doc_service: DocumentService = DocumentService(_config.storage, _config.llm, _profile)


def get_config() -> AppConfig:
    return _config


def get_profile() -> UserProfile:
    return _profile


def get_job_service() -> JobDataService:
    return _job_service


def get_doc_service() -> DocumentService:
    return _doc_service
