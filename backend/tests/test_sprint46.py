"""
Sprint 46 — Artifact Templates tests
GET  /artifacts/templates
POST /artifacts/templates
DELETE /artifacts/templates/{id}
"""
import json
import pytest
from backend import models


# ── Helpers ────────────────────────────────────────────────────────────────────

def _seed_builtin(db):
    """Insert one built-in template directly (bypasses lifespan seed)."""
    t = models.ArtifactTemplate(
        name="Executive Summary",
        description="KPIs for decision-makers",
        sections=json.dumps(["entity_stats", "enrichment_coverage"]),
        default_title="Executive Summary Report",
        is_builtin=True,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


def _seed_user_template(db):
    t = models.ArtifactTemplate(
        name="My Custom Template",
        description="Custom",
        sections=json.dumps(["entity_stats"]),
        default_title="Custom Report",
        is_builtin=False,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


# ── Tests ──────────────────────────────────────────────────────────────────────

def test_list_templates_requires_auth(client):
    resp = client.get("/artifacts/templates")
    assert resp.status_code in (401, 403)


def test_list_templates_includes_builtins(client, auth_headers, db_session):
    # Seed 4 built-ins (simulating lifespan seed)
    BUILTIN = [
        ("Executive Summary",  ["entity_stats","enrichment_coverage","top_brands"]),
        ("Research Analysis",  ["topic_clusters","enrichment_coverage","entity_stats"]),
        ("Data Quality Audit", ["entity_stats","harmonization_log","enrichment_coverage"]),
        ("Full Report",        ["entity_stats","enrichment_coverage","top_brands","topic_clusters","harmonization_log"]),
    ]
    for name, sections in BUILTIN:
        db_session.add(models.ArtifactTemplate(
            name=name, sections=json.dumps(sections),
            is_builtin=True, description="", default_title="",
        ))
    db_session.commit()

    resp = client.get("/artifacts/templates", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 4
    names = [t["name"] for t in data]
    assert "Executive Summary" in names
    assert "Full Report" in names
    # sections should be deserialized as list
    for t in data:
        assert isinstance(t["sections"], list)
        assert t["is_builtin"] is True


def test_create_template_editor_plus(client, editor_headers, db_session):
    payload = {
        "name": "My Report",
        "description": "Test",
        "sections": ["entity_stats", "top_brands"],
        "default_title": "My Test Report",
    }
    resp = client.post("/artifacts/templates", json=payload, headers=editor_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "My Report"
    assert data["sections"] == ["entity_stats", "top_brands"]
    assert data["is_builtin"] is False


def test_create_template_invalid_section_422(client, editor_headers, db_session):
    payload = {
        "name": "Bad Template",
        "sections": ["entity_stats", "nonexistent_section"],
    }
    resp = client.post("/artifacts/templates", json=payload, headers=editor_headers)
    assert resp.status_code == 422


def test_delete_builtin_template_403(client, auth_headers, db_session):
    tmpl = _seed_builtin(db_session)
    resp = client.delete(f"/artifacts/templates/{tmpl.id}", headers=auth_headers)
    assert resp.status_code == 403


def test_viewer_cannot_create_template(client, viewer_headers, db_session):
    payload = {"name": "Viewer Template", "sections": ["entity_stats"]}
    resp = client.post("/artifacts/templates", json=payload, headers=viewer_headers)
    assert resp.status_code in (401, 403)
