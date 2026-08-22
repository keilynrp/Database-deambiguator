"""HTML renderer over the section payload (unify-report-format-coverage,
phase 2).

Block markup uses the same CSS classes the hand-written `_section_*` builders
did (`grid`, `stat-card`, `callout`, `bar-wrap`, …), so a section's *contents*
are unchanged by migration. The section shell around them is not: since
report-presentation 5.1 it carries the presentation contract — an exhibit
eyebrow, the takeaway as the heading, and a method footer. All data is
HTML-escaped.
"""
from __future__ import annotations

from html import escape

from backend.reporting.document import (
    LocalizedReportDocument,
    ManualNote,
    SectionError,
    executive_summary_items,
)
from backend.reporting.localize import assert_localized_section, assert_localized_document
from backend.reporting.section_data import (
    Block,
    Meter,
    Narrative,
    SectionData,
    StatGrid,
    Table,
)

SUPPORTED_BLOCKS: frozenset[type] = frozenset({StatGrid, Table, Narrative, Meter})


def _pct(value: str) -> int:
    """Best-effort percentage from a cell like '64' or '64%'."""
    digits = "".join(ch for ch in str(value) if ch.isdigit() or ch == ".")
    try:
        return max(0, min(100, round(float(digits))))
    except ValueError:
        return 0


def _stat_grid(block: StatGrid) -> str:
    cards = "".join(
        f'<div class="stat-card"><div class="label">{escape(item.label)}</div>'
        f'<div class="value">{escape(item.value)}</div>'
        + (f'<div class="sub">{escape(item.sub)}</div>' if item.sub else "")
        + "</div>"
        for item in block.items
    )
    return f'<div class="grid">{cards}</div>'


def _table(block: Table) -> str:
    head = "".join(f"<th>{escape(col)}</th>" for col in block.columns)
    body_rows = []
    for row in block.rows:
        cells = []
        for idx, cell in enumerate(row):
            if idx == block.bar_column:
                pct = _pct(cell)
                cells.append(
                    '<td><div class="bar-wrap">'
                    f'<div class="bar-bg"><div class="bar" style="width:{pct}%"></div></div>'
                    f"<span>{escape(cell)}</span></div></td>"
                )
            else:
                cells.append(f"<td>{escape(cell)}</td>")
        body_rows.append("<tr>" + "".join(cells) + "</tr>")
    return (
        "<table><thead><tr>"
        + head
        + "</tr></thead><tbody>"
        + "".join(body_rows)
        + "</tbody></table>"
    )


def _narrative(block: Narrative) -> str:
    paras = "".join(f"<p>{escape(p)}</p>" for p in block.paragraphs)
    return f'<div class="callout"><h3>{escape(block.heading)}</h3>{paras}</div>'


def _meter(block: Meter) -> str:
    pct = max(0, min(100, round(block.pct)))
    return (
        f'<div class="label">{escape(block.label)}</div>'
        '<div class="bar-wrap">'
        f'<div class="bar-bg"><div class="bar" style="width:{pct}%"></div></div>'
        f"<span>{pct}%</span></div>"
    )


def _render_block(block: Block) -> str:
    if isinstance(block, StatGrid):
        return _stat_grid(block)
    if isinstance(block, Table):
        return _table(block)
    if isinstance(block, Narrative):
        return _narrative(block)
    if isinstance(block, Meter):
        return _meter(block)
    raise TypeError(f"HTML renderer cannot render {type(block).__name__}")


def _exhibit_label(section: SectionData) -> str:
    """The eyebrow above the heading: which exhibit this is, and of what.

    The dataset label lives here rather than in the heading because the heading
    now states the finding. Losing the label entirely would cost the reader the
    ability to scan a report by section, which is what the label was for.

    `exhibit` is None whenever a section is rendered outside document assembly —
    a collector cannot know its own ordinal — so the prefix is conditional while
    the label is not.
    """
    label = escape(section.title)
    if section.exhibit is None:
        return f'<div class="exhibit-label">{label}</div>'
    return (
        '<div class="exhibit-label">'
        f'<span class="ord">Exhibit {section.exhibit}</span>'
        f"&nbsp;·&nbsp;{label}"
        "</div>"
    )


def render_html(section: SectionData) -> str:
    """One section as a self-contained document exhibit.

    The shape carries the presentation contract: the ordinal identifies the
    exhibit, the heading asserts the finding, the label stays available as
    secondary text, and the method footer travels underneath so a reader who
    quotes a figure out of the section can still see what it is.

    `section` must already be localized — this renderer resolves nothing.
    See `backend.reporting.localize` for why a renderer used to do that
    itself, and `assert_localized_section` for what replaced it: a renderer
    that receives a raw payload now fails loudly instead of shipping a
    catalog key.
    """
    assert_localized_section(section)

    body = "".join(_render_block(block) for block in section.blocks)
    return (
        "<section>\n    "
        + _exhibit_label(section)
        + f"\n    <h2>{escape(section.takeaway)}</h2>\n    "
        + body
        + f'\n    <p class="method">{escape(section.method)}</p>\n</section>'
    )


def _manual_note(note: ManualNote, default_title: str) -> str:
    """An analyst-authored note as its own exhibit-less section.

    `note.content` is free text a person typed — never a localization
    target, at any stage (see `ManualNote`). Only the fallback title, used
    when the analyst left `note.title` blank, is owned copy, and it arrives
    here already resolved by `localize_document`. Delegates to
    `report_builder._section_manual_note` (imported lazily, same reason
    `_CSS` is below) rather than duplicating its escaping/paragraph logic.
    """
    from backend.report_builder import _section_manual_note

    return _section_manual_note(note.title, note.content, default_title)


def _executive_summary(doc: LocalizedReportDocument) -> str:
    """Every numbered section's takeaway, ordered by materiality.

    Ordered, not filtered. A reader can see that a section was computed and
    had nothing notable to say — which is itself information — while the
    findings that matter lead. Non-material entries are de-emphasized rather
    than dropped.
    """
    items = executive_summary_items(doc)
    if not items:
        return ""

    lines = "".join(
        f'<li{" class=\"muted\"" if item.muted else ""}>'
        f'<span class="ord">Exhibit {item.exhibit}</span>&nbsp;·&nbsp;'
        f"{escape(item.takeaway)}"
        f"</li>"
        for item in items
    )
    return (
        "<section>"
        f"<h2>{escape(doc.executive_summary_title)}</h2>"
        f'<ul class="summary-list">{lines}</ul>'
        "</section>"
    )


def render_html_document(doc: LocalizedReportDocument) -> str:
    """The full HTML/PDF document: cover, disclosure, summary, sections, footer.

    `doc` must be a `LocalizedReportDocument` — the only way to obtain one is
    `localize.localize_document()` — so there is no code path into this
    function that has not gone through the single localization pass. This is
    the boundary #292 exists to establish: previously the cover, the
    executive summary, and the stakeholder reading each resolved (or failed
    to resolve) their own copy; now all of it comes from `doc`.
    """
    from datetime import datetime, timezone

    from backend.report_builder import _CSS

    assert_localized_document(doc)

    logo_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4"/>
    </svg>"""
    cover = f"""<div class="cover">
        <div class="logo">
            <div class="logo-icon">{logo_svg}</div>
            <span style="font-size:20px;font-weight:700;color:#111827">UKIP</span>
        </div>
        <h1>{doc.title}</h1>
        <p class="meta">{doc.domain_caption}: <b>{doc.domain_name}</b> &nbsp;·&nbsp; {doc.generated_caption}: <b>{doc.generated_at}</b></p>
        <p class="meta" style="margin-top:8px">{doc.stakeholder_lens_caption}: <b>{doc.stakeholder_label}</b></p>
    </div>"""

    # Stakeholder reading leads, exactly as it did when `build()` rendered it
    # ahead of the numbered-section loop; manual notes follow it and precede
    # every numbered section, matching that same original order. Everything
    # after that renders in `doc.sections`' own order, which is already
    # request order — SectionData and SectionError share one sequence (see
    # ReportDocument.sections) precisely so a failed section renders in its
    # own request-order slot instead of trailing every successful one.
    stakeholder = next(
        (s for s in doc.sections if isinstance(s, SectionData) and s.key == "stakeholder_reading"),
        None,
    )
    rest = [
        s for s in doc.sections
        if not (isinstance(s, SectionData) and s.key == "stakeholder_reading")
    ]

    body_sections = [render_html(stakeholder)] if stakeholder is not None else []
    body_sections.extend(
        note_html
        for note in doc.manual_notes
        if (note_html := _manual_note(note, doc.manual_note_default_title))
    )
    for entry in rest:
        if isinstance(entry, SectionError):
            body_sections.append(
                f'<section><h2>{entry.title}</h2>'
                f'<p style="color:#ef4444">{doc.section_error_prefix} {entry.detail}</p></section>'
            )
        else:
            body_sections.append(render_html(entry))

    summary = _executive_summary(doc)
    if summary:
        body_sections.insert(0, summary)
    if doc.disclosure:
        body_sections.insert(
            0, f'<section class="ukip-language-disclosure"><p>{doc.disclosure}</p></section>'
        )

    footer = f'<footer>{doc.generated_by_caption} &nbsp;·&nbsp; {doc.generated_at}</footer>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{doc.title}</title>
  <style>{_CSS}</style>
</head>
<body>
  {cover}
  {"".join(body_sections)}
  {footer}
</body>
</html>"""
