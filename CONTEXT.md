# Domain Glossary

## Job
A scraped job posting retrieved from a job board (LinkedIn, Indeed, Glassdoor, Naukri).
Identified by a `uuid` generated at merge time. Carries a `first_seen_date` to detect reposts.

## JobStatus
The user's workflow state for a Job. One of: `new` → `interesting` → `applied`.
Stored in SQLite alongside the `uuid`. A Job without a SQLite row is implicitly `new`.

## RelevanceScore
An LLM-assigned 0–10 score indicating how well a Job matches the UserProfile.
Computed during Pipeline processing and stored on the Job record.

## CountryConfig
Per-country scraping parameters: which job boards to use, search terms, `country_indeed` value,
and location string. Lives in `config/countries.yaml`. User-editable to add or remove countries.

## UserProfile
The user's skills, experience, education, and target role preferences.
Lives in `config/profile.yaml`. Source of truth for RelevanceScore computation and Document generation.

## Document
A generated DOCX file — either a cover letter or a CV — tailored to a specific Job and
styled to the conventions of the Job's target country. Linked to a Job via SQLite.

## Pipeline
The GitHub Actions cron process that scrapes Jobs, computes RelevanceScores,
and writes country-partitioned Parquet files to `daily_data/`.

## Backend
The FastAPI application running on Render. Reads Parquet files and SQLite, exposes a REST API
for job listing, status management, and Document generation.

## Frontend
The Vue.js SPA running on Vercel. Consumes the Backend API. Provides the job browsing,
status workflow, and Document download UI.
