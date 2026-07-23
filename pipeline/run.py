from __future__ import annotations

from core.config import load_app, load_countries, load_profile
from core.storage import ensure_db_schema
from pipeline.processor import process
from pipeline.scraper import scrape_country


def main() -> None:
    config = load_countries()
    profile = load_profile()
    app = load_app()

    ensure_db_schema(app.storage)

    for country in config.countries:
        scrape_country(country, config.scraping, app.storage)

    process(config, profile, app.llm, app.storage)


if __name__ == "__main__":
    main()
