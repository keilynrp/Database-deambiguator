#!/usr/bin/env node
/**
 * EN/ES parity gate for the message catalog.
 *
 *   node scripts/check-i18n-parity.mjs
 *
 * ## What this checks, and what it deliberately does not
 *
 * It verifies that **every key exists in every language**. It says nothing
 * about whether the text is a correct translation: a Spanish value that is
 * fluent nonsense, an English string copy-pasted into the Spanish block, or a
 * placeholder like "TODO" all pass. This is a completeness check, not a
 * quality one, and claiming otherwise would manufacture exactly the false
 * confidence the i18n work has already been bitten by.
 *
 * ## Why it covers the frontend catalog too
 *
 * `frontend/app/i18n/translations.ts` is the source; `backend/i18n/catalog.*.json`
 * is a generated mirror. Gating only the mirror would move the failure one file
 * upstream rather than prevent it — a one-sided key added to the source would
 * project cleanly into a one-sided key.
 *
 * Both are checked because the projection is committed separately and could be
 * edited by hand. The drift gate catches that too; overlapping coverage on a
 * generated artefact is cheap.
 *
 * ## History
 *
 * The plan for this work claimed such a gate already existed and that this
 * phase would "extend" it. It did not exist — not in CI, not in the test suite,
 * and not in the type system, because `LanguageContext.tsx` casts the catalog
 * to `Record<Language, Record<string, string>>` and a cast checks nothing. The
 * catalog happened to be at exact parity, held by whoever last edited it.
 */
import { extractCatalogs, fail as failWith, readProjection } from "./lib/i18n-catalog.mjs";

const TAG = "i18n-parity";
/** @type {(message: string) => never} */
const fail = (message) => failWith(TAG, message);

/** English is the reference language: keys are English-derived. */
const REFERENCE = "en";

const MAX_LISTED = 15;

/**
 * Compare every language's key set against every other's.
 *
 * @returns {{language: string, key: string}[]} one entry per missing key
 */
function findOneSidedKeys(catalogs) {
  const languages = Object.keys(catalogs).sort();
  const everyKey = new Set(languages.flatMap((l) => Object.keys(catalogs[l])));

  const missing = [];
  for (const key of [...everyKey].sort()) {
    for (const language of languages) {
      if (!(key in catalogs[language])) missing.push({ language, key });
    }
  }
  return missing;
}

function report(label, catalogs) {
  const languages = Object.keys(catalogs).sort();

  if (!languages.includes(REFERENCE)) {
    fail(`${label}: the reference language '${REFERENCE}' is absent`);
  }
  for (const language of languages) {
    if (Object.keys(catalogs[language]).length === 0) {
      fail(`${label}: language '${language}' has no keys at all`);
    }
  }

  const missing = findOneSidedKeys(catalogs);
  if (missing.length === 0) {
    const counts = languages.map((l) => `${l}=${Object.keys(catalogs[l]).length}`).join(" ");
    console.log(`[${TAG}] OK — ${label}: every key present in every language (${counts}).`);
    return 0;
  }

  console.error(`[${TAG}] ${label}: ${missing.length} one-sided key(s).`);
  for (const { language, key } of missing.slice(0, MAX_LISTED)) {
    console.error(`  - '${key}' is missing from '${language}'`);
  }
  if (missing.length > MAX_LISTED) {
    console.error(`  ... and ${missing.length - MAX_LISTED} more`);
  }
  return missing.length;
}

function main() {
  let failures = 0;

  failures += report("frontend catalog (translations.ts)", extractCatalogs(fail));

  const projections = {};
  for (const language of ["en", "es"]) {
    const projected = readProjection(language);
    if (projected === null) {
      fail(`the '${language}' projection is missing — run scripts/generate-i18n-projection.mjs`);
    }
    projections[language] = projected;
  }
  failures += report("backend projection (backend/i18n)", projections);

  if (failures > 0) {
    console.error(
      `\n[${TAG}] Every key must exist in English and Spanish. Add the missing value, ` +
        `or remove the key from the language that has it.`,
    );
    console.error(
      `[${TAG}] Note: this gate checks presence only. It cannot tell a translation ` +
        `from a placeholder.`,
    );
    process.exit(1);
  }
}

main();
