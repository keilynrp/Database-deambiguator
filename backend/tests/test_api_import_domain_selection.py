"""Contract tests for the target domain of API-based scientific imports.

Background: ``/import/pubmed`` and ``/import/openalex`` write ``RawEntity.domain``
straight from the request payload, with a ``"science"`` default. Nothing
downstream re-derives the domain, so whatever the request says is final.

Two invariants are guarded here:

1. ``domain`` must be a domain that exists in the schema registry. An unknown
   value used to be accepted verbatim, silently creating orphan records under a
   domain no schema, facet, or dashboard knows about.

2. The ``"science"`` default must stay put — existing clients (and the import
   UI before it grew a domain picker) omit the field entirely.
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
    def test_defaults_to_science_when_omitted(self, model):
        assert model(query="cancer").domain == "science"

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
    def test_error_names_the_available_domains(self, client, auth_headers, endpoint):
        resp = client.post(
            endpoint,
            json={"query": "cancer", "limit": 10, "domain": "nope"},
            headers=auth_headers,
        )
        assert resp.status_code == 422
        # The operator needs to know what they *could* have picked.
        assert "science" in resp.text
