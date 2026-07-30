"""Per-format section coverage — the single source of truth for parity.

The section picker offers one vocabulary and four export formats, but the
formats do not render the same set. This module declares, per format, which
sections it actually renders today. It is:

  * read by the parity guard test as the ratchet target — every section must
    eventually be supported by every format, or explicitly declared
    unsupported;
  * (from phase 4) surfaced through `GET /reports/sections` so a caller can see
    availability before exporting instead of discovering a silent drop after.

The strangler migration edits `SECTION_FORMAT_SUPPORT` one section at a time as
each gains a real renderer. HTML and PDF share the one HTML pipeline, so their
coverage is identical by construction.
"""
from __future__ import annotations

from backend import report_builder

# Ordered, alias-free public section ids — the vocabulary GET /reports/sections
# returns. Derived from the builder registry so this list cannot drift from it.
PUBLIC_SECTIONS: tuple[str, ...] = tuple(
    section
    for section in report_builder.SECTION_BUILDERS
    if section not in report_builder.SECTION_ALIASES
)

EXPORT_FORMATS: tuple[str, ...] = ("html", "pdf", "excel", "pptx")

# Sections each format renders TODAY. HTML/PDF render the full set through
# report_builder.build(); Excel and PPTX each implemented a subset. Migration
# grows the Excel and PPTX sets until every format equals PUBLIC_SECTIONS.
SECTION_FORMAT_SUPPORT: dict[str, frozenset[str]] = {
    "html": frozenset(PUBLIC_SECTIONS),
    "pdf": frozenset(PUBLIC_SECTIONS),
    "excel": frozenset({
        "entity_stats",
        "enrichment_coverage",
        "top_secondary_labels",
        "impact_projection",
        "institutional_benchmark",
        "hidden_patterns",
        "decision_recommendations",
        "topic_clusters",
        "harmonization_log",
        "authority_control",
        "collaboration_graph",
        "journal_portfolio",
    }),
    "pptx": frozenset({
        "entity_stats",
        "enrichment_coverage",
        "top_secondary_labels",
        "topic_clusters",
        "impact_projection",
        "institutional_benchmark",
        "hidden_patterns",
        "decision_recommendations",
        "harmonization_log",
        "authority_control",
        "collaboration_graph",
        "journal_portfolio",
    }),
}


# ── Presentation elements (report-presentation 6.1) ──────────────────────────
#
# Section coverage answers "does this format render this section". It does not
# answer "does it render the statements that make the section's figures
# readable", which is a second dimension: a format could render every section
# and still ship a table with no finding above it and no caveat below.
#
# Where each element lands, per format:
#
#   | element  | html / pdf                  | excel                        | pptx                          |
#   |----------|-----------------------------|------------------------------|-------------------------------|
#   | takeaway | the section `<h2>`          | row 1 of the section's sheet | the slide title               |
#   | method   | `<p class="method">` footer | above each table, and the    | slide footer (clipped) and    |
#   |          |                             | `Methodology` sheet          | speaker notes (in full)       |
#   | exhibit  | the eyebrow, `Exhibit N ·`  | — see below                  | — see below                   |

PRESENTATION_ELEMENTS: tuple[str, ...] = ("takeaway", "method", "exhibit")

#: Not declarable as unsupported. A format that renders a section at all must
#: carry these: the published requirement is that no format "may declare these
#: elements unsupported while rendering the section they describe". The point of
#: naming them here is that the *declaration* below is itself constrained — a
#: future format cannot opt out by omitting them from its entry.
REQUIRED_PRESENTATION_ELEMENTS: frozenset[str] = frozenset({"takeaway", "method"})

#: Which presentation elements each format carries.
#:
#: `exhibit` is deliberately HTML/PDF only (design decision 7). An ordinal is a
#: within-document reference, and Excel and PPTX are not paged documents: they
#: also render a different *set* of sections than the document does, so an
#: ordinal assigned here would disagree with the PDF of the same generation
#: without saying so. Their reference is the sheet tab and the slide title.
PRESENTATION_SUPPORT: dict[str, frozenset[str]] = {
    "html": frozenset({"takeaway", "method", "exhibit"}),
    "pdf": frozenset({"takeaway", "method", "exhibit"}),
    "excel": frozenset({"takeaway", "method"}),
    "pptx": frozenset({"takeaway", "method"}),
}


def supports(export_format: str, section: str) -> bool:
    """Whether `export_format` renders `section` today."""
    return section in SECTION_FORMAT_SUPPORT.get(export_format, frozenset())


def carries(export_format: str, element: str) -> bool:
    """Whether `export_format` renders presentation `element`."""
    return element in PRESENTATION_SUPPORT.get(export_format, frozenset())


def unsupported_sections(export_format: str, sections: list[str]) -> list[str]:
    """Requested sections that `export_format` cannot render, order preserved."""
    supported = SECTION_FORMAT_SUPPORT.get(export_format, frozenset())
    canonical = report_builder.canonical_sections(sections)
    return [s for s in canonical if s not in supported]
