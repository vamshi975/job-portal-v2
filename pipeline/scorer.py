from __future__ import annotations

import pandas as pd

from core.config import LLMConfig, UserProfile

# Full LLM scoring implementation arrives in ticket #7.
# Stub returns a neutral mid-score so the pipeline runs end-to-end today.


def score_jobs(df: pd.DataFrame, profile: UserProfile, llm: LLMConfig) -> pd.DataFrame:
    df = df.copy()
    df["relevance_score"] = 5.0
    return df
