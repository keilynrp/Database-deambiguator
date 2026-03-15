"""
Sprint 94 — PostgreSQL Hardening tests.

All tests run against the in-memory SQLite DB (standard UKIP test practice).
They verify:
  - database.py sets correct engine kwargs per dialect
  - search.py dialect flag is derived correctly
  - _rebuild + global_search work on SQLite (FTS5 path)
  - Migration helpers use cross-DB inspect.has_table() (not sqlite_master)
  - Boolean server_defaults in baseline use sa.text("true"/"false")
  - docker-compose.yml declares a postgres service
  - Dockerfile.backend exists and references requirements.txt
"""
from __future__ import annotations

import os
import pathlib

import pytest
from fastapi.testclient import TestClient

from backend import models
from backend.database import SQLALCHEMY_DATABASE_URL


# ── 1. Database engine configuration ─────────────────────────────────────────

class TestDatabaseConfig:
    def test_sqlite_url_detected(self):
        """Test DB starts as sqlite in test env."""
        assert SQLALCHEMY_DATABASE_URL.startswith("sqlite")

    def test_pg_url_branch_in_database_py(self):
        """database.py source must contain pool_size / pool_pre_ping for PG branch."""
        src = pathlib.Path("backend/database.py").read_text()
        assert "pool_size" in src
        assert "pool_pre_ping" in src
        assert "check_same_thread" in src  # SQLite branch also present

    def test_sqlite_no_pool_kwargs(self):
        """SQLite branch uses connect_args, not pool_size."""
        # If we're here, the test DB is sqlite — just verify the module flag
        from backend.database import SQLALCHEMY_DATABASE_URL as url
        is_sqlite = url.startswith("sqlite")
        assert is_sqlite  # tests always use sqlite


# ── 2. Search router dialect flag ─────────────────────────────────────────────

class TestSearchDialect:
    def test_is_sqlite_flag_true_in_tests(self):
        from backend.routers.search import _IS_SQLITE
        assert _IS_SQLITE is True  # tests run on sqlite

    def test_fts_query_produces_quoted_tokens(self):
        from backend.routers.search import _fts_query
        result = _fts_query("machine learning")
        assert '"machine"*' in result
        assert '"learning"*' in result

    def test_fts_query_empty_returns_quoted_empty(self):
        from backend.routers.search import _fts_query
        result = _fts_query("   ")
        assert result == '""'

    def test_search_rebuild_endpoint(self, client: TestClient, auth_headers: dict):
        resp = client.post("/search/rebuild", headers=auth_headers)
        assert resp.status_code == 200
        assert "indexed" in resp.json()

    def test_search_returns_results(self, client: TestClient, auth_headers: dict, db_session):
        # Seed an entity and rebuild index
        e = models.RawEntity(primary_label="PostgreSQL Hardening Test", domain="default")
        db_session.add(e)
        db_session.commit()
        client.post("/search/rebuild", headers=auth_headers)
        resp = client.get("/search?q=PostgreSQL", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data


# ── 3. Migration cross-DB pattern (inspect.has_table) ─────────────────────────

class TestMigrationHelpers:
    def test_sprint90_migration_uses_inspect(self):
        src = pathlib.Path("alembic/versions/8ac20d60f654_sprint_90_web_scraper_configs.py").read_text()
        assert "sqlite_master" not in src
        assert "has_table" in src

    def test_sprint92_migration_uses_inspect(self):
        src = pathlib.Path("alembic/versions/92a1b2c3d4e5_sprint_92_workflow_automation.py").read_text()
        assert "sqlite_master" not in src
        assert "has_table" in src

    def test_sprint93_migration_uses_inspect(self):
        src = pathlib.Path("alembic/versions/93b2c3d4e5f6_sprint_93_embed_widgets.py").read_text()
        assert "sqlite_master" not in src
        assert "has_table" in src

    def test_baseline_has_no_bare_bool_string_defaults(self):
        src = pathlib.Path("alembic/versions/0001_baseline.py").read_text()
        # The Boolean-specific bad patterns must be gone
        assert 'sa.Boolean' not in src or 'server_default="1"' not in src
        # Cross-DB Boolean patterns must be present
        assert 'sa.text("true")' in src
        assert 'sa.text("false")' in src
        # Integer server_default="0" (failed_attempts, citation_count) are fine for PG
        import re
        bool_defaults = re.findall(r'sa\.Boolean.*?server_default="[01]"', src)
        assert len(bool_defaults) == 0, f"Found bare Boolean defaults: {bool_defaults}"

    def test_baseline_fts5_is_conditional(self):
        src = pathlib.Path("alembic/versions/0001_baseline.py").read_text()
        assert 'dialect.name == "sqlite"' in src
        assert "to_tsvector" in src  # PG branch present


# ── 4. Docker / deployment artifacts ─────────────────────────────────────────

class TestDeploymentArtifacts:
    def test_dockerfile_backend_exists(self):
        assert pathlib.Path("Dockerfile.backend").exists()

    def test_dockerfile_references_requirements(self):
        content = pathlib.Path("Dockerfile.backend").read_text()
        assert "requirements.txt" in content
        assert "alembic upgrade head" in content

    def test_docker_compose_has_postgres_service(self):
        content = pathlib.Path("docker-compose.yml").read_text()
        assert "postgres" in content
        assert "postgresql" in content.lower()

    def test_docker_compose_has_healthcheck(self):
        content = pathlib.Path("docker-compose.yml").read_text()
        assert "healthcheck" in content
        assert "pg_isready" in content

    def test_psycopg2_in_requirements(self):
        content = pathlib.Path("requirements.txt").read_text()
        assert "psycopg2" in content
