## 1. Editorial groundwork (blocks everything downstream)

The 39 judgments — 13 sections × takeaway, materiality threshold, caveat — are
the long pole. Draft from what each collector already computes, then review
section by section. Unreviewed placeholder text is a blocking defect, not a
default: a takeaway is an assertion, and a wrong one is worse than silence.

- [x] 1.1 Tabulate, per section, which figures its collector computes today — the raw material a takeaway can legally cite
- [x] 1.2 Draft takeaway phrasing for the 13 sections, citing only figures from 1.1
- [x] 1.3 Draft materiality thresholds per section, with the reasoning for each cut-off
- [x] 1.4 Draft the caveat per section; carry over the two known ones (NIF is a field-normalized proxy and not the JIF; works count is local and not the OpenAlex global figure)
- [x] 1.5 Give `impact_projection` and `hidden_patterns` extra scrutiny — both names promise more certainty than a derived figure may support
- [x] 1.6 Review 1.2–1.5 with the user — approved as drafted. The two capped-below-`lead` judgments (impact_projection on a wide range, hidden_patterns always) stand; revisit if a real PDF reads wrong

## 2. Data contract

- [x] 2.1 Add `takeaway`, `materiality` and `method` to `SectionData` with temporary defaults so existing collectors keep constructing
- [x] 2.2 Define the materiality ordinal and its comparison semantics — `Materiality(IntEnum)`, higher is more material so `sorted(reverse=True)` leads
- [x] 2.3 Extend `test_section_data.py` for the new fields — ordering, defaults, immutability, `has_presentation`. Blank-rejection deliberately deferred to 3.7: enforcing it now breaks all eleven un-migrated collectors, so it lands when the defaults come off

## 3. Collectors

- [x] 3.1 Populate the three fields — all 13 sections now carry takeaway, method and materiality
- [x] 3.2 Empty/insufficient-data takeaway per collector, ranked `EMPTY` below any section with a finding
- [x] 3.3 Establish how Excel and PPTX render `topic_clusters` today given it has no collector, and whether the support matrix overstates reality — answered: three bespoke writers, three limits (15/20/50), all bypassing the payload
- [x] 3.4 Migrate `topic_clusters` to a collector — done. One cap of 20 in the payload (no renderer truncates, so the payload limit is the universal limit and it has to be legible on a slide). Excel loses detail, 50 -> 20; raising it needs generic PPTX truncation, which is every section's problem, not this one's
- [x] 3.5 Decide `agentic_trace` — migrated, not excepted. It maps cleanly onto Narrative blocks, and migrating fixed two live defects: it styled itself with `class="card"`/`class="muted"`, neither of which exists in the stylesheet, and carried a hard-coded Spanish paragraph in an English report
- [x] 3.6 Reconcile the section name with its content — display label only ("Topic Clusters" -> "Top Concepts"). The `topic_clusters` key is unchanged: it is in the vocabulary `GET /reports/sections` returns and the generated SDKs expose, so renaming it breaks callers for a tidiness gain
- [x] 3.7 Remove the temporary defaults so the type enforces the contract — `takeaway` and `method` are now required and validated non-blank; `materiality` keeps its default because "unremarkable" is an answer while a blank takeaway is an unwritten section
- [ ] 3.8 Per-section tests asserting the takeaway cites only figures the section renders, covering empty and boundary cases — still open; 3.7 enforces presence, not truthfulness

## 4. Assembly

Scope discovered while starting 4.1, and larger than the original wording
implied. `build()` iterates `SECTION_BUILDERS`, which returns **rendered HTML
strings** — it never holds a `SectionData`. Neither an exhibit ordinal nor an
executive summary can be produced from a string that has already been rendered,
so this group is not "add numbering": it is migrating HTML/PDF assembly from
the builder map to the collector map, which is what the Excel and PPTX
exporters already did.

HTML/PDF is the last format still assembled from string builders. This is the
remaining piece of the strangler `unify-report-format-coverage` began.

What makes it tractable: all 13 `_section_*` functions are already thin
wrappers of the form `render_html(collect_*(...))`, so the collectors are
proven against the current HTML output. What carries over is the dispatch —
collectors come in three signature shapes, and `build()` already branches on
exactly those today for the string builders:

  - `(db, domain_id, org_id)` — most sections
  - `(db, domain_id, org_id, benchmark_org)` — decision_recommendations,
    impact_projection, hidden_patterns
  - `(db, domain_id, org_id, benchmark_profile_id, benchmark_org)` —
    institutional_benchmark

Risk worth naming: HTML/PDF is the most-used output and the one just confirmed
working in production by exporting a real report. This refactor touches the
path that currently works.

- [ ] 4.1 Migrate `build()` from `SECTION_BUILDERS` to the collectors, carrying over the existing three-way signature dispatch
- [ ] 4.2 Keep the per-section error boundary: a collector that raises must still yield an error block rather than failing the whole report
- [ ] 4.3 Add an `exhibit` ordinal to `SectionData`, assigned in `build()` after selection and before rendering
- [ ] 4.4 Build the executive summary: every rendered section's takeaway, ordered by materiality, non-material ones de-emphasized
- [ ] 4.5 Test that ordinals shift with section selection while section keys do not
- [ ] 4.6 Diff the rendered HTML before and after the migration for a representative report — the collectors are proven per-section, the assembly is not
- [ ] 4.7 Decide what happens to `SECTION_BUILDERS` once nothing reads it: remove, or keep as a compatibility shim with a reason

## 5. Renderers

- [ ] 5.1 HTML/PDF: exhibit ordinal, takeaway as the heading with the dataset label as secondary text, method footer, executive summary
- [ ] 5.2 Excel: `Methodology` sheet listing every exhibit's source and caveat
- [ ] 5.3 Excel: caveat row directly above each section's table, so a copied range carries its warning
- [ ] 5.4 PPTX: takeaway as slide title, method in slide footer, full caveat in speaker notes
- [ ] 5.5 Verify the HTML view deliberately — HTML and PDF share one document, so nothing here can be scoped to print

## 6. Parity enforcement

- [ ] 6.1 Extend the format-support matrix to cover presentation elements as a dimension
- [ ] 6.2 Parity test: a format that renders a section must emit its takeaway and disclosure
- [ ] 6.3 Confirm a format that declares a section unsupported is exempt, and that existing omitted-section reporting is unchanged

## 7. Verification

- [ ] 7.1 Render a real report in all four formats and read them as a reader would
- [ ] 7.2 Confirm the PDF's executive summary and exhibits survive pagination — this change lands on top of the paged-layout fix
- [ ] 7.3 Full backend suite
- [ ] 7.4 Re-read every takeaway against its rendered section, checking for claims the data does not support
