from __future__ import annotations

import json
import math
import re
import time
from typing import Optional

import pandas as pd

from core.config import LLMConfig, UserProfile

BATCH_SIZE = 10
_BATCH_DELAY = 0.5  # seconds between batches to avoid rate limits


def _profile_summary(profile: UserProfile) -> str:
    all_skills = (
        profile.skills.programming
        + profile.skills.ml_frameworks
        + profile.skills.cloud
        + profile.skills.ai_llm
        + profile.skills.data_engineering
        + profile.skills.tools
    )
    lang_str = ", ".join(
        f"{e.language} ({e.level})" for e in profile.languages
    )
    return (
        f"Role: {profile.personal.current_title}\n"
        f"Experience: {profile.personal.experience_years} years\n"
        f"Skills: {', '.join(all_skills)}\n"
        f"Target roles: {', '.join(profile.target_roles)}\n"
        f"Industries: {', '.join(profile.industries)}\n"
        f"Languages: {lang_str}"
    )


def _score_prompt(batch: list[dict], profile_text: str) -> str:
    lines = []
    for i, job in enumerate(batch, 1):
        desc = (job.get("description") or "")[:600].replace("\n", " ")
        lines.append(
            f"{i}. [{job.get('country', '')}] {job.get('title', '')} "
            f"@ {job.get('company', '')} — {desc}"
        )
    n = len(batch)
    return (
        f"Score each job 0-10 for fit with this candidate. Be strict.\n\n"
        f"CANDIDATE:\n{profile_text}\n\n"
        f"SCORING RUBRIC:\n"
        f"9-10 = Excellent: core skills match, right seniority, target role or close variant\n"
        f"7-8  = Good: most skills match, minor gap (e.g. different cloud provider)\n"
        f"5-6  = Partial: some relevance but significant gaps or tangential field\n"
        f"0-4  = Poor: wrong field, wrong level, or missing most required skills\n"
        f"Penalise heavily: recruitment/staffing agencies, very senior (principal/director), "
        f"intern/student, job requires skills absent from profile.\n"
        f"Reward: AI/ML/Data roles, Python, Azure, RAG/LLM, German-speaking roles.\n\n"
        f"Return ONLY a valid JSON array of exactly {n} numbers (0-10). "
        f"No explanation, no text outside the array.\n"
        f"Example for {n} jobs: {json.dumps([5.0] * n)}\n\n"
        f"JOBS:\n" + "\n".join(lines)
    )


def _parse_scores(text: str, expected: int) -> Optional[list[float]]:
    match = re.search(r"\[[-\d\s.,]+\]", text)
    if not match:
        return None
    try:
        raw = json.loads(match.group())
        if len(raw) == expected and all(isinstance(s, (int, float)) for s in raw):
            return [max(0.0, min(10.0, float(s))) for s in raw]
    except (json.JSONDecodeError, TypeError, ValueError):
        pass
    return None


def score_jobs(df: pd.DataFrame, profile: UserProfile, llm: LLMConfig) -> pd.DataFrame:
    df = df.copy()

    if not llm.base_url or not llm.model:
        print("[scorer] LLM not configured — assigning neutral score 5.0 to all jobs")
        df["relevance_score"] = 5.0
        return df

    from openai import OpenAI  # lazy import keeps startup fast when LLM is skipped

    client = OpenAI(base_url=llm.base_url, api_key=llm.api_key or "not-set")
    profile_text = _profile_summary(profile)
    jobs_list = df.to_dict("records")
    scores = [5.0] * len(jobs_list)

    total_batches = math.ceil(len(jobs_list) / BATCH_SIZE)
    print(
        f"[scorer] Scoring {len(jobs_list)} jobs in {total_batches} batches "
        f"via {llm.model}"
    )

    for batch_idx, start in enumerate(range(0, len(jobs_list), BATCH_SIZE)):
        batch = jobs_list[start : start + BATCH_SIZE]
        try:
            prompt = _score_prompt(batch, profile_text)
            resp = client.chat.completions.create(
                model=llm.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=150,
            )
            raw_text = resp.choices[0].message.content or ""
            parsed = _parse_scores(raw_text, len(batch))
            if parsed:
                for j, score in enumerate(parsed):
                    scores[start + j] = score
            else:
                print(
                    f"[scorer] Batch {batch_idx+1}/{total_batches}: "
                    f"parse failed, raw={raw_text[:80]!r}"
                )
        except Exception as exc:
            print(f"[scorer] Batch {batch_idx+1}/{total_batches}: API error — {exc}")

        if start + BATCH_SIZE < len(jobs_list):
            time.sleep(_BATCH_DELAY)

    df["relevance_score"] = scores
    above = (df["relevance_score"] >= llm.relevance_score_threshold).sum()
    print(
        f"[scorer] Done. Mean score: {df['relevance_score'].mean():.2f}, "
        f"above {llm.relevance_score_threshold}: {above}/{len(df)}"
    )
    return df
