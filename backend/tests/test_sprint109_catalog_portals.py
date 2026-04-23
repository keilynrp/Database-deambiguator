import json

from backend import models
from backend.auth import create_access_token, hash_password


def test_catalog_portal_create_and_results_global_scope(client, auth_headers, db_session):
    db_session.add_all(
        [
            models.RawEntity(
                primary_label="Portal Record A",
                secondary_label="Alpha Author",
                canonical_id="10.1000/a",
                entity_type="publication",
                domain="science",
                validation_status="valid",
                enrichment_status="completed",
                enrichment_citation_count=32,
                quality_score=0.86,
                source="scientific_import",
                attributes_json=json.dumps({"journal": "Nature", "year": 2024}),
            ),
            models.RawEntity(
                primary_label="Portal Record B",
                secondary_label="Beta Author",
                canonical_id="10.1000/b",
                entity_type="publication",
                domain="science",
                validation_status="pending",
                enrichment_status="none",
                enrichment_citation_count=0,
                quality_score=0.41,
                source="demo",
                attributes_json=json.dumps({"journal": "Cell", "year": 2023}),
            ),
            models.RawEntity(
                primary_label="Out of Scope",
                entity_type="software",
                domain="default",
                validation_status="valid",
                enrichment_status="none",
                source="user",
            ),
        ]
    )
    db_session.commit()

    create_resp = client.post(
        "/catalogs",
        json={
            "title": "Science Catalog",
            "slug": "science-catalog",
            "description": "Portal for science entities",
            "domain_id": "science",
            "visibility": "private",
            "source_label": "Latest science import",
            "source_context": {"format": "wos_plaintext", "rows": 2},
            "ft_entity_type": "publication",
            "featured_facets": ["entity_type", "enrichment_status", "source"],
            "default_sort": "primary_label",
            "default_order": "asc",
        },
        headers=auth_headers,
    )
    assert create_resp.status_code == 201, create_resp.text
    portal = create_resp.json()
    assert portal["slug"] == "science-catalog"
    assert portal["domain_id"] == "science"
    assert portal["source_label"] == "Latest science import"
    assert portal["source_context"]["format"] == "wos_plaintext"

    summary_resp = client.get("/catalogs/science-catalog", headers=auth_headers)
    assert summary_resp.status_code == 200
    summary = summary_resp.json()
    assert summary["summary"]["total_records"] == 2
    assert summary["summary"]["enriched_records"] == 1

    results_resp = client.get("/catalogs/science-catalog/results", headers=auth_headers)
    assert results_resp.status_code == 200, results_resp.text
    results = results_resp.json()
    assert results["total"] == 2
    assert [item["primary_label"] for item in results["items"]] == ["Portal Record A", "Portal Record B"]
    assert "enrichment_status" in results["facets"]

    record_id = results["items"][0]["id"]
    detail_resp = client.get(f"/catalogs/science-catalog/records/{record_id}", headers=auth_headers)
    assert detail_resp.status_code == 200
    assert detail_resp.json()["primary_label"] == "Portal Record A"


def test_catalog_portal_is_scoped_to_active_organization(client, db_session):
    admin = models.User(
        username="catalog_admin",
        password_hash=hash_password("catalog-pass-123"),
        role="admin",
        is_active=True,
    )
    outsider = models.User(
        username="catalog_outsider",
        password_hash=hash_password("catalog-pass-456"),
        role="admin",
        is_active=True,
    )
    db_session.add_all([admin, outsider])
    db_session.flush()

    org_a = models.Organization(name="Org A", slug="org-a-catalog", owner_id=admin.id, is_active=True)
    org_b = models.Organization(name="Org B", slug="org-b-catalog", owner_id=outsider.id, is_active=True)
    db_session.add_all([org_a, org_b])
    db_session.flush()

    db_session.add_all(
        [
            models.OrganizationMember(org_id=org_a.id, user_id=admin.id, role="admin"),
            models.OrganizationMember(org_id=org_b.id, user_id=outsider.id, role="admin"),
        ]
    )
    admin.org_id = org_a.id
    outsider.org_id = org_b.id
    db_session.flush()

    db_session.add_all(
        [
            models.RawEntity(primary_label="Org A Record", entity_type="publication", domain="science", org_id=org_a.id),
            models.RawEntity(primary_label="Org B Record", entity_type="publication", domain="science", org_id=org_b.id),
        ]
    )
    db_session.commit()

    admin_headers = {"Authorization": f"Bearer {create_access_token(subject=admin.username, role='admin')}"}
    outsider_headers = {"Authorization": f"Bearer {create_access_token(subject=outsider.username, role='admin')}"}

    create_resp = client.post(
        "/catalogs",
        json={
            "title": "Org A Portal",
            "slug": "org-a-portal",
            "domain_id": "science",
            "visibility": "private",
            "ft_entity_type": "publication",
        },
        headers=admin_headers,
    )
    assert create_resp.status_code == 201, create_resp.text

    owner_results = client.get("/catalogs/org-a-portal/results", headers=admin_headers)
    assert owner_results.status_code == 200
    assert owner_results.json()["total"] == 1
    assert owner_results.json()["items"][0]["primary_label"] == "Org A Record"

    outsider_results = client.get("/catalogs/org-a-portal/results", headers=outsider_headers)
    assert outsider_results.status_code == 404
