"""
Sprint 81 — Alert Channels: Slack/Teams/Discord/webhook push notifications
Sprint 82 — API Keys: long-lived programmatic access tokens

Tests cover:
  Sprint 81:
    - GET /alert-channels/events
    - POST /alert-channels (create)
    - GET  /alert-channels (list)
    - GET  /alert-channels/{id}
    - PUT  /alert-channels/{id}
    - DELETE /alert-channels/{id}
    - POST /alert-channels/{id}/test (always returns 200 — network may fail)
    - Validation: unknown event, invalid type
    - RBAC: editor/viewer cannot access
    - Model fields

  Sprint 82:
    - GET /api-keys/scopes
    - POST /api-keys (create — full key returned once)
    - GET  /api-keys (list — no full key in response)
    - DELETE /api-keys/{id} (revoke)
    - Validation: invalid scope, empty name
    - API key auth: use returned key as Bearer token
    - User isolation: other users cannot see each other's keys
    - Model fields
"""
import hashlib
import json
import pytest
from backend import models
from backend.routers.api_keys import _generate_key


# ═══════════════════════════════════════════════════════════════════════════════
# Sprint 81 — Alert Channels
# ═══════════════════════════════════════════════════════════════════════════════

def _create_channel(client, headers, name="Slack #eng", ch_type="slack", events=None):
    return client.post(
        "/alert-channels",
        json={
            "name": name,
            "type": ch_type,
            "webhook_url": "https://hooks.slack.com/services/TEST",
            "events": events or ["entities.imported"],
        },
        headers=headers,
    )


class TestAlertChannelEvents:
    def test_catalogue_returns_list(self, client, auth_headers):
        r = client.get("/alert-channels/events", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) >= 5

    def test_catalogue_has_fields(self, client, auth_headers):
        r = client.get("/alert-channels/events", headers=auth_headers)
        for e in r.json():
            assert "id" in e and "label" in e and "description" in e

    def test_editor_cannot_access_events(self, client, editor_headers):
        r = client.get("/alert-channels/events", headers=editor_headers)
        assert r.status_code == 403


class TestAlertChannelCRUD:
    def test_create_returns_201(self, client, auth_headers):
        r = _create_channel(client, auth_headers)
        assert r.status_code == 201
        d = r.json()
        assert d["name"] == "Slack #eng"
        assert d["type"] == "slack"
        assert d["events"] == ["entities.imported"]
        assert d["is_active"] is True
        assert d["total_fired"] == 0
        assert "webhook_url" not in d   # never exposed

    def test_list(self, client, auth_headers):
        _create_channel(client, auth_headers, name="List Test")
        r = client.get("/alert-channels", headers=auth_headers)
        assert r.status_code == 200
        assert any(c["name"] == "List Test" for c in r.json())

    def test_get_single(self, client, auth_headers):
        created = _create_channel(client, auth_headers, name="Get Test").json()
        r = client.get(f"/alert-channels/{created['id']}", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["id"] == created["id"]

    def test_get_404(self, client, auth_headers):
        r = client.get("/alert-channels/99999", headers=auth_headers)
        assert r.status_code == 404

    def test_update_events(self, client, auth_headers):
        created = _create_channel(client, auth_headers, name="Update Events").json()
        r = client.put(
            f"/alert-channels/{created['id']}",
            json={"events": ["report.sent", "report.failed"]},
            headers=auth_headers,
        )
        assert r.status_code == 200
        assert set(r.json()["events"]) == {"report.sent", "report.failed"}

    def test_pause_channel(self, client, auth_headers):
        created = _create_channel(client, auth_headers, name="Pause Test").json()
        r = client.put(
            f"/alert-channels/{created['id']}",
            json={"is_active": False},
            headers=auth_headers,
        )
        assert r.status_code == 200
        assert r.json()["is_active"] is False

    def test_delete(self, client, auth_headers):
        created = _create_channel(client, auth_headers, name="Delete Test").json()
        r = client.delete(f"/alert-channels/{created['id']}", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["deleted"] == created["id"]

    def test_delete_404(self, client, auth_headers):
        r = client.delete("/alert-channels/99999", headers=auth_headers)
        assert r.status_code == 404

    def test_test_endpoint_returns_200(self, client, auth_headers):
        """Test endpoint always returns 200; success depends on network."""
        created = _create_channel(client, auth_headers, name="Test Endpoint").json()
        r = client.post(f"/alert-channels/{created['id']}/test", headers=auth_headers)
        assert r.status_code == 200
        assert "success" in r.json()

    def test_test_404(self, client, auth_headers):
        r = client.post("/alert-channels/99999/test", headers=auth_headers)
        assert r.status_code == 404


class TestAlertChannelValidation:
    def test_invalid_event_rejected(self, client, auth_headers):
        r = client.post(
            "/alert-channels",
            json={"name": "Bad Events", "type": "slack", "webhook_url": "https://x.com", "events": ["not.a.real.event"]},
            headers=auth_headers,
        )
        assert r.status_code == 422

    def test_invalid_type_rejected(self, client, auth_headers):
        r = client.post(
            "/alert-channels",
            json={"name": "Bad Type", "type": "discord_x", "webhook_url": "https://x.com", "events": []},
            headers=auth_headers,
        )
        assert r.status_code == 422

    def test_discord_type_accepted(self, client, auth_headers):
        r = _create_channel(client, auth_headers, name="Discord", ch_type="discord")
        assert r.status_code == 201

    def test_teams_type_accepted(self, client, auth_headers):
        r = _create_channel(client, auth_headers, name="Teams", ch_type="teams")
        assert r.status_code == 201


class TestAlertChannelRBAC:
    def test_viewer_cannot_list(self, client, viewer_headers):
        r = client.get("/alert-channels", headers=viewer_headers)
        assert r.status_code == 403

    def test_editor_cannot_create(self, client, editor_headers):
        r = _create_channel(client, editor_headers)
        assert r.status_code == 403

    def test_unauthenticated_rejected(self, client):
        r = client.get("/alert-channels")
        assert r.status_code == 401


class TestAlertChannelModel:
    def test_model_fields(self, db_session):
        ch = models.AlertChannel(
            name="Model Test",
            type="slack",
            webhook_url="https://hooks.slack.com/services/TEST",
            events=json.dumps(["entities.imported", "report.sent"]),
            is_active=True,
            total_fired=0,
        )
        db_session.add(ch)
        db_session.commit()
        db_session.refresh(ch)
        assert ch.id is not None
        assert json.loads(ch.events) == ["entities.imported", "report.sent"]
        assert ch.is_active is True or ch.is_active == 1


# ═══════════════════════════════════════════════════════════════════════════════
# Sprint 82 — API Keys
# ═══════════════════════════════════════════════════════════════════════════════

def _create_key(client, headers, name="CI Pipeline", scopes=None):
    return client.post(
        "/api-keys",
        json={"name": name, "scopes": scopes or ["read"]},
        headers=headers,
    )


class TestApiKeyScopes:
    def test_scopes_endpoint(self, client, auth_headers):
        r = client.get("/api-keys/scopes", headers=auth_headers)
        assert r.status_code == 200
        scope_ids = [s["id"] for s in r.json()]
        assert "read" in scope_ids
        assert "write" in scope_ids
        assert "admin" in scope_ids

    def test_scopes_unauthenticated(self, client):
        r = client.get("/api-keys/scopes")
        assert r.status_code == 401


class TestApiKeyCRUD:
    def test_create_returns_201_with_key(self, client, auth_headers):
        r = _create_key(client, auth_headers)
        assert r.status_code == 201
        d = r.json()
        assert "key" in d
        assert d["key"].startswith("ukip_")
        assert d["name"] == "CI Pipeline"
        assert d["scopes"] == ["read"]
        assert d["is_active"] is True
        assert len(d["key_prefix"]) == 16

    def test_list_does_not_expose_full_key(self, client, auth_headers):
        _create_key(client, auth_headers, name="List Key")
        r = client.get("/api-keys", headers=auth_headers)
        assert r.status_code == 200
        for k in r.json():
            assert "key" not in k   # full key never in list
            assert "key_prefix" in k

    def test_revoke_key(self, client, auth_headers):
        created = _create_key(client, auth_headers, name="Revoke Test").json()
        r = client.delete(f"/api-keys/{created['id']}", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["revoked"] == created["id"]

    def test_revoke_404(self, client, auth_headers):
        r = client.delete("/api-keys/99999", headers=auth_headers)
        assert r.status_code == 404

    def test_revoked_key_appears_inactive_in_list(self, client, auth_headers):
        created = _create_key(client, auth_headers, name="Inactive Check").json()
        client.delete(f"/api-keys/{created['id']}", headers=auth_headers)
        r = client.get("/api-keys", headers=auth_headers)
        match = next((k for k in r.json() if k["id"] == created["id"]), None)
        assert match is not None
        assert match["is_active"] is False

    def test_key_format(self, client, auth_headers):
        created = _create_key(client, auth_headers, name="Format Check").json()
        full_key = created["key"]
        assert full_key.startswith("ukip_")
        assert len(full_key) >= 20
        # prefix is first 16 chars
        assert created["key_prefix"] == full_key[:16]


class TestApiKeyAuth:
    def test_api_key_authenticates_requests(self, client, auth_headers):
        """A valid API key should authenticate GET /entities (requires auth)."""
        created = _create_key(client, auth_headers, name="Auth Test").json()
        full_key = created["key"]
        r = client.get("/api-keys", headers={"Authorization": f"Bearer {full_key}"})
        assert r.status_code == 200

    def test_invalid_api_key_rejected(self, client):
        r = client.get("/api-keys", headers={"Authorization": "Bearer ukip_INVALIDDDD"})
        assert r.status_code == 401

    def test_revoked_key_rejected(self, client, auth_headers):
        created = _create_key(client, auth_headers, name="Revoke Auth Test").json()
        full_key = created["key"]
        client.delete(f"/api-keys/{created['id']}", headers=auth_headers)
        r = client.get("/api-keys", headers={"Authorization": f"Bearer {full_key}"})
        assert r.status_code == 401


class TestApiKeyValidation:
    def test_invalid_scope_rejected(self, client, auth_headers):
        r = client.post("/api-keys", json={"name": "Bad Scope", "scopes": ["superpower"]}, headers=auth_headers)
        assert r.status_code == 422

    def test_empty_scopes_rejected(self, client, auth_headers):
        r = client.post("/api-keys", json={"name": "No Scope", "scopes": []}, headers=auth_headers)
        assert r.status_code == 422

    def test_empty_name_rejected(self, client, auth_headers):
        r = _create_key(client, auth_headers, name="")
        assert r.status_code == 422

    def test_multiple_scopes_accepted(self, client, auth_headers):
        r = _create_key(client, auth_headers, name="Multi Scope", scopes=["read", "write"])
        assert r.status_code == 201
        assert set(r.json()["scopes"]) == {"read", "write"}


class TestApiKeyUserIsolation:
    def test_editor_cannot_see_admin_keys(self, client, auth_headers, editor_headers):
        admin_key = _create_key(client, auth_headers, name="Admin Private Key").json()
        r = client.get("/api-keys", headers=editor_headers)
        assert r.status_code == 200
        ids = [k["id"] for k in r.json()]
        assert admin_key["id"] not in ids

    def test_editor_cannot_revoke_admin_key(self, client, auth_headers, editor_headers):
        admin_key = _create_key(client, auth_headers, name="Admin Key to Protect").json()
        r = client.delete(f"/api-keys/{admin_key['id']}", headers=editor_headers)
        assert r.status_code == 404  # isolation: returns 404, not 403


class TestApiKeyModel:
    def test_generate_key_format(self):
        full_key, prefix, key_hash = _generate_key()
        assert full_key.startswith("ukip_")
        assert prefix == full_key[:16]
        assert len(key_hash) == 64  # SHA-256 hex
        assert key_hash == hashlib.sha256(full_key.encode()).hexdigest()

    def test_model_fields(self, db_session):
        user = models.User(username="apikey_test_u", password_hash="x", role="viewer", is_active=True)
        db_session.add(user)
        db_session.flush()

        _, prefix, key_hash = _generate_key()
        k = models.ApiKey(
            user_id=user.id,
            name="Model Test Key",
            key_prefix=prefix,
            key_hash=key_hash,
            scopes=json.dumps(["read", "write"]),
            is_active=True,
        )
        db_session.add(k)
        db_session.commit()
        db_session.refresh(k)
        assert k.id is not None
        assert k.key_prefix == prefix
        assert k.key_hash == key_hash
        assert json.loads(k.scopes) == ["read", "write"]
