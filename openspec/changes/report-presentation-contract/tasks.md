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
- [ ] 1.6 Review 1.2–1.5 with the user, section by section; record decisions (draft in `editorial-draft.md`; 11 of 13 drafted, 2 blocked on 3.3/3.4)

## 2. Data contract

- [x] 2.1 Add `takeaway`, `materiality` and `method` to `SectionData` with temporary defaults so existing collectors keep constructing
- [x] 2.2 Define the materiality ordinal and its comparison semantics — `Materiality(IntEnum)`, higher is more material so `sorted(reverse=True)` leads
- [x] 2.3 Extend `test_section_data.py` for the new fields — ordering, defaults, immutability, `has_presentation`. Blank-rejection deliberately deferred to 3.7: enforcing it now breaks all eleven un-migrated collectors, so it lands when the defaults come off

## 3. Collectors

- [ ] 3.1 Populate the three fields in the 11 sections that already have a `collect_*`, one section per commit-sized step
- [ ] 3.2 Add the empty/insufficient-data takeaway path per collector, and rank it below any section with a finding
- [x] 3.3 Establish how Excel and PPTX render `topic_clusters` today given it has no collector, and whether the support matrix overstates reality — answered: three bespoke writers, three limits (15/20/50), all bypassing the payload
- [x] 3.4 Migrate `topic_clusters` to a collector — done. One cap of 20 in the payload (no renderer truncates, so the payload limit is the universal limit and it has to be legible on a slide). Excel loses detail, 50 -> 20; raising it needs generic PPTX truncation, which is every section's problem, not this one's
- [ ] 3.5 Decide `agentic_trace`: migrate to a collector, or record a declared exception with a reason
- [ ] 3.6 Reconcile the section name with its content — all three implementations show most-frequent concepts, not clusters
- [ ] 3.7 Remove the temporary defaults from 2.1 so the type enforces the contract
- [ ] 3.8 Per-section tests asserting the takeaway cites only figures the section renders, covering empty and boundary cases

## 4. Assembly

- [ ] 4.1 Assign exhibit ordinals in `build()` after section selection
- [ ] 4.2 Build the executive summary: every rendered section's takeaway, ordered by materiality, non-material ones de-emphasized
- [ ] 4.3 Test that ordinals shift with section selection while section keys do not

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
