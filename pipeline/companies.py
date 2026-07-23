from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


def collect_unique_companies(daily_data_dir: str) -> list[str]:
    companies: list[str] = []
    for parquet in Path(daily_data_dir).rglob("*.parquet"):
        try:
            df = pd.read_parquet(parquet, columns=["company"])
            companies.extend(c for c in df["company"].dropna().unique())
        except Exception:
            pass
    cleaned = [re.sub(r"[^\w\s]", "", c) for c in companies]
    return sorted(set(cleaned))
