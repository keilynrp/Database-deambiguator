## Why

Generated reports currently title each section with the name of the data
(`Authority Control`, `Journal Portfolio`) rather than what the data says, and
carry no source or methodology line. Two consequences, one cosmetic and one not.

The cosmetic one: a reader has to derive every conclusion themselves, so the
document reads as an exported dashboard rather than an analysis.

The one that matters: several figures in these reports are easy to misread, and
nothing in the document warns the reader. The journal NIF is a field-normalized
open proxy, **not** the Journal Impact Factor, and the works count behind it is
local rather than OpenAlex's global figure. A recurring, generated report is
made to be circulated and cited; an unlabelled proxy will eventually be quoted
as the thing it approximates. Stating the method under the exhibit is the
correction, and it is also simply honest.

This is the presentation half of a two-part effort. Palette, typography and
visual identity are deliberately excluded — see "Out of scope" — because they
are the more subjective half and should not hold this one up.

## What Changes

- Every rendered section becomes a numbered **exhibit** with a stable
  identifier, so a reader can cite "Exhibit 4" and a later reader can find it.
- Section headings state the **finding**, derived from the data, instead of
  naming the dataset. `Authority Control` becomes something of the shape
  *"Disambiguation resolved 91% of ambiguous records; 9,462 await review"*.
  The label survives as a secondary line, so the section remains scannable.
- Every exhibit carries a **source and methodology footer**: origin of the data,
  as-of date, and any caveat needed to read the number correctly.
- An **executive summary** collects all 14 takeaways at the front, **ordered by
  materiality** rather than by section order, with non-material findings
  visually de-emphasized. Coverage stays complete — a reader can see that a
  section was computed and had nothing notable to say — while the findings that
  matter lead. This requires each section to declare a materiality signal, not
  merely a takeaway.
- Sections whose data is empty or insufficient say so explicitly rather than
  rendering an empty table under a confident heading.

Takeaway text and methodology notes are **data**, produced by the section
builders alongside the figures they describe, not strings assembled in the
renderer. This follows the separation `report-format-parity` already requires,
and is what lets non-HTML formats carry the same statements.

### Out of scope

Palette, typography, font installation, and component treatment. Those follow in
a separate change once this contract exists — visual work applied to headings
that still name datasets would be decoration over the actual problem.

Paged-layout mechanics (`@page`, running headers, page numbering, break
control) are also excluded: that is a rendering defect being fixed separately
and needs no requirement change.

## Capabilities

### New Capabilities

- `report-presentation`: what a rendered report must state about itself —
  exhibit identity, findings-first headings, source and methodology disclosure,
  and explicit empty-state language.

### Modified Capabilities

- `report-format-parity`: the parity requirement currently covers section
  *availability* per format. It is extended to cover presentation elements, and
  **all four formats must carry them** — none may declare takeaway or
  methodology text unsupported. Excel and PPTX are not documents, so each needs
  a placement decision rather than a rendering: a dedicated methodology sheet
  plus per-table header for Excel, slide footer plus speaker notes for PPTX.

  This is the deliberate, more expensive reading of parity. The argument for it
  is that Excel is the format most often re-cut and pasted elsewhere, which is
  exactly the path by which a proxy metric loses its caveat.

## Impact

- `backend/report_builder.py` — 14 section builders gain structured takeaway and
  methodology output; `SECTION_LABELS` gains an exhibit-ordering contract.
- `backend/reporting/format_support.py` — the support matrix gains presentation
  elements as a dimension.
- `backend/exporters/excel_exporter.py` — gains a methodology sheet and
  per-table caveat headers.
- The PPTX exporter — gains slide footers and speaker notes carrying the same
  statements.
- HTML and PDF share one renderer, so both inherit the change together.
- Consumers of `GET /reports/sections` see richer section metadata; the
  endpoint's response shape changes additively.

## Open questions

These need answers before or during the specs phase; they are domain judgments,
not implementation choices.

1. **Per-section takeaway phrasing.** What is the finding each of the 14
   sections is actually reporting? The code supplies the numbers but not the
   editorial judgment about which one leads.
2. **Materiality threshold per section.** Ordering the summary by materiality
   requires each section to answer "is this figure worth a reader's attention
   right now" — a different judgment from what the takeaway says. A coverage
   drop of 2 points is not material; 20 is.
3. **The honest caveat per metric.** NIF-vs-JIF and local-vs-global works count
   are known; the remaining sections need the same treatment, particularly
   `impact_projection` and `hidden_patterns`, whose names promise more certainty
   than a derived figure may support.

Resolved during proposal review: the executive summary carries all 14 takeaways
ordered by materiality, and all four export formats carry the presentation
elements.

The first three are per-section editorial judgments. The intended path is to
draft them from what each builder computes and review them section by section,
rather than block the specs phase on 42 open decisions.
