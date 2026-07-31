"""The audit log has to be *readable* for a rollout window to mean anything.

Two defects made the API-key scope rollout unreviewable in production:

1. The action filter upper-cased its argument, so any action not written in
   upper case — `api_key.scope_violation` among them — matched nothing.
2. `/audit-log/stats` built its daily roll-up with SQLite-only date arithmetic,
   which is a 500 on the PostgreSQL that production runs.

Both tests assert on *content*, not shape: a status code or a set of keys is
exactly what let these ship.
"""
from datetime import datetime, timedelta, timezone

from backend import models


SCOPE_VIOLATION = "api_key.scope_violation"


def _add_entry(db_session, action: str, endpoint: str = "/entities") -> models.AuditLog:
    entry = models.AuditLog(
        action=action,
        entity_type="api_key",
        endpoint=endpoint,
        method="GET",
    )
    db_session.add(entry)
    db_session.commit()
    db_session.refresh(entry)
    return entry


# ── The filter has to find what the writer wrote ─────────────────────────────

def test_filter_finds_a_lower_case_action(client, auth_headers, db_session):
    """`api_key.scope_violation` is written lower case, so it must filter that way.

    Upper-casing the argument turned the one query the rollout depends on into
    a guaranteed empty result.
    """
    _add_entry(db_session, SCOPE_VIOLATION)

    resp = client.get(f"/audit-log?action={SCOPE_VIOLATION}", headers=auth_headers)

    assert resp.status_code == 200
    items = resp.json()["items"]
    assert items, f"no rows returned for action={SCOPE_VIOLATION}"
    assert all(item["action"] == SCOPE_VIOLATION for item in items)


def test_filter_is_case_insensitive_both_ways(client, auth_headers, db_session):
    """An upper-case argument still finds an upper-case action, and vice versa.

    The existing `?action=CREATE` behaviour must survive the fix.
    """
    _add_entry(db_session, "CREATE")
    _add_entry(db_session, SCOPE_VIOLATION)

    upper = client.get("/audit-log?action=create", headers=auth_headers)
    assert upper.status_code == 200
    assert [i["action"] for i in upper.json()["items"]] == ["CREATE"]

    lower = client.get(
        f"/audit-log?action={SCOPE_VIOLATION.upper()}", headers=auth_headers
    )
    assert lower.status_code == 200
    assert [i["action"] for i in lower.json()["items"]] == [SCOPE_VIOLATION]


def test_filter_excludes_other_actions(client, auth_headers, db_session):
    """Case-insensitivity must not turn the filter into a pass-through."""
    _add_entry(db_session, SCOPE_VIOLATION)
    _add_entry(db_session, "DELETE")

    resp = client.get(f"/audit-log?action={SCOPE_VIOLATION}", headers=auth_headers)

    assert resp.status_code == 200
    actions = {item["action"] for item in resp.json()["items"]}
    assert actions == {SCOPE_VIOLATION}


# ── The stats roll-up has to run on the database production uses ─────────────

def test_stats_daily_rollup_counts_todays_entries(client, auth_headers, db_session):
    """`last_7_days` must contain today's rows — on SQLite *and* PostgreSQL.

    The previous test asserted only that the key existed, which a 200 on SQLite
    satisfied while production returned 500.
    """
    for _ in range(3):
        _add_entry(db_session, SCOPE_VIOLATION)

    resp = client.get("/audit-log/stats", headers=auth_headers)

    assert resp.status_code == 200, resp.text
    data = resp.json()

    today = datetime.now(timezone.utc).date().isoformat()
    by_day = {row["date"]: row["count"] for row in data["last_7_days"]}
    assert today in by_day, f"today ({today}) missing from {data['last_7_days']}"
    assert by_day[today] >= 3

    assert data["by_action"][SCOPE_VIOLATION] >= 3


def test_stats_rollup_excludes_entries_older_than_the_window(
    client, auth_headers, db_session
):
    """A row from 30 days ago must not appear in a 7-day roll-up.

    Guards the boundary the raw SQL expressed as `DATE('now', '-6 days')`.
    """
    old = _add_entry(db_session, SCOPE_VIOLATION)
    old.created_at = datetime.now(timezone.utc) - timedelta(days=30)
    db_session.commit()

    resp = client.get("/audit-log/stats", headers=auth_headers)

    assert resp.status_code == 200, resp.text
    stale_day = (datetime.now(timezone.utc) - timedelta(days=30)).date().isoformat()
    days = {row["date"] for row in resp.json()["last_7_days"]}
    assert stale_day not in days
