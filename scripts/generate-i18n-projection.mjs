#!/usr/bin/env node
/**
 * Project the frontend message catalog into JSON the backend can load.
 *
 *   node scripts/generate-i18n-projection.mjs           # rewrite the projection
 *   node scripts/generate-i18n-projection.mjs --check   # fail if it would change
 *
 * `frontend/app/i18n/translations.ts` is the single definition of every
 * user-facing string. It is TypeScript, so the backend cannot import it, and a
 * hand-maintained Python copy is precisely the drift this exists to prevent.
 *
 * The source is parsed with the TypeScript compiler's own AST rather than with
 * a regex. The catalog holds apostrophes (`Análisis completo →`, `l'entité`),
 * escapes and interpolation braces; a regex over quoted strings gets those
 * subtly wrong, and "subtly wrong translations" is a defect nobody notices
 * until a reader does.
 *
 * `--check` regenerates twice and compares before comparing to the committed
 * file, so the drift gate also proves the generator is deterministic. A gate
 * that flaps is a gate the team learns to ignore.
 */
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

import {
  PROJECTION_DIR as OUT_DIR,
  extractCatalogs as readSource,
  fail as failWith,
} from "./lib/i18n-catalog.mjs";

const CHECK_ONLY = process.argv.includes("--check");

/** @type {(message: string) => never} */
const fail = (message) => failWith("i18n-projection", message);

/** The AST reader is shared with the parity gate so both see one catalog. */
const extractCatalogs = () => readSource(fail);

/** Sorted keys and a trailing newline: the file has to diff cleanly. */
function render(entries) {
  const sorted = {};
  for (const key of Object.keys(entries).sort()) sorted[key] = entries[key];
  return `${JSON.stringify(sorted, null, 2)}\n`;
}

function main() {
  const catalogs = extractCatalogs();
  const languages = Object.keys(catalogs).sort();

  if (languages.length === 0) fail("the source catalog declares no languages");

  const rendered = new Map();
  for (const language of languages) {
    const once = render(catalogs[language]);
    const twice = render(extractCatalogs()[language]);
    if (once !== twice) {
      fail(`the generator is not deterministic for '${language}' — refusing to write`);
    }
    rendered.set(join(OUT_DIR, `catalog.${language}.json`), once);
  }

  if (CHECK_ONLY) {
    const stale = [];
    for (const [path, content] of rendered) {
      const current = existsSync(path) ? readFileSync(path, "utf8") : null;
      if (current !== content) stale.push(path);
    }
    if (stale.length > 0) {
      console.error("[i18n-projection] DRIFT: the committed projection is stale.");
      console.error("The frontend catalog changed without regenerating the backend copy.");
      for (const path of stale) console.error(`  - ${path}`);
      console.error("Run:  node scripts/generate-i18n-projection.mjs");
      process.exit(1);
    }
    const counts = languages.map((l) => `${l}=${Object.keys(catalogs[l]).length}`).join(" ");
    console.log(`[i18n-projection] OK — projection matches the source (${counts}).`);
    return;
  }

  mkdirSync(OUT_DIR, { recursive: true });
  for (const [path, content] of rendered) {
    writeFileSync(path, content, "utf8");
    console.log(`[i18n-projection] wrote ${path}`);
  }
}

main();
