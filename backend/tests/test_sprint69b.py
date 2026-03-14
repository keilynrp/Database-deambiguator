"""
Sprint 69B — AI Context Analysis tests.

Covers:
- ContextEngine.build_analysis_prompt() structure and content
- ContextEngine.build_diff_analysis_prompt() structure and content
- POST /context/sessions/{id}/insights endpoint (mocked LLM)
- POST /context/sessions/diff/insights endpoint (mocked LLM)
- ToolRegistry: analyze_domain tool registration and invocation
- Error paths: no integration, missing sessions
"""
import json
import pytest
from unittest.mock import MagicMock, patch

from backend import models
from backend.context_engine import ContextEngine
from backend.tool_registry import get_registry, _registry


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_snapshot(domain_id="default", total=100, enriched=50, critical=2, warning=3, topics=None):
    return json.dumps({
        "domain_id":    domain_id,
        "generated_at": "2026-02-01T10:00:00+00:00",
        "schema":       {"name": "Default Schema", "primary_entity": "Entity", "attributes": []},
        "entity_stats": {"total": total, "enriched": enriched, "pct_enriched": round(enriched / total * 100, 1) if total else 0.0},
        "gaps":         {"critical": critical, "warning": warning, "ok": 8},
        "top_topics":   topics or [{"concept": "AI", "count": 10}, {"concept": "ML", "count": 7}],
    })


def _create_session(db, domain_id="default", label="Test", **kwargs):
    record = models.AnalysisContext(
        domain_id=domain_id,
        label=label,
        context_snapshot=_make_snapshot(domain_id=domain_id, **kwargs),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


# ── ContextEngine prompt builders ─────────────────────────────────────────────

class TestBuildAnalysisPrompt:
    def _engine(self):
        return ContextEngine()

    def test_prompt_contains_domain_section(self):
        snap = _make_snapshot(domain_id="science")
        prompt = self._engine().build_analysis_prompt(snap)
        assert "science" in prompt

    def test_prompt_contains_entity_count(self):
        snap = _make_snapshot(total=250, enriched=100)
        prompt = self._engine().build_analysis_prompt(snap)
        assert "250" in prompt

    def test_prompt_contains_critical_gaps(self):
        snap = _make_snapshot(critical=5)
        prompt = self._engine().build_analysis_prompt(snap)
        assert "5" in prompt

    def test_prompt_contains_top_concepts(self):
        snap = _make_snapshot(topics=[{"concept": "NeuralNetworks", "count": 3}])
        prompt = self._engine().build_analysis_prompt(snap)
        assert "NeuralNetworks" in prompt

    def test_prompt_contains_analysis_instructions(self):
        snap = _make_snapshot()
        prompt = self._engine().build_analysis_prompt(snap)
        assert "recommendations" in prompt.lower()

    def test_prompt_contains_snapshot_header(self):
        snap = _make_snapshot()
        prompt = self._engine().build_analysis_prompt(snap)
        assert "DOMAIN SNAPSHOT" in prompt

    def test_empty_topics_handled(self):
        # Build a snapshot JSON with no topics directly (avoid the or-fallback in helper)
        snap = json.dumps({
            "domain_id": "default", "generated_at": "2026-01-01T00:00:00+00:00",
            "schema": {}, "entity_stats": {"total": 10, "enriched": 5, "pct_enriched": 50.0},
            "gaps": {"critical": 0, "warning": 0, "ok": 5}, "top_topics": [],
        })
        prompt = self._engine().build_analysis_prompt(snap)
        assert "none" in prompt.lower()


class TestBuildDiffAnalysisPrompt:
    def _engine(self):
        return ContextEngine()

    def _make_diff(self, total_change=20, critical_change=-1):
        return {
            "snapshot_a_domain": "science",
            "snapshot_b_domain": "science",
            "snapshot_a_generated": "2026-01-01T00:00:00",
            "snapshot_b_generated": "2026-02-01T00:00:00",
            "entity_stats": {
                "total":    {"before": 100, "after": 100 + total_change, "change": total_change},
                "enriched": {"before": 50, "after": 60, "change": 10},
                "pct_enriched": {"before": 50.0, "after": 55.0, "change": 5.0},
            },
            "gaps": {
                "critical": {"before": 3, "after": 3 + critical_change, "change": critical_change},
                "warning":  {"before": 5, "after": 4, "change": -1},
                "ok":       {"before": 8, "after": 10, "change": 2},
            },
            "top_topics": [
                {"concept": "AI", "before": 5, "after": 8, "change": 3},
                {"concept": "CV", "before": 2, "after": 0, "change": -2},
            ],
        }

    def test_diff_prompt_contains_delta_header(self):
        diff = self._make_diff()
        prompt = self._engine().build_diff_analysis_prompt(diff)
        assert "SNAPSHOT DELTA" in prompt

    def test_diff_prompt_contains_domain_names(self):
        diff = self._make_diff()
        prompt = self._engine().build_diff_analysis_prompt(diff)
        assert "science" in prompt

    def test_diff_prompt_shows_entity_change(self):
        diff = self._make_diff(total_change=20)
        prompt = self._engine().build_diff_analysis_prompt(diff)
        assert "100" in prompt
        assert "120" in prompt

    def test_diff_prompt_shows_changed_concepts(self):
        diff = self._make_diff()
        prompt = self._engine().build_diff_analysis_prompt(diff)
        assert "AI" in prompt

    def test_diff_prompt_contains_next_steps_instruction(self):
        diff = self._make_diff()
        prompt = self._engine().build_diff_analysis_prompt(diff)
        assert "next steps" in prompt.lower()

    def test_diff_prompt_no_changed_topics_shows_placeholder(self):
        diff = self._make_diff()
        diff["top_topics"] = []
        prompt = self._engine().build_diff_analysis_prompt(diff)
        # Should not raise; placeholder handled gracefully
        assert "SNAPSHOT DELTA" in prompt


# ── Session insights endpoint ──────────────────────────────────────────────────

_MOCK_ANALYSIS = "The domain has good coverage with 3 critical gaps. Recommend enriching 50 more entities."


class TestSessionInsightsEndpoint:
    def test_insights_returns_analysis(self, client, auth_headers, db_session):
        record = _create_session(db_session, label="Insights test")
        with patch("backend.routers.context._run_insights", return_value=_MOCK_ANALYSIS):
            resp = client.post(f"/context/sessions/{record.id}/insights", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["analysis"] == _MOCK_ANALYSIS
        assert data["session_id"] == record.id

    def test_insights_returns_domain_and_label(self, client, auth_headers, db_session):
        record = _create_session(db_session, domain_id="science", label="My Session")
        with patch("backend.routers.context._run_insights", return_value=_MOCK_ANALYSIS):
            resp = client.post(f"/context/sessions/{record.id}/insights", headers=auth_headers)
        data = resp.json()
        assert data["domain_id"] == "science"
        assert data["label"] == "My Session"

    def test_insights_not_found(self, client, auth_headers):
        resp = client.post("/context/sessions/999999/insights", headers=auth_headers)
        assert resp.status_code == 404

    def test_insights_requires_auth(self, client, db_session):
        record = _create_session(db_session)
        resp = client.post(f"/context/sessions/{record.id}/insights")
        assert resp.status_code in (401, 403)

    def test_insights_no_integration_returns_400(self, client, auth_headers, db_session):
        record = _create_session(db_session)
        # Don't mock _run_insights; let it hit the real path with no integration
        resp = client.post(f"/context/sessions/{record.id}/insights", headers=auth_headers)
        # No AI integration configured in test DB → 400
        assert resp.status_code == 400
        assert "No active AI provider" in resp.json()["detail"]


# ── Diff insights endpoint ─────────────────────────────────────────────────────

class TestDiffInsightsEndpoint:
    def test_diff_insights_returns_analysis(self, client, auth_headers, db_session):
        a = _create_session(db_session, label="Before", total=100)
        b = _create_session(db_session, label="After", total=120)
        with patch("backend.routers.context._run_insights", return_value=_MOCK_ANALYSIS):
            resp = client.post(f"/context/sessions/diff/insights?a={a.id}&b={b.id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["analysis"] == _MOCK_ANALYSIS
        assert data["session_a_id"] == a.id
        assert data["session_b_id"] == b.id

    def test_diff_insights_includes_diff_summary(self, client, auth_headers, db_session):
        a = _create_session(db_session, total=100)
        b = _create_session(db_session, total=150)
        with patch("backend.routers.context._run_insights", return_value=_MOCK_ANALYSIS):
            resp = client.post(f"/context/sessions/diff/insights?a={a.id}&b={b.id}", headers=auth_headers)
        data = resp.json()
        assert "diff_summary" in data
        assert data["diff_summary"]["entity_stats"]["total"]["change"] == 50

    def test_diff_insights_missing_a(self, client, auth_headers, db_session):
        b = _create_session(db_session)
        resp = client.post(f"/context/sessions/diff/insights?a=999999&b={b.id}", headers=auth_headers)
        assert resp.status_code == 404

    def test_diff_insights_missing_b(self, client, auth_headers, db_session):
        a = _create_session(db_session)
        resp = client.post(f"/context/sessions/diff/insights?a={a.id}&b=999999", headers=auth_headers)
        assert resp.status_code == 404

    def test_diff_insights_requires_auth(self, client, db_session):
        a = _create_session(db_session)
        b = _create_session(db_session)
        resp = client.post(f"/context/sessions/diff/insights?a={a.id}&b={b.id}")
        assert resp.status_code in (401, 403)


# ── ToolRegistry: analyze_domain ──────────────────────────────────────────────

class TestAnalyzeDomainTool:
    def test_analyze_domain_registered(self):
        import backend.tool_registry as tr
        tr._registry = None  # force rebuild
        registry = get_registry()
        names = [t["name"] for t in registry.list_tools()]
        assert "analyze_domain" in names

    def test_analyze_domain_has_description(self):
        import backend.tool_registry as tr
        tr._registry = None
        registry = get_registry()
        tool = next(t for t in registry.list_tools() if t["name"] == "analyze_domain")
        assert len(tool["description"]) > 20

    def test_analyze_domain_has_domain_id_param(self):
        import backend.tool_registry as tr
        tr._registry = None
        registry = get_registry()
        tool = next(t for t in registry.list_tools() if t["name"] == "analyze_domain")
        assert "domain_id" in tool["parameters"]

    def test_analyze_domain_returns_expected_keys(self, db_session):
        import backend.tool_registry as tr
        tr._registry = None
        registry = get_registry()
        result = registry.invoke("analyze_domain", {"domain_id": "default"}, db_session)
        assert "domain_id" in result
        assert "gap_summary" in result
        assert "top_concepts" in result
        assert "health_score" in result

    def test_analyze_domain_health_score_range(self, db_session):
        import backend.tool_registry as tr
        tr._registry = None
        registry = get_registry()
        result = registry.invoke("analyze_domain", {"domain_id": "default"}, db_session)
        score = result["health_score"]
        assert score is None or (0 <= score <= 100)

    def test_analyze_domain_invokable_via_endpoint(self, client, auth_headers):
        import backend.tool_registry as tr
        tr._registry = None
        resp = client.post(
            "/context/invoke",
            json={"tool": "analyze_domain", "params": {"domain_id": "default"}},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        result = resp.json()["result"]
        assert "gap_summary" in result

    def test_total_tools_count_increased(self):
        import backend.tool_registry as tr
        tr._registry = None
        registry = get_registry()
        assert len(registry.list_tools()) >= 6  # was 5, now at least 6
