"""
Embed widget distribution contract — the part a customer copies and pastes.

Spec: openspec/changes/fix-embed-widget-distribution/specs/embed-widget-distribution/spec.md
  - "Embed snippets are usable without hand-editing"
  - "The iframe snippet targets the rendering page"
  - "The JS snippet renders presentable output"

All three defects under test here shipped in Sprint 93 with zero coverage:
the iframe pointed at a route that never existed, both snippets hardcoded
localhost, and the JS snippet rendered a raw JSON dump.
"""
from __future__ import annotations

import re

import pytest

PUBLIC_API = "https://api.ukip.example.com"
PUBLIC_APP = "https://ukip.example.com"


@pytest.fixture()
def public_urls(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("UKIP_PUBLIC_API_URL", PUBLIC_API)
    monkeypatch.setenv("FRONTEND_URL", PUBLIC_APP)


@pytest.fixture()
def widget_token(client, auth_headers) -> str:
    response = client.post(
        "/widgets",
        json={"name": "Dist Test", "widget_type": "entity_stats", "config": {}},
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["public_token"]


def _snippet(client, token: str) -> dict:
    response = client.get(f"/embed/{token}/snippet")
    assert response.status_code == 200, response.text
    return response.json()


# ── Usable without hand-editing ───────────────────────────────────────────────

class TestNoHandEditing:
    def test_snippets_carry_no_localhost(self, client, widget_token, public_urls):
        data = _snippet(client, widget_token)
        combined = data["iframe_snippet"] + data["js_snippet"]
        assert "localhost" not in combined
        assert "127.0.0.1" not in combined

    def test_js_snippet_uses_configured_api_base(
        self, client, widget_token, public_urls
    ):
        data = _snippet(client, widget_token)
        assert f"{PUBLIC_API}/embed/{widget_token}/data" in data["js_snippet"]

    def test_api_base_falls_back_to_request_origin(
        self, client, widget_token, monkeypatch
    ):
        """Unset env must yield the origin the request arrived on — 'probably
        right' — never a hardcoded dev host — 'definitely wrong'."""
        monkeypatch.delenv("UKIP_PUBLIC_API_URL", raising=False)
        data = _snippet(client, widget_token)
        assert "http://testserver/embed/" in data["js_snippet"]
        assert "localhost:8000" not in data["js_snippet"]

    def test_trailing_slashes_do_not_double(
        self, client, widget_token, monkeypatch
    ):
        monkeypatch.setenv("UKIP_PUBLIC_API_URL", PUBLIC_API + "/")
        monkeypatch.setenv("FRONTEND_URL", PUBLIC_APP + "/")
        data = _snippet(client, widget_token)
        combined = data["iframe_snippet"] + data["js_snippet"]
        assert "//embed" not in combined.replace("://", "")


# ── Iframe targets the rendering page ─────────────────────────────────────────

class TestIframeTarget:
    def test_iframe_points_at_frontend_embed_route(
        self, client, widget_token, public_urls
    ):
        data = _snippet(client, widget_token)
        assert f'src="{PUBLIC_APP}/embed/{widget_token}"' in data["iframe_snippet"]

    def test_no_frame_path_anywhere(self, client, widget_token, public_urls):
        """/embed/{token}/frame never existed; nothing may reference it."""
        data = _snippet(client, widget_token)
        assert "/frame" not in data["iframe_snippet"] + data["js_snippet"]

    def test_iframe_has_a_title_for_accessibility(
        self, client, widget_token, public_urls
    ):
        data = _snippet(client, widget_token)
        assert 'title="' in data["iframe_snippet"]


# ── JS snippet renders, not dumps ─────────────────────────────────────────────

class TestJsSnippetRendering:
    def test_no_raw_json_dump(self, client, widget_token, public_urls):
        js = _snippet(client, widget_token)["js_snippet"]
        assert "JSON.stringify" not in js
        assert "<pre>" not in js

    def test_dependency_free(self, client, widget_token, public_urls):
        """No external script/style: the snippet must work on any page as-is."""
        js = _snippet(client, widget_token)["js_snippet"]
        assert not re.search(r'<script[^>]+src\s*=', js)
        assert "<link" not in js
        assert "@import" not in js

    def test_renders_labelled_values(self, client, widget_token, public_urls):
        """The renderer must reference real payload fields, not echo the blob."""
        js = _snippet(client, widget_token)["js_snippet"]
        assert "textContent" in js or "innerText" in js


# ── Config endpoint exposes what the frontend needs ───────────────────────────

class TestConfigExposesAllowedOrigins:
    def test_config_includes_allowed_origins(self, client, auth_headers):
        """The embed page needs allowed_origins to emit its frame-ancestors
        header; the public config endpoint is where it can get them."""
        created = client.post(
            "/widgets",
            json={
                "name": "Origins Test",
                "widget_type": "entity_stats",
                "config": {},
                "allowed_origins": "https://cliente.example.com",
            },
            headers=auth_headers,
        ).json()
        response = client.get(f"/embed/{created['public_token']}/config")
        assert response.status_code == 200
        assert response.json()["allowed_origins"] == "https://cliente.example.com"


# ── CORS: the JS snippet runs on the customer's origin ────────────────────────

class TestEmbedCors:
    """A public embed endpoint must tell the browser a third party may read it.

    Spec: design decision 5. The task 4.4 live check found the JS snippet dead on
    every customer site: CORS answers from the global ALLOWED_ORIGINS, which lists
    UKIP's own app origins, so the endpoint returned 200 with no ACAO and the
    browser discarded the body. This is not a loosening — `curl` already reads
    these endpoints from anywhere, so the header grants a browser only what every
    other client has. The credential is the token in the path.
    """

    CUSTOMER = "https://cliente.example.com"
    OTHER = "https://otro-cliente.example.com"

    @pytest.fixture()
    def open_widget(self, client, auth_headers) -> str:
        created = client.post(
            "/widgets",
            json={
                "name": "Open Embed",
                "widget_type": "entity_stats",
                "config": {},
                "allowed_origins": "*",
            },
            headers=auth_headers,
        )
        assert created.status_code == 201, created.text
        return created.json()["public_token"]

    @pytest.fixture()
    def restricted_widget(self, client, auth_headers) -> str:
        created = client.post(
            "/widgets",
            json={
                "name": "Restricted Embed",
                "widget_type": "entity_stats",
                "config": {},
                "allowed_origins": self.CUSTOMER,
            },
            headers=auth_headers,
        )
        assert created.status_code == 201, created.text
        return created.json()["public_token"]

    def test_open_widget_allows_any_origin(self, client, open_widget):
        response = client.get(
            f"/embed/{open_widget}/data", headers={"Origin": self.CUSTOMER}
        )
        assert response.status_code == 200, response.text
        assert response.headers.get("access-control-allow-origin") == "*"

    def test_open_widget_needs_no_vary(self, client, open_widget):
        """A literal `*` does not vary, so it is safe (and cheaper) to cache."""
        response = client.get(
            f"/embed/{open_widget}/data", headers={"Origin": self.CUSTOMER}
        )
        assert "origin" not in (response.headers.get("vary", "").lower())

    def test_restricted_widget_reflects_its_own_origin(
        self, client, restricted_widget
    ):
        response = client.get(
            f"/embed/{restricted_widget}/data", headers={"Origin": self.CUSTOMER}
        )
        assert response.status_code == 200, response.text
        assert response.headers.get("access-control-allow-origin") == self.CUSTOMER

    def test_restricted_widget_varies_on_origin(self, client, restricted_widget):
        """Without Vary, a cache or CDN serves one customer's ACAO to another."""
        response = client.get(
            f"/embed/{restricted_widget}/data", headers={"Origin": self.CUSTOMER}
        )
        assert "origin" in response.headers.get("vary", "").lower()

    def test_a_disallowed_origin_is_still_refused(self, client, restricted_widget):
        """The existing 403 stands; CORS does not widen who may read."""
        response = client.get(
            f"/embed/{restricted_widget}/data", headers={"Origin": self.OTHER}
        )
        assert response.status_code == 403
        assert response.headers.get("access-control-allow-origin") is None

    def test_never_allows_credentials(self, client, open_widget):
        """No cookie or session is involved, and `*` with credentials is invalid."""
        response = client.get(
            f"/embed/{open_widget}/data", headers={"Origin": self.CUSTOMER}
        )
        assert response.headers.get("access-control-allow-credentials") is None

    def test_config_endpoint_carries_the_same_policy(self, client, restricted_widget):
        """The middleware fetches /config server-side, but a browser may too."""
        response = client.get(
            f"/embed/{restricted_widget}/config", headers={"Origin": self.CUSTOMER}
        )
        assert response.status_code == 200, response.text
        assert response.headers.get("access-control-allow-origin") == self.CUSTOMER

    def test_snippet_endpoint_is_not_given_cors(self, client, open_widget):
        """The snippet is for an operator to copy out of the UKIP UI, not for a
        customer page to fetch. Scope stays as narrow as the use."""
        response = client.get(
            f"/embed/{open_widget}/snippet", headers={"Origin": self.CUSTOMER}
        )
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") is None
