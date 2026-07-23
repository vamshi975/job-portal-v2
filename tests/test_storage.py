"""
Validates the SQLite schema: tables, columns, constraints, and indexes exist.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from core.config import StorageConfig
from core.storage import ensure_db_schema, get_db_connection


@pytest.fixture
def tmp_storage(tmp_path: Path) -> StorageConfig:
    return StorageConfig(
        daily_data_dir=str(tmp_path / "daily_data"),
        processed_data_dir=str(tmp_path / "data"),
        documents_dir=str(tmp_path / "documents"),
        db_path=str(tmp_path / "data" / "jobs.db"),
    )


def test_schema_creates_tables(tmp_storage):
    ensure_db_schema(tmp_storage)
    with get_db_connection(tmp_storage) as conn:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
    assert "job_status" in tables
    assert "documents" in tables


def test_job_status_columns(tmp_storage):
    ensure_db_schema(tmp_storage)
    with get_db_connection(tmp_storage) as conn:
        cols = {
            row[1]
            for row in conn.execute("PRAGMA table_info(job_status)")
        }
    assert {"uuid", "status", "notes", "updated_at"} <= cols


def test_documents_columns(tmp_storage):
    ensure_db_schema(tmp_storage)
    with get_db_connection(tmp_storage) as conn:
        cols = {
            row[1]
            for row in conn.execute("PRAGMA table_info(documents)")
        }
    assert {"id", "job_uuid", "doc_type", "file_path", "country_style", "created_at"} <= cols


def test_status_constraint(tmp_storage):
    ensure_db_schema(tmp_storage)
    from datetime import datetime
    with get_db_connection(tmp_storage) as conn:
        conn.execute(
            "INSERT INTO job_status (uuid, status, updated_at) VALUES (?, ?, ?)",
            ("test-uuid", "interesting", datetime.utcnow().isoformat()),
        )
    with get_db_connection(tmp_storage) as conn:
        with pytest.raises(Exception):
            conn.execute(
                "INSERT INTO job_status (uuid, status, updated_at) VALUES (?, ?, ?)",
                ("test-uuid-2", "invalid_status", datetime.utcnow().isoformat()),
            )
            conn.commit()


def test_indexes_exist(tmp_storage):
    ensure_db_schema(tmp_storage)
    with get_db_connection(tmp_storage) as conn:
        indexes = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index'"
            )
        }
    assert "idx_job_status_status" in indexes
    assert "idx_documents_job_uuid" in indexes


def test_idempotent(tmp_storage):
    ensure_db_schema(tmp_storage)
    ensure_db_schema(tmp_storage)  # must not raise on second call
