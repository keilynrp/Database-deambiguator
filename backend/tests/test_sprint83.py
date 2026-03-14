"""
Sprint 83 — Performance: analytics TTL cache + virtual scroll (backend tests only)

Tests cover:
  - Cache stores result and returns same object on second call
  - Cache invalidation clears all entries
  - POST /analytics/cache/invalidate returns 200 (admin+)
  - RBAC: viewer cannot invalidate cache
  - 200-row entities endpoint returns up to 200 rows
"""
import time
import pytest

from backend.routers.analytics import _SimpleCache, _analytics_cache, _dashboard_cache, invalidate_analytics_for_domain


class TestSimpleCache:
    def test_miss_returns_none(self):
        c = _SimpleCache(ttl_seconds=60)
        assert c.get("missing_key") is None

    def test_set_and_get(self):
        c = _SimpleCache(ttl_seconds=60)
        c.set("k", {"data": 42})
        assert c.get("k") == {"data": 42}

    def test_ttl_expiry(self):
        c = _SimpleCache(ttl_seconds=0)  # expire immediately
        c.set("k", "value")
        time.sleep(0.01)
        assert c.get("k") is None  # expired

    def test_invalidate_all(self):
        c = _SimpleCache(ttl_seconds=60)
        c.set("a", 1)
        c.set("b", 2)
        n = c.invalidate()
        assert n == 2
        assert c.get("a") is None

    def test_invalidate_prefix(self):
        c = _SimpleCache(ttl_seconds=60)
        c.set("topics_default_30", 1)
        c.set("topics_science_30", 2)
        c.set("dashboard_default", 3)
        n = c.invalidate("topics_")
        assert n == 2
        assert c.get("dashboard_default") == 3

    def test_thread_safety_multiple_sets(self):
        import threading
        c = _SimpleCache(ttl_seconds=60)
        errors = []

        def worker(i):
            try:
                c.set(f"key_{i}", i)
                _ = c.get(f"key_{i}")
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert not errors


class TestInvalidationEndpoint:
    def test_invalidate_requires_admin(self, client, auth_headers):
        r = client.post("/analytics/cache/invalidate", headers=auth_headers)
        assert r.status_code == 200
        assert "invalidated" in r.json()

    def test_invalidate_viewer_forbidden(self, client, viewer_headers):
        r = client.post("/analytics/cache/invalidate", headers=viewer_headers)
        assert r.status_code == 403

    def test_invalidate_returns_count(self, client, auth_headers):
        # Seed cache with fake entries
        _analytics_cache.set("topics_default_30", {"topics": []})
        _dashboard_cache.set("dashboard_default", {"kpis": {}})
        r = client.post("/analytics/cache/invalidate", headers=auth_headers)
        data = r.json()
        assert data["invalidated"] >= 2

    def test_invalidate_with_prefix(self, client, auth_headers):
        _analytics_cache.set("topics_mydom_30", 1)
        _analytics_cache.set("correlation_mydom_20", 2)
        r = client.post("/analytics/cache/invalidate?prefix=topics_mydom", headers=auth_headers)
        assert r.status_code == 200

    def test_invalidate_analytics_for_domain_helper(self):
        _analytics_cache.set("topics_test_30", "cached")
        _dashboard_cache.set("dashboard_test", "cached_dash")
        invalidate_analytics_for_domain("test")
        assert _analytics_cache.get("topics_test_30") is None
        assert _dashboard_cache.get("dashboard_test") is None


class TestEntities200Rows:
    def test_entities_accepts_limit_200(self, client, auth_headers):
        r = client.get("/entities?limit=200", headers=auth_headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)
