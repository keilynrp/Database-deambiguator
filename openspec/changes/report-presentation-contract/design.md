## Context

Reports are assembled by `report_builder.build()`, which runs a set of section
builders and concatenates their output. Eleven of the thirteen public sections
already follow a data/presentation split introduced by `report-format-parity`:
a `collect_<section>()` returns a `SectionData(key, title, blocks)`, and three
renderers — `html_renderer`, `excel_renderer`, `pptx_renderer` — turn that into
their format. PDF shares the HTML renderer.

That existing fan-out is the whole reason this change is cheap. The presentation
contract does not need a parallel mechanism: whatever `SectionData` carries,
every format already receives.

Two facts constrain the work:

- Two sections have **no collector**, and they are irregular in different ways:

  | section | collector | Excel | PPTX |
  |---|---|---|---|
  | `agentic_trace` | no | not rendered | not rendered |
  | `topic_clusters` | no | **rendered** | **rendered** |

  `agentic_trace` is simply outside the migration. `topic_clusters` is the
  awkward one, and task 3.3 established why: the matrix is truthful — all three
  formats do render it — but each does so through a bespoke legacy writer that
  issues its own `TopicAnalyzer().top_topics()` call, bypassing the payload the
  parity requirement says renderers must derive output from.

  They also disagree. HTML/PDF shows the top 15 under the heading "Topic
  Clusters", PPTX the top 20 under "Top Concepts", Excel the top 50 on a sheet
  called "Concepts". And all three call `top_topics` — most frequent concepts —
  so the section key misdescribes what every implementation actually shows.

  This makes migrating it a prerequisite rather than a choice: with three
  divergent renderings there is no single payload for a takeaway to describe.
- HTML and PDF are the same document. A presentation element cannot be added for
  print without appearing on screen.

## Goals / Non-Goals

**Goals:**

- Every rendered section states its finding, its exhibit identity, and the
  method behind its figures, in all four export formats.
- Takeaway and methodology are **data**, so a new format inherits them without
  re-deriving anything.
- A reader who quotes a figure out of the report carries its caveat with it.

**Non-Goals:**

- Palette, typography, font installation, component styling. Separate change.
- Paged-layout mechanics (`@page`, running headers, break control) — a rendering
  defect fixed separately, requiring no requirement change.
- Growing Excel/PPTX section coverage from 12 to 13. Pre-existing gap, tracked by
  `report-format-parity`; this change must not silently absorb it.

## Decisions

### 1. Extend `SectionData` rather than add a parallel structure

`SectionData` gains `takeaway`, `materiality` and `method`. The three renderers
each learn to place them.

*Alternative considered:* a separate `PresentationMeta` keyed by section, resolved
at render time. Rejected — it splits a section's figures from the sentence that
describes them, so the two can drift, and drift here means a report that states
a finding its own table contradicts. Keeping them in one object makes that a type
error rather than a review problem.

### 2. Takeaway is produced by the collector, not the renderer

The sentence is derived from the same numbers the section renders, inside
`collect_*`, and passed through untouched.

*Alternative considered:* renderers compose the sentence from structured parts.
Rejected — it puts editorial logic in three places and guarantees the formats
eventually disagree. It also violates the separation `report-format-parity`
already requires.

### 3. Exhibit numbers are assigned at assembly, not by collectors

A collector cannot know it is Exhibit 4: numbering depends on which sections were
selected and in what order, both request-scoped. `build()` assigns ordinals after
collecting and before rendering.

Consequence worth stating: **exhibit numbers are not stable across reports with
different section selections.** Two reports of the same domain can number the
same section differently. The stable identifier is the section `key`; the exhibit
number is a within-document reference only. Any citation guidance must say so.

### 4. Materiality is an ordinal, not a boolean

The executive summary orders all thirteen takeaways by materiality with
non-material ones de-emphasized, which needs a sort key, not a filter. An ordinal
also lets a section say "notable but not leading" instead of forcing a binary.

Each collector computes its own materiality from its own thresholds — a two-point
coverage drop is noise, twenty points is not, and only the section knows which is
which.

### 5. Method text is required, not optional

A section with nothing to disclose still states its source and as-of date. Making
it optional means the sections that most need a caveat are the ones most likely
to omit it, because their author is closest to the data and least likely to see
the ambiguity.

### 6. Excel and PPTX placement

Neither is a document, so each needs a placement rather than a rendering:

- **Excel** — a dedicated `Methodology` sheet listing every exhibit with its
  takeaway, source and caveat, plus a caveat row above each section's table so a
  copied range carries its warning.
- **PPTX** — takeaway becomes the slide title, method goes in the slide footer,
  full caveat in speaker notes.

The Excel decision is the one that matters: it is the format most often re-cut
and pasted, which is exactly the path by which a proxy metric loses its caveat.

## Risks / Trade-offs

- **A generated sentence can state something false.** A takeaway is derived text
  asserting a finding; a wrong threshold produces a confident, wrong claim — worse
  than the current silence. → The takeaway must be derived only from figures the
  same section renders, and tested per section against fixtures including the
  empty and boundary cases.

- **Thirty-nine editorial decisions (13 sections × takeaway, materiality, caveat)
  are the real cost, not the code.** → Draft from what each collector computes,
  review section by section, and treat unreviewed placeholder text as a blocking
  defect rather than a default.

- **`topic_clusters` renders differently in every format today** — 15, 20 and 50
  rows under three different headings, from three writers that each query
  directly. This is a pre-existing violation of the parity requirement, not
  something this change introduces, but it blocks the change: a takeaway drawn
  from what each format renders would state three different findings. →
  Migrating it to a collector is a prerequisite (task 3.4), and the divergence
  should be fixed deliberately rather than by silently adopting whichever limit
  the collector happens to use — someone has to decide whether the answer is
  15, 20 or 50.

- **`agentic_trace` has no collector and no Excel/PPTX support.** → Decide
  explicitly: migrate, or record a declared exception with a reason (task 3.5).

- **Exhibit numbers shift between reports.** → Documented above; the section key
  is the stable identifier.

- **Screen and print share one document.** An executive summary tuned for a paged
  report also lands on the HTML view. → Verify the HTML view deliberately rather
  than assuming print-only scoping is available; it is not.

## Migration Plan

Additive throughout. `SectionData` gains fields with defaults so existing
collectors keep constructing, then each collector is filled in and the default
removed once all thirteen supply real values — the type then enforces the
contract instead of documentation asking for it.

No data migration; nothing is persisted. Rollback is a revert.

## Open Questions

1. Per-section takeaway phrasing — which figure leads for each of the thirteen.
2. Per-section materiality thresholds — what makes a figure worth attention now.
3. Per-section caveat — known for journal NIF (field-normalized proxy, not JIF)
   and works count (local, not OpenAlex global); the rest need the same
   treatment, especially `impact_projection` and `hidden_patterns`, whose names
   promise more certainty than a derived figure may support.
4. `agentic_trace` — migrate to a collector, or declare an exception.
5. ~~`topic_clusters` — how do Excel and PPTX render it today without a
   payload?~~ **Answered (task 3.3).** The support matrix is truthful: all
   three formats render it, each through a bespoke legacy writer that issues
   its own `TopicAnalyzer().top_topics()` call. That violates the published
   `report-format-parity` requirement that renderers derive output solely from
   the section payload.

   Worse, the three disagree:

   | format | limit | heading shown |
   |---|---|---|
   | HTML/PDF | `top_n=15` | "Topic Clusters" |
   | PPTX | `top_n=20` | "Top Concepts" |
   | Excel | `top_n=50` | sheet "Concepts" |

   And every implementation calls `top_topics` — most frequent concepts — not
   clusters, so the section key misdescribes what all three actually show.

   Consequence for this change: a takeaway written from what each format
   renders would produce three different sentences. The section must be
   migrated to a collector before it can carry the contract; there is no
   single payload to describe today.
