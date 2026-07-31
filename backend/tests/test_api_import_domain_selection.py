"""Contract tests for the target domain of API-based scientific imports.

Background: ``/import/pubmed`` and ``/import/openalex`` write ``RawEntity.domain``
straight from the request payload. Nothing downstream re-derives the domain and
nothing can re-file a record afterwards, so whatever the request says is final.

Two invariants are guarded here:

1. ``domain`` must be a domain that exists in the schema registry. An unknown
   value used to be accepted verbatim, silently creating orphan records under a
   domain no schema, facet, or dashboard knows about.

2. ``domain`` must be *stated*. It used to default to ``"science"``, which meant
   a caller who never thought about the field got a permanent, invisible answer
   to a question they did not know was being asked — the exact failure the field
   was introduced to end. A silent default is indistinguishable from a deliberate
   choice once the record is written, so an unstated domain is now a 422.

   This is a breaking API change, and deliberately so: the callers it breaks are
   precisely the ones that were being answered for.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.routers.api_import import OpenAlexImportRequest, PubMedImportRequest
from backend.schema_registry import registry


REQUEST_MODELS = [PubMedImportRequest, OpenAlexImportRequest]
ENDPOINTS = ["/import/pubmed", "/import/openalex"]


# ── Schema-level contract ────────────────────────────────────────────────────


class TestImportRequestDomainValidation:
    @pytest.mark.parametrize("model", REQUEST_MODELS)
    def test_omitting_domain_is_rejected_rather_than_defaulted(self, model):
        with pytest.raises(ValidationError) as exc:
            model(query="cancer")
        assert "domain" in str(exc.value)

    @pytest.mark.parametrize("model", REQUEST_MODELS)
    def test_no_domain_is_privileged_by_omission(self, model):
        """Guards against the default returning under another name.

        A 422 for the missing field is not enough on its own: re-adding
        ``default="science"`` would be caught, but ``default=None`` coerced
        downstream would not. Nothing may fill this field but the caller.
        """
        with pytest.raises(ValidationError):
            model(query="cancer", domain=None)

    @pytest.mark.parametrize("model", REQUEST_MODELS)
    def test_accepts_any_registered_domain(self, model):
        for domain_id in registry.domains:
            assert model(query="cancer", domain=domain_id).domain == domain_id

    @pytest.mark.parametrize("model", REQUEST_MODELS)
    def test_rejects_unregistered_domain(self, model):
        with pytest.raises(ValidationError) as exc:
            model(query="cancer", domain="biomedical-typo")
        assert "biomedical-typo" in str(exc.value)

    @pytest.mark.parametrize("model", REQUEST_MODELS)
    def test_rejects_empty_domain(self, model):
        with pytest.raises(ValidationError):
            model(query="cancer", domain="")


# ── Endpoint-level contract ──────────────────────────────────────────────────


class TestImportEndpointDomainValidation:
    """Validation must reject before any adapter is built, so these never
    touch the network."""

    @pytest.mark.parametrize("endpoint", ENDPOINTS)
    def test_unknown_domain_is_rejected_with_422(self, client, auth_headers, endpoint):
        resp = client.post(
            endpoint,
            json={"query": "cancer", "limit": 10, "domain": "not-a-real-domain"},
            headers=auth_headers,
        )
        assert resp.status_code == 422, resp.text
        assert "not-a-real-domain" in resp.text

    @pytest.mark.parametrize("endpoint", ENDPOINTS)
    def test_omitted_domain_is_rejected_with_422(self, client, auth_headers, endpoint):
        """The regression: this used to return 202 and file under Science."""
        resp = client.post(
            endpoint,
            json={"query": "cancer", "limit": 10},
            headers=auth_headers,
        )
        assert resp.status_code == 422, resp.text
        assert "domain" in resp.text

    @pytest.mark.parametrize("endpoint", ENDPOINTS)
    def test_error_names_the_available_domains(self, client, auth_headers, endpoint):
        resp = client.post(
            endpoint,
            json={"query": "cancer", "limit": 10, "domain": "nope"},
            headers=auth_headers,
        )
        assert resp.status_code == 422
        # The operator needs to know what they *could* have picked.
        assert "science" in resp.text
