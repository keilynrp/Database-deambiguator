from fastapi.testclient import TestClient


def test_tenant_model_returns_target_state_and_migration_waves(client: TestClient, auth_headers: dict):
    response = client.get("/ops/tenant-model", headers=auth_headers)
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "baseline"
    assert body["target_model"]["tenant_anchor"] == "Organization"
    assert len(body["migration_waves"]) == 4
    assert body["summary"]["total_resources"] == len(body["resources"])


def test_tenant_model_prioritizes_core_data_plane_first(client: TestClient, auth_headers: dict):
    response = client.get("/ops/tenant-model", headers=auth_headers)
    assert response.status_code == 200

    resources = response.json()["resources"]
    assert resources[0]["migration_wave"] == 1

    raw_entities = next(resource for resource in resources if resource["resource"] == "raw_entities")
    workflows = next(resource for resource in resources if resource["resource"] == "workflows")
    dashboards = next(resource for resource in resources if resource["resource"] == "user_dashboards")

    assert raw_entities["target_scope"] == "org_id required"
    assert workflows["migration_wave"] == 2
    assert dashboards["migration_wave"] == 3


def test_tenant_model_resources_include_rationale_and_touchpoints(client: TestClient, auth_headers: dict):
    response = client.get("/ops/tenant-model", headers=auth_headers)
    assert response.status_code == 200

    for resource in response.json()["resources"]:
        assert resource["why"]
        assert resource["touchpoints"]


def test_tenant_model_requires_admin(client: TestClient, viewer_headers: dict):
    response = client.get("/ops/tenant-model", headers=viewer_headers)
    assert response.status_code == 403
