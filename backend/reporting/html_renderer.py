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

from backend.reporting.localize import localize_section
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


def render_html(section: SectionData, language: str | None = None) -> str:
    """One section as a self-contained document exhibit.

    The shape carries the presentation contract: the ordinal identifies the
    exhibit, the heading asserts the finding, the label stays available as
    secondary text, and the method footer travels underneath so a reader who
    quotes a figure out of the section can still see what it is.
    """
    # Resolve any catalog keys the collector emitted, once, here — see
    # backend/reporting/localize.py for why this is not threaded through
    # the collectors instead.
    section = localize_section(section, language)

    body = "".join(_render_block(block) for block in section.blocks)
    return (
        "<section>\n    "
        + _exhibit_label(section)
        + f"\n    <h2>{escape(section.takeaway)}</h2>\n    "
        + body
        + f'\n    <p class="method">{escape(section.method)}</p>\n</section>'
    )
