"""
Sprint 84 — Demo-Readiness: Sales Deck endpoints

Tests cover:
  - GET /exports/sales-deck/data returns JSON with kpis + value_props
  - GET /exports/sales-deck returns HTML with correct Content-Type
  - HTML contains key elements (hero text, KPI data, print button)
  - Unauthenticated requests return 401
"""


class TestSalesDeckData:
    def test_returns_200(self, client, auth_headers):
        r = client.get("/exports/sales-deck/data", headers=auth_headers)
        assert r.status_code == 200

    def test_has_kpis(self, client, auth_headers):
        data = client.get("/exports/sales-deck/data", headers=auth_headers).json()
        assert "kpis" in data
        kpis = data["kpis"]
        assert "total_entities" in kpis
        assert "enrichment_pct" in kpis
        assert "avg_quality_pct" in kpis
        assert "domains_count" in kpis

    def test_has_value_props(self, client, auth_headers):
        data = client.get("/exports/sales-deck/data", headers=auth_headers).json()
        assert "value_props" in data
        assert len(data["value_props"]) >= 4
        for vp in data["value_props"]:
            assert "icon" in vp and "title" in vp and "desc" in vp

    def test_has_domain_breakdown(self, client, auth_headers):
        data = client.get("/exports/sales-deck/data", headers=auth_headers).json()
        assert "domain_breakdown" in data

    def test_unauthenticated_returns_401(self, client):
        r = client.get("/exports/sales-deck/data")
        assert r.status_code == 401


class TestSalesDeckHTML:
    def test_returns_html(self, client, auth_headers):
        r = client.get("/exports/sales-deck", headers=auth_headers)
        assert r.status_code == 200
        assert "text/html" in r.headers.get("content-type", "")

    def test_html_has_title(self, client, auth_headers):
        html = client.get("/exports/sales-deck", headers=auth_headers).text
        assert "Universal Knowledge Intelligence Platform" in html

    def test_html_has_print_button(self, client, auth_headers):
        html = client.get("/exports/sales-deck", headers=auth_headers).text
        assert "window.print()" in html

    def test_html_has_kpi_section(self, client, auth_headers):
        html = client.get("/exports/sales-deck", headers=auth_headers).text
        assert "kpi" in html.lower() or "Platform at a Glance" in html

    def test_unauthenticated_returns_401(self, client):
        r = client.get("/exports/sales-deck")
        assert r.status_code == 401

    def test_html_viewer_accessible(self, client, viewer_headers):
        r = client.get("/exports/sales-deck", headers=viewer_headers)
        assert r.status_code == 200
