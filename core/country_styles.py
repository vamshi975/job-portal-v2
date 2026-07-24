from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CountryStyle:
    name: str
    doc_language: str  # "de" | "en"
    font_family: str
    font_size_pt: int
    margin_cm: float
    include_photo_placeholder: bool
    include_address_block: bool  # recipient address block in cover letter
    cl_greeting: str
    cl_closing: str
    cl_subject_prefix: str  # "Bewerbung als" / "Application for"
    cl_notes: str  # injected into the LLM prompt for style guidance
    cv_section_headers: dict[str, str] = field(default_factory=dict)


_STYLES: dict[str, CountryStyle] = {
    "Germany": CountryStyle(
        name="Germany",
        doc_language="de",
        font_family="Arial",
        font_size_pt=11,
        margin_cm=2.5,
        include_photo_placeholder=False,
        include_address_block=True,
        cl_greeting="Sehr geehrte Damen und Herren,",
        cl_closing="Mit freundlichen Grüßen",
        cl_subject_prefix="Bewerbung als",
        cl_notes=(
            "Write in formal German (Sie-form). Follow the Anschreiben structure: "
            "opening hook referencing the specific role → motivation and cultural fit → "
            "skills evidence with a concrete achievement → call to action. "
            "Be precise and fact-based; avoid hollow phrases like 'I am highly motivated'. "
            "Maximum 3 short paragraphs, ~250 words total."
        ),
        cv_section_headers={
            "summary": "Profil",
            "experience": "Berufserfahrung",
            "education": "Ausbildung",
            "skills": "Kenntnisse",
            "languages": "Sprachkenntnisse",
        },
    ),
    "Netherlands": CountryStyle(
        name="Netherlands",
        doc_language="en",
        font_family="Calibri",
        font_size_pt=11,
        margin_cm=2.0,
        include_photo_placeholder=False,
        include_address_block=False,
        cl_greeting="Dear Hiring Team,",
        cl_closing="Kind regards,",
        cl_subject_prefix="Application for",
        cl_notes=(
            "Write in professional English. Dutch companies value directness and "
            "concrete impact. Avoid over-formal language. Focus on results and "
            "metrics. 3 concise paragraphs, ~200 words."
        ),
        cv_section_headers={
            "summary": "Professional Summary",
            "experience": "Work Experience",
            "education": "Education",
            "skills": "Skills",
            "languages": "Languages",
        },
    ),
    "Belgium": CountryStyle(
        name="Belgium",
        doc_language="en",
        font_family="Calibri",
        font_size_pt=11,
        margin_cm=2.0,
        include_photo_placeholder=False,
        include_address_block=False,
        cl_greeting="Dear Hiring Team,",
        cl_closing="Kind regards,",
        cl_subject_prefix="Application for",
        cl_notes=(
            "Write in professional English. Belgian companies value thoroughness and "
            "multicultural awareness. Show adaptability and teamwork. "
            "3 paragraphs: motivation, relevant skills, closing. ~200 words."
        ),
        cv_section_headers={
            "summary": "Professional Summary",
            "experience": "Work Experience",
            "education": "Education",
            "skills": "Skills",
            "languages": "Languages",
        },
    ),
    "India": CountryStyle(
        name="India",
        doc_language="en",
        font_family="Calibri",
        font_size_pt=11,
        margin_cm=2.5,
        include_photo_placeholder=False,
        include_address_block=False,
        cl_greeting="Dear Hiring Manager,",
        cl_closing="Yours sincerely,",
        cl_subject_prefix="Application for",
        cl_notes=(
            "Write in formal English. Mention availability / notice period if applicable. "
            "Include a strong objective sentence at the opening. "
            "3–4 short paragraphs covering motivation, key skills, experience, and next steps."
        ),
        cv_section_headers={
            "summary": "Career Objective",
            "experience": "Work Experience",
            "education": "Educational Qualifications",
            "skills": "Technical Skills",
            "languages": "Languages Known",
        },
    ),
    "United States": CountryStyle(
        name="United States",
        doc_language="en",
        font_family="Calibri",
        font_size_pt=11,
        margin_cm=2.5,
        include_photo_placeholder=False,
        include_address_block=False,
        cl_greeting="Dear Hiring Manager,",
        cl_closing="Best regards,",
        cl_subject_prefix="Application for",
        cl_notes=(
            "Write in active voice with strong action verbs. No personal details (no age, no photo). "
            "ATS-friendly: echo key phrases from the job description naturally. "
            "3 paragraphs: hook + fit, evidence + metrics, enthusiasm + CTA. Max 200 words."
        ),
        cv_section_headers={
            "summary": "Professional Summary",
            "experience": "Work Experience",
            "education": "Education",
            "skills": "Skills",
            "languages": "Languages",
        },
    ),
    "Canada": CountryStyle(
        name="Canada",
        doc_language="en",
        font_family="Calibri",
        font_size_pt=11,
        margin_cm=2.5,
        include_photo_placeholder=False,
        include_address_block=False,
        cl_greeting="Dear Hiring Manager,",
        cl_closing="Best regards,",
        cl_subject_prefix="Application for",
        cl_notes=(
            "Write in professional English, similar to US style. Active voice, results-oriented. "
            "Mention willingness to relocate or remote work flexibility if applicable. "
            "3 concise paragraphs. Max 200 words."
        ),
        cv_section_headers={
            "summary": "Professional Summary",
            "experience": "Work Experience",
            "education": "Education",
            "skills": "Skills",
            "languages": "Languages",
        },
    ),
    "Denmark": CountryStyle(
        name="Denmark",
        doc_language="en",
        font_family="Calibri",
        font_size_pt=11,
        margin_cm=2.0,
        include_photo_placeholder=False,
        include_address_block=False,
        cl_greeting="Dear team,",
        cl_closing="Best regards,",
        cl_subject_prefix="Application for",
        cl_notes=(
            "Write in English. Danish companies value informality and authenticity — "
            "avoid stiff formality. Open with a specific, direct hook. "
            "Show personality alongside competence. 2–3 short paragraphs, max 180 words."
        ),
        cv_section_headers={
            "summary": "Professional Summary",
            "experience": "Work Experience",
            "education": "Education",
            "skills": "Skills",
            "languages": "Languages",
        },
    ),
    "Sweden": CountryStyle(
        name="Sweden",
        doc_language="en",
        font_family="Calibri",
        font_size_pt=11,
        margin_cm=2.0,
        include_photo_placeholder=False,
        include_address_block=False,
        cl_greeting="Dear hiring team,",
        cl_closing="Best regards,",
        cl_subject_prefix="Application for",
        cl_notes=(
            "Write in English (personligt brev style). Swedish companies value honesty, "
            "humility, and team-first thinking. Avoid boasting; frame achievements as "
            "team contributions. Show genuine curiosity about the company. "
            "2–3 paragraphs: who you are, what you contribute, why this company. Warm but professional."
        ),
        cv_section_headers={
            "summary": "Professional Summary",
            "experience": "Work Experience",
            "education": "Education",
            "skills": "Skills",
            "languages": "Languages",
        },
    ),
}

# Generic English fallback for unknown countries
_FALLBACK = CountryStyle(
    name="Generic",
    doc_language="en",
    font_family="Calibri",
    font_size_pt=11,
    margin_cm=2.5,
    include_photo_placeholder=False,
    include_address_block=False,
    cl_greeting="Dear Hiring Manager,",
    cl_closing="Best regards,",
    cl_subject_prefix="Application for",
    cl_notes="Write in professional English. 3 concise paragraphs. Max 200 words.",
    cv_section_headers={
        "summary": "Professional Summary",
        "experience": "Work Experience",
        "education": "Education",
        "skills": "Skills",
        "languages": "Languages",
    },
)


def get_style(country: str) -> CountryStyle:
    return _STYLES.get(country, _FALLBACK)
