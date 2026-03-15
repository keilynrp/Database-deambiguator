"""Sprint 88 — Additional clustering algorithms tests."""
import pytest
from backend import models
from backend.clustering.algorithms import (
    fingerprint, fingerprint_similarity,
    ngram_similarity,
    cologne_phonetic, cologne_similarity,
    metaphone, metaphone_similarity,
)
from backend.routers.deps import _build_disambig_groups


# ── Unit tests: algorithms ─────────────────────────────────────────────────────

class TestFingerprint:
    def test_sorts_tokens(self):
        assert fingerprint("Apple Inc") == fingerprint("Inc Apple")

    def test_strips_punctuation(self):
        assert fingerprint("Apple, Inc.") == fingerprint("Apple Inc")

    def test_case_insensitive(self):
        assert fingerprint("APPLE INC") == fingerprint("apple inc")

    def test_similarity_matching(self):
        assert fingerprint_similarity("Apple, Inc.", "inc apple") == 100

    def test_similarity_non_matching(self):
        assert fingerprint_similarity("Apple", "Google") == 0


class TestNgramSimilarity:
    def test_identical_strings(self):
        assert ngram_similarity("hello", "hello") == 100

    def test_completely_different(self):
        assert ngram_similarity("xyz", "abc") == 0

    def test_partial_overlap(self):
        score = ngram_similarity("colour", "color")
        assert 0 < score < 100

    def test_ocr_error_tolerance(self):
        # "smith" vs "smth" — should have meaningful overlap
        score = ngram_similarity("smith", "smth")
        assert score >= 40

    def test_short_string(self):
        # Very short strings
        score = ngram_similarity("a", "a")
        assert score == 100


class TestColognePhonetic:
    def test_mueller_variants(self):
        # Classic Cologne test: Müller ≈ Mueller ≈ Muller
        assert cologne_phonetic("Mueller") == cologne_phonetic("Muller")

    def test_empty_string(self):
        assert cologne_phonetic("") == ""

    def test_returns_string(self):
        result = cologne_phonetic("Schmidt")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_similarity_matching(self):
        assert cologne_similarity("Mueller", "Muller") == 100

    def test_similarity_different_names(self):
        # Very different names should not match
        assert cologne_similarity("Schmidt", "Johnson") == 0


class TestMetaphone:
    def test_smith_smyth(self):
        assert metaphone("Smith") == metaphone("Smyth")

    def test_returns_string(self):
        result = metaphone("Garcia")
        assert isinstance(result, str)

    def test_empty_string(self):
        assert metaphone("") == ""

    def test_similarity_matching(self):
        assert metaphone_similarity("Smith", "Smyth") == 100

    def test_similarity_different(self):
        assert metaphone_similarity("Garcia", "Thompson") == 0


# ── Integration tests: endpoint ───────────────────────────────────────────────

def _seed(db, primary_label, **kwargs):
    defaults = dict(entity_type="paper", domain="default",
                    validation_status="pending", enrichment_status="none", source="user")
    defaults.update(kwargs)
    e = models.RawEntity(primary_label=primary_label, **defaults)
    db.add(e)
    db.commit()
    db.refresh(e)
    return e


class TestDisambiguateAlgorithmParam:
    def test_default_algorithm_token_sort(self, client, auth_headers, db_session):
        _seed(db_session, "John Smith")
        _seed(db_session, "Smith John")
        res = client.get("/disambiguate/primary_label", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert "algorithm" in data
        assert data["algorithm"] == "token_sort"

    def test_fingerprint_algorithm(self, client, auth_headers, db_session):
        _seed(db_session, "Apple, Inc.")
        _seed(db_session, "inc apple")
        res = client.get("/disambiguate/primary_label?algorithm=fingerprint", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["algorithm"] == "fingerprint"
        # Groups should contain algorithm_used field
        if data["groups"]:
            assert data["groups"][0]["algorithm_used"] == "fingerprint"

    def test_ngram_algorithm(self, client, auth_headers, db_session):
        _seed(db_session, "colour")
        _seed(db_session, "color")
        res = client.get("/disambiguate/primary_label?algorithm=ngram&threshold=50", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["algorithm"] == "ngram"

    def test_phonetic_algorithm(self, client, auth_headers, db_session):
        _seed(db_session, "Mueller")
        _seed(db_session, "Muller")
        res = client.get("/disambiguate/primary_label?algorithm=phonetic", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["algorithm"] == "phonetic"

    def test_invalid_algorithm_returns_422(self, client, auth_headers, db_session):
        res = client.get("/disambiguate/primary_label?algorithm=invalid_algo", headers=auth_headers)
        assert res.status_code == 422

    def test_response_includes_algorithm_used_in_groups(self, client, auth_headers, db_session):
        _seed(db_session, "Smith John")
        _seed(db_session, "John Smith")
        res = client.get("/disambiguate/primary_label?algorithm=token_sort&threshold=70", headers=auth_headers)
        assert res.status_code == 200
        groups = res.json()["groups"]
        for g in groups:
            assert "algorithm_used" in g
