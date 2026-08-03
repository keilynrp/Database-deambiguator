## 1. Inventory

- [x] 1.1 Enumerate every candidate user-facing string literal in `backend/` (excluding `tests/`, `alembic/`), recording file, line and text — 127 candidates, extractor kept at `extract_candidates.js`
- [x] 1.2 Classify each candidate by hand as `label`, `operator-message`, `email`, `analysis-prose`, or `false-positive` — see `inventory.md`
- [x] 1.3 Commit the classified inventory to the change directory as the migration's worklist, with per-category counts
- [x] 1.4 Confirm with the product owner that everything classified `analysis-prose` is staying English, since that is the boundary the whole scope rests on — **answered 2026-07-31: only 6 of the 22 stay English.** The other 16 interpolate nothing and are localised like any other label

Three findings from 1.2 change the plan; all are recorded in `inventory.md`:

- **`analysis-prose` means convert to English, not skip.** Those strings are Spanish today, so honouring "analysis stays English" is work, not an exemption. The exact string reported in #209 is one of them, which makes the headline bug fixable independently of the catalog — see phase 1b.
- **14 Spanish strings must be preserved verbatim.** `field_correspondence.py` and `backfill_canonical_id_entity_type.py` hold input-matching aliases that let users upload Spanish spreadsheets. Migrating them would break Spanish CSV imports. Both earlier counts included them.
- **The `analysis-prose` boundary was drawn by module, not by property.** Asking 1.4 forced a reading of all 22 strings, and only 6 embed English data — the condition the "stays English" argument actually rests on. The other 16 are fixed sentences that were classified together merely for sharing a file. They move to the catalog (phase 6), and phase 1b shrinks accordingly.

## 1b. Fix the reported symptom first

Independent of the catalog, and shippable on its own.

Scope is the **6 data-composing strings only** (see inventory correction 3). The 16 static
sentences that used to sit in this phase are catalog work and moved to phase 6 — converting
them to English here would be writing text this change then replaces.

- [x] 1b.1 Failing test written first — `test_report_language_hidden_patterns.py`, 6 tests, one per
      composed string, RED 6/6 before the conversions. **Scoped to the composed strings, not the
      section.** The task as written ("no Spanish appears in the section") is a phase-6 assertion:
      the static sentences in the same modules are still Spanish by design until 6.4–6.7, so that
      test would be red for reasons this phase does not own. It belongs at 6.9 and is noted there.
- [x] 1b.2 Converted the 4 composed `services/pattern_discovery.py` strings, every interpolation
      argument preserved: semantic cluster label (175), impact-outlier evidence (215), provider-gap
      evidence (266), collaboration-bridge evidence (338).
- [x] 1b.3 Converted `services/researcher_topic_analytics.py` 276 and 278 (both branches of the
      headline conditional).
- [x] 1b.4 Rendered the real section and read it. **The headline symptom is gone** —
      `Concentración temática: knowledge graph` now reads `Thematic concentration: knowledge graph`.

Two things the reading showed that the tests did not:

- **1b makes the mixing more visible before phase 6 removes it.** A single table row now reads
  `Output de impacto atípico | Graph Learning for Research Intelligence clearly exceeds the
  portfolio citation baseline (420 citations). | Usarlo como ancla del brief…` — Spanish label,
  English evidence, Spanish action. That is the correct intermediate state and it is defensible
  (the sentence quoting English data is the one that had to change first), but it is worse-looking
  than before and should not surprise anyone reviewing a report between 1b and phase 6.
- **`collect_hidden_patterns` caps at `limit=6`, so `collaboration_bridge` never reaches the
  report** with this fixture — six higher-scoring patterns crowd it out. Its string was still
  converted, and the test exercises it at `limit=12`. Worth confirming in phase 6 whether that cap
  is intended, since a pattern type that can never render is a separate question from language.

`services/impact_projection.py` is deliberately absent: all ten of its strings are static, so it contributes nothing here and appears in phase 6 instead.

## 2. Catalog projection

- [x] 2.1 `scripts/generate-i18n-projection.mjs` emits one JSON file per language. Parsed with the **TypeScript compiler's AST**, not a regex: the catalog holds apostrophes (`Cramér's V`), arrows (`Análisis completo →`) and interpolation braces (`{platform}`), and a regex over quoted strings gets those subtly wrong — a defect nobody notices until a reader does. Spot-checked all four forms survive.
- [x] 2.2 Committed as `backend/i18n/catalog.en.json` and `catalog.es.json` — **3402 keys each**, matching the source exactly. `backend/i18n/__init__.py` exposes `CATALOG_DIR`, `LANGUAGES`, `DEFAULT_LANGUAGE` only; lookup arrives in phase 3.
- [x] 2.3 Determinism is enforced **inside the generator** rather than by a test. `--check` renders twice and compares before comparing to the committed file, so every CI run proves it. A pytest that shells out to Node would skip wherever Node is absent, and a gate that silently skips is a gate that cannot fail — see 4.3.
- [x] 2.4 CI gate `i18n-projection-drift` in `.github/workflows/lint.yml`, blocking. Given its own job rather than folded into `frontend-lint-repo`, which is `continue-on-error: true` and would have made the gate advisory without saying so.

Mutation-checked, since a gate that passes when written has proven nothing:

| mutation | pytest | `--check` |
|---|---|---|
| keys unsorted | fails `test_keys_are_sorted` | exit 1 |
| one key dropped | fails `test_every_key_in_the_source_survives_the_projection` | exit 1 |
| unmodified | 7 passed | exit 0 |

`test_i18n_catalog_projection.py` counts keys **off `translations.ts` directly**, not off the generator's output — a generator that drops keys and a test reading only that generator's output would agree with each other and both be wrong.

## 3. Catalog module

- [ ] 3.1 Write failing tests for lookup: existing key in EN, same key in ES, absent key
- [ ] 3.2 Implement the catalog loader and `translate(key, lang, **params)`
- [ ] 3.3 Test: an absent key returns the key itself, logs a warning, and does not raise
- [ ] 3.4 Test: interpolation parameters survive in both languages, and interpolated values are not translated
- [ ] 3.5 Test: a key lacking a surface prefix (`report.`, `email.`, `validation.`) is rejected

## 4. Parity gate

**There is no parity gate to extend.** Verified 2026-08-02: nothing in `.github/workflows/`,
`frontend/package.json`, `frontend/scripts/` or `frontend/__tests__/` checks EN/ES parity, and
`LanguageContext.tsx` casts the catalog to `Record<Language, Record<string, string>>`, so the
type system does not check it either. The two sides are at exact parity today (3,402 keys each,
zero one-sided, zero duplicates) purely by discipline. This phase writes the gate.

- [ ] 4.1 Write the parity gate over the **frontend** catalog first — it is the source the backend projects from, and gating only the projection would move the failure upstream rather than prevent it
- [ ] 4.2 Extend the same gate to the backend projection; assert it fails on an EN-only key and on an ES-only key
- [ ] 4.3 Mutation-check the gate: introduce a one-sided key on each side and confirm CI actually goes red — a gate that passes when written has proven nothing
- [ ] 4.4 Confirm the gate is green against the catalog as it stands, so it lands enforcing rather than with a baseline of existing violations
- [ ] 4.5 Document in the gate itself that it verifies presence, not translation quality

## 5. Locale resolution

- [ ] 5.1 Write failing tests for the precedence chain: explicit parameter over header, header over default, default English
- [ ] 5.2 Implement the resolver as a FastAPI dependency
- [ ] 5.3 Test: an unsupported language falls back to English, succeeds, and logs the fallback
- [ ] 5.4 Test: report generation ignores `Accept-Language` entirely — a Spanish-browser operator with no explicit parameter gets an English artefact (decided 2026-07-31; the header still applies to the rest of the API)

## 6. Migrate strings

Ordered by count so the largest surfaces land first; each module is independently revertable.

- [ ] 6.1 `services/domain_neutral_labels.py`
- [ ] 6.2 `services/audience_presets.py`
- [ ] 6.3 `enrichment_worker.py`
- [ ] 6.4 `services/impact_projection.py` — all 10 strings, including the static recommendations reclassified in correction 3
- [ ] 6.5 `services/pattern_discovery.py` — the 6 static strings; the 4 composed sentences were converted to English in 1b and take no key
- [ ] 6.6 `services/field_correspondence.py`
- [ ] 6.7 `routers/dashboards.py`, `analyzers/correlation.py`, `services/researcher_topic_analytics.py`
- [ ] 6.8 Remaining single-string modules from the inventory
- [ ] 6.9 Verify no user-facing Spanish literal remains outside the catalog, using the classified inventory rather than the regex
- [ ] 6.10 Add the section-wide assertion deferred from 1b.1: an English-generated report's Hidden Patterns section contains no Spanish at all. Only meaningful once 6.4–6.7 have landed

## 7. Email

- [ ] 7.1 Migrate password-reset subject and body to catalog keys in both languages
- [ ] 7.2 Test: the subject resolves per language, with English as the default
- [ ] 7.3 Add the subject change to the deploy note — nothing depends on the current Spanish text (confirmed 2026-07-31), but it is outward-facing and recipients will see it change

## 8. Report language

- [ ] 8.1 Write a failing test that `POST /reports/generate` accepts a language and produces Spanish section titles
- [ ] 8.2 Add the parameter and thread the resolved language through the builder to the PDF, PPTX and Excel exporters
- [ ] 8.3 Test all three formats: catalog text is localised in each, per the parity contract those formats already carry
- [ ] 8.4 Test: omitting the parameter preserves the behaviour of existing callers
- [ ] 8.5 Render the disclosure that analysis text and provider-supplied names remain English, and test that a non-English artefact carries it
- [ ] 8.6 Regenerate `sdk/openapi.json` and the SDK clients; confirm the drift gates pass

## 9. Verification

- [ ] 9.1 Full backend suite green
- [ ] 9.2 Generate a real Spanish report in all three formats and read it — the defect in #209 was found by reading output, not by a test
- [ ] 9.3 Confirm the reverse case: an English report contains no Spanish, which is the original bug
- [ ] 9.4 Update issue #209 with what shipped and what deliberately did not
