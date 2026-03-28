from fastapi.testclient import TestClient


def test_enterprise_readiness_register_returns_prioritized_baseline(client: TestClient, auth_headers: dict):
    response = client.get("/ops/enterprise-readiness", headers=auth_headers)
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "baseline"
    assert body["focus_mvp"] == "research_intelligence"
    assert body["summary"]["total_gaps"] == len(body["gaps"])
    assert body["summary"]["priority_counts"]["P0"] >= 1

    priorities = [gap["priority"] for gap in body["gaps"]]
    assert priorities == sorted(priorities, key=lambda value: {"P0": 0, "P1": 1, "P2": 2}[value])


def test_enterprise_readiness_gaps_include_impact_and_recommendation(client: TestClient, auth_headers: dict):
    response = client.get("/ops/enterprise-readiness", headers=auth_headers)
    assert response.status_code == 200

    for gap in response.json()["gaps"]:
        assert gap["impact"]
        assert gap["recommendation"]
        assert gap["related_work"]


def test_enterprise_readiness_roadmap_hooks_reference_follow_up_work(client: TestClient, auth_headers: dict):
    response = client.get("/ops/enterprise-readiness", headers=auth_headers)
    assert response.status_code == 200

    hooks = response.json()["roadmap_hooks"]
    hook_ids = {hook["id"] for hook in hooks}
    assert "EPIC-012" in hook_ids
    assert "US-042" in hook_ids


def test_enterprise_readiness_requires_admin(client: TestClient, viewer_headers: dict):
    response = client.get("/ops/enterprise-readiness", headers=viewer_headers)
    assert response.status_code == 403
