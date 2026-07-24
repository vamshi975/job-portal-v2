# ADR-0002 — Use pandas in-memory cache for parquet queries (not DuckDB)

**Status:** Accepted

## Context

The FastAPI backend needs to query `data/last_30_days.parquet` for job listings,
search, filtering, and dashboard aggregations. Two realistic options were:

| Option | Pros | Cons |
|--------|------|------|
| **pandas in-memory** | No extra dep; simple mtime reload; fast for <100k rows | Full file loads into RAM |
| **DuckDB** | SQL on parquet; column-pruning; handles GB-scale files | Extra dependency; more moving parts for a personal tool |

## Decision

Load the parquet into a pandas DataFrame on first access and re-read it only when
the file's `mtime` changes (`JobDataService._is_stale()`). All filtering and
aggregation happens with standard pandas operations in `backend/services/jobs.py`
and the routers.

## Rationale

- The processed file contains at most ~12 000 jobs (8 countries × 10 searches × 50 results
  × 30 days, heavily deduplicated). This fits comfortably in RAM on Render's free tier.
- A pipeline run replaces the whole file, so mtime-based cache invalidation is exact.
- Adding DuckDB would save tens of milliseconds per request in exchange for an
  extra runtime dependency and SQL error-handling paths — not worth it for a
  single-user tool.

## Future

If the data grows beyond a few hundred MB (e.g. extended to many more countries
or longer history), swap `JobDataService._reload()` for DuckDB's
`duckdb.read_parquet()` with column pushdown — the rest of the code is unchanged.
