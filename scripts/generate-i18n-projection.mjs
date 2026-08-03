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
import { createRequire } from "node:module";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const SOURCE = join(ROOT, "frontend", "app", "i18n", "translations.ts");
const OUT_DIR = join(ROOT, "backend", "i18n");

const CHECK_ONLY = process.argv.includes("--check");

// TypeScript is a frontend dependency, not a repo-root one.
const require = createRequire(join(ROOT, "frontend", "package.json"));
const ts = require("typescript");

function fail(message) {
  console.error(`[i18n-projection] ${message}`);
  process.exit(1);
}

/** Read `export const translations = { en: {...}, es: {...} }` off the AST. */
function extractCatalogs() {
  if (!existsSync(SOURCE)) fail(`source catalog not found at ${SOURCE}`);

  const source = ts.createSourceFile(
    SOURCE,
    readFileSync(SOURCE, "utf8"),
    ts.ScriptTarget.Latest,
    /* setParentNodes */ true,
  );

  let translations = null;
  source.forEachChild((node) => {
    if (!ts.isVariableStatement(node)) return;
    for (const decl of node.declarationList.declarations) {
      if (ts.isIdentifier(decl.name) && decl.name.text === "translations") {
        translations = decl.initializer;
      }
    }
  });

  if (!translations || !ts.isObjectLiteralExpression(translations)) {
    fail("could not find `export const translations = { ... }` in the source");
  }

  const catalogs = {};
  for (const languageProp of translations.properties) {
    if (!ts.isPropertyAssignment(languageProp)) {
      fail("a language entry is not a plain property — spreads are not supported");
    }
    const language = propertyName(languageProp.name);
    if (!ts.isObjectLiteralExpression(languageProp.initializer)) {
      fail(`the '${language}' entry is not an object literal`);
    }

    const entries = {};
    for (const entry of languageProp.initializer.properties) {
      if (!ts.isPropertyAssignment(entry)) {
        fail(`'${language}' contains an entry that is not a key: value pair`);
      }
      const key = propertyName(entry.name);
      if (!ts.isStringLiteral(entry.initializer) && !ts.isNoSubstitutionTemplateLiteral(entry.initializer)) {
        fail(`'${language}.${key}' is not a plain string literal`);
      }
      if (key in entries) {
        fail(`'${language}.${key}' is defined twice in the source catalog`);
      }
      // `.text` is the *cooked* value: escapes already resolved, quotes gone.
      entries[key] = entry.initializer.text;
    }
    catalogs[language] = entries;
  }

  return catalogs;
}

function propertyName(name) {
  if (ts.isIdentifier(name)) return name.text;
  if (ts.isStringLiteral(name)) return name.text;
  fail("a computed or numeric property name appears in the catalog");
}

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
