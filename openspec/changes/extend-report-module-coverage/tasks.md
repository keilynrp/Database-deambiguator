# Tasks — extend report coverage to authority, coauthorship and journals

TDD throughout. Each section is authored once against the format-neutral payload
from `unify-report-format-coverage`; the parity test from that change is the gate
that proves it reached all four formats.

## 0. Prerequisite

- [x] 0.1 Confirm `unify-report-format-coverage` is merged and its parity test
      has no remaining `xfail`. **Satisfied 2026-07-25:** merged via PR #187
      (squash `f4838c0`) + #189 (`2af0dea`); parity guard on main = 41 passed,
      0 xfailed.

## 1. Authority control section

- [x] 1.1 Failing test: section reports total, confirmed and pending-review
      counts from seeded `AuthorityRecord` rows.
      (`test_report_module_coverage.py`.)
- [x] 1.2 Implement `collect_authority_control` — aggregate counts, status
      distribution, mean confidence. Scope via `scope_query_to_org`. Note:
      `AuthorityRecord` has no domain column, so `domain_id` is accepted for
      signature consistency but is not a filter (org-scoped only).
- [x] 1.3 Failing test: unresolved conflicts are listed with confidence and
      `nil_reason`.
- [x] 1.4 Add the conflicts table block, with an explicit limit
      (`_AUTHORITY_CONFLICT_LIMIT = 10`), lowest-confidence first. When the limit
      is hit the narrative says so, so the table is never mistaken for the whole
      queue (prod holds ~9.4k pending).
- [x] 1.5 Failing test: a backlog produces a prose reliability statement.
- [x] 1.6 Add the `Narrative` block ("Reliability reading").
- [x] 1.7 Failing test: no authority records → explanatory empty state, not a
      zero-conflict finding. Implemented as an early-return Narrative stating
      resolution has not been run and explicitly **not** claiming zero conflicts.
      (Deliberate divergence from change 1's convention of dropping empty states:
      here an empty section would read as false reassurance.)
- [x] 1.8 Test: tenant isolation — another org's records never appear.
- [x] 1.9 Register the section; parity test picks it up across all four formats.
      Registered in `SECTION_BUILDERS`/`SECTION_LABELS`, both format-support sets,
      and both exporter collector loops; markers added to the parity guard. Guard
      45 passed / 0 xfailed. The guard's seed now includes authority records so
      the **populated** path is exercised in every format, not the empty state.
      ⚠️ **Latent break caught here:** `_ReportRequest.sections` capped at
      `max_length=10`; an 11th public section made "select all + export" a 422
      (the picker selects every section by default, and Pydantic does not validate
      field defaults, so only real callers broke). Cap now derived:
      `_MAX_REQUEST_SECTIONS = len(_ALL_REPORT_SECTIONS)`, with a regression test.

## 2. Readiness caveat

- [x] 2.1 Failing test: pending-to-total above threshold adds a backlog caveat
      to the stakeholder reading.
- [x] 2.2 Compute the ratio and thread it into `collect_stakeholder_reading`
      (`_authority_backlog_ratio`). The caveat qualifies the readiness language
      as provisional; the ratio is always disclosed.
- [x] 2.3 Failing test: the observed ratio is always disclosed, above or below
      threshold.
- [x] 2.4 Failing test: below threshold raises no caveat.
- [x] 2.5 Surface the threshold as configuration
      (`UKIP_REPORT_AUTHORITY_BACKLOG_THRESHOLD`, `_authority_backlog_threshold()`,
      default 0.15, clamped to [0,1]). Documented as a starting point for judgement,
      not a derived constant, and declared in `docker-compose.prod.yml` per the
      "any code-read env var must also be declared in prod compose" rule.

## 3. Collaboration graph section

- [x] 3.1 Failing test: section reports author, edge and community counts.
- [x] 3.2 Implement `collect_collaboration_graph` reading precomputed
      `AuthorStats` / `CoauthorEdge`. Scope via `scope_query_to_org` (authors are
      counted through `AuthorStats`, which carries `org_id`; `Author` has none).
- [x] 3.3 Failing test: most central authors listed with degree, centrality,
      publication count.
- [x] 3.4 Add the centrality table block (top `_COLLAB_TOP_LIMIT`, centrality desc).
- [x] 3.5 Failing test: bridge authors spanning communities are identified.
- [x] 3.6 Bridge detection from precomputed `community_id` only — a self-join on
      `AuthorStats` over `CoauthorEdge` endpoints where the two communities differ.
      No traversal.
- [x] 3.7 Failing test: rendering issues no graph computation — monkeypatches
      `recompute_coauthor_stats`, `graph_analytics.detect_communities` and
      `pagerank` to raise, and asserts the section still renders.
- [x] 3.8 Failing test: stale `computed_at` → staleness notice
      (`_COLLAB_STALENESS_DAYS = 30`). Absent-timestamp is a legacy-row case not
      reproducible via the constructor (column defaults to now()) but is handled
      defensively.
- [x] 3.9 Failing test: no author stats → explanatory empty state.
- [x] 3.10 Test: tenant isolation.
- [x] 3.11 Register the section (builders/labels, both support sets, both exporter
      loops, parity markers). Guard's seed extended with authors + a cross-community
      edge so the populated path renders in every format.

## 4. Journal portfolio section

- [x] 4.1 Failing test: distinct journals, DOAJ share and APC exposure.
- [x] 4.2 Implement `collect_journal_portfolio`. Scope via `scope_query_to_org`.
- [x] 4.3 Failing test: `nif_bayes` never renders without `[nif_ci_low, nif_ci_high]`.
- [x] 4.4 Top-journals table with the interval bound to the estimate — a single
      `_bayes_with_interval()` cell formats "e [lo, hi]" and returns "—" when the
      interval is missing, so there is **no code path** that emits the estimate
      bare.
- [x] 4.5 Failing test: NIF labelled a field-normalized open proxy, never a JIF.
      The column header says "NIF (field-normalized)" and a narrative states it is
      NOT a Journal Impact Factor.
- [x] 4.6 Failing test: `works_2yr` labelled as local coverage ("Local works
      (2yr)" column + a narrative note that it is this workspace's count, not the
      journal's global volume).
- [x] 4.7 Failing test: no journal metrics → explanatory empty state.
- [x] 4.8 Test: tenant isolation.
- [x] 4.9 Register the section (builders/labels, both support sets, both exporter
      loops, parity markers). Guard seed extended with a journal carrying a full
      credible interval so the populated table renders in every format.

## 5. Surfacing

- [x] 5.1 The three sections appear in `GET /reports/sections` with per-format
      availability — automatic, since the listing derives from `SECTION_LABELS`
      and `format_support`. ⚠️ Caught here: a copy-paste registration left
      `collaboration_graph`/`journal_portfolio` out of the **pptx** support set
      even though the pptx exporter loop rendered them, so the omission header and
      the listing would have wrongly reported them as pptx-omitted. Fixed — both
      support sets now include all three.
- [ ] 5.2 Frontend section picker offers them. **Deferred to a follow-up frontend
      PR (off main, like #189).** The picker fetches sections dynamically, so the
      three appear automatically once the backend merges — but with the default
      icon and no description until `SECTION_ICONS` + `sectionDescriptions` gain
      entries. Depends on this backend landing first.
- [ ] 5.3 Translation parity for new UI strings (EN + ES). With 5.2 (the section
      descriptions are the only new strings).

## 6. Close out

- [ ] 6.1 Performance check: each new section measured against the largest
      available dataset; document the timings. **Pending** — needs a real dataset;
      the collectors are aggregate queries + a capped top-N (10–12 rows) and the
      collaboration bridge join reads precomputed columns only, so the expected
      cost is low, but this wants measurement on prod-scale data (≈9.4k authority
      records).
- [~] 6.2 Full backend suite green (`pytest backend/tests/`). Run in progress.
- [ ] 6.3 Frontend gates: ESLint `--max-warnings=0`, Design System governance,
      translation parity. With the 5.2 frontend follow-up.
- [ ] 6.4 Manual check: a report with all three new sections exported in all
      four formats, NIF labelling and credible intervals verified by eye on the
      real artifact. **Pending** — needs a deploy; the NIF/CI guarantees are
      covered programmatically (4.3/4.5/4.6) but the human artifact check remains.
