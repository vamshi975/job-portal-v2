# Job Portal v2

Multi-country job scraper with LLM relevance scoring, a FastAPI backend, and a Vue.js frontend. Scrapes LinkedIn, Indeed, Glassdoor, and Naukri across 8 configurable countries; scores each job against a YAML user profile using Gemma 4 31B; surfaces them through a job list UI with a **New → Interesting → Applied** workflow and per-application DOCX document generation.

**Stack**: Python 3.10+ · UV · FastAPI · Vue.js · GitHub Actions · SQLite

---

## Prerequisites

- [UV](https://docs.astral.sh/uv/getting-started/installation/) (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Python 3.10+ (UV manages this automatically)
- Node.js 18+ (for the frontend, when ready)
- A Google API key with access to Gemma 4 31B (for LLM scoring and document generation)

---

## Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/vamshi975/job-portal-v2.git
cd job-portal-v2
uv sync
```

### 2. Configure environment variables

Copy the example and fill in your credentials:

```bash
cp .env.example .env
```

Required variables:

```
GOOGLE_API_KEY=your-google-api-key-here
GOOGLE_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
GOOGLE_MODEL=gemma-4-31b-it
```

Get your API key at [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey) (free tier available).

The pipeline and backend both read these at startup. If they are absent, LLM scoring falls back to a neutral score of `5.0` and document generation uses placeholder text.

### 3. Edit your profile

`config/profile.yaml` is the source of truth for LLM scoring and document generation. Fill in your real skills, experience, education, and target roles:

```bash
# open in your editor
code config/profile.yaml
```

### 4. Edit scraping targets (optional)

`config/countries.yaml` controls which countries are scraped, which sites are used per country, and which search terms are run. Add or remove countries freely — no code changes needed.

---

## Running the pipeline

The pipeline scrapes jobs, deduplicates them, detects language, and scores them against your profile.

```bash
uv run python pipeline/run.py
```

Output files:
- `daily_data/YYYY-MM-DD_<country>.parquet` — raw daily scrapes
- `data/last_30_days.parquet` — deduplicated, scored, merged

The GitHub Actions scheduler runs this automatically on weekdays at 19:00 UTC and commits the updated parquet files. To trigger a manual run from GitHub: **Actions → Pipeline Runner → Run workflow**.

---

## Running the backend

```bash
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API is available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

Key endpoints:

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/jobs` | List jobs with filters: `country`, `status`, `min_score`, `search`, `page` |
| `GET` | `/jobs/{id}` | Job detail including description and current status |
| `PATCH` | `/jobs/{id}/status` | Update status (`new` / `interesting` / `applied`) |
| `GET` | `/dashboard` | Aggregated counts for the dashboard |
| `POST` | `/jobs/{id}/documents` | Enqueue DOCX generation (runs in background) |
| `GET` | `/jobs/{id}/documents` | List generated documents for a job |
| `GET` | `/jobs/{id}/documents/{doc_id}/download` | Download a DOCX file |

---

## Running the tests

```bash
uv run --with pytest --with httpx pytest tests/ -v
```

---

## Project structure

```
job-portal-v2/
├── config/
│   ├── app.yaml          # LLM settings, storage paths, CORS origins
│   ├── countries.yaml    # Scraping targets per country
│   └── profile.yaml      # Your skills, experience, target roles
│
├── core/                 # Shared code (used by pipeline + backend)
│   ├── config.py         # Pydantic models for all three YAML files
│   ├── country_styles.py # Per-country CV/cover letter style registry
│   └── storage.py        # SQLite schema, parquet helpers
│
├── pipeline/             # GitHub Actions scrape-score-save job
│   ├── run.py            # Entry point
│   ├── scraper.py        # jobspy wrapper
│   ├── processor.py      # Dedup, language detection, merge
│   └── scorer.py         # Batch LLM scoring via Gemma 4 31B
│
├── backend/              # FastAPI application
│   ├── main.py
│   ├── dependencies.py   # Module-level singletons (config, services)
│   ├── schemas.py        # Pydantic response models
│   ├── routers/
│   │   ├── jobs.py       # /jobs endpoints
│   │   ├── dashboard.py  # /dashboard endpoint
│   │   └── documents.py  # /jobs/{id}/documents endpoints
│   └── services/
│       ├── jobs.py       # Parquet cache with mtime-gated reload
│       ├── documents.py  # python-docx assemblers (cover letter + CV)
│       └── llm.py        # LLM prompts for CL body and CV summary
│
├── frontend/             # Vue.js app (in progress)
├── tests/
│   ├── test_scorer.py
│   ├── test_backend.py
│   └── test_documents.py
│
├── docs/adr/             # Architecture decision records
├── pyproject.toml
└── uv.lock
```

---

## Configuration reference

### `config/app.yaml`

```yaml
llm:
  base_url: ""                    # overridden by GOOGLE_BASE_URL env var
  model: ""                       # overridden by GOOGLE_MODEL env var
  relevance_score_threshold: 6.0  # jobs below this score are filtered in the API

storage:
  daily_data_dir: daily_data
  processed_data_dir: data
  db_path: data/jobs.db

backend:
  cors_origins:
    - "http://localhost:5173"
    # add your Vercel URL here after first deploy
```

### `config/countries.yaml`

Controls which countries are scraped. Each entry sets the sites, search terms, location string, and result limit. Add a new country block to extend scraping — no code changes required.

### `config/profile.yaml`

Drives LLM scoring (the rubric compares jobs against your skills and target roles) and document generation (cover letters and CVs are personalised from this file). Keep it up to date for best results.

---

## GitHub Actions

The pipeline runs automatically on weekdays at 19:00 UTC. Required repository secrets:

| Secret | Value |
|--------|-------|
| `GOOGLE_API_KEY` | Your Google AI Studio API key |
| `GOOGLE_BASE_URL` | `https://generativelanguage.googleapis.com/v1beta/openai/` |
| `GOOGLE_MODEL` | `gemma-4-31b-it` |

Set these under **Settings → Secrets and variables → Actions**.
