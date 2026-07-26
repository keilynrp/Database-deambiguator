#!/usr/bin/env python3
"""Python SDK smoke test — authenticate, list entities, get a typed result.

Runs the generated `sdk/python` client against a live backend. Not a unit test:
it needs a running server and real credentials, so it lives here rather than in
backend/tests.

    pip install ./sdk/python
    UKIP_SMOKE_PASSWORD=... python sdk/smoke/smoke.py

Config (env):
    UKIP_SMOKE_BASE_URL   default http://localhost:8000
    UKIP_SMOKE_USERNAME   default superadmin
    UKIP_SMOKE_PASSWORD   required
    UKIP_SMOKE_EXPECT_ENFORCEMENT  "1" to also run the scope-403 check (3.4);
                                   the server must have API-key scopes enforced.

Exit code is nonzero on any failed assertion, so CI can gate on it.
"""

from __future__ import annotations

import os
import sys
import urllib.parse
import urllib.request

# The generated client is a standalone package; import it by its generated name.
from ukip_universal_knowledge_intelligence_platform_client import AuthenticatedClient
from ukip_universal_knowledge_intelligence_platform_client.api.entities import get_entities

BASE_URL = os.environ.get("UKIP_SMOKE_BASE_URL", "http://localhost:8000").rstrip("/")
USERNAME = os.environ.get("UKIP_SMOKE_USERNAME", "superadmin")
PASSWORD = os.environ.get("UKIP_SMOKE_PASSWORD")
EXPECT_ENFORCEMENT = os.environ.get("UKIP_SMOKE_EXPECT_ENFORCEMENT") == "1"


def fail(message: str) -> None:
    print(f"[python-smoke] FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def http_json(method: str, path: str, *, token: str | None = None, form=None, json_body=None):
    """Minimal stdlib HTTP helper — used for login and the scope-403 probe so the
    smoke does not depend on generator fidelity for those steps."""
    url = f"{BASE_URL}{path}"
    data = None
    headers = {}
    if form is not None:
        data = urllib.parse.urlencode(form).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    elif json_body is not None:
        import json as _json

        data = _json.dumps(json_body).encode()
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            import json as _json

            return resp.status, _json.loads(resp.read() or b"null")
    except urllib.error.HTTPError as exc:
        import json as _json

        body = exc.read()
        try:
            parsed = _json.loads(body or b"null")
        except ValueError:
            parsed = {"detail": body.decode(errors="replace")}
        return exc.code, parsed


def login() -> str:
    if not PASSWORD:
        fail("UKIP_SMOKE_PASSWORD is not set")
    status, body = http_json("POST", "/auth/token", form={"username": USERNAME, "password": PASSWORD})
    if status != 200 or not isinstance(body, dict) or not body.get("access_token"):
        fail(f"login failed (status {status}): {str(body)[:200]}")
    print("[python-smoke] authenticated")
    return body["access_token"]


def check_list_entities(token: str) -> None:
    """3.1 + 3.3: the client sends the credential as a bearer token and returns a
    typed result."""
    client = AuthenticatedClient(base_url=BASE_URL, token=token)
    result = get_entities.sync(client=client)
    if result is None:
        fail("get_entities returned None (request failed under the client)")
    if not isinstance(result, list):
        fail(f"expected a list from get_entities, got {type(result).__name__}")
    print(f"[python-smoke] get_entities OK — typed list of {len(result)} item(s)")


def check_scope_403(admin_token: str) -> None:
    """3.4: a read-scoped key attempting a write yields a distinguishable 403."""
    status, body = http_json(
        "POST",
        "/api-keys",
        token=admin_token,
        json_body={"name": "smoke-read-only", "scopes": ["read"]},
    )
    if status not in (200, 201) or not isinstance(body, dict):
        fail(f"could not create a read-scoped key (status {status}): {str(body)[:200]}")
    raw_key = body.get("key") or body.get("api_key") or body.get("raw_key")
    if not raw_key:
        fail(f"api-key create response has no raw key: {list(body)}")

    # Attempt a write with the read-only key: creating another API key is a
    # known-existing write route (we just used it), so there is no 405 ambiguity.
    # The key is owned by an admin, so RBAC (role) passes and only the scope
    # check can block — under enforcement this must 403 before the handler runs,
    # and the body must name the missing scope (not a role).
    status, body = http_json(
        "POST", "/api-keys", token=raw_key, json_body={"name": "smoke-write-attempt", "scopes": ["read"]}
    )
    if status != 403:
        fail(f"expected 403 for a read key writing under enforcement, got {status}: {str(body)[:200]}")
    detail = str(body.get("detail", body)).lower()
    if "scope" not in detail:
        fail(f"403 body does not name a scope (role 403?): {str(body)[:200]}")
    print("[python-smoke] scope-403 OK — read key blocked from write, body names the scope")


def main() -> None:
    # Deliberately does NOT echo USERNAME: it is half of a live credential pair,
    # and CI logs are broadly readable (CodeQL clear-text-logging).
    print(f"[python-smoke] target {BASE_URL}")
    token = login()
    check_list_entities(token)
    if EXPECT_ENFORCEMENT:
        check_scope_403(token)
    else:
        print("[python-smoke] skipping scope-403 (UKIP_SMOKE_EXPECT_ENFORCEMENT != 1)")
    print("[python-smoke] PASS")


if __name__ == "__main__":
    main()
