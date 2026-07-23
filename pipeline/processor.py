from __future__ import annotations

import uuid as uuid_lib
from typing import List

import pandas as pd

from core.config import CountriesConfig, LLMConfig, StorageConfig, UserProfile
from core.storage import (
    delete_old_daily_files,
    processed_parquet_path,
    read_daily_parquets,
)
from pipeline.scorer import score_jobs
from pipeline.utils.geo import extract_city
from pipeline.utils.language import detect_language


def _deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates(subset=["title", "company", "location", "search_term"])
    df = df.drop_duplicates(subset=["title", "company", "location", "description"])
    return df


def _apply_filters(
    df: pd.DataFrame,
    exclude_keywords: List[str],
    exclude_companies: List[str],
) -> pd.DataFrame:
    if exclude_keywords:
        pattern = "|".join(exclude_keywords)
        df = df[~df["title"].str.contains(pattern, case=False, na=False)]
    if exclude_companies:
        df = df[~df["company"].isin(exclude_companies)]
    return df


def process(
    config: CountriesConfig,
    profile: UserProfile,
    llm: LLMConfig,
    storage: StorageConfig,
    since_days: int = 30,
) -> None:
    frames: list[pd.DataFrame] = []
    for country in config.countries:
        df = read_daily_parquets(storage, country.name, since_days)
        if not df.empty:
            frames.append(df)

    if not frames:
        print("[processor] No data to process.")
        return

    all_jobs = pd.concat(frames, ignore_index=True)
    all_jobs = _deduplicate(all_jobs)
    all_jobs = _apply_filters(
        all_jobs,
        config.filtering.exclude_title_keywords,
        config.filtering.exclude_companies,
    )

    all_jobs["lang"] = all_jobs["description"].apply(detect_language)
    all_jobs["city"] = all_jobs["location"].fillna("").apply(extract_city)
    all_jobs["uuid"] = [str(uuid_lib.uuid4()) for _ in range(len(all_jobs))]

    all_jobs = score_jobs(all_jobs, profile, llm)

    out = processed_parquet_path(storage)
    all_jobs.to_parquet(out)
    print(f"[processor] {len(all_jobs)} jobs → {out}")

    delete_old_daily_files(storage, config.scraping.max_days_to_keep)
