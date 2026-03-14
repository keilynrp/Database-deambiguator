"""
Sprint 68D — API public documentation tests.

Verifies:
- /openapi.json is accessible and valid
- /docs (Swagger UI) is accessible
- /redoc is accessible
- OpenAPI spec has required metadata (version, description, tags)
- All expected tag groups are present in the spec
- swagger_ui_parameters are present in the spec
- Tag descriptions are non-empty
"""
import pytest


# ── OpenAPI JSON endpoint ──────────────────────────────────────────────────────

class TestOpenAPIEndpoint:
    def test_openapi_json_returns_200(self, client):
        resp = client.get("/openapi.json")
        assert resp.status_code == 200

    def test_openapi_json_content_type(self, client):
        resp = client.get("/openapi.json")
        assert "application/json" in resp.headers["content-type"]

    def test_openapi_has_title(self, client):
        data = client.get("/openapi.json").json()
        assert "UKIP" in data["info"]["title"]

    def test_openapi_has_version(self, client):
        data = client.get("/openapi.json").json()
        assert data["info"]["version"] == "1.0.0"

    def test_openapi_has_description(self, client):
        data = client.get("/openapi.json").json()
        assert len(data["info"]["description"]) > 50

    def test_openapi_description_contains_auth_section(self, client):
        data = client.get("/openapi.json").json()
        assert "Authentication" in data["info"]["description"]

    def test_openapi_has_contact(self, client):
        data = client.get("/openapi.json").json()
        assert "contact" in data["info"]

    def test_openapi_has_license(self, client):
        data = client.get("/openapi.json").json()
        assert "license" in data["info"]
        assert data["info"]["license"]["name"] == "MIT"


# ── Tag metadata ───────────────────────────────────────────────────────────────

EXPECTED_TAGS = [
    "auth", "users", "entities", "ingestion", "domains",
    "harmonization", "disambiguation", "authority", "analytics",
    "ai-rag", "stores", "reports", "annotations", "webhooks",
    "notifications", "scheduled-imports", "search", "entity-linker",
    "audit", "branding", "context", "artifacts", "demo",
]


class TestOpenAPITags:
    def _get_tags(self, client):
        data = client.get("/openapi.json").json()
        return {t["name"]: t for t in data.get("tags", [])}

    def test_all_expected_tags_present(self, client):
        tags = self._get_tags(client)
        for name in EXPECTED_TAGS:
            assert name in tags, f"Tag '{name}' missing from OpenAPI spec"

    def test_all_tags_have_descriptions(self, client):
        tags = self._get_tags(client)
        for name, tag in tags.items():
            assert tag.get("description"), f"Tag '{name}' has empty description"

    def test_auth_tag_exists(self, client):
        tags = self._get_tags(client)
        assert "auth" in tags

    def test_entities_tag_exists(self, client):
        tags = self._get_tags(client)
        assert "entities" in tags

    def test_analytics_tag_exists(self, client):
        tags = self._get_tags(client)
        assert "analytics" in tags

    def test_ingestion_tag_exists(self, client):
        tags = self._get_tags(client)
        assert "ingestion" in tags


# ── Swagger UI & ReDoc ─────────────────────────────────────────────────────────

class TestDocPages:
    def test_swagger_ui_accessible(self, client):
        resp = client.get("/docs")
        assert resp.status_code == 200

    def test_swagger_ui_html(self, client):
        resp = client.get("/docs")
        assert "text/html" in resp.headers["content-type"]
        assert "swagger" in resp.text.lower()

    def test_redoc_accessible(self, client):
        resp = client.get("/redoc")
        assert resp.status_code == 200

    def test_redoc_html(self, client):
        resp = client.get("/redoc")
        assert "text/html" in resp.headers["content-type"]

    def test_swagger_ui_persist_auth_parameter(self, client):
        """Swagger UI should include persistAuthorization=true."""
        resp = client.get("/docs")
        assert "persistAuthorization" in resp.text

    def test_swagger_ui_filter_parameter(self, client):
        """Swagger UI should include the filter parameter."""
        resp = client.get("/docs")
        assert "filter" in resp.text


# ── Endpoint tagging — spot-checks ────────────────────────────────────────────

class TestEndpointTags:
    def _paths(self, client):
        return client.get("/openapi.json").json().get("paths", {})

    def test_auth_token_tagged(self, client):
        paths = self._paths(client)
        assert "/auth/token" in paths
        tags = paths["/auth/token"]["post"].get("tags", [])
        assert "auth" in tags

    def test_entities_endpoint_tagged(self, client):
        paths = self._paths(client)
        assert "/entities" in paths
        tags = paths["/entities"]["get"].get("tags", [])
        assert "entities" in tags

    def test_upload_endpoint_tagged(self, client):
        paths = self._paths(client)
        assert "/upload" in paths
        tags = paths["/upload"]["post"].get("tags", [])
        assert "ingestion" in tags

    def test_dashboard_summary_tagged(self, client):
        paths = self._paths(client)
        assert "/dashboard/summary" in paths
        tags = paths["/dashboard/summary"]["get"].get("tags", [])
        assert "analytics" in tags

    def test_dashboard_compare_tagged(self, client):
        paths = self._paths(client)
        assert "/dashboard/compare" in paths
        tags = paths["/dashboard/compare"]["get"].get("tags", [])
        assert "analytics" in tags

    def test_domains_endpoint_tagged(self, client):
        paths = self._paths(client)
        assert "/domains" in paths
        tags = paths["/domains"]["get"].get("tags", [])
        assert "domains" in tags

    def test_harmonization_steps_tagged(self, client):
        paths = self._paths(client)
        assert "/harmonization/steps" in paths
        tags = paths["/harmonization/steps"]["get"].get("tags", [])
        assert "harmonization" in tags

    def test_stores_endpoint_tagged(self, client):
        paths = self._paths(client)
        assert "/stores" in paths
        tags = paths["/stores"]["get"].get("tags", [])
        assert "stores" in tags

    def test_rag_query_tagged(self, client):
        paths = self._paths(client)
        assert "/rag/query" in paths
        tags = paths["/rag/query"]["post"].get("tags", [])
        assert "ai-rag" in tags

    def test_rules_endpoint_tagged(self, client):
        paths = self._paths(client)
        assert "/rules" in paths
        tags = paths["/rules"]["get"].get("tags", [])
        assert "disambiguation" in tags
