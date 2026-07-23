from __future__ import annotations

import time
from datetime import date
from typing import Optional

import pandas as pd
from jobspy import scrape_jobs

from core.config import CountryConfig, ScrapingSettings, StorageConfig
from core.storage import daily_parquet_path

_EMPTY_COLUMNS = [
    "id", "site", "job_url", "job_url_direct", "title", "company", "location",
    "job_type", "date_posted", "interval", "min_amount", "max_amount", "currency",
    "is_remote", "job_function", "emails", "description", "company_url",
    "company_url_direct", "company_addresses", "company_industry",
    "company_num_employees", "company_revenue", "company_description",
    "logo_photo_url", "banner_photo_url", "ceo_name", "ceo_photo_url",
    "search_term", "country",
]


def _scrape_one(
    site: str,
    search_term: str,
    country: CountryConfig,
    results_wanted: int,
) -> pd.DataFrame:
    try:
        df = scrape_jobs(
            site_name=[site],
            search_term=search_term,
            location=country.location,
            results_wanted=results_wanted,
            country_indeed=country.country_indeed,
        )
        df["search_term"] = search_term
        df["country"] = country.name
        return df
    except Exception as exc:
        print(f"[scraper] {country.name}/{site}/{search_term}: {exc}")
        return pd.DataFrame(columns=_EMPTY_COLUMNS)


def scrape_country(
    country: CountryConfig,
    settings: ScrapingSettings,
    storage: StorageConfig,
    run_date: Optional[date] = None,
) -> None:
    run_date = run_date or date.today()
    frames: list[pd.DataFrame] = []

    for search_term in country.search_terms:
        for site in country.sites:
            df = _scrape_one(site, search_term, country, settings.results_per_search)
            if not df.empty:
                frames.append(df)
            time.sleep(settings.request_delay_seconds)

    if not frames:
        print(f"[scraper] No results for {country.name}")
        return

    all_jobs = pd.concat(frames, ignore_index=True).drop_duplicates()
    out = daily_parquet_path(storage, country.name, run_date)
    all_jobs.to_parquet(out)
    print(f"[scraper] {country.name}: {len(all_jobs)} jobs → {out}")
