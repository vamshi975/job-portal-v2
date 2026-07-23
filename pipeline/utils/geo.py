from __future__ import annotations

import pandas as pd


def extract_city(location: str) -> str:
    if not location or pd.isnull(location):
        return ""
    return location.split(",")[0].strip()
