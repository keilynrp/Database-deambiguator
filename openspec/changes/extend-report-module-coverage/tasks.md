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

- [ ] 2.1 Failing test: pending-to-total above threshold adds a backlog caveat
      to the stakeholder reading. (RED — the reading cannot see authority data.)
- [ ] 2.2 Compute the ratio and thread it into
      `_section_stakeholder_reading`.
- [ ] 2.3 Failing test: the observed ratio is always disclosed, above or below
      threshold.
- [ ] 2.4 Failing test: below threshold raises no caveat.
- [ ] 2.5 Surface the threshold as configuration; document the default and that
      it is a starting point, not a derived constant.

## 3. Collaboration graph section

- [ ] 3.1 Failing test: section reports author, edge and community counts from
      seeded `Author` / `CoauthorEdge` / `AuthorStats`.
- [ ] 3.2 Implement `collect_collaboration_graph` reading precomputed
      `AuthorStats`. Scope via `scope_query_to_org`.
- [ ] 3.3 Failing test: most central authors listed with degree, centrality and
      publication count.
- [ ] 3.4 Add the centrality table block.
- [ ] 3.5 Failing test: bridge authors spanning communities are identified.
- [ ] 3.6 Implement bridge detection from precomputed columns only.
- [ ] 3.7 Failing test: rendering issues no graph computation — assert the
      section does not invoke the graph analytics path.
- [ ] 3.8 Failing test: absent or stale `computed_at` → staleness notice.
- [ ] 3.9 Failing test: no author stats → explanatory empty state.
- [ ] 3.10 Test: tenant isolation.
- [ ] 3.11 Register the section.

## 4. Journal portfolio section

- [ ] 4.1 Failing test: section reports distinct journals, DOAJ share and APC
      exposure from seeded `JournalMetric` rows.
- [ ] 4.2 Implement `collect_journal_portfolio`. Scope via
      `scope_query_to_org`.
- [ ] 4.3 Failing test: `nif_bayes` never renders without
      `[nif_ci_low, nif_ci_high]`.
- [ ] 4.4 Implement the top-journals table with the interval bound to the
      estimate so they cannot be separated.
- [ ] 4.5 Failing test: rendered output labels NIF as a field-normalized open
      proxy and never as a Journal Impact Factor.
- [ ] 4.6 Failing test: `works_2yr` is labelled as local coverage.
- [ ] 4.7 Failing test: no journal metrics → explanatory empty state.
- [ ] 4.8 Test: tenant isolation.
- [ ] 4.9 Register the section.

## 5. Surfacing

- [ ] 5.1 The three sections appear in `GET /reports/sections` with per-format
      availability.
- [ ] 5.2 Frontend section picker offers them.
- [ ] 5.3 Translation parity for new UI strings (EN + ES).

## 6. Close out

- [ ] 6.1 Performance check: each new section measured against the largest
      available dataset; document the timings.
- [ ] 6.2 Full backend suite green (`pytest backend/tests/`).
- [ ] 6.3 Frontend gates: ESLint `--max-warnings=0`, Design System governance,
      translation parity.
- [ ] 6.4 Manual check: a report with all three new sections exported in all
      four formats, NIF labelling and credible intervals verified by eye on the
      real artifact.
