"""
Sprint 92 — Workflow Automation Engine tests.

15 tests:
  Unit (workflow_engine):
    - evaluate_condition field_equals (match + no match)
    - evaluate_condition field_contains
    - evaluate_condition field_empty
    - evaluate_condition enrichment_status_is
    - evaluate_conditions (empty = True)
    - _action_log_only returns ok
    - run_workflow skips when conditions fail
    - run_workflow success with log_only action
  Integration (router):
    - POST /workflows creates workflow (201)
    - GET /workflows lists workflows
    - GET /workflows/{id} returns detail
    - PUT /workflows/{id} updates workflow
    - POST /workflows/{id}/run manual trigger
    - GET /workflows/{id}/runs execution history
    - DELETE /workflows/{id} removes workflow
"""
from __future__ import annotations

import json
import pytest
from fastapi.testclient import TestClient

from backend import models
from backend.workflow_engine import (
    _evaluate_condition,
    _evaluate_conditions,
    _action_log_only,
    run_workflow,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_entity(db, label="TestEntity", enrichment_status="completed", enrichment_concepts=None):
    e = models.RawEntity(
        primary_label=label,
        domain="default",
        enrichment_status=enrichment_status,
        enrichment_concepts=enrichment_concepts,
    )
    db.add(e)
    db.commit()
    db.refresh(e)
    return e


def _make_workflow(db, trigger="manual", conditions=None, actions=None, user_id=1):
    wf = models.Workflow(
        name="Test Workflow",
        trigger_type=trigger,
        conditions=json.dumps(conditions or []),
        actions=json.dumps(actions or [{"type": "log_only", "config": {}}]),
        created_by=user_id,
    )
    db.add(wf)
    db.commit()
    db.refresh(wf)
    return wf


# ── Unit: workflow_engine ─────────────────────────────────────────────────────

class TestConditionEvaluation:
    def test_field_equals_match(self, db_session):
        entity = _make_entity(db_session)
        cond = {"type": "field_equals", "field": "enrichment_status", "value": "completed"}
        assert _evaluate_condition(entity, cond) is True

    def test_field_equals_no_match(self, db_session):
        entity = _make_entity(db_session)
        cond = {"type": "field_equals", "field": "enrichment_status", "value": "failed"}
        assert _evaluate_condition(entity, cond) is False

    def test_field_contains(self, db_session):
        entity = _make_entity(db_session, enrichment_concepts="machine learning, NLP")
        cond = {"type": "field_contains", "field": "enrichment_concepts", "value": "NLP"}
        assert _evaluate_condition(entity, cond) is True

    def test_field_empty_true(self, db_session):
        entity = _make_entity(db_session, enrichment_concepts=None)
        cond = {"type": "field_empty", "field": "enrichment_concepts", "value": ""}
        assert _evaluate_condition(entity, cond) is True

    def test_field_empty_false(self, db_session):
        entity = _make_entity(db_session, enrichment_concepts="some concept")
        cond = {"type": "field_empty", "field": "enrichment_concepts", "value": ""}
        assert _evaluate_condition(entity, cond) is False

    def test_enrichment_status_is(self, db_session):
        entity = _make_entity(db_session, enrichment_status="failed")
        cond = {"type": "enrichment_status_is", "field": "", "value": "failed"}
        assert _evaluate_condition(entity, cond) is True

    def test_empty_conditions_always_true(self, db_session):
        entity = _make_entity(db_session)
        assert _evaluate_conditions(entity, []) is True

    def test_log_only_action_returns_ok(self, db_session):
        entity = _make_entity(db_session)
        result = _action_log_only(entity, {})
        assert result["ok"] is True
        assert result["entity_id"] == entity.id


class TestRunWorkflow:
    def test_run_skips_when_conditions_fail(self, db_session):
        entity = _make_entity(db_session, enrichment_status="pending")
        wf = _make_workflow(
            db_session,
            conditions=[{"type": "enrichment_status_is", "field": "", "value": "completed"}],
        )
        run = run_workflow(wf, entity, db_session)
        assert run.status == "skipped"

    def test_run_success_with_log_only(self, db_session):
        entity = _make_entity(db_session)
        wf = _make_workflow(db_session, actions=[{"type": "log_only", "config": {}}])
        run = run_workflow(wf, entity, db_session)
        assert run.status == "success"
        steps = json.loads(run.steps_log)
        assert steps[0]["action"] == "log_only"
        assert steps[0]["result"]["ok"] is True


# ── Integration: router ───────────────────────────────────────────────────────

class TestWorkflowRouter:
    def test_create_workflow(self, client: TestClient, auth_headers: dict):
        resp = client.post("/workflows", json={
            "name": "Auto Tag on Enrich",
            "trigger_type": "entity.enriched",
            "conditions": [
                {"type": "field_empty", "field": "enrichment_concepts", "value": ""}
            ],
            "actions": [
                {"type": "log_only", "config": {}}
            ],
        }, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Auto Tag on Enrich"
        assert data["trigger_type"] == "entity.enriched"

    def test_list_workflows(self, client: TestClient, auth_headers: dict):
        client.post("/workflows", json={
            "name": "List Test WF",
            "trigger_type": "manual",
            "conditions": [],
            "actions": [{"type": "log_only", "config": {}}],
        }, headers=auth_headers)
        resp = client.get("/workflows", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert data["total"] >= 1

    def test_get_workflow_detail(self, client: TestClient, auth_headers: dict):
        create = client.post("/workflows", json={
            "name": "Detail WF",
            "trigger_type": "entity.flagged",
            "conditions": [],
            "actions": [{"type": "log_only", "config": {}}],
        }, headers=auth_headers)
        wf_id = create.json()["id"]
        resp = client.get(f"/workflows/{wf_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == wf_id

    def test_update_workflow(self, client: TestClient, auth_headers: dict):
        create = client.post("/workflows", json={
            "name": "Update Me",
            "trigger_type": "manual",
            "conditions": [],
            "actions": [{"type": "log_only", "config": {}}],
        }, headers=auth_headers)
        wf_id = create.json()["id"]
        resp = client.put(f"/workflows/{wf_id}", json={"name": "Updated Name", "is_active": False}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated Name"
        assert resp.json()["is_active"] is False

    def test_manual_run(self, client: TestClient, auth_headers: dict, db_session):
        entity = _make_entity(db_session, label="Run Target Entity")
        wf = _make_workflow(db_session, trigger="manual")
        resp = client.post(f"/workflows/{wf.id}/run", json={"entity_id": entity.id}, headers=auth_headers)
        assert resp.status_code == 201
        run = resp.json()
        assert run["status"] in ("success", "skipped", "error")
        assert run["workflow_id"] == wf.id

    def test_list_runs(self, client: TestClient, auth_headers: dict, db_session):
        entity = _make_entity(db_session, label="History Entity")
        wf = _make_workflow(db_session, trigger="manual")
        client.post(f"/workflows/{wf.id}/run", json={"entity_id": entity.id}, headers=auth_headers)
        resp = client.get(f"/workflows/{wf.id}/runs", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1

    def test_delete_workflow(self, client: TestClient, auth_headers: dict):
        create = client.post("/workflows", json={
            "name": "Delete Me",
            "trigger_type": "manual",
            "conditions": [],
            "actions": [{"type": "log_only", "config": {}}],
        }, headers=auth_headers)
        wf_id = create.json()["id"]
        resp = client.delete(f"/workflows/{wf_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["deleted"] is True
        get_resp = client.get(f"/workflows/{wf_id}", headers=auth_headers)
        assert get_resp.status_code == 404
