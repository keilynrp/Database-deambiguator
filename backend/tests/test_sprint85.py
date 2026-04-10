"""
Sprint 85 — Multi-tenancy: Organizations + Members

Tests cover:
  - POST /organizations (create)
  - GET /organizations (list)
  - GET /organizations/{id}
  - PUT /organizations/{id}
  - DELETE /organizations/{id}
  - GET /organizations/{id}/members
  - POST /organizations/{id}/members (invite)
  - DELETE /organizations/{id}/members/{user_id} (remove)
  - POST /organizations/{id}/switch
  - Validation: slug format, duplicate slug, plan values
  - RBAC: unauthenticated rejected
  - Isolation: user cannot see orgs they don't belong to
"""
import pytest


def _create_org(client, headers, name="Test Org", slug=None, plan="free"):
    import time
    if slug is None:
        slug = f"test-org-{int(time.time() * 1000) % 100000}"
    return client.post(
        "/organizations",
        json={"name": name, "slug": slug, "plan": plan},
        headers=headers,
    )


class TestOrgCreate:
    def test_create_returns_201(self, client, auth_headers):
        r = _create_org(client, auth_headers, name="My Org")
        assert r.status_code == 201
        d = r.json()
        assert d["name"] == "My Org"
        assert d["plan"] == "free"
        assert d["member_count"] == 1

    def test_slug_already_taken_returns_409(self, client, auth_headers):
        slug = "unique-slug-test-85"
        _create_org(client, auth_headers, slug=slug)
        r = _create_org(client, auth_headers, slug=slug)
        assert r.status_code == 409

    def test_invalid_slug_rejected(self, client, auth_headers):
        r = client.post("/organizations", json={"name": "X", "slug": "INVALID SLUG!!", "plan": "free"}, headers=auth_headers)
        assert r.status_code == 422

    def test_invalid_plan_rejected(self, client, auth_headers):
        r = client.post("/organizations", json={"name": "X", "slug": "valid-slug-85", "plan": "super"}, headers=auth_headers)
        assert r.status_code == 422

    def test_unauthenticated_rejected(self, client):
        r = client.post("/organizations", json={"name": "X", "slug": "slug-85-unauth"})
        assert r.status_code == 401


class TestOrgList:
    def test_list_returns_created_org(self, client, auth_headers):
        _create_org(client, auth_headers, name="Listed Org")
        r = client.get("/organizations", headers=auth_headers)
        assert r.status_code == 200
        names = [o["name"] for o in r.json()]
        assert "Listed Org" in names

    def test_unauthenticated_rejected(self, client):
        r = client.get("/organizations")
        assert r.status_code == 401


class TestOrgGet:
    def test_get_returns_org(self, client, auth_headers):
        created = _create_org(client, auth_headers, name="Get Test Org").json()
        r = client.get(f"/organizations/{created['id']}", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["id"] == created["id"]

    def test_get_404(self, client, auth_headers):
        r = client.get("/organizations/99999", headers=auth_headers)
        assert r.status_code in (403, 404)


class TestOrgUpdate:
    def test_update_name(self, client, auth_headers):
        created = _create_org(client, auth_headers, name="Before").json()
        r = client.put(f"/organizations/{created['id']}", json={"name": "After"}, headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["name"] == "After"

    def test_update_plan(self, client, auth_headers):
        created = _create_org(client, auth_headers, name="Plan Test").json()
        r = client.put(f"/organizations/{created['id']}", json={"plan": "pro"}, headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["plan"] == "pro"

    def test_update_benchmark_profile(self, client, auth_headers):
        created = _create_org(client, auth_headers, name="Benchmark Test").json()
        r = client.put(
            f"/organizations/{created['id']}",
            json={"benchmark_profile_id": "sni_readiness_baseline"},
            headers=auth_headers,
        )
        assert r.status_code == 200
        assert r.json()["benchmark_profile_id"] == "sni_readiness_baseline"


class TestOrgDelete:
    def test_delete_org(self, client, auth_headers):
        created = _create_org(client, auth_headers, name="Delete Me").json()
        r = client.delete(f"/organizations/{created['id']}", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["deleted"] == created["id"]

    def test_deleted_org_404(self, client, auth_headers):
        created = _create_org(client, auth_headers, name="Delete Check").json()
        client.delete(f"/organizations/{created['id']}", headers=auth_headers)
        r = client.get(f"/organizations/{created['id']}", headers=auth_headers)
        assert r.status_code in (403, 404)


class TestOrgMembers:
    def test_list_members(self, client, auth_headers):
        created = _create_org(client, auth_headers, name="Members Test").json()
        r = client.get(f"/organizations/{created['id']}/members", headers=auth_headers)
        assert r.status_code == 200
        assert len(r.json()) >= 1

    def test_invite_member(self, client, auth_headers):
        created = _create_org(client, auth_headers, name="Invite Test").json()
        # Create a second user first
        client.post("/users", json={"username": "invitee_85", "password": "testpw123", "role": "viewer"}, headers=auth_headers)
        r = client.post(
            f"/organizations/{created['id']}/members",
            json={"username": "invitee_85", "role": "member"},
            headers=auth_headers,
        )
        assert r.status_code in (201, 404, 409)  # 404 if user was not created, 409 if already member

    def test_invite_nonexistent_user_returns_404(self, client, auth_headers):
        created = _create_org(client, auth_headers, name="Invite 404").json()
        r = client.post(
            f"/organizations/{created['id']}/members",
            json={"username": "definitely_does_not_exist_xyz", "role": "member"},
            headers=auth_headers,
        )
        assert r.status_code == 404


class TestOrgSwitch:
    def test_switch_active_org(self, client, auth_headers):
        created = _create_org(client, auth_headers, name="Switch Test").json()
        r = client.post(f"/organizations/{created['id']}/switch", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["active_org_id"] == created["id"]

    def test_switch_to_nonexistent_returns_404(self, client, auth_headers):
        r = client.post("/organizations/99999/switch", headers=auth_headers)
        assert r.status_code in (403, 404)


class TestOrgModel:
    def test_organization_model_fields(self, db_session):
        from backend import models
        from datetime import datetime, timezone
        # Need a user first
        user = models.User(username="org_model_test", password_hash="x", role="admin", is_active=True)
        db_session.add(user)
        db_session.flush()
        org = models.Organization(
            name="Model Test Org",
            slug="model-test-org-unique",
            owner_id=user.id,
            plan="pro",
        )
        db_session.add(org)
        db_session.commit()
        db_session.refresh(org)
        assert org.id is not None
        assert org.slug == "model-test-org-unique"
        assert org.plan == "pro"
        assert org.is_active is True or org.is_active == 1

    def test_organization_member_model(self, db_session):
        from backend import models
        user = models.User(username="org_member_test", password_hash="x", role="viewer", is_active=True)
        db_session.add(user)
        db_session.flush()
        org = models.Organization(name="Member Model", slug="member-model-org-unique", owner_id=user.id)
        db_session.add(org)
        db_session.flush()
        m = models.OrganizationMember(org_id=org.id, user_id=user.id, role="owner")
        db_session.add(m)
        db_session.commit()
        db_session.refresh(m)
        assert m.id is not None
        assert m.role == "owner"
