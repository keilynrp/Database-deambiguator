"""
Sprint 50 — Context-Aware RAG
POST /rag/query with use_context + domain_id
POST /context/invoke — topic and enrichment tools
"""
import pytest


# ── Context-aware RAG ─────────────────────────────────────────────────────────

def test_rag_query_plain_still_works(client, auth_headers):
    """Plain RAG query (no context) continues to work as before."""
    resp = client.post(
        "/rag/query",
        json={"question": "What entities are in the catalog?", "top_k": 3},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data or "error" in data
    # context_injected must be present and False when use_context not set
    assert data.get("context_injected") is False


def test_rag_query_with_context_flag(client, auth_headers):
    """use_context=True + domain_id attaches context (context_injected=True if domain valid)."""
    resp = client.post(
        "/rag/query",
        json={"question": "Summarize the data quality.", "use_context": True, "domain_id": "default"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    # With no active AI integration the RAG may return an error, but the shape is valid
    assert "context_injected" in data
    assert data["context_injected"] is True


def test_rag_query_context_invalid_domain_still_ok(client, auth_headers):
    """use_context with a missing domain falls back gracefully — no 500."""
    resp = client.post(
        "/rag/query",
        json={"question": "test", "use_context": True, "domain_id": "no_such_domain_xyz"},
        headers=auth_headers,
    )
    # Should be 200 with context_injected=False (fallback) or a valid RAG answer
    assert resp.status_code == 200


# ── Tool invocations (Sprint 49/50 cross-coverage) ───────────────────────────

def test_invoke_get_topics(client, editor_headers):
    resp = client.post(
        "/context/invoke",
        json={"tool": "get_topics", "params": {"domain_id": "default", "top_n": 5}},
        headers=editor_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["tool"] == "get_topics"
    assert isinstance(data["result"], list)


def test_invoke_get_enrichment_stats(client, editor_headers):
    resp = client.post(
        "/context/invoke",
        json={"tool": "get_enrichment_stats", "params": {"domain_id": "default"}},
        headers=editor_headers,
    )
    assert resp.status_code == 200
    result = resp.json()["result"]
    assert "total_enriched" in result
    assert "avg_citation_count" in result


def test_invoke_missing_tool_field_422(client, editor_headers):
    """Body without 'tool' key should return 422."""
    resp = client.post(
        "/context/invoke",
        json={"params": {}},
        headers=editor_headers,
    )
    assert resp.status_code == 422
