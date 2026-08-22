"""Renderer-neutral report document aggregate, and its localized boundary.

`SectionData` is one section. A report is several of them plus a handful of
document-level scalars (title, domain, generated-at, the stakeholder lens
label) that used to be resolved ad hoc at each call site — the cover's own
inline `translate()` calls, the executive summary's hardcoded English
heading, a bespoke default title for a manual note. `ReportDocument`
aggregates those into one renderer-neutral value so there is one thing to
localize, not several scattered call sites that each have to remember to.

`ReportDocument` may still carry catalog keys, exactly like an unmigrated
`SectionData` field — collectors and assembly code are unaffected in how they
build one. `LocalizedReportDocument` is the boundary: the only way to obtain
one is `localize.localize_document()`, and everything in it — every section,
every document-level string — is resolved into one language. A
renderer/exporter that accepts a `LocalizedReportDocument` cannot render a
raw collector payload for owned copy, because there is no other way to
construct the type it requires.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .section_data import Materiality, SectionData

__all__ = [
    "ReportDocument",
    "LocalizedReportDocument",
    "ManualNote",
    "SectionError",
    "SummaryItem",
    "executive_summary_items",
]


@dataclass(frozen=True)
class ManualNote:
    """An analyst-authored note, as submitted with the export request.

    Deliberately not `SectionData`: its content is free text a person typed,
    not a computed finding with a takeaway/method — the type would not fit
    without inventing filler for fields that mean something everywhere else.
    HTML/PPTX render one per note; Excel writes all of them as rows on one
    sheet — a real, pre-existing structural difference #292 does not change.
    `content` is provider/user data and is never treated as a catalog key,
    at any stage; only the *default* title (used when `title` is blank) is
    owned copy, resolved once as `LocalizedReportDocument.
    manual_note_default_title`.
    """
    title: str
    content: str


@dataclass(frozen=True)
class SectionError:
    """A section whose collector raised, carried through assembly instead of
    aborting the whole document (report_builder.build()'s per-section error
    boundary). `title` is deferred like any other owned-copy field — a bare
    catalog key or literal, resolved at localization. `detail` is the
    exception's own message: diagnostic, not owned copy, so it is never
    treated as a catalog key and passes through localization unchanged.
    """
    section_key: str
    title: str
    detail: str


@dataclass(frozen=True)
class ReportDocument:
    """Semantic, pre-localization report aggregate.

    `sections` is in render order. Not every entry carries an `exhibit`
    number — the stakeholder reading and manual notes do not, matching the
    pre-#292 behavior where only the collector-driven, numbered sections feed
    the executive summary / methodology view (`executive_summary_items`
    filters on `exhibit is not None` for exactly this reason).

    Every `str` field may be a literal or a catalog key (optionally carrying
    params via `localize.with_params()`), the same contract `SectionData`
    fields already have. Nothing here is resolved yet.
    """
    domain_id: str
    domain_name: str
    title: str
    generated_at: str
    stakeholder_label: str
    sections: tuple[SectionData, ...] = field(default_factory=tuple)
    errors: tuple[SectionError, ...] = field(default_factory=tuple)
    manual_notes: tuple[ManualNote, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class LocalizedReportDocument:
    """The localized boundary. Every string is final, in `language`.

    Constructible only by `localize.localize_document()` — see that
    function's docstring for the invariant this type exists to make
    structural rather than conventional.
    """
    language: str
    domain_id: str
    domain_name: str
    title: str
    generated_at: str
    stakeholder_label: str
    #: Static captions for the cover — "Domain", "Generated", "Stakeholder
    #: lens" — resolved alongside everything else so the cover has no
    #: literals of its own left to forget to translate.
    domain_caption: str
    generated_caption: str
    stakeholder_lens_caption: str
    executive_summary_title: str
    manual_note_default_title: str
    disclosure: str | None
    sections: tuple[SectionData, ...] = field(default_factory=tuple)
    errors: tuple[SectionError, ...] = field(default_factory=tuple)
    manual_notes: tuple[ManualNote, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class SummaryItem:
    """One line of the executive summary / methodology view."""
    exhibit: int
    takeaway: str
    muted: bool


def executive_summary_items(doc: LocalizedReportDocument) -> tuple[SummaryItem, ...]:
    """Every numbered section's takeaway, ranked by materiality.

    Renderer-neutral data for a view every format that has an executive-
    summary-shaped surface (HTML's Executive Summary, Excel's Methodology)
    can share instead of each re-deriving the ranking. Sections without an
    exhibit number (stakeholder reading, manual notes) are excluded, matching
    behavior that predates #292: they were never part of `collected` either.

    Ties break on exhibit order, so the sequence is stable for a given
    section selection rather than depending on collection order.
    """
    numbered = [s for s in doc.sections if s.exhibit is not None]
    ranked = sorted(numbered, key=lambda s: (-int(s.materiality), s.exhibit or 0))
    return tuple(
        SummaryItem(
            exhibit=s.exhibit,  # type: ignore[arg-type]
            takeaway=s.takeaway,
            muted=s.materiality <= Materiality.ROUTINE,
        )
        for s in ranked
    )
