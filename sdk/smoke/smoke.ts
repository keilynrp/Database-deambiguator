/**
 * TypeScript SDK smoke test — authenticate, list entities, get a typed result.
 *
 * Runs the generated `sdk/typescript` client against a live backend. Not a unit
 * test: it needs a running server and real credentials.
 *
 *   npx tsx sdk/smoke/smoke.ts
 *
 * Config (env):
 *   UKIP_SMOKE_BASE_URL   default http://localhost:8000
 *   UKIP_SMOKE_USERNAME   default superadmin
 *   UKIP_SMOKE_PASSWORD   required
 *
 * Exits nonzero on any failed assertion so CI can gate on it.
 */
import { getEntities } from "../typescript";
// The shared client singleton is not re-exported from the package index; it
// lives in client.gen. Import it directly to configure base URL + auth.
import { client } from "../typescript/client.gen";

const BASE_URL = (process.env.UKIP_SMOKE_BASE_URL ?? "http://localhost:8000").replace(/\/+$/, "");
const USERNAME = process.env.UKIP_SMOKE_USERNAME ?? "superadmin";
const PASSWORD = process.env.UKIP_SMOKE_PASSWORD;

function fail(message: string): never {
  console.error(`[ts-smoke] FAIL: ${message}`);
  process.exit(1);
}

async function login(): Promise<string> {
  if (!PASSWORD) fail("UKIP_SMOKE_PASSWORD is not set");
  // /auth/token is an OAuth2 password flow: form-urlencoded, not JSON.
  const body = new URLSearchParams({ username: USERNAME, password: PASSWORD });
  const resp = await fetch(`${BASE_URL}/auth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  if (!resp.ok) fail(`login failed (status ${resp.status}): ${(await resp.text()).slice(0, 200)}`);
  const json = (await resp.json()) as { access_token?: string };
  if (!json.access_token) fail("login response has no access_token");
  console.log("[ts-smoke] authenticated");
  return json.access_token;
}

async function main(): Promise<void> {
  console.log(`[ts-smoke] target ${BASE_URL} as ${USERNAME}`);
  const token = await login();

  // 3.1: configure the client with one credential, sent as a bearer token.
  client.setConfig({
    baseUrl: BASE_URL,
    headers: { Authorization: `Bearer ${token}` },
  });

  // 3.2: list entities and get a typed result.
  const { data, error, response } = await getEntities();
  if (error !== undefined) {
    fail(`get_entities returned an error (status ${response?.status}): ${JSON.stringify(error).slice(0, 200)}`);
  }
  if (!Array.isArray(data)) {
    fail(`expected an array from getEntities, got ${typeof data}`);
  }
  console.log(`[ts-smoke] getEntities OK — typed array of ${data.length} item(s)`);
  console.log("[ts-smoke] PASS");
}

main().catch((err) => fail(err instanceof Error ? err.message : String(err)));
