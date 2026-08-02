#!/usr/bin/env python3
"""Review the warn-mode observation window for API key scope enforcement.

Task 6.2 of the `enforce-api-key-scopes` change: with
`UKIP_API_KEY_SCOPES_ENFORCED=0`, every request that *would* have been refused
is recorded as an `api_key.scope_violation` audit event instead of being
blocked. Before flipping the flag (task 6.4) someone has to look at what the
window actually caught, because flipping it turns each of those into a live
403 for a real integrator.

Run it against production:

    python scripts/check_api_key_scope_violations.py --base-url https://api.ukip.inbounduxd.com

The password is read from a hidden prompt, or from ADMIN_PASSWORD if set. The
access token is held in memory for the duration of the run and never printed,
so the output of this script is safe to paste into a ticket or a chat.
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone

ACTION = "api_key.scope_violation"
PAGE_SIZE = 200  # the endpoint's documented maximum


def _raw_request(
    url: str,
    *,
    method: str = "GET",
    data: bytes | None = None,
    headers: dict | None = None,
    timeout: int = 30,
) -> tuple[int, str]:
    """Like `_request`, but returns the status instead of raising on 4xx/5xx.

    The probe *expects* error statuses — a 404 is the successful outcome of the
    write attempt — so it cannot use the raising variant.
    """
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            return resp.status, resp.read().decode(errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode(errors="replace")
    except urllib.error.URLError as exc:
        raise SystemExit(f"Could not reach {url}: {exc.reason}") from exc


def _request(url: str, *, data: bytes | None = None, headers: dict | None = None, timeout: int = 30):
    req = urllib.request.Request(url, data=data, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 — operator-supplied URL
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")[:400]
        raise SystemExit(f"HTTP {exc.code} from {url}\n{body}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Could not reach {url}: {exc.reason}") from exc


def _login(base_url: str, username: str, password: str) -> str:
    payload = urllib.parse.urlencode({"username": username, "password": password}).encode()
    data = _request(
        f"{base_url}/auth/token",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = data.get("access_token")
    if not token:
        raise SystemExit("Login succeeded but returned no access_token.")
    return token


def _fetch_violations(base_url: str, token: str) -> list[dict]:
    headers = {"Authorization": f"Bearer {token}"}
    items: list[dict] = []
    skip = 0
    while True:
        query = urllib.parse.urlencode({"action": ACTION, "skip": skip, "limit": PAGE_SIZE})
        page = _request(f"{base_url}/audit-log?{query}", headers=headers)
        batch = page.get("items", [])
        items.extend(batch)
        total = page.get("total", len(items))
        skip += PAGE_SIZE
        if len(items) >= total or not batch:
            return items


def _fetch_own_keys(base_url: str, token: str) -> list[dict]:
    """The authenticating user's API keys.

    `GET /api-keys` filters by `user_id == current_user.id`, and no admin-wide
    listing endpoint exists anywhere in the app, so this is a partial view even
    for a super_admin. It is reported as such rather than dressed up as a
    global answer.
    """
    return _request(f"{base_url}/api-keys", headers={"Authorization": f"Bearer {token}"})


def _report_traffic(keys: list[dict]) -> None:
    print(f"\n{'-' * 68}")
    print("  Was there any API-key traffic to observe? (partial view)")
    print(f"{'-' * 68}\n")

    if not keys:
        print("  The authenticating user owns no API keys at all.\n")
    else:
        print(f"  Keys owned by the authenticating user: {len(keys)}\n")
        for k in keys:
            scopes = ", ".join(k.get("scopes") or []) or "(none)"
            used = k.get("last_used_at") or "NEVER USED"
            active = "active" if k.get("is_active") else "inactive"
            print(f"    {str(k.get('key_prefix')):<20} {active:<9} last used: {used}")
            print(f"    {'':<20} scopes: {scopes}")
        never = [k for k in keys if not k.get("last_used_at")]
        if never:
            print(f"\n  {len(never)} of these have never been used.")

    print("\n  LIMITATION: `GET /api-keys` returns only the authenticating user's")
    print("  keys, and the app exposes no admin-wide listing. Keys belonging to")
    print("  other users are invisible here, so this cannot confirm on its own")
    print("  that the observation window saw real traffic. For the global answer,")
    print("  run this against the production database:\n")
    print("    SELECT COUNT(*) AS keys_total,")
    print("           COUNT(last_used_at) AS ever_used,")
    print("           COUNT(*) FILTER (WHERE last_used_at > NOW() - INTERVAL '7 days')")
    print("             AS used_last_7d,")
    print("           MAX(last_used_at) AS most_recent_use")
    print("    FROM api_keys WHERE is_active;\n")


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


#: Probe keys are named with this prefix so their own violations can be told
#: apart from an integrator's. Without that, `--probe` pollutes the very
#: measurement this script exists to make: the synthetic violation it creates
#: is counted as a real one, and the operator is advised to contact the owner
#: of a key the script made up.
_PROBE_KEY_NAME_PREFIX = "scope-probe "


def _enforcement_enabled(base_url: str) -> bool | None:
    """Whether the deployment is enforcing scopes. None when unreadable.

    Read so the verdict below can describe the deployment as it is. A verdict
    hardcoded for warn mode tells an operator not to flip a flag that is
    already flipped, which is worse than saying nothing.
    """
    try:
        health = _request(f"{base_url}/health")
        return bool(health.get("features", {}).get("api_key_scopes_enforced"))
    except SystemExit:
        return None


def _probe_key_prefixes(keys: list[dict]) -> set[str]:
    return {
        k["key_prefix"]
        for k in keys
        if (k.get("name") or "").startswith(_PROBE_KEY_NAME_PREFIX) and k.get("key_prefix")
    }


def _report(items: list[dict], probe_prefixes: set[str] = frozenset(), enforced: bool | None = None) -> int:
    # ASCII only from here down: this output is meant to be pasted into a
    # ticket, and a Windows console will mangle anything else.
    mode = {True: "ENFORCING", False: "warn mode", None: "mode unknown"}[enforced]
    print(f"\n{'=' * 68}")
    print(f"  api_key.scope_violation - observation window ({mode})")
    print(f"{'=' * 68}\n")

    probe_items = [i for i in items if (i.get("details") or {}).get("key_prefix") in probe_prefixes]
    items = [i for i in items if i not in probe_items]
    if probe_items:
        print(f"  Ignoring {len(probe_items)} violation(s) from this script's own")
        print("  --probe keys. They are synthetic and say nothing about integrators.\n")

    if not items:
        print("  No violations recorded.\n")
        print("  Read this carefully before treating it as a green light: an empty")
        print("  result means either that no key was ever used outside its scopes,")
        print("  or that no scoped key was used at all. Those are very different")
        print("  situations and this query cannot tell them apart.")
        if enforced:
            print("\n  Enforcement is already ON, so this says no caller has been")
            print("  refused - not that none would be. A key that is never used")
            print("  cannot violate anything.\n")
        else:
            print("  Confirm there was real API-key traffic in the window before")
            print("  flipping the flag.\n")
        return 0

    timestamps = sorted(t for t in (_parse_ts(i.get("created_at")) for i in items) if t)
    by_prefix: Counter = Counter()
    by_scope: Counter = Counter()
    by_endpoint: Counter = Counter()
    granted_by_prefix: dict[str, set] = {}
    enforced_seen = set()

    for item in items:
        details = item.get("details") or {}
        prefix = details.get("key_prefix") or f"key#{item.get('resource_id')}"
        by_prefix[prefix] += 1
        by_scope[details.get("required") or "?"] += 1
        by_endpoint[f"{details.get('method') or item.get('method') or '?'} "
                    f"{details.get('path') or item.get('endpoint') or '?'}"] += 1
        granted_by_prefix.setdefault(prefix, set()).update(details.get("granted") or [])
        enforced_seen.add(bool(details.get("enforced")))

    print(f"  Total violations : {len(items)}")
    if timestamps:
        span_days = (timestamps[-1] - timestamps[0]).days
        print(f"  First seen       : {timestamps[0].isoformat()}")
        print(f"  Last seen        : {timestamps[-1].isoformat()}")
        print(f"  Span             : {span_days} day(s)")
    print(f"  Distinct keys    : {len(by_prefix)}")
    if True in enforced_seen:
        print("\n  !! Some events have enforced=true - the flag is already ON for")
        print("     those, and they were real 403s, not warnings.")

    heading = ("Keys currently BEING REFUSED (403)" if enforced
               else "Keys that would start getting 403s")
    print(f"\n  {heading} - contact these owners:")
    for prefix, count in by_prefix.most_common():
        granted = ", ".join(sorted(granted_by_prefix.get(prefix, set()))) or "(none)"
        print(f"    {prefix:<20} {count:>5} event(s)   granted: {granted}")

    print("\n  Scopes the keys were missing:")
    for scope, count in by_scope.most_common():
        print(f"    {scope:<28} {count:>5}")

    print("\n  Endpoints (top 15):")
    for endpoint, count in by_endpoint.most_common(15):
        print(f"    {endpoint:<50} {count:>5}")

    if enforced:
        print("\n  Verdict: enforcement is ALREADY ON, so these are live 403s a real")
        print("  caller is getting right now, not a forecast. Widen the key's scopes")
        print("  or fix the integration - or set UKIP_API_KEY_SCOPES_ENFORCED=0 to")
        print("  return to warn mode while you do.\n")
    elif enforced is False:
        print("\n  Verdict: do NOT flip UKIP_API_KEY_SCOPES_ENFORCED to 1 until every")
        print("  key above has had its scopes widened or its caller fixed. Flipping")
        print("  now turns each of these into a live 403 for a real integrator.\n")
    else:
        print("\n  Verdict withheld: could not read /health, so the enforcement state")
        print("  is unknown and any recommendation here would be a guess.\n")
    return 1


def _probe(base_url: str, token: str) -> int:
    """Positive control: prove the violation path actually records in production.

    An empty observation window has three possible causes, and the audit query
    alone cannot separate them:

      1. no key was ever used outside its scopes  <- what we hope
      2. no key was used at all
      3. the recording path is broken and would never write anything

    This creates a read-scoped key, makes one write attempt with it, and looks
    for the resulting audit event. If the event appears, causes 2 and 3 are
    both ruled out and the window means something. If it does not, we have
    found a bug that would have made enforcement fail silently.

    The write attempt targets a deliberately nonexistent entity id. In warn
    mode the request *proceeds* after the violation is recorded, so the target
    has to be one where proceeding changes nothing: DELETE on an id that does
    not exist is a 404 and mutates no row.
    """
    admin = {"Authorization": f"Bearer {token}"}
    probe_name = f"scope-probe {datetime.now(timezone.utc).isoformat(timespec='seconds')}"
    key_id = None

    print(f"\n{'=' * 68}")
    print("  PROBE - positive control for the violation recording path")
    print(f"{'=' * 68}\n")

    try:
        created = _request(
            f"{base_url}/api-keys",
            data=json.dumps({
                "name": probe_name,
                "scopes": ["read"],
                # Belt and braces: if the revoke below fails, the key dies on
                # its own rather than living in production indefinitely.
                "expires_days": 1,
            }).encode(),
            headers={**admin, "Content-Type": "application/json"},
        )
        key_id = created.get("id")
        raw_key = created.get("key")
        prefix = created.get("key_prefix")
        if not raw_key:
            raise SystemExit("Key creation returned no key material; cannot probe.")
        print(f"  1. Created read-scoped key {prefix} (id={key_id}, expires in 1 day)")

        status, body = _raw_request(
            f"{base_url}/entities/999999999",
            method="DELETE",
            headers={"Authorization": f"Bearer {raw_key}"},
        )
        print(f"  2. DELETE /entities/999999999 with that key -> HTTP {status}")
        if status == 403:
            print("     403 means enforcement is already ON, not warn mode.")
        elif status == 404:
            print("     404 is the expected warn-mode result: the scope check")
            print("     recorded and allowed, then the entity was not found.")
        else:
            print(f"     Unexpected status. Body: {body[:200]}")

        violations = _fetch_violations(base_url, token)
        mine = [
            v for v in violations
            if (v.get("details") or {}).get("key_prefix") == prefix
        ]
        print(f"  3. Audit events for {prefix}: {len(mine)}")

        if mine:
            detail = mine[0].get("details") or {}
            print(f"     required={detail.get('required')} "
                  f"granted={detail.get('granted')} enforced={detail.get('enforced')}")
            print("\n  RESULT: the recording path works in production. An empty")
            print("  observation window from here on means 'no violations', not")
            print("  'nothing was ever recorded'.\n")
            return 0

        print("\n  RESULT: NO audit event was recorded for a request that should")
        print("  have produced one. This is a bug: with enforcement on, the")
        print("  403s would fire with no audit trail behind them. Do not flip")
        print("  UKIP_API_KEY_SCOPES_ENFORCED until this is understood.\n")
        return 1
    finally:
        if key_id is not None:
            status, _ = _raw_request(
                f"{base_url}/api-keys/{key_id}", method="DELETE", headers=admin
            )
            ok = "revoked" if status < 400 else f"REVOKE FAILED (HTTP {status})"
            print(f"  4. Probe key id={key_id}: {ok}")
            if status >= 400:
                print("     Revoke it by hand. It expires in 1 day regardless.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True, help="e.g. https://api.ukip.inbounduxd.com")
    parser.add_argument("--username", default=os.environ.get("ADMIN_USERNAME", "admin"))
    parser.add_argument(
        "--probe",
        action="store_true",
        help="Create a throwaway read-scoped key, make one write attempt with it, "
             "confirm the violation was recorded, then revoke it. Writes to "
             "production: it creates and deletes a real API key.",
    )
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    password = os.environ.get("ADMIN_PASSWORD") or getpass.getpass(
        f"Password for {args.username} at {base_url}: "
    )

    token = _login(base_url, args.username, password)
    del password
    enforced = _enforcement_enabled(base_url)
    items = _fetch_violations(base_url, token)
    keys = _fetch_own_keys(base_url, token)
    exit_code = _report(items, _probe_key_prefixes(keys), enforced)
    _report_traffic(keys)
    if args.probe:
        exit_code = _probe(base_url, token) or exit_code
    del token
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
