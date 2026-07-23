"""
Validates that all three YAML config files parse without errors and
that key invariants hold (e.g. Glassdoor excluded for Denmark/Sweden).
"""
from __future__ import annotations

import pytest
from core.config import load_app, load_countries, load_profile


def test_countries_load():
    config = load_countries()
    assert len(config.countries) == 8
    names = [c.name for c in config.countries]
    for expected in ["Germany", "Netherlands", "Belgium", "India",
                     "United States", "Canada", "Denmark", "Sweden"]:
        assert expected in names


def test_no_glassdoor_for_denmark_sweden():
    config = load_countries()
    no_glassdoor = {"Denmark", "Sweden"}
    for country in config.countries:
        if country.name in no_glassdoor:
            assert "glassdoor" not in country.sites, (
                f"{country.name} must not include Glassdoor (raises exception)"
            )


def test_india_has_naukri():
    config = load_countries()
    india = next(c for c in config.countries if c.name == "India")
    assert "naukri" in india.sites


def test_all_countries_have_search_terms():
    config = load_countries()
    for country in config.countries:
        assert len(country.search_terms) > 0, f"{country.name} has no search terms"


def test_filtering_has_keywords():
    config = load_countries()
    assert len(config.filtering.exclude_title_keywords) > 0
    assert len(config.filtering.exclude_companies) > 0


def test_profile_loads():
    profile = load_profile()
    assert profile.personal.name == "Vamshi Bhushanaboina"
    assert profile.personal.experience_years == 5
    assert len(profile.target_roles) > 0
    assert len(profile.languages) >= 2


def test_profile_skills_populated():
    profile = load_profile()
    assert len(profile.skills.programming) > 0
    assert len(profile.skills.cloud) > 0
    assert len(profile.skills.ai_llm) > 0


def test_app_loads():
    app = load_app()
    assert app.llm.relevance_score_threshold == 6.0
    assert app.storage.db_path == "data/jobs.db"
    assert "http://localhost:5173" in app.backend.cors_origins
