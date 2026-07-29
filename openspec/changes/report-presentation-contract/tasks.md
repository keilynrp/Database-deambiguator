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
- [x] 3.8 Per-section tests asserting the takeaway cites only figures the section renders — needed populated fixtures to mean anything: against the default empty database every section returns its empty-state takeaway, cites nothing, and passes. Populating it immediately surfaced a real violation in `top_secondary_labels`

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

- [x] 4.1 Migrate `build()` from `SECTION_BUILDERS` to the collectors, carrying over the existing three-way signature dispatch
- [x] 4.2 Keep the per-section error boundary: a collector that raises must still yield an error block rather than failing the whole report
- [x] 4.3 Add an `exhibit` ordinal to `SectionData`, assigned in `build()` after selection and before rendering — numbered only once a section has collected, so an erroring section leaves no gap in the sequence
- [x] 4.4 Build the executive summary — ordered by materiality, ties broken by exhibit order; built after the loop but inserted before it, since it cannot know the findings until every section has collected
- [x] 4.5 Test that ordinals shift with section selection while section keys do not — plus gapless numbering, summary coverage, ordering, muting and escaping (`test_report_assembly.py`)
- [x] 4.6 Diff the rendered HTML before and after the migration — byte-identical over all 13 sections once the two generation timestamps are normalised (14,699 bytes either way)
- [x] 4.7 `SECTION_BUILDERS` is kept — the premise "once nothing reads it" was wrong. Seven call sites read it as the section *registry*, not as builders: four endpoints validate names against it, scheduled reports filter on it, and `format_support` derives `PUBLIC_SECTIONS` from it. Added a guard test so the two maps cannot drift apart

## 5. Renderers

- [x] 5.1 HTML/PDF: exhibit ordinal, takeaway as the heading with the dataset label as secondary text, method footer, executive summary. The section shell is now eyebrow (`Exhibit N · Label`) → `<h2>` takeaway → blocks → `<p class="method">`; the summary moved off inline styles onto the stylesheet. Reading a populated 13-section report found three defects the change had just promoted into headings — see below

Three defects surfaced by putting the takeaway in the `<h2>`. All were
pre-existing and all were invisible while the takeaway only appeared in a
summary list; none would have been caught by a fixture, because each needs real
figures to read wrong:

  - `stakeholder_reading` rendered `quality.average` — a 0–1 fraction — as a
    percentage without scaling, reporting **"quality 1%"** for a real average of
    0.82. Every other consumer of that field multiplies by 100
    (`impact_projection`, both dashboards). Fixed, with a regression test.
  - `"1 harmonization operations applied"` and `"linked by 1 collaborations"` —
    unconditional plurals, now in the most prominent line of their sections.
  - **Not fixed, needs a decision:** `build()` is the only renderer that does not
    run its section list through `canonical_sections()`. Excel and PPTX both do.
    Requesting `top_secondary_labels` and its deprecated alias `top_brands`
    together renders the same section twice, as two differently-numbered
    exhibits, and states the same finding twice in the summary. Exhibit numbering
    is what makes this legible as a defect rather than mere repetition.
- [x] 5.2 Excel: `Methodology` sheet listing every rendered section's finding and disclosure, keyed on the sheet name rather than an exhibit ordinal (design decision 7 — see below). Built after the section sheets and moved to position 2, behind `Summary`: the same shape as the HTML executive summary, and for the same reason
- [x] 5.3 Excel: caveat row directly above each section's table, so a copied range carries its warning. Placement is one of two, never both: above each table where there is one (each table is a separately copyable range), or under the takeaway where there is none — the disclosure is mandatory, not conditional on which block types a section happens to use

Two things 5.2 surfaced:

  - **No exhibit ordinal in Excel or PPTX.** Recorded as design decision 7. The
    three formats do not render the same set — `agentic_trace` is unsupported in
    both, and the Excel exporter iterates its own collector map rather than the
    requested order — so a workbook numbering its own exhibits would agree with
    the PDF up to the first divergence and then be off by one for everything
    after, silently, from the same request. In a workbook the sheet tab is how a
    reader navigates and cites anyway.
  - **`harmonization_log` was the one section outside the contract.** Its sheet
    comes from a bespoke writer rather than the shared payload, so it never
    entered the collected list and would have had no finding and no disclosure
    while the parity map claims Excel renders it. Fixed by collecting its payload
    for the Methodology row and the caveat row, without migrating the writer: its
    sheet carries row ids, executed-at and reverted over up to 200 rows, and 3.4
    already showed what migrating costs when the payload cap is lower than the
    sheet's. Migrating it stays open under `report-format-parity`.

Reading a workbook built from a deliberately singular dataset — one entity, one
journal, one author, one operation — found **five more unconditional plurals**,
in five separately-authored collectors, plus two verbs agreeing with the wrong
count ("1 of 1 entity pass validation"). All are now routed through one
`_plural()` helper. This is the same class of defect 5.1 found twice: the
takeaway is a heading in HTML and the first row of a sheet in Excel, so a count
of one is no longer buried in a summary list.
- [x] 5.4 PPTX: label as an eyebrow in the accent bar, takeaway as the slide title, method clipped in the slide footer, the whole of it in the speaker notes. Applied to **every** slide of a section, not just the first — a slide is the unit that gets pulled out of a deck and pasted into someone else's

Three things 5.4 settled:

  - **The last three sections bypassing the payload are gone.** `entity_stats`,
    `enrichment_coverage` and `top_secondary_labels` still had hand-built slides
    issuing their own queries — the same violation 3.3 found in `topic_clusters`,
    so they carried no takeaway and no disclosure while the parity map claimed
    PPTX rendered them. Migrated rather than supplemented (94 lines deleted), and
    it cost no detail: the payload is richer than all three were — four KPI cards
    rather than two, a `Source` column, 15 rows rather than 10.
  - **The eyebrow is not upper-cased**, though the HTML one reads that way. CSS
    does it with `text-transform`, which leaves the string alone; PPTX has no
    equivalent, so upper-casing would mean changing the text — and the label is
    what every format's parity marker matches on. Upper-casing it first broke 19
    tests, including the whole `pptx:` half of the parity guard.
  - **Sections spill onto a second slide sooner.** Usable vertical space dropped
    from 5.3" to 4.55" once the header gained a line and the footer took the
    bottom, so three sections now take two slides where they took one. That is
    the cost of the contract, not a defect: the alternative is content sitting
    underneath the disclosure. Blocks taller than one slide still overflow, which
    is the generic PPTX truncation problem 3.4 already named as every section's
    rather than any one section's.
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
