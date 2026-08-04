/**
 * Shared reader for `frontend/app/i18n/translations.ts`.
 *
 * Both the projection generator and the parity gate need the same view of the
 * catalog. Parsing it twice, two different ways, is how the two gates end up
 * disagreeing about what the catalog contains — and a disagreement between
 * gates is worse than either gate missing something, because each one then
 * vouches for a different file.
 *
 * The source is read through the TypeScript compiler's AST rather than a
 * regex. The catalog holds apostrophes (`Cramér's V`), arrows
 * (`Análisis completo →`), accented text and interpolation braces
 * (`{platform}`); a regex over quoted strings gets those subtly wrong, and
 * subtly wrong translations are a defect nobody notices until a reader does.
 */
import { existsSync, readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

export const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..", "..");
export const SOURCE = join(ROOT, "frontend", "app", "i18n", "translations.ts");
export const PROJECTION_DIR = join(ROOT, "backend", "i18n");

// TypeScript is a frontend dependency, not a repo-root one.
const require = createRequire(join(ROOT, "frontend", "package.json"));
const ts = require("typescript");

/** Abort with a prefixed message. Callers pass their own tag. */
export function fail(tag, message) {
  console.error(`[${tag}] ${message}`);
  process.exit(1);
}

function propertyName(name, onError) {
  if (ts.isIdentifier(name)) return name.text;
  if (ts.isStringLiteral(name)) return name.text;
  onError("a computed or numeric property name appears in the catalog");
}

/**
 * Read `export const translations = { en: {...}, es: {...} }` off the AST.
 *
 * @param {(message: string) => never} onError called with a human-readable
 *   reason; must not return. Kept as a parameter so each caller can label the
 *   failure with its own gate name.
 * @returns {Record<string, Record<string, string>>} language → key → value
 */
export function extractCatalogs(onError) {
  if (!existsSync(SOURCE)) onError(`source catalog not found at ${SOURCE}`);

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
    onError("could not find `export const translations = { ... }` in the source");
  }

  const catalogs = {};
  for (const languageProp of translations.properties) {
    if (!ts.isPropertyAssignment(languageProp)) {
      onError("a language entry is not a plain property — spreads are not supported");
    }
    const language = propertyName(languageProp.name, onError);
    if (!ts.isObjectLiteralExpression(languageProp.initializer)) {
      onError(`the '${language}' entry is not an object literal`);
    }

    const entries = {};
    for (const entry of languageProp.initializer.properties) {
      if (!ts.isPropertyAssignment(entry)) {
        onError(`'${language}' contains an entry that is not a key: value pair`);
      }
      const key = propertyName(entry.name, onError);
      if (
        !ts.isStringLiteral(entry.initializer) &&
        !ts.isNoSubstitutionTemplateLiteral(entry.initializer)
      ) {
        onError(`'${language}.${key}' is not a plain string literal`);
      }
      if (key in entries) {
        onError(`'${language}.${key}' is defined twice in the source catalog`);
      }
      // `.text` is the *cooked* value: escapes already resolved, quotes gone.
      entries[key] = entry.initializer.text;
    }
    catalogs[language] = entries;
  }

  return catalogs;
}

/** Read the committed JSON projection for one language. */
export function readProjection(language) {
  const path = join(PROJECTION_DIR, `catalog.${language}.json`);
  if (!existsSync(path)) return null;
  return JSON.parse(readFileSync(path, "utf8"));
}
