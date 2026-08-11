"""Resolve catalog keys inside a section payload, once, at the render boundary.

#209 translated section titles by replacing them at the single point every
section passes through, keyed by section id. That worked because the id *is* the
key. The rest of a section's text — stat labels, table headers, method notes,
narrative paragraphs — is built inside each collector, and there is no id to
derive a key from.

Threading a language into all nineteen collectors was the alternative. It was
rejected for the reason the title seam existed in the first place: a collector
added later can forget to translate, and nothing catches it. Here a renderer
localizes everything it is handed, so omission is not expressible.

**No schema change.** A field still holds a `str`. If that string starts with one
of the backend's surface prefixes it is a catalog key and gets resolved;
otherwise it passes through untouched. So a collector migrates one field at a
time, and a payload with no keys renders exactly as it does today.

The prefixes are ours (`report.`, `email.`, …) and a human-authored label does
not begin with one, so the test is unambiguous in practice as well as in theory.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from backend.i18n.catalog import SURFACE_PREFIXES, translate

from .section_data import Meter, Narrative, SectionData, StatGrid, StatItem, Table

__all__ = ["localize_section", "looks_like_key"]


def looks_like_key(value: Any) -> bool:
    """True when a string is a catalog key rather than literal copy."""
    return isinstance(value, str) and value.startswith(SURFACE_PREFIXES)


def _text(value: Any, language: str | None) -> Any:
    """Resolve one slot. Anything that is not a key is returned unchanged."""
    if not looks_like_key(value):
        return value
    return translate(value, language)


def _tuple(values: tuple, language: str | None) -> tuple:
    return tuple(_text(v, language) for v in values)


def _block(block: Any, language: str | None) -> Any:
    if isinstance(block, StatGrid):
        return replace(
            block,
            items=tuple(
                replace(
                    item,
                    label=_text(item.label, language),
                    # `value` is a figure the collector computed. It is data, not
                    # copy, and translating it would change what the report says.
                    sub=_text(item.sub, language),
                )
                for item in block.items
                if isinstance(item, StatItem)
            ),
        )
    if isinstance(block, Table):
        # Only headers. Cells hold entity labels, concept names and figures —
        # provider data the system does not own.
        return replace(block, columns=_tuple(block.columns, language))
    if isinstance(block, Narrative):
        return replace(
            block,
            heading=_text(block.heading, language),
            paragraphs=_tuple(block.paragraphs, language),
        )
    if isinstance(block, Meter):
        return replace(block, label=_text(block.label, language))
    return block


def localize_section(section: SectionData, language: str | None = None) -> SectionData:
    """Return `section` with every catalog key resolved into `language`.

    Idempotent on already-literal payloads, which is what makes it safe to call
    unconditionally from every renderer while the collectors migrate one at a
    time.
    """
    return replace(
        section,
        title=_text(section.title, language),
        takeaway=_text(section.takeaway, language),
        method=_text(section.method, language),
        blocks=tuple(_block(b, language) for b in section.blocks),
    )
