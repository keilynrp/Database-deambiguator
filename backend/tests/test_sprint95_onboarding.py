"""
Sprint 95/104 onboarding tests.

15 tests cover:
  GET /onboarding/status:
    - returns 5 steps for fresh user
    - step list contains required fields
    - percent is an integer between 0 and 100
    - requires authentication
    - step completion changes with DB state
    - commercial MVP metadata is present
    - onboarding journey is present
    - next recommended step is derived from current progress
"""
from __future__ import annotations

import json

from fastapi.testclient import TestClient

from backend import models


def _get_status(client, auth_headers):
    response = client.get("/onboarding/status", headers=auth_headers)
    assert response.status_code == 200
    return response.json()


class TestOnboardingStatus:
    def test_returns_five_steps(self, client: TestClient, auth_headers: dict, db_session):
        data = _get_status(client, auth_headers)
        assert len(data["steps"]) == 5

    def test_step_has_required_fields(self, client: TestClient, auth_headers: dict, db_session):
        data = _get_status(client, auth_headers)
        step = data["steps"][0]
        for field in ("key", "label", "description", "href", "icon", "completed"):
            assert field in step, f"Missing field: {field}"

    def test_percent_is_integer_0_to_100(self, client: TestClient, auth_headers: dict, db_session):
        data = _get_status(client, auth_headers)
        assert 0 <= data["percent"] <= 100
        assert isinstance(data["percent"], int)

    def test_requires_auth(self, client: TestClient):
        response = client.get("/onboarding/status")
        assert response.status_code == 401

    def test_import_data_step_incomplete_initially(self, client: TestClient, auth_headers: dict, db_session):
        data = _get_status(client, auth_headers)
        step = next(step for step in data["steps"] if step["key"] == "import_data")
        assert step["completed"] is False

    def test_import_data_completes_after_entity(self, client: TestClient, auth_headers: dict, db_session):
        entity = models.RawEntity(primary_label="Onboarding Test Entity", domain="default")
        db_session.add(entity)
        db_session.commit()

        data = _get_status(client, auth_headers)
        step = next(step for step in data["steps"] if step["key"] == "import_data")
        assert step["completed"] is True

    def test_enrich_entity_completes_after_enrichment(self, client: TestClient, auth_headers: dict, db_session):
        entity = models.RawEntity(
            primary_label="Enriched Entity",
            domain="default",
            enrichment_status="completed",
        )
        db_session.add(entity)
        db_session.commit()

        data = _get_status(client, auth_headers)
        step = next(step for step in data["steps"] if step["key"] == "enrich_entity")
        assert step["completed"] is True

    def test_create_rule_completes_after_rule(self, client: TestClient, auth_headers: dict, db_session):
        rule = models.NormalizationRule(
            field_name="primary_label",
            original_value="Mikrosoft",
            normalized_value="Microsoft",
        )
        db_session.add(rule)
        db_session.commit()

        data = _get_status(client, auth_headers)
        step = next(step for step in data["steps"] if step["key"] == "create_rule")
        assert step["completed"] is True

    def test_create_workflow_completes_after_workflow(self, client: TestClient, auth_headers: dict, db_session):
        workflow = models.Workflow(
            name="Onboarding Test Workflow",
            trigger_type="manual",
            conditions=json.dumps([]),
            actions=json.dumps([{"type": "log_only", "config": {}}]),
        )
        db_session.add(workflow)
        db_session.commit()

        data = _get_status(client, auth_headers)
        step = next(step for step in data["steps"] if step["key"] == "create_workflow")
        assert step["completed"] is True

    def test_completed_count_reflects_reality(self, client: TestClient, auth_headers: dict, db_session):
        data = _get_status(client, auth_headers)
        manual_count = sum(1 for step in data["steps"] if step["completed"])
        assert data["completed"] == manual_count

    def test_all_done_is_bool(self, client: TestClient, auth_headers: dict, db_session):
        data = _get_status(client, auth_headers)
        assert isinstance(data["all_done"], bool)

    def test_total_is_five(self, client: TestClient, auth_headers: dict, db_session):
        data = _get_status(client, auth_headers)
        assert data["total"] == 5

    def test_commercial_mvp_metadata_present(self, client: TestClient, auth_headers: dict, db_session):
        data = _get_status(client, auth_headers)
        mvp = data["commercial_mvp"]

        assert mvp["key"] == "research_intelligence"
        assert "ideal_customer" in mvp
        assert "initial_dataset" in mvp
        assert isinstance(mvp["primary_outcomes"], list)
        assert len(mvp["primary_outcomes"]) >= 3

    def test_journey_present_with_required_fields(self, client: TestClient, auth_headers: dict, db_session):
        data = _get_status(client, auth_headers)

        assert len(data["journey"]) == 4
        for step in data["journey"]:
            for field in ("key", "label", "description", "href"):
                assert field in step, f"Missing journey field: {field}"

    def test_next_recommended_step_defaults_to_import_data(self, client: TestClient, auth_headers: dict, db_session):
        data = _get_status(client, auth_headers)

        assert data["next_recommended_step"]["key"] == "import_data"
        assert "reason" in data["next_recommended_step"]

    def test_next_recommended_step_advances_after_import(self, client: TestClient, auth_headers: dict, db_session):
        entity = models.RawEntity(primary_label="Imported Entity", domain="default")
        db_session.add(entity)
        db_session.commit()

        data = _get_status(client, auth_headers)
        assert data["next_recommended_step"]["key"] == "enrich_entity"
