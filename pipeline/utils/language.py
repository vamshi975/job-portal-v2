from __future__ import annotations

import langid


def detect_language(text: str) -> str:
    if not text or not isinstance(text, str):
        return "not_detected"
    try:
        lang, _ = langid.classify(text)
        return lang
    except Exception:
        return "not_detected"
