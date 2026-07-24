"""
Unit tests for LLM relevance scoring.
The LLM call itself is mocked; this validates prompt construction and
score parsing without hitting the network.
"""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from core.config import LLMConfig, UserProfile, SkillsConfig, PersonalInfo, LanguageEntry


@pytest.fixture
def sample_profile() -> UserProfile:
    return UserProfile(
        personal=PersonalInfo(
            name="Test User",
            current_title="Data Scientist",
            experience_years=5,
        ),
        skills=SkillsConfig(
            programming=["Python", "SQL"],
            ml_frameworks=["scikit-learn", "PyTorch"],
            cloud=["Azure"],
            ai_llm=["RAG", "LLM"],
            data_engineering=["PySpark"],
            tools=["Docker"],
        ),
        languages=[LanguageEntry(language="English", level="C1")],
        target_roles=["Data Scientist", "ML Engineer"],
        industries=["Finance"],
    )


@pytest.fixture
def sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "uuid": "uuid-1",
                "title": "Data Scientist",
                "company": "Acme GmbH",
                "country": "Germany",
                "description": "We need Python and ML skills.",
            },
            {
                "uuid": "uuid-2",
                "title": "Java Developer",
                "company": "Java Corp",
                "country": "Germany",
                "description": "Spring Boot, Java, Kubernetes.",
            },
        ]
    )


def test_fallback_when_no_config(sample_df, sample_profile):
    """Returns neutral 5.0 scores when LLM is not configured."""
    from pipeline.scorer import score_jobs

    llm = LLMConfig(base_url="", model="")
    result = score_jobs(sample_df, sample_profile, llm)
    assert "relevance_score" in result.columns
    assert list(result["relevance_score"]) == [5.0, 5.0]


def test_scores_from_llm_response(sample_df, sample_profile):
    """Parses a well-formed JSON array from the LLM response."""
    from pipeline.scorer import score_jobs

    llm = LLMConfig(base_url="https://example.com/v1/", model="gemma-4-31b-it")
    llm.relevance_score_threshold = 6.0

    mock_choice = MagicMock()
    mock_choice.message.content = json.dumps([8.5, 2.0])

    mock_resp = MagicMock()
    mock_resp.choices = [mock_choice]

    with patch("openai.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_resp
        mock_openai_cls.return_value = mock_client

        result = score_jobs(sample_df, sample_profile, llm)

    assert result.iloc[0]["relevance_score"] == 8.5
    assert result.iloc[1]["relevance_score"] == 2.0


def test_fallback_on_parse_failure(sample_df, sample_profile):
    """Falls back to 5.0 when the LLM returns unparseable output."""
    from pipeline.scorer import score_jobs

    llm = LLMConfig(base_url="https://example.com/v1/", model="gemma-4-31b-it")

    mock_choice = MagicMock()
    mock_choice.message.content = "I cannot score these jobs right now."

    mock_resp = MagicMock()
    mock_resp.choices = [mock_choice]

    with patch("openai.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_resp
        mock_openai_cls.return_value = mock_client

        result = score_jobs(sample_df, sample_profile, llm)

    assert list(result["relevance_score"]) == [5.0, 5.0]


def test_scores_clamped_to_range(sample_df, sample_profile):
    """Clamps out-of-range scores to [0, 10]."""
    from pipeline.scorer import score_jobs

    llm = LLMConfig(base_url="https://example.com/v1/", model="gemma-4-31b-it")

    mock_choice = MagicMock()
    mock_choice.message.content = json.dumps([15.0, -3.0])  # out of range

    mock_resp = MagicMock()
    mock_resp.choices = [mock_choice]

    with patch("openai.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_resp
        mock_openai_cls.return_value = mock_client

        result = score_jobs(sample_df, sample_profile, llm)

    assert result.iloc[0]["relevance_score"] == 10.0
    assert result.iloc[1]["relevance_score"] == 0.0


def test_fallback_on_api_error(sample_df, sample_profile):
    """Falls back to 5.0 when the API call raises an exception."""
    from pipeline.scorer import score_jobs

    llm = LLMConfig(base_url="https://example.com/v1/", model="gemma-4-31b-it")

    with patch("openai.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = RuntimeError("timeout")
        mock_openai_cls.return_value = mock_client

        result = score_jobs(sample_df, sample_profile, llm)

    assert list(result["relevance_score"]) == [5.0, 5.0]


def test_original_df_not_mutated(sample_df, sample_profile):
    """score_jobs must not modify the input DataFrame."""
    from pipeline.scorer import score_jobs

    llm = LLMConfig(base_url="", model="")
    original_cols = set(sample_df.columns)
    score_jobs(sample_df, sample_profile, llm)
    assert set(sample_df.columns) == original_cols
