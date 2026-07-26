# SDK smoke tests

Live checks that the generated clients actually work against a running backend:
authenticate, list entities, and get a typed result. These are **not** unit
tests — they need a server and real credentials, so they live here rather than
in `backend/tests`. The `sdk-smoke` CI job runs both against an ephemeral
backend; you can also run them locally against your Docker stack.

## What they cover

| Check | Script | Task |
|---|---|---|
| Client sends the credential as a bearer token | both | 3.1 |
| TS: authenticate → list entities → typed array | `smoke.ts` | 3.2 |
| Python: authenticate → list entities → typed list | `smoke.py` | 3.3 |
| Read-scoped key + a write under enforcement → a 403 that names the scope | `smoke.py` (opt-in) | 3.4 |

## Configuration (env)

| Variable | Default | Notes |
|---|---|---|
| `UKIP_SMOKE_BASE_URL` | `http://localhost:8000` | Target backend origin. |
| `UKIP_SMOKE_USERNAME` | `superadmin` | |
| `UKIP_SMOKE_PASSWORD` | — | **Required.** |
| `UKIP_SMOKE_EXPECT_ENFORCEMENT` | unset | `1` runs the scope-403 check (3.4). The server must have `UKIP_API_KEY_SCOPES_ENFORCED=1`. |

## Running against your local Docker stack

```bash
# Python
pip install ./sdk/python
UKIP_SMOKE_PASSWORD=<admin-pass> python sdk/smoke/smoke.py

# TypeScript (no build step; tsx runs the .ts directly)
UKIP_SMOKE_PASSWORD=<admin-pass> npx tsx sdk/smoke/smoke.ts
```

The scope-403 check (3.4) needs enforcement on. The default local
`docker-compose.yml` runs with it off; start the backend with
`UKIP_API_KEY_SCOPES_ENFORCED=1` (or point the smoke at a deployment that has it)
and set `UKIP_SMOKE_EXPECT_ENFORCEMENT=1`.

Each script exits nonzero on the first failed assertion, so CI gates on it.
