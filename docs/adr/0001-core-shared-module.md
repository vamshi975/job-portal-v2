# ADR 0001: Shared code lives in `core/`, imported by both pipeline and backend

## Status
Accepted

## Context
The Pipeline (GitHub Actions) and Backend (FastAPI on Render) are separate processes with
separate runtimes. Both need to:
- Load and validate the same YAML config files (`countries.yaml`, `profile.yaml`, `app.yaml`)
- Work with the same Job data model (Pydantic schema matching the Parquet schema)
- Read/write to the same storage paths (parquet files, SQLite)

Three options were considered:

1. **`core/` shared module** — a top-level Python package imported by both `pipeline/` and `backend/`
2. **backend imports pipeline** — pipeline owns the models; backend imports them (one-way dependency)
3. **Duplicate** — each process has its own copy of config loading and models

## Decision
Use option 1: a `core/` module at repo root.

## Rationale
- This is a solo personal project with a single `pyproject.toml` — both processes run in the
  same Python environment, so there is no packaging or versioning cost to sharing `core/`.
- Config loading with Pydantic validation is non-trivial and must not diverge.
- Option 2 creates a semantic mismatch (backend depending on pipeline is conceptually wrong).
- Option 3 guarantees drift.

## Consequences
- Any breaking change to `core/` models or config schema affects both processes simultaneously.
- This is acceptable: the pipeline and backend are always deployed together from the same repo.
