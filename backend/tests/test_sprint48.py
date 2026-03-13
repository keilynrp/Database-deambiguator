"""
Sprint 48 — Context Engine + Memory Layer
GET  /context/snapshot/{domain_id}
GET  /context/sessions
POST /context/sessions
DELETE /context/sessions/{id}
"""
import pytest


def test_snapshot_requires_auth(client):
    resp = client.get("/context/snapshot/default")
    assert resp.status_code in (401, 403)


def test_snapshot_invalid_domain_404(client, auth_headers):
    resp = client.get("/context/snapshot/no_such_domain_xyz", headers=auth_headers)
    assert resp.status_code == 404


def test_snapshot_returns_shape(client, auth_headers):
    resp = client.get("/context/snapshot/default", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "domain_id" in data
    assert "entity_stats" in data
    assert "gaps" in data
    assert "top_topics" in data
    assert data["domain_id"] == "default"


def test_snapshot_entity_stats_keys(client, auth_headers):
    resp = client.get("/context/snapshot/default", headers=auth_headers)
    assert resp.status_code == 200
    stats = resp.json()["entity_stats"]
    assert "total" in stats
    assert "enriched" in stats
    assert "pct_enriched" in stats


def test_create_session_editor_plus(client, editor_headers):
    resp = client.post(
        "/context/sessions",
        json={"domain_id": "default", "label": "Test Snapshot"},
        headers=editor_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["domain_id"] == "default"
    assert data["label"] == "Test Snapshot"
    assert "context_snapshot" in data
    assert "id" in data


def test_list_and_delete_session(client, editor_headers, auth_headers):
    # Create
    created = client.post(
        "/context/sessions",
        json={"domain_id": "default", "label": "To Delete"},
        headers=editor_headers,
    ).json()
    session_id = created["id"]

    # List — should appear
    listing = client.get("/context/sessions", headers=auth_headers).json()
    assert any(s["id"] == session_id for s in listing)

    # Delete
    del_resp = client.delete(f"/context/sessions/{session_id}", headers=editor_headers)
    assert del_resp.status_code == 204

    # List — should be gone
    listing2 = client.get("/context/sessions", headers=auth_headers).json()
    assert not any(s["id"] == session_id for s in listing2)
