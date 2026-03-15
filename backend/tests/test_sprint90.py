"""
Sprint 90 — Web Scraper Enrichment tests.

14 tests:
  - CRUD (create, list, get, update, delete)
  - Test endpoint with mock httpx
  - Run endpoint with mock httpx
  - Worker integration (enrich_with_web_scrapers)
  - Circuit breaker activates on repeated failures
  - Rate limit respected between requests
"""
from __future__ import annotations

import json
import time
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend import models
from backend.adapters.web_scraper import (
    ScrapeError,
    WebScraperAdapter,
    _url_encode,
    adapter_from_config,
)
from backend.circuit_breaker import CircuitBreaker, CircuitOpenError


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture()
def scraper_payload():
    return {
        "name": "Test Scraper",
        "url_template": "https://example.com/search?q={primary_label}",
        "selector_type": "css",
        "selector": "p.description",
        "field_map": {"0": "enrichment_concepts"},
        "rate_limit_secs": 0.1,
        "is_active": True,
    }


@pytest.fixture()
def created_scraper(client: TestClient, auth_headers: dict, scraper_payload: dict):
    resp = client.post("/scrapers", json=scraper_payload, headers=auth_headers)
    assert resp.status_code == 201
    yield resp.json()
    # Cleanup
    client.delete(f"/scrapers/{resp.json()['id']}", headers=auth_headers)


# ── Unit: WebScraperAdapter ───────────────────────────────────────────────────

class TestWebScraperAdapter:
    def _make_adapter(self, **kwargs):
        defaults = dict(
            name="test",
            url_template="https://example.com/{primary_label}",
            selector_type="css",
            selector="p",
            field_map={"0": "enrichment_concepts"},
            rate_limit_secs=0.0,
        )
        defaults.update(kwargs)
        return WebScraperAdapter(**defaults)

    def _mock_response(self, html: str, status: int = 200):
        mock = MagicMock()
        mock.status_code = status
        mock.text = html
        return mock

    def test_url_encode(self):
        assert _url_encode("Python (language)") == "Python%20%28language%29"

    def test_scrape_css_success(self):
        adapter = self._make_adapter()
        html = "<html><body><p>Concept A</p><p>Concept B</p></body></html>"
        with patch("httpx.get", return_value=self._mock_response(html)):
            result = adapter.scrape("python")
        assert result == {"enrichment_concepts": "Concept A"}

    def test_scrape_http_error_raises(self):
        adapter = self._make_adapter()
        with patch("httpx.get", return_value=self._mock_response("", status=404)):
            with pytest.raises(ScrapeError, match="HTTP 404"):
                adapter.scrape("python")

    def test_scrape_network_error_raises(self):
        adapter = self._make_adapter()
        with patch("httpx.get", side_effect=Exception("connection refused")):
            with pytest.raises(ScrapeError, match="Network error"):
                adapter.scrape("python")

    def test_empty_selector_returns_empty_dict(self):
        adapter = self._make_adapter(field_map={})
        html = "<html><body><p>Some text</p></body></html>"
        with patch("httpx.get", return_value=self._mock_response(html)):
            result = adapter.scrape("python")
        # With empty field_map, texts are joined into enrichment_concepts
        assert "enrichment_concepts" in result

    def test_xpath_selector(self):
        adapter = self._make_adapter(selector_type="xpath", selector="//p/text()")
        html = "<html><body><p>XPath Result</p></body></html>"
        with patch("httpx.get", return_value=self._mock_response(html)):
            result = adapter.scrape("test")
        assert "enrichment_concepts" in result

    def test_adapter_from_config(self):
        cfg = MagicMock()
        cfg.name = "cfg_scraper"
        cfg.url_template = "https://example.com/{primary_label}"
        cfg.selector_type = "css"
        cfg.selector = "p"
        cfg.field_map = json.dumps({"0": "enrichment_concepts"})
        cfg.rate_limit_secs = 1.0
        adapter = adapter_from_config(cfg)
        assert adapter.name == "cfg_scraper"
        assert adapter.field_map == {"0": "enrichment_concepts"}


# ── Unit: Circuit breaker with scraper ───────────────────────────────────────

class TestScraperCircuitBreaker:
    def test_circuit_opens_after_failures(self):
        cb = CircuitBreaker(name="test_s90", failure_threshold=2, recovery_timeout=300)
        scraper = WebScraperAdapter(
            name="failing",
            url_template="https://example.com/{primary_label}",
            selector_type="css",
            selector="p",
            field_map={},
            rate_limit_secs=0.0,
        )

        with patch("httpx.get", side_effect=Exception("network down")):
            with pytest.raises(ScrapeError):
                cb.call(scraper.scrape, "test1")
            with pytest.raises(ScrapeError):
                cb.call(scraper.scrape, "test2")
            # Circuit should now be open
            with pytest.raises(CircuitOpenError):
                cb.call(scraper.scrape, "test3")


# ── Integration: CRUD endpoints ───────────────────────────────────────────────

class TestScraperCRUD:
    def test_create_scraper(self, client: TestClient, auth_headers: dict, scraper_payload: dict):
        resp = client.post("/scrapers", json=scraper_payload, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == scraper_payload["name"]
        assert data["selector_type"] == "css"
        assert data["field_map"] == {"0": "enrichment_concepts"}
        client.delete(f"/scrapers/{data['id']}", headers=auth_headers)

    def test_list_scrapers(self, client: TestClient, auth_headers: dict, created_scraper: dict):
        resp = client.get("/scrapers", headers=auth_headers)
        assert resp.status_code == 200
        ids = [s["id"] for s in resp.json()]
        assert created_scraper["id"] in ids

    def test_get_scraper(self, client: TestClient, auth_headers: dict, created_scraper: dict):
        resp = client.get(f"/scrapers/{created_scraper['id']}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == created_scraper["name"]

    def test_get_scraper_not_found(self, client: TestClient, auth_headers: dict):
        resp = client.get("/scrapers/99999", headers=auth_headers)
        assert resp.status_code == 404

    def test_update_scraper(self, client: TestClient, auth_headers: dict, created_scraper: dict):
        resp = client.put(
            f"/scrapers/{created_scraper['id']}",
            json={"name": "Updated Scraper", "is_active": False},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated Scraper"
        assert resp.json()["is_active"] is False

    def test_delete_scraper(self, client: TestClient, auth_headers: dict, scraper_payload: dict):
        create = client.post("/scrapers", json=scraper_payload, headers=auth_headers)
        scraper_id = create.json()["id"]
        resp = client.delete(f"/scrapers/{scraper_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["deleted"] == scraper_id
        # Confirm gone
        assert client.get(f"/scrapers/{scraper_id}", headers=auth_headers).status_code == 404


# ── Integration: Test endpoint ────────────────────────────────────────────────

class TestScraperTestEndpoint:
    def test_test_endpoint_success(self, client: TestClient, auth_headers: dict, created_scraper: dict):
        html = "<html><body><p class=\"description\">Scraped Concept</p></body></html>"
        mock_resp = MagicMock(status_code=200, text=html)
        with patch("httpx.get", return_value=mock_resp):
            resp = client.post(
                f"/scrapers/{created_scraper['id']}/test",
                json={"primary_label": "Python"},
                headers=auth_headers,
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert "enrichment_concepts" in data["fields"]

    def test_test_endpoint_scrape_error(self, client: TestClient, auth_headers: dict, created_scraper: dict):
        with patch("httpx.get", side_effect=Exception("timeout")):
            resp = client.post(
                f"/scrapers/{created_scraper['id']}/test",
                json={"primary_label": "Python"},
                headers=auth_headers,
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is False
        assert "error" in data


# ── Integration: Worker function ──────────────────────────────────────────────

class TestEnrichWithWebScrapers:
    def test_worker_enriches_entity(self, db_session):
        import json as _json
        from backend.enrichment_worker import enrich_with_web_scrapers

        # Create scraper config directly in the test DB session
        cfg = models.WebScraperConfig(
            name="Worker Test Scraper",
            url_template="https://example.com/{primary_label}",
            selector_type="css",
            selector="p",
            field_map=_json.dumps({"0": "enrichment_concepts"}),
            rate_limit_secs=0.0,
            is_active=True,
        )
        db_session.add(cfg)

        entity = models.RawEntity(
            primary_label="Python programming",
            enrichment_status="failed",
            domain="default",
        )
        db_session.add(entity)
        db_session.commit()
        db_session.refresh(entity)

        html = "<html><body><p>High-level language</p></body></html>"
        mock_resp = MagicMock(status_code=200, text=html)
        with patch("httpx.get", return_value=mock_resp):
            result = enrich_with_web_scrapers(db_session, entity)

        assert result is True
        assert entity.enrichment_status == "completed"
        assert entity.enrichment_source == "Worker Test Scraper"
