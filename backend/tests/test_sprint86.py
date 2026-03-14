"""
Sprint 86 — Collaborative Annotations (Enhanced): Resolve + React + Stats

Tests cover:
  - POST /annotations/{id}/resolve toggles is_resolved
  - POST /annotations/{id}/resolve on a reply returns 400
  - POST /annotations/{id}/react toggles emoji reaction
  - POST /annotations/{id}/react with invalid emoji returns 422
  - GET /annotations/stats/{entity_id} returns thread counts
  - Model fields: is_resolved, emoji_reactions
"""
import json
import pytest
from backend import models


def _create_annotation(client, headers, entity_id=1, content="Test annotation"):
    return client.post(
        "/annotations",
        json={"entity_id": entity_id, "content": content, "parent_id": None},
        headers=headers,
    )


def _create_reply(client, headers, parent_id: int, entity_id=1, content="A reply"):
    return client.post(
        "/annotations",
        json={"entity_id": entity_id, "content": content, "parent_id": parent_id},
        headers=headers,
    )


class TestAnnotationResolve:
    def test_resolve_toggles_to_true(self, client, auth_headers):
        ann = _create_annotation(client, auth_headers, content="Resolvable").json()
        r = client.post(f"/annotations/{ann['id']}/resolve", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["is_resolved"] is True

    def test_resolve_toggles_back_to_false(self, client, auth_headers):
        ann = _create_annotation(client, auth_headers, content="Toggle back").json()
        client.post(f"/annotations/{ann['id']}/resolve", headers=auth_headers)
        r = client.post(f"/annotations/{ann['id']}/resolve", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["is_resolved"] is False

    def test_resolve_sets_resolved_at(self, client, auth_headers):
        ann = _create_annotation(client, auth_headers, content="Check resolved_at").json()
        r = client.post(f"/annotations/{ann['id']}/resolve", headers=auth_headers)
        data = r.json()
        assert data["is_resolved"] is True
        assert data["resolved_at"] is not None

    def test_resolve_reply_returns_400(self, client, auth_headers):
        parent = _create_annotation(client, auth_headers, content="Parent").json()
        reply = _create_reply(client, auth_headers, parent_id=parent["id"], content="Reply").json()
        r = client.post(f"/annotations/{reply['id']}/resolve", headers=auth_headers)
        assert r.status_code == 400

    def test_resolve_nonexistent_returns_404(self, client, auth_headers):
        r = client.post("/annotations/99999/resolve", headers=auth_headers)
        assert r.status_code == 404

    def test_viewer_cannot_resolve(self, client, viewer_headers):
        # viewer cannot create annotations either, so we check the endpoint RBAC
        r = client.post("/annotations/1/resolve", headers=viewer_headers)
        assert r.status_code in (403, 404)


class TestAnnotationReact:
    def test_react_adds_reaction(self, client, auth_headers):
        ann = _create_annotation(client, auth_headers, content="React test").json()
        r = client.post(f"/annotations/{ann['id']}/react?emoji=%F0%9F%91%8D", headers=auth_headers)  # 👍
        assert r.status_code == 200
        data = r.json()
        reactions = data.get("emoji_reactions", {})
        assert "👍" in reactions
        assert len(reactions["👍"]) == 1

    def test_react_toggles_off(self, client, auth_headers):
        ann = _create_annotation(client, auth_headers, content="Toggle off").json()
        # Add reaction
        client.post(f"/annotations/{ann['id']}/react?emoji=%F0%9F%91%8D", headers=auth_headers)
        # Remove reaction (toggle)
        r = client.post(f"/annotations/{ann['id']}/react?emoji=%F0%9F%91%8D", headers=auth_headers)
        data = r.json()
        reactions = data.get("emoji_reactions", {})
        assert "👍" not in reactions or len(reactions.get("👍", [])) == 0

    def test_invalid_emoji_returns_422(self, client, auth_headers):
        ann = _create_annotation(client, auth_headers, content="Bad emoji").json()
        r = client.post(f"/annotations/{ann['id']}/react?emoji=X", headers=auth_headers)
        assert r.status_code == 422

    def test_multiple_emojis(self, client, auth_headers):
        ann = _create_annotation(client, auth_headers, content="Multi emoji").json()
        client.post(f"/annotations/{ann['id']}/react?emoji=%F0%9F%91%8D", headers=auth_headers)  # 👍
        r = client.post(f"/annotations/{ann['id']}/react?emoji=%E2%9D%A4%EF%B8%8F", headers=auth_headers)  # ❤️
        data = r.json()
        reactions = data.get("emoji_reactions", {})
        assert "👍" in reactions
        assert "❤️" in reactions

    def test_unauthenticated_cannot_react(self, client):
        r = client.post("/annotations/1/react?emoji=%F0%9F%91%8D")
        assert r.status_code == 401


class TestAnnotationStats:
    def test_stats_returns_counts(self, client, auth_headers):
        # Create 2 threads, resolve 1
        a1 = _create_annotation(client, auth_headers, content="Thread 1", entity_id=9001).json()
        a2 = _create_annotation(client, auth_headers, content="Thread 2", entity_id=9001).json()
        client.post(f"/annotations/{a1['id']}/resolve", headers=auth_headers)
        r = client.get("/annotations/stats/9001", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert data["total_threads"] >= 2
        assert data["resolved_threads"] >= 1
        assert data["unresolved_threads"] == data["total_threads"] - data["resolved_threads"]

    def test_stats_empty_entity(self, client, auth_headers):
        r = client.get("/annotations/stats/99999", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert data["total_threads"] == 0
        assert data["resolved_threads"] == 0

    def test_stats_unauthenticated(self, client):
        r = client.get("/annotations/stats/1")
        assert r.status_code == 401


class TestAnnotationModel:
    def test_model_fields(self, db_session):
        user = models.User(username="ann86_test_u", password_hash="x", role="editor", is_active=True)
        db_session.add(user)
        db_session.flush()
        ann = models.Annotation(
            entity_id=1,
            author_id=user.id,
            author_name=user.username,
            content="Sprint 86 test",
            is_resolved=False,
            emoji_reactions=json.dumps({"👍": [user.id]}),
        )
        db_session.add(ann)
        db_session.commit()
        db_session.refresh(ann)
        assert ann.id is not None
        assert ann.is_resolved is False or ann.is_resolved == 0
        assert json.loads(ann.emoji_reactions) == {"👍": [user.id]}
