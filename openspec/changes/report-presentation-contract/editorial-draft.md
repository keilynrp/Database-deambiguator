# Editorial draft — 39 decisions pending review (task 1.6)

Draft only. Per the design, unreviewed placeholder text is a **blocking defect**,
not a default: a takeaway is an assertion, and a wrong one is worse than the
current silence.

Figures marked **[NEW]** do not exist yet. Four sections render tables without
any named metric, so a takeaway drawn from them needs a figure computed and
rendered first — the contract forbids citing what the section does not show.

Placeholders are `{name}`. Materiality is an ordinal; `lead` sorts above
`notable`, which sorts above `routine`, which sorts above `empty`.

---

## 1. entity_stats

- **Takeaway** — `{valid} of {total} entities pass validation ({valid_pct}%); {pending} remain unresolved`
- **Cites** — `total`, `valid_pct`, `pending`, `enriched` (all existing)
- **Materiality** — `lead` when `valid_pct < 85`; `notable` when `pending > 0`; else `routine`
- **Caveat** — Counts are scoped to this domain and organization. "Valid" is the record's status flag, not an assessment of the data's quality.

## 2. enrichment_coverage

- **Takeaway** — `Enrichment covers {pct}% of records; mean citation count {avg_cit}`
- **Cites** — `pct`, `avg_cit` (existing)
- **Materiality** — `lead` when `pct < 60`; `notable` when `pct < 85`; else `routine`
- **Caveat** — The mean is taken over enriched records only, so records never enriched do not pull it down. It therefore describes the enriched subset, not the portfolio. As-of the last enrichment run.

## 3. decision_recommendations

- **[NEW] figure** — count of recommendations, and count at highest priority
- **Takeaway** — `{n} recommended actions, {n_high} of them high priority`
- **Materiality** — `lead` when `n_high > 0`; `notable` when `n > 0`; else `empty`
- **Caveat** — Recommendations are heuristics derived from the current snapshot, not a ranked plan. They reflect what the data suggests, not institutional priority.

## 4. impact_projection

- **Takeaway** — `Projected impact {score}/100, probable range {p10}–{p90}`
- **Cites** — `score`, `range.p10`, `range.p90`, `confidence` (existing)
- **Materiality** — `notable` when the p10–p90 spread is narrow; `routine` when wide. **A wide range is low information and must not lead.**
- **Caveat** — **A Monte Carlo projection over current records, not an observation.** The range is the projection's own uncertainty; a wide range means the model cannot distinguish outcomes, not that impact is variable. The section's name promises more certainty than the figure supports.

## 5. hidden_patterns

- **[NEW] figure** — count of patterns detected, and the strongest association
- **Takeaway** — `{n} patterns detected; the strongest links {a} and {b}`
- **Materiality** — `notable` when `n > 0`; else `empty`. **Never `lead`** — see caveat.
- **Caveat** — Statistical co-occurrence within this corpus, not causation, and sensitive to corpus size: a small corpus produces spurious associations. Treat as a prompt to investigate, not a finding.

## 6. agentic_trace

- **Blocked** — no collector, and not rendered by Excel or PPTX. Task 3.4 decides: migrate, or declare an exception.

## 7. institutional_benchmark

- **Takeaway** — `Benchmark readiness {readiness_pct}% against {profile} — status {status}`
- **Cites** — `readiness_pct`, `status`, `profile` (existing)
- **Materiality** — `lead` when `status != "ready"`; else `notable`
- **Caveat** — Measured against the selected benchmark profile and comparison organization. Readiness describes conformance to that profile's rules, not standing among peers.

## 8. top_secondary_labels

- **[NEW] figure** — share of classified entities covered by the top N labels
- **Takeaway** — `The top {n} classifications cover {pct}% of classified entities`
- **Materiality** — `notable` when `pct > 60` (concentration is a finding); else `routine`
- **Caveat** — Denominator is classified entities only; unclassified records are excluded and do not appear as a gap. High concentration may reflect the classifier's coverage rather than the portfolio.

## 9. topic_clusters

- **Blocked** — no collector, yet the support matrix declares Excel and PPTX render it. Task 3.3 establishes how, before a takeaway can attach to anything.

## 10. harmonization_log

- **[NEW] figure** — count of applied operations, and the most recent timestamp
- **Takeaway** — `{n} harmonization operations applied, most recently {date}`
- **Materiality** — `routine` when `n > 0`; `empty` otherwise. Rarely leads.
- **Caveat** — The log records operations applied, not proposed or rejected. It shows what changed, not what was reviewed.

## 11. authority_control

- **Takeaway** — `{confirmed} of {total} authority records confirmed; {pending} await human review (mean confidence {mean_confidence})`
- **Cites** — `total`, `confirmed`, `pending`, `mean_confidence` (existing)
- **Materiality** — `lead` when `pending > confirmed`; `notable` when `pending > 0`; else `routine`
- **Caveat** — Mean confidence is the matcher's own score, not agreement with a human reviewer. Pending records are unreviewed, so their contribution to the mean is unvalidated.

## 12. collaboration_graph

- **Takeaway** — `{authors} authors across {communities} communities, linked by {collaborations} collaborations`
- **Cites** — `authors`, `collaborations`, `communities` (existing)
- **Materiality** — `notable` when `communities > 1`; else `routine`
- **Caveat** — Co-authorship is derived from local records, and author identities are derived rather than canonical, so the same person may appear more than once. Community detection is one partition among several possible.

## 13. journal_portfolio

- **Takeaway** — `{total} journals; {doaj_pct}% listed in DOAJ, {apc_count} charging an APC`
- **Cites** — `total`, `doaj_pct`, `apc_count` (existing)
- **Materiality** — `notable` when `doaj_pct < 50`; else `routine`
- **Caveat** — **NIF is a field-normalized two-year mean citedness computed from OpenAlex — an open proxy, not the Journal Impact Factor, and not comparable to a published JIF.** The works count behind it is local to this corpus, not OpenAlex's global figure for the journal. DOAJ and APC status as-of the last journal sync.

---

## Review notes

**Four sections need a new figure** (3, 5, 8, 10). Each adds work to group 3:
compute, render, test. The alternative was takeaways drawn from nothing, which
would have parked those sections permanently at the bottom of the summary.

**Two sections cannot be drafted yet** (6, 9) — both blocked on structural
decisions rather than editorial ones.

**Two takeaways are deliberately capped below `lead`.** `impact_projection` when
its range is wide, and `hidden_patterns` always. Both have names that sound more
conclusive than their figures are, and the executive summary is exactly where
that would mislead. This is a judgment worth disagreeing with explicitly if you
read those sections differently.

**Three caveats state what a figure is *not*** — NIF is not the JIF, the
enrichment mean is not the portfolio, benchmark readiness is not peer standing.
Those are the three most likely to be quoted out of context.
