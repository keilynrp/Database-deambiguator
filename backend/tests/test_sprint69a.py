"""
Sprint 69A — Memory Layer tests.

Covers:
- DB migration: notes + pinned columns on analysis_contexts
- Session CRUD: GET /sessions/{id}, PATCH /sessions/{id}
- Session diff: GET /sessions/diff?a=&b=
- ContextEngine.diff_snapshots() + build_recall_prompt() unit tests
- Memory-aware RAG: session_id field in RAGQueryPayload
"""
import json
import pytest
from unittest.mock import patch

from backend import models
from backend.context_engine import ContextEngine
from backend.schemas import AnalysisContextUpdate


# ── Fixtures ───────────────────────────────────────────────────────────────────

def _make_snapshot(domain_id="default", total=100, enriched=50, critical=2, warning=3, topics=None):
    return json.dumps({
        "domain_id":    domain_id,
        "generated_at": "2026-01-15T10:00:00+00:00",
        "schema":       {"name": "Default", "primary_entity": "Entity", "attributes": []},
        "entity_stats": {"total": total, "enriched": enriched, "pct_enriched": round(enriched / total * 100, 1) if total else 0.0},
        "gaps":         {"critical": critical, "warning": warning, "ok": 10},
        "top_topics":   topics or [{"concept": "ML", "count": 5}, {"concept": "AI", "count": 3}],
    })


def _create_session(db, domain_id="default", label="Test Session", total=100, enriched=50):
    record = models.AnalysisContext(
        domain_id=domain_id,
        label=label,
        context_snapshot=_make_snapshot(domain_id=domain_id, total=total, enriched=enriched),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


# ── DB migration ───────────────────────────────────────────────────────────────

class TestAnalysisContextMigration:
    def test_notes_column_exists(self, db_session):
        from sqlalchemy import inspect
        from backend.database import engine
        cols = [c["name"] for c in inspect(engine).get_columns("analysis_contexts")]
        assert "notes" in cols

    def test_pinned_column_exists(self, db_session):
        from sqlalchemy import inspect
        from backend.database import engine
        cols = [c["name"] for c in inspect(engine).get_columns("analysis_contexts")]
        assert "pinned" in cols


# ── Session CRUD ───────────────────────────────────────────────────────────────

class TestContextSessionCRUD:
    def test_create_session_returns_201(self, client, auth_headers):
        resp = client.post(
            "/context/sessions",
            json={"domain_id": "default", "label": "Sprint 69 test"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["domain_id"] == "default"
        assert data["label"] == "Sprint 69 test"
        assert data["pinned"] is False
        assert data["notes"] is None

    def test_get_session_returns_parsed_snapshot(self, client, auth_headers, db_session):
        record = _create_session(db_session, label="Detail test")
        resp = client.get(f"/context/sessions/{record.id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == record.id
        assert isinstance(data["context_snapshot"], dict)
        assert "entity_stats" in data["context_snapshot"]

    def test_get_session_not_found(self, client, auth_headers):
        resp = client.get("/context/sessions/999999", headers=auth_headers)
        assert resp.status_code == 404

    def test_list_sessions_includes_new_session(self, client, auth_headers, db_session):
        record = _create_session(db_session, label="List test")
        resp = client.get("/context/sessions", headers=auth_headers)
        assert resp.status_code == 200
        ids = [s["id"] for s in resp.json()]
        assert record.id in ids

    def test_patch_label(self, client, auth_headers, db_session):
        record = _create_session(db_session, label="Original")
        resp = client.patch(
            f"/context/sessions/{record.id}",
            json={"label": "Updated label"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["label"] == "Updated label"

    def test_patch_notes(self, client, auth_headers, db_session):
        record = _create_session(db_session)
        resp = client.patch(
            f"/context/sessions/{record.id}",
            json={"notes": "Important baseline snapshot"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["notes"] == "Important baseline snapshot"

    def test_patch_pinned(self, client, auth_headers, db_session):
        record = _create_session(db_session)
        assert record.pinned is False
        resp = client.patch(
            f"/context/sessions/{record.id}",
            json={"pinned": True},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["pinned"] is True

    def test_patch_partial_does_not_overwrite_other_fields(self, client, auth_headers, db_session):
        record = _create_session(db_session, label="Keep me")
        client.patch(f"/context/sessions/{record.id}", json={"pinned": True}, headers=auth_headers)
        resp = client.get(f"/context/sessions/{record.id}", headers=auth_headers)
        assert resp.json()["label"] == "Keep me"
        assert resp.json()["pinned"] is True

    def test_patch_viewer_forbidden(self, client, viewer_headers, db_session):
        record = _create_session(db_session)
        resp = client.patch(
            f"/context/sessions/{record.id}",
            json={"label": "Viewer attempt"},
            headers=viewer_headers,
        )
        assert resp.status_code in (401, 403)

    def test_patch_not_found(self, client, auth_headers):
        resp = client.patch(
            "/context/sessions/999999",
            json={"label": "ghost"},
            headers=auth_headers,
        )
        assert resp.status_code == 404


# ── Session Diff ───────────────────────────────────────────────────────────────

class TestContextSessionDiff:
    def test_diff_returns_expected_keys(self, client, auth_headers, db_session):
        a = _create_session(db_session, label="Snap A", total=100, enriched=40)
        b = _create_session(db_session, label="Snap B", total=120, enriched=60)
        resp = client.get(f"/context/sessions/diff?a={a.id}&b={b.id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "entity_stats" in data
        assert "gaps" in data
        assert "top_topics" in data

    def test_diff_entity_stats_change(self, client, auth_headers, db_session):
        a = _create_session(db_session, label="Snap A", total=100, enriched=40)
        b = _create_session(db_session, label="Snap B", total=120, enriched=60)
        data = client.get(f"/context/sessions/diff?a={a.id}&b={b.id}", headers=auth_headers).json()
        assert data["entity_stats"]["total"]["change"] == 20
        assert data["entity_stats"]["enriched"]["change"] == 20

    def test_diff_domain_labels_included(self, client, auth_headers, db_session):
        a = _create_session(db_session, domain_id="science")
        b = _create_session(db_session, domain_id="healthcare")
        data = client.get(f"/context/sessions/diff?a={a.id}&b={b.id}", headers=auth_headers).json()
        assert data["snapshot_a_domain"] == "science"
        assert data["snapshot_b_domain"] == "healthcare"

    def test_diff_missing_session_a(self, client, auth_headers, db_session):
        b = _create_session(db_session)
        resp = client.get(f"/context/sessions/diff?a=999999&b={b.id}", headers=auth_headers)
        assert resp.status_code == 404

    def test_diff_missing_session_b(self, client, auth_headers, db_session):
        a = _create_session(db_session)
        resp = client.get(f"/context/sessions/diff?a={a.id}&b=999999", headers=auth_headers)
        assert resp.status_code == 404

    def test_diff_requires_auth(self, client, db_session):
        a = _create_session(db_session)
        b = _create_session(db_session)
        resp = client.get(f"/context/sessions/diff?a={a.id}&b={b.id}")
        assert resp.status_code in (401, 403)


# ── ContextEngine unit tests ───────────────────────────────────────────────────

class TestContextEngineUnit:
    def _engine(self):
        return ContextEngine()

    def test_diff_snapshots_basic(self):
        a = _make_snapshot(total=100, enriched=50, critical=2, warning=3)
        b = _make_snapshot(total=120, enriched=70, critical=1, warning=1)
        result = self._engine().diff_snapshots(a, b)
        assert result["entity_stats"]["total"]["change"] == 20
        assert result["entity_stats"]["enriched"]["change"] == 20
        assert result["gaps"]["critical"]["change"] == -1
        assert result["gaps"]["warning"]["change"] == -2

    def test_diff_snapshots_before_after(self):
        a = _make_snapshot(total=50, enriched=10)
        b = _make_snapshot(total=50, enriched=10)
        result = self._engine().diff_snapshots(a, b)
        assert result["entity_stats"]["total"]["before"] == 50
        assert result["entity_stats"]["total"]["after"] == 50
        assert result["entity_stats"]["total"]["change"] == 0

    def test_diff_snapshots_empty(self):
        empty = json.dumps({"entity_stats": {}, "gaps": {}, "top_topics": []})
        result = self._engine().diff_snapshots(empty, empty)
        assert result["entity_stats"]["total"]["change"] == 0
        assert result["gaps"]["critical"]["change"] == 0

    def test_diff_topics_merged(self):
        a = _make_snapshot(topics=[{"concept": "ML", "count": 5}])
        b = _make_snapshot(topics=[{"concept": "ML", "count": 8}, {"concept": "NLP", "count": 3}])
        result = self._engine().diff_snapshots(a, b)
        topics = {t["concept"]: t for t in result["top_topics"]}
        assert topics["ML"]["change"] == 3
        assert topics["NLP"]["change"] == 3   # new concept: before=0, after=3

    def test_diff_topics_concept_removed(self):
        a = _make_snapshot(topics=[{"concept": "ML", "count": 5}, {"concept": "CV", "count": 2}])
        b = _make_snapshot(topics=[{"concept": "ML", "count": 5}])
        result = self._engine().diff_snapshots(a, b)
        topics = {t["concept"]: t for t in result["top_topics"]}
        assert topics["CV"]["change"] == -2   # dropped concept: after=0

    def test_build_recall_prompt_contains_section_headers(self):
        snap = _make_snapshot()
        prompt = self._engine().build_recall_prompt("My Session", snap, "What are the top topics?")
        assert "=== MEMORY CONTEXT ===" in prompt
        assert "======================" in prompt

    def test_build_recall_prompt_contains_query(self):
        snap = _make_snapshot()
        prompt = self._engine().build_recall_prompt("X", snap, "My unique query string")
        assert "My unique query string" in prompt

    def test_build_recall_prompt_contains_label(self):
        snap = _make_snapshot()
        prompt = self._engine().build_recall_prompt("Session Alpha", snap, "q")
        assert "Session Alpha" in prompt

    def test_build_recall_prompt_contains_entity_stats(self):
        snap = _make_snapshot(total=250, enriched=100)
        prompt = self._engine().build_recall_prompt("", snap, "q")
        assert "250" in prompt
        assert "100" in prompt


# ── Memory-aware RAG ───────────────────────────────────────────────────────────

class TestMemoryAwareRAG:
    def test_rag_payload_accepts_session_id(self):
        from backend.routers.ai_rag import RAGQueryPayload
        p = RAGQueryPayload(question="test", session_id=42)
        assert p.session_id == 42

    def test_rag_payload_session_id_defaults_none(self):
        from backend.routers.ai_rag import RAGQueryPayload
        p = RAGQueryPayload(question="test")
        assert p.session_id is None

    def test_rag_without_session_context_injected_false(self, client, auth_headers):
        with patch("backend.routers.ai_rag.rag_engine.query_catalog",
                   return_value={"answer": "ok", "sources": []}):
            resp = client.post(
                "/rag/query",
                json={"question": "test", "use_context": False},
                headers=auth_headers,
            )
        assert resp.status_code == 200
        assert resp.json()["context_injected"] is False
        assert resp.json()["memory_session_id"] is None

    def test_rag_with_valid_session_injects_context(self, client, auth_headers, db_session):
        record = _create_session(db_session, label="RAG memory test")
        with patch("backend.routers.ai_rag.rag_engine.query_catalog",
                   return_value={"answer": "ok", "sources": []}) as mock_q:
            resp = client.post(
                "/rag/query",
                json={"question": "What are the gaps?", "session_id": record.id},
                headers=auth_headers,
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["context_injected"] is True
        assert data["memory_session_id"] == record.id
        # Verify the extra_system_context was passed through
        call_kwargs = mock_q.call_args.kwargs
        assert call_kwargs["extra_system_context"] is not None
        assert "MEMORY CONTEXT" in call_kwargs["extra_system_context"]

    def test_rag_with_unknown_session_id_falls_back(self, client, auth_headers):
        with patch("backend.routers.ai_rag.rag_engine.query_catalog",
                   return_value={"answer": "ok", "sources": []}):
            resp = client.post(
                "/rag/query",
                json={"question": "test", "session_id": 999999},
                headers=auth_headers,
            )
        assert resp.status_code == 200
        assert resp.json()["context_injected"] is False

    def test_rag_session_id_takes_priority_over_use_context(self, client, auth_headers, db_session):
        record = _create_session(db_session)
        with patch("backend.routers.ai_rag.rag_engine.query_catalog",
                   return_value={"answer": "ok", "sources": []}) as mock_q:
            resp = client.post(
                "/rag/query",
                json={"question": "test", "session_id": record.id, "use_context": True, "domain_id": "default"},
                headers=auth_headers,
            )
        assert resp.status_code == 200
        # The injected context should come from the recalled session (has "MEMORY CONTEXT")
        call_kwargs = mock_q.call_args.kwargs
        assert "MEMORY CONTEXT" in call_kwargs["extra_system_context"]


# ── Schema validation ──────────────────────────────────────────────────────────

class TestSchemaValidation:
    def test_analysis_context_update_empty_is_valid(self):
        update = AnalysisContextUpdate()
        assert update.label is None
        assert update.notes is None
        assert update.pinned is None

    def test_analysis_context_update_partial(self):
        update = AnalysisContextUpdate(pinned=True)
        dumped = update.model_dump(exclude_unset=True)
        assert dumped == {"pinned": True}
        assert "label" not in dumped

    def test_analysis_context_response_includes_new_fields(self, client, auth_headers, db_session):
        record = _create_session(db_session)
        resp = client.get("/context/sessions", headers=auth_headers)
        session = next((s for s in resp.json() if s["id"] == record.id), None)
        assert session is not None
        assert "pinned" in session
        assert "notes" in session
