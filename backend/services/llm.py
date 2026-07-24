from __future__ import annotations

from core.config import LLMConfig, UserProfile
from core.country_styles import CountryStyle


def _all_skills(profile: UserProfile) -> str:
    skills = (
        profile.skills.programming
        + profile.skills.ml_frameworks
        + profile.skills.cloud
        + profile.skills.ai_llm
        + profile.skills.data_engineering
        + profile.skills.tools
    )
    return ", ".join(skills)


def generate_cover_letter_body(
    llm: LLMConfig,
    profile: UserProfile,
    job_title: str,
    company: str,
    description: str,
    style: CountryStyle,
) -> str:
    """Return the body paragraphs of a cover letter (no header/greeting/closing).

    Falls back to a structured placeholder when LLM is not configured.
    """
    if not llm.base_url or not llm.model:
        return _cl_placeholder(profile, job_title, company, style)

    from openai import OpenAI

    client = OpenAI(base_url=llm.base_url, api_key=llm.api_key or "not-set")
    prompt = (
        f"Write the body paragraphs of a professional cover letter. "
        f"Do NOT include a salutation, header, or closing — just the body.\n\n"
        f"CANDIDATE:\n"
        f"Name: {profile.personal.name}\n"
        f"Title: {profile.personal.current_title}\n"
        f"Experience: {profile.personal.experience_years} years\n"
        f"Skills: {_all_skills(profile)}\n"
        f"Industries: {', '.join(profile.industries)}\n\n"
        f"TARGET JOB:\n"
        f"Role: {job_title}\n"
        f"Company: {company}\n"
        f"Description (excerpt): {description[:1000]}\n\n"
        f"STYLE REQUIREMENTS:\n"
        f"{style.cl_notes}\n\n"
        f"Output only the letter body — plain text, paragraphs separated by blank lines. "
        f"No markdown, no headings, no bullet points."
    )

    try:
        resp = client.chat.completions.create(
            model=llm.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500,
        )
        text = (resp.choices[0].message.content or "").strip()
        return text if text else _cl_placeholder(profile, job_title, company, style)
    except Exception as exc:
        print(f"[llm] Cover letter generation failed: {exc}")
        return _cl_placeholder(profile, job_title, company, style)


def generate_cv_summary(
    llm: LLMConfig,
    profile: UserProfile,
    job_title: str,
    company: str,
    description: str,
    style: CountryStyle,
) -> str:
    """Return a tailored 3–4 sentence professional summary for the CV.

    Falls back to a generic placeholder when LLM is not configured.
    """
    if not llm.base_url or not llm.model:
        return _cv_summary_placeholder(profile)

    from openai import OpenAI

    client = OpenAI(base_url=llm.base_url, api_key=llm.api_key or "not-set")
    lang_note = (
        "Write in German. Do not use first-person pronouns (typical for German Profil sections)."
        if style.doc_language == "de"
        else "Write in English using third-person or noun-phrase style (e.g. 'Experienced data scientist...')."
    )
    prompt = (
        f"Write a tailored professional summary (3–4 sentences) for the CV's profile section.\n\n"
        f"CANDIDATE:\n"
        f"Title: {profile.personal.current_title}, {profile.personal.experience_years} years experience\n"
        f"Skills: {_all_skills(profile)}\n"
        f"Industries: {', '.join(profile.industries)}\n\n"
        f"TARGET JOB: {job_title} at {company}\n"
        f"Job description excerpt: {description[:500]}\n\n"
        f"REQUIREMENTS:\n"
        f"{lang_note}\n"
        f"Be specific, achievement-oriented, and echo keywords from the job description naturally.\n"
        f"Output only the summary text — no heading, no markdown."
    )

    try:
        resp = client.chat.completions.create(
            model=llm.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=200,
        )
        text = (resp.choices[0].message.content or "").strip()
        return text if text else _cv_summary_placeholder(profile)
    except Exception as exc:
        print(f"[llm] CV summary generation failed: {exc}")
        return _cv_summary_placeholder(profile)


# ── fallback placeholders ──────────────────────────────────────────────────────


def _cl_placeholder(
    profile: UserProfile, job_title: str, company: str, style: CountryStyle
) -> str:
    if style.doc_language == "de":
        return (
            f"mit großem Interesse habe ich Ihre Stellenausschreibung als {job_title} "
            f"bei {company} gelesen. Die beschriebene Aufgabe passt hervorragend zu meinem "
            f"Hintergrund als {profile.personal.current_title} mit {profile.personal.experience_years} "
            f"Jahren Erfahrung in den Bereichen {', '.join(profile.industries)}.\n\n"
            f"In meiner bisherigen Laufbahn habe ich umfangreiche Kenntnisse in "
            f"{', '.join(profile.skills.programming + profile.skills.ai_llm[:2])} erworben. "
            f"[Fügen Sie hier ein konkretes Beispiel aus Ihrer Erfahrung ein.]\n\n"
            f"Über die Möglichkeit, mich in einem persönlichen Gespräch vorzustellen, "
            f"würde ich mich sehr freuen."
        )
    return (
        f"I am writing to express my strong interest in the {job_title} position at {company}. "
        f"With {profile.personal.experience_years} years of experience as a "
        f"{profile.personal.current_title} across {', '.join(profile.industries)}, "
        f"I am confident I can make a meaningful contribution to your team.\n\n"
        f"My expertise spans {', '.join(profile.skills.programming + profile.skills.ai_llm[:2])}, "
        f"and I have a proven track record of delivering impactful data solutions. "
        f"[Add a specific achievement relevant to this role here.]\n\n"
        f"I look forward to the opportunity to discuss how my background aligns with "
        f"your team's goals. Thank you for your consideration."
    )


def _cv_summary_placeholder(profile: UserProfile) -> str:
    return (
        f"Experienced {profile.personal.current_title} with "
        f"{profile.personal.experience_years}+ years across "
        f"{', '.join(profile.industries)} industries. "
        f"Specialises in {', '.join(profile.skills.ai_llm[:3])} and "
        f"{', '.join(profile.skills.cloud[:2])} cloud platforms. "
        f"Proven ability to design and deploy end-to-end machine learning pipelines at scale."
    )
