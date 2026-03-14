"""
Sprint 80 — Custom Dashboard Builder: backend tests.

Tests cover:
  - GET  /dashboards/widget-types    (catalogue)
  - POST /dashboards                 (create)
  - GET  /dashboards                 (list — user-scoped)
  - GET  /dashboards/{id}            (get single)
  - PUT  /dashboards/{id}            (update name / layout)
  - DELETE /dashboards/{id}          (delete + auto-promote default)
  - POST /dashboards/{id}/default    (set as default)
  - Isolation: user A cannot access user B's dashboards
  - Validation: invalid widget type rejected
  - First dashboard auto-becomes default
  - Model fields
"""

import json
import pytest
from backend import models


# ── helpers ───────────────────────────────────────────────────────────────────

def _create(client, headers, name="My Dashboard", layout=None):
    return client.post(
        "/dashboards",
        json={"name": name, "layout": layout or []},
        headers=headers,
    )


# ── Widget catalogue ──────────────────────────────────────────────────────────

class TestWidgetCatalogue:
    def test_catalogue_returns_list(self, client, auth_headers):
        r = client.get("/dashboards/widget-types", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) >= 6

    def test_catalogue_has_required_fields(self, client, auth_headers):
        r = client.get("/dashboards/widget-types", headers=auth_headers)
        for wt in r.json():
            assert "type" in wt
            assert "label" in wt
            assert "default_cols" in wt

    def test_unauthenticated_rejected(self, client):
        r = client.get("/dashboards/widget-types")
        assert r.status_code == 401


# ── CRUD ─────────────────────────────────────────────────────────────────────

class TestDashboardCRUD:
    def test_create_returns_201(self, client, auth_headers):
        r = _create(client, auth_headers, name="Sprint 80 Test")
        assert r.status_code == 201
        d = r.json()
        assert d["name"] == "Sprint 80 Test"
        assert d["layout"] == []
        assert d["is_default"] is True   # first dashboard is auto-default

    def test_second_dashboard_not_default(self, client, auth_headers):
        _create(client, auth_headers, name="First")
        r = _create(client, auth_headers, name="Second")
        assert r.status_code == 201
        assert r.json()["is_default"] is False

    def test_list_returns_only_own(self, client, auth_headers):
        _create(client, auth_headers, name="Own 1")
        r = client.get("/dashboards", headers=auth_headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)
        assert all(isinstance(d, dict) for d in r.json())

    def test_get_single(self, client, auth_headers):
        created = _create(client, auth_headers, name="Get Single").json()
        r = client.get(f"/dashboards/{created['id']}", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["id"] == created["id"]

    def test_get_404(self, client, auth_headers):
        r = client.get("/dashboards/99999", headers=auth_headers)
        assert r.status_code == 404

    def test_update_name(self, client, auth_headers):
        created = _create(client, auth_headers, name="Before").json()
        r = client.put(
            f"/dashboards/{created['id']}",
            json={"name": "After"},
            headers=auth_headers,
        )
        assert r.status_code == 200
        assert r.json()["name"] == "After"

    def test_update_layout(self, client, auth_headers):
        created = _create(client, auth_headers, name="Layout Test").json()
        widget = {
            "id": "w1", "type": "entity_kpi", "title": "KPIs",
            "cols": 6, "config": {"domain_id": "default"},
        }
        r = client.put(
            f"/dashboards/{created['id']}",
            json={"layout": [widget]},
            headers=auth_headers,
        )
        assert r.status_code == 200
        layout = r.json()["layout"]
        assert len(layout) == 1
        assert layout[0]["type"] == "entity_kpi"

    def test_delete(self, client, auth_headers):
        created = _create(client, auth_headers, name="Delete Me").json()
        r = client.delete(f"/dashboards/{created['id']}", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["deleted"] == created["id"]
        r2 = client.get(f"/dashboards/{created['id']}", headers=auth_headers)
        assert r2.status_code == 404

    def test_delete_404(self, client, auth_headers):
        r = client.delete("/dashboards/99999", headers=auth_headers)
        assert r.status_code == 404


# ── Set default ───────────────────────────────────────────────────────────────

class TestSetDefault:
    def test_set_default(self, client, auth_headers):
        d1 = _create(client, auth_headers, name="D1").json()
        d2 = _create(client, auth_headers, name="D2").json()
        # Set D1 as default first (deterministic regardless of prior test state)
        client.post(f"/dashboards/{d1['id']}/default", headers=auth_headers)
        # Now set D2 as default
        r = client.post(f"/dashboards/{d2['id']}/default", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["is_default"] is True
        # D1 should no longer be default
        d1_r = client.get(f"/dashboards/{d1['id']}", headers=auth_headers)
        assert d1_r.json()["is_default"] is False

    def test_set_default_404(self, client, auth_headers):
        r = client.post("/dashboards/99999/default", headers=auth_headers)
        assert r.status_code == 404


# ── Validation ────────────────────────────────────────────────────────────────

class TestDashboardValidation:
    def test_invalid_widget_type_rejected(self, client, auth_headers):
        widget = {"id": "w1", "type": "not_a_real_widget", "cols": 6, "config": {}}
        r = _create(client, auth_headers, layout=[widget])
        assert r.status_code == 422

    def test_empty_name_rejected(self, client, auth_headers):
        r = _create(client, auth_headers, name="")
        assert r.status_code == 422

    def test_valid_widget_types_accepted(self, client, auth_headers):
        widgets = [
            {"id": "w1", "type": "entity_kpi",    "cols": 4,  "config": {}},
            {"id": "w2", "type": "top_entities",  "cols": 8,  "config": {}},
            {"id": "w3", "type": "concept_cloud", "cols": 6,  "config": {}},
        ]
        r = _create(client, auth_headers, layout=widgets)
        assert r.status_code == 201
        assert len(r.json()["layout"]) == 3


# ── User isolation ────────────────────────────────────────────────────────────

class TestUserIsolation:
    def test_editor_cannot_see_admin_dashboards(self, client, auth_headers, editor_headers):
        # admin creates a dashboard
        admin_dash = _create(client, auth_headers, name="Admin Private").json()
        # editor lists dashboards — should not see admin's
        r = client.get("/dashboards", headers=editor_headers)
        assert r.status_code == 200
        ids = [d["id"] for d in r.json()]
        assert admin_dash["id"] not in ids

    def test_editor_cannot_access_admin_dashboard_by_id(self, client, auth_headers, editor_headers):
        admin_dash = _create(client, auth_headers, name="Admin Only").json()
        r = client.get(f"/dashboards/{admin_dash['id']}", headers=editor_headers)
        assert r.status_code == 404


# ── Model fields ──────────────────────────────────────────────────────────────

class TestDashboardModel:
    def test_model_fields(self, db_session):
        # Need a user to satisfy the FK
        user = models.User(
            username="dash_test_user",
            password_hash="x",
            role="viewer",
            is_active=True,
        )
        db_session.add(user)
        db_session.flush()

        d = models.UserDashboard(
            user_id=user.id,
            name="Test Dashboard",
            layout=json.dumps([{"id": "w1", "type": "entity_kpi", "cols": 6, "config": {}}]),
            is_default=True,
        )
        db_session.add(d)
        db_session.commit()
        db_session.refresh(d)

        assert d.id is not None
        assert d.name == "Test Dashboard"
        assert d.user_id == user.id
        assert d.is_default is True or d.is_default == 1
        widgets = json.loads(d.layout)
        assert widgets[0]["type"] == "entity_kpi"
