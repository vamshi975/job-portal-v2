from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

import yaml
from pydantic import BaseModel, Field

CONFIG_DIR = Path(__file__).parent.parent / "config"


# ── countries.yaml ────────────────────────────────────────────────────────────

class CountryConfig(BaseModel):
    name: str
    country_indeed: str
    location: str
    sites: List[str]
    search_terms: List[str]


class ScrapingSettings(BaseModel):
    results_per_search: int = 50
    request_delay_seconds: int = 10
    max_days_to_keep: int = 60


class FilteringSettings(BaseModel):
    exclude_title_keywords: List[str] = []
    exclude_companies: List[str] = []


class CountriesConfig(BaseModel):
    countries: List[CountryConfig]
    scraping: ScrapingSettings = Field(default_factory=ScrapingSettings)
    filtering: FilteringSettings = Field(default_factory=FilteringSettings)


# ── profile.yaml ──────────────────────────────────────────────────────────────

class PersonalInfo(BaseModel):
    name: str
    current_title: str
    experience_years: int
    nationality: Optional[str] = None
    location: Optional[str] = None
    german_residence: bool = False


class SkillsConfig(BaseModel):
    programming: List[str] = []
    ml_frameworks: List[str] = []
    cloud: List[str] = []
    ai_llm: List[str] = []
    data_engineering: List[str] = []
    tools: List[str] = []


class LanguageEntry(BaseModel):
    language: str
    level: str


class EducationEntry(BaseModel):
    degree: str
    field: str
    institution: str
    country: str
    year: Optional[str] = None


class ExperienceEntry(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    start_date: str  # "YYYY-MM" or "Month YYYY"
    end_date: str = "present"
    bullets: List[str] = []


class UserProfile(BaseModel):
    personal: PersonalInfo
    skills: SkillsConfig = Field(default_factory=SkillsConfig)
    industries: List[str] = []
    experience: List[ExperienceEntry] = []
    education: List[EducationEntry] = []
    languages: List[LanguageEntry] = []
    target_roles: List[str] = []


# ── app.yaml ──────────────────────────────────────────────────────────────────

class LLMConfig(BaseModel):
    base_url: str = Field(
        default_factory=lambda: os.environ.get("GOOGLE_BASE_URL", "")
    )
    model: str = Field(
        default_factory=lambda: os.environ.get("GOOGLE_MODEL", "")
    )
    api_key: str = Field(
        default_factory=lambda: os.environ.get("GOOGLE_API_KEY", "")
    )
    relevance_score_threshold: float = 6.0


class StorageConfig(BaseModel):
    daily_data_dir: str = "daily_data"
    processed_data_dir: str = "data"
    documents_dir: str = "documents"
    db_path: str = "data/jobs.db"
    processed_filename: str = "last_30_days.parquet"


class BackendConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: List[str] = []


class AppConfig(BaseModel):
    llm: LLMConfig = Field(default_factory=LLMConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    backend: BackendConfig = Field(default_factory=BackendConfig)


# ── loaders ───────────────────────────────────────────────────────────────────

def _load_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_countries() -> CountriesConfig:
    return CountriesConfig(**_load_yaml(CONFIG_DIR / "countries.yaml"))


def load_profile() -> UserProfile:
    return UserProfile(**_load_yaml(CONFIG_DIR / "profile.yaml"))


def load_app() -> AppConfig:
    raw = _load_yaml(CONFIG_DIR / "app.yaml")
    return AppConfig(**raw)
