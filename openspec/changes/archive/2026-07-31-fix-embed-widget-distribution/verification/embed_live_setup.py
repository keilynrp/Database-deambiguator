"""Task 4.4 — seed a real widget and emit a scratch page that pastes both snippets.

The gap this closes: every earlier check exercised the headers, or the snippet
string, or a mocked config API. None pasted the emitted snippets into a page
served from a *different origin* and watched what a browser does with them —
which is the only arrangement that resembles a customer site, and the only one
where a cross-origin fetch is subject to CORS.

Runs against the docker stack (Postgres, real backend, real frontend), not a
SQLite improvisation, because the iframe snippet targets the app and the app has
to be there to render it.
"""
import io
import json
import pathlib
import sys
import urllib.error
import urllib.request
import uuid

API = "http://localhost:8000"
# Stands in for the customer's site. Deliberately absent from ALLOWED_ORIGINS:
# a real embedder never is.
CUSTOMER_ORIGIN = "http://localhost:8899"
OUT = pathlib.Path(__file__).parent


def call(method, path, body=None, token=None, origin=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method)
    if data:
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    if origin:
        req.add_header("Origin", origin)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read()
            return r.status, {k.lower(): v for k, v in r.headers.items()}, (
                json.loads(raw) if raw else None
            )
    except urllib.error.HTTPError as e:
        return e.code, {k.lower(): v for k, v in e.headers.items()}, (
            e.read() or b""
        ).decode("utf-8", "replace")[:300]


def login(user, pw):
    body = urllib.parse.urlencode({"username": user, "password": pw}).encode()
    req = urllib.request.Request(API + "/auth/token", data=body, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["access_token"]


def upload_csv(token, rows):
    """Seed through the real ingest path rather than writing rows behind it."""
    csv = "title,category\n" + "\n".join(f"{a},{b}" for a, b in rows)
    boundary = "----ukip" + uuid.uuid4().hex
    parts = []
    for name, value in (("domain", "default"), ("field_mapping", '{"title": "primary_label", "category": "secondary_label"}')):
        parts.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'
        )
    parts.append(
        f'--{boundary}\r\nContent-Disposition: form-data; name="file"; '
        f'filename="live.csv"\r\nContent-Type: text/csv\r\n\r\n{csv}\r\n'
    )
    parts.append(f"--{boundary}--\r\n")
    data = "".join(parts).encode()
    req = urllib.request.Request(API + "/upload", data=data, method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        return e.code, (e.read() or b"").decode("utf-8", "replace")[:400]


def main():
    import os

    token = login(
        os.environ.get("LIVE_ADMIN_USER", "admin"),
        os.environ["LIVE_ADMIN_PASS"],
    )
    print("[ok] authenticated")

    st, res = upload_csv(
        token,
        [(f"Live Entity {i}", "Review" if i % 2 else "Trial") for i in range(12)],
    )
    print(f"[{'ok' if st in (200, 201) else 'FAIL'}] upload -> {st} {str(res)[:160]}")

    st, _, listing = call("GET", "/entities?limit=1", token=token)
    total = (listing or {}).get("total") if isinstance(listing, dict) else None
    print(f"[ok] entities in db: {total}")

    widgets = {}
    for wtype, allowed in (("entity_stats", "*"), ("quality_score", CUSTOMER_ORIGIN)):
        st, _, w = call(
            "POST", "/widgets",
            {
                "name": f"Live {wtype}",
                "widget_type": wtype,
                "config": {},
                "allowed_origins": allowed,
            },
            token=token,
        )
        if st not in (200, 201):
            print(f"[FAIL] create {wtype}: {st} {w}")
            return 1
        tok = w.get("public_token")
        widgets[wtype] = (tok, allowed)
        print(f"[ok] widget {wtype} token={tok[:8]}… allowed_origins={allowed}")

    snippets = {}
    for wtype, (tok, _) in widgets.items():
        st, _, s = call("GET", f"/embed/{tok}/snippet")
        if st != 200:
            print(f"[FAIL] snippet {wtype}: {st} {s}")
            return 1
        snippets[wtype] = s
    print("[ok] both snippets fetched")

    print("\n--- resolved bases in the emitted snippets ---")
    s = snippets["entity_stats"]
    print("  iframe src :", s["iframe_snippet"].split('src="')[1].split('"')[0])
    print("  js fetch   :", s["js_snippet"].split("fetch('")[1].split("'")[0])

    print("\n--- CORS on /embed/{token}/data, as a customer origin sees it ---")
    for wtype, (tok, allowed) in widgets.items():
        st, hdrs, _ = call("GET", f"/embed/{tok}/data", origin=CUSTOMER_ORIGIN)
        print(
            f"  {wtype:14} allowed_origins={allowed:24} status={st}  "
            f"ACAO={hdrs.get('access-control-allow-origin')!r}"
        )
    print("  (for contrast, the app's own origin)")
    tok = widgets["entity_stats"][0]
    st, hdrs, _ = call("GET", f"/embed/{tok}/data", origin="http://localhost:3004")
    print(
        f"  {'entity_stats':14} origin=http://localhost:3004      status={st}  "
        f"ACAO={hdrs.get('access-control-allow-origin')!r}"
    )

    (OUT / "snippets.json").write_text(json.dumps(snippets, indent=2), encoding="utf-8")

    page = [
        "<!-- Served from http://localhost:8899 — a third-party site. -->",
        "<h1>Customer site</h1>",
        "<p>Both blocks below are pasted verbatim from /embed/{token}/snippet.</p>",
    ]
    for wtype in ("entity_stats", "quality_score"):
        s = snippets[wtype]
        page += [
            f"<h2>{wtype} — iframe form</h2>", s["iframe_snippet"],
            f"<h2>{wtype} — JS form</h2>", s["js_snippet"],
        ]
    (OUT / "customer_page.html").write_text("\n".join(page), encoding="utf-8")
    print("\n[ok] wrote customer_page.html")
    (OUT / "tokens.json").write_text(
        json.dumps({k: v[0] for k, v in widgets.items()}), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    import urllib.parse  # noqa: E402  (used by login)

    sys.exit(main())
