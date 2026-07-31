## 1. Inventory

- [x] 1.1 Enumerate every candidate user-facing string literal in `backend/` (excluding `tests/`, `alembic/`), recording file, line and text — 127 candidates, extractor kept at `extract_candidates.js`
- [x] 1.2 Classify each candidate by hand as `label`, `operator-message`, `email`, `analysis-prose`, or `false-positive` — see `inventory.md`
- [x] 1.3 Commit the classified inventory to the change directory as the migration's worklist, with per-category counts
- [ ] 1.4 Confirm with the product owner that everything classified `analysis-prose` is staying English, since that is the boundary the whole scope rests on

Two findings from 1.2 change the plan; both are recorded in `inventory.md`:

- **`analysis-prose` means convert to English, not skip.** Those 22 strings are Spanish today, so honouring "analysis stays English" is work, not an exemption. The exact string reported in #209 is one of them, which makes the headline bug fixable independently of the catalog — see phase 1b.
- **14 Spanish strings must be preserved verbatim.** `field_correspondence.py` and `backfill_canonical_id_entity_type.py` hold input-matching aliases that let users upload Spanish spreadsheets. Migrating them would break Spanish CSV imports. Both earlier counts included them.

## 1b. Fix the reported symptom first

Independent of the catalog, and shippable on its own.

- [ ] 1b.1 Write a failing test asserting no Spanish appears in an English-generated report's Hidden Patterns section
- [ ] 1b.2 Convert the 10 `services/pattern_discovery.py` strings to English, preserving every interpolation argument
- [ ] 1b.3 Convert the 10 `services/impact_projection.py` strings to English
- [ ] 1b.4 Convert `services/researcher_topic_analytics.py` lines 276 and 278
- [ ] 1b.5 Generate a real report and read it — this defect was found by reading output, not by a test

## 2. Catalog projection

- [ ] 2.1 Add a script that emits a JSON projection of `frontend/app/i18n/translations.ts`, one object per language
- [ ] 2.2 Commit the generated projection under `backend/i18n/`
- [ ] 2.3 Test: regenerating the projection from an unchanged source produces a byte-identical file (deterministic ordering)
- [ ] 2.4 CI gate: fail when the committed projection differs from a fresh regeneration

## 3. Catalog module

- [ ] 3.1 Write failing tests for lookup: existing key in EN, same key in ES, absent key
- [ ] 3.2 Implement the catalog loader and `translate(key, lang, **params)`
- [ ] 3.3 Test: an absent key returns the key itself, logs a warning, and does not raise
- [ ] 3.4 Test: interpolation parameters survive in both languages, and interpolated values are not translated
- [ ] 3.5 Test: a key lacking a surface prefix (`report.`, `email.`, `validation.`) is rejected

## 4. Parity gate

- [ ] 4.1 Extend the translation parity gate to the backend projection; assert it fails on an EN-only key and on an ES-only key
- [ ] 4.2 Mutation-check the gate: introduce a one-sided key and confirm CI actually goes red — a gate that passes when written has proven nothing
- [ ] 4.3 Document in the gate itself that it verifies presence, not translation quality

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
- [ ] 6.4 `services/impact_projection.py`
- [ ] 6.5 `services/pattern_discovery.py` — labels only; the composed pattern sentences stay English
- [ ] 6.6 `services/field_correspondence.py`
- [ ] 6.7 `routers/dashboards.py`, `analyzers/correlation.py`, `services/researcher_topic_analytics.py`
- [ ] 6.8 Remaining single-string modules from the inventory
- [ ] 6.9 Verify no user-facing Spanish literal remains outside the catalog, using the classified inventory rather than the regex

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
