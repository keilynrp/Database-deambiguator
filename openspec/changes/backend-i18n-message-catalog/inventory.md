# String inventory — task 1

127 candidates extracted from `backend/` (excluding `tests/`, `alembic/`, `__pycache__`, `openalex_lake/`) with a deliberately over-inclusive heuristic, then **classified by reading each one**. The extractor decides nothing; that is the point. Two earlier heuristic counts disagreed (96 across 17 modules, 71 across 16) and both admitted strings that must not be touched.

## Totals

| category | count | action |
|---|---|---|
| `label` / `operator-message` | 54 | migrate to catalog, EN + ES |
| `email` | 4 | migrate to catalog, EN + ES |
| `analysis-prose` | 22 | **convert to English**, no key |
| `false-positive` | 47 | leave alone |
| **total** | **127** | |

**37% of the candidates are false positives.** A regex-driven migration would have translated English docstrings and, worse, destroyed working input aliases.

## Two corrections to the plan

**1. "Analysis prose stays English" is not "leave it alone".**

The proposal says composed analysis text is not localised. It is currently **Spanish**, so honouring that decision means *converting these 22 strings to English*, not skipping them. The headline symptom in #209 — `"Concentración temática: Political science"` in an English report — is in this bucket. It is fixed by writing the sentence in English, not by adding a catalog key.

This makes the reported bug considerably cheaper to fix than the catalog work, and it can ship first, independently.

**2. Fourteen Spanish strings must be preserved exactly as they are.**

`services/field_correspondence.py` and `scripts/backfill_canonical_id_entity_type.py` hold Spanish strings that are **input-matching aliases**, not output: they map incoming CSV headers (`"Identificador único"`, `"Tipo de publicación"`, `"institución"`) onto canonical fields so that a user can upload a Spanish spreadsheet.

Translating them, or moving them to a message catalog, would break Spanish CSV imports. They are Spanish on purpose and belong to the data layer, not the presentation layer. Both earlier counts included them.

## `label` / `operator-message` → catalog (54)

| module | n | notes |
|---|---|---|
| `services/domain_neutral_labels.py` | 14 | field labels, examples, two destructive-action confirmations |
| `services/agentic_research_chat.py` | 12 | fallback replies and suggested follow-up questions (lines 330–341, 414–427) |
| `enrichment_worker.py` | 11 | remediation hints and failure reasons shown to operators |
| `services/audience_presets.py` | 9 | preset names, descriptions, export CTAs |
| `routers/dashboards.py` | 2 | dashboard title and description |
| `routers/demo.py` | 2 | demo portal description |
| `services/assistant_actions.py` | 2 | action descriptions |
| `services/researcher_topic_analytics.py` | 2 | metric descriptions (lines 521–522) |

## `email` → catalog (4)

`routers/auth_users.py` lines 158–162: password-reset subject and body. Outward-facing — the only strings here that reach someone who is not logged in.

## `analysis-prose` → convert to English (22)

| module | n | notes |
|---|---|---|
| `services/pattern_discovery.py` | 10 | includes the exact string reported in #209 |
| `services/impact_projection.py` | 10 | threshold-selected recommendations and the methodology sentence |
| `services/researcher_topic_analytics.py` | 2 | lines 276, 278 |

## `false-positive` → leave alone (47)

| kind | n | why |
|---|---|---|
| English docstring with an accented term | 27 | `Cramér's V`, `García → garcia`, `Kölner Phonetik`, `"Müller"`, `"English and Spanish names"` — matched on orthography, not language |
| Input-matching alias | 14 | see correction 2 — `field_correspondence.py` (10), `backfill_canonical_id_entity_type.py` (4) |
| Regex / character class | 5 | Spanish-language intent detection in `agentic_research_chat.py` (128, 132, 136), a multilingual stopword set in `institution_reconciliation.py` (82), an accent-inclusive character class in `semantic_keyword_signal_engine.py` (43) — these parse input, they are never displayed |
| English LLM prompt | 1 | `routers/ingest_helpers.py` (75) — matched on the word "no" appearing twice |

## Noted in passing, not part of this change

`services/agentic_research_chat.py` detects user intent with Spanish-only regexes (`cuant`, `distribución`, `evidencia`, `patrón`). An English-speaking user's question will not match any intent branch. That is an input-side language gap, the mirror image of #209, and it is not fixed by a message catalog. Worth its own issue.
