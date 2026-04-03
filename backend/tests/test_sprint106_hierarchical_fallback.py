from __future__ import annotations

from unittest.mock import patch

from backend import models
from backend.authority.base import AuthorityCandidate
from backend.authority.hierarchical_fallback import apply_hierarchical_fallback


_PATCH = "backend.routers.authority._authority_resolve_all"


def _candidate(
    *,
    authority_source: str = "wikidata",
    authority_id: str = "Q42",
    canonical_label: str = "Machine Learning",
    confidence: float = 0.63,
    resolution_status: str = "ambiguous",
):
    return AuthorityCandidate(
        authority_source=authority_source,
        authority_id=authority_id,
        canonical_label=canonical_label,
        aliases=[],
        description="Broader topic",
        confidence=confidence,
        uri="https://example.org/authority",
        score_breakdown={
            "identifiers": 0.55,
            "name": confidence,
            "affiliation": 0.0,
            "coauthorship": 0.0,
            "topic": 0.0,
        },
        evidence=["hierarchy_test_candidate"],
        resolution_status=resolution_status,
        merged_sources=[],
    )


def test_apply_hierarchical_fallback_marks_partial_ancestor_match_for_concepts():
    candidates = apply_hierarchical_fallback(
        "Machine Learning for Healthcare",
        "concept",
        [_candidate()],
    )

    assert candidates[0].resolution_status == "partial_ancestor_match"
    assert candidates[0].hierarchy_distance == 1
    assert "hierarchical_fallback:wikidata" in candidates[0].evidence


def test_apply_hierarchical_fallback_skips_people():
    candidates = apply_hierarchical_fallback(
        "Gabriel Garcia Marquez",
        "person",
        [_candidate(canonical_label="Gabriel Garcia", confidence=0.66)],
    )

    assert candidates[0].resolution_status == "ambiguous"
    assert candidates[0].hierarchy_distance is None


class TestHierarchicalFallbackEndpoint:
    def test_concept_resolution_persists_partial_ancestor_match(self, client, editor_headers, db_session):
        with patch(_PATCH, return_value=[_candidate()]):
            resp = client.post("/authority/resolve", json={
                "field_name": "research_topic",
                "value": "Machine Learning for Healthcare",
                "entity_type": "concept",
            }, headers=editor_headers)

        assert resp.status_code == 201
        payload = resp.json()[0]
        assert payload["resolution_status"] == "partial_ancestor_match"
        assert payload["hierarchy_distance"] == 1
        assert "hierarchical_fallback:wikidata" in payload["evidence"]

        record = db_session.query(models.AuthorityRecord).one()
        assert record.resolution_status == "partial_ancestor_match"
        assert record.hierarchy_distance == 1

    def test_person_resolution_does_not_apply_hierarchical_fallback(self, client, editor_headers, db_session):
        with patch(_PATCH, return_value=[_candidate(canonical_label="Gabriel Garcia", confidence=0.66)]):
            resp = client.post("/authority/resolve", json={
                "field_name": "author_name",
                "value": "Gabriel Garcia Marquez",
                "entity_type": "person",
            }, headers=editor_headers)

        assert resp.status_code == 201
        payload = resp.json()[0]
        assert payload["resolution_status"] == "ambiguous"
        assert payload["hierarchy_distance"] is None
