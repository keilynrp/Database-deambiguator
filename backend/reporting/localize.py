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

from backend.i18n import DEFAULT_LANGUAGE
from backend.i18n.catalog import SURFACE_PREFIXES, translate

from .document import LocalizedReportDocument, ReportDocument, SectionError
from .section_data import Meter, Narrative, SectionData, StatGrid, StatItem, Table

__all__ = [
    "localize_section",
    "localize_document",
    "looks_like_key",
    "with_params",
    "resolve_value",
    "assert_localized_section",
    "assert_localized_document",
    "UnresolvedCatalogKeyError",
]


class UnresolvedCatalogKeyError(RuntimeError):
    """A renderer/exporter received owned copy that was never localized.

    Raised by `assert_localized_section` / `assert_localized_document`, which
    every renderer entry point calls instead of resolving keys itself (see
    those functions' docstrings). This is the structural half of the
    localized-document boundary: a renderer that is handed a raw collector
    payload — or a `LocalizedReportDocument` some bypass smuggled an
    unresolved key into — fails loudly here rather than silently shipping a
    catalog key to a reader.
    """


#: Separates a key from its interpolation arguments, as in
#: `report.stat.total.sub.pct?pct=42`. A collector knows the numbers when it
#: builds the payload; the renderer knows the language. Neither knows both, so
#: the key carries the arguments across.
#:
#: The alternative was a second field on every slot — a schema change to
#: SectionData, which the format-parity contract also depends on. This keeps a
#: slot a plain `str`, which is what lets a collector migrate one field at a
#: time. `?` cannot appear in a catalog key, so the split is unambiguous.
_PARAM_SEP = "?"


def looks_like_key(value: Any) -> bool:
    """True when a string is a catalog key rather than literal copy."""
    return isinstance(value, str) and value.startswith(SURFACE_PREFIXES)


def _split_params(value: str) -> tuple[str, dict[str, str]]:
    key, _, raw = value.partition(_PARAM_SEP)
    if not raw:
        return key, {}
    params: dict[str, str] = {}
    for pair in raw.split("&"):
        name, _, val = pair.partition("=")
        if name:
            params[name] = val
    return key, params


def with_params(key: str, **params: object) -> str:
    """Build a key that carries its interpolation arguments.

    Used by collectors: `with_params("report.x.sub", pct=42)`. Resolving it is
    the renderer's job, once it knows the language.
    """
    if not params:
        return key
    encoded = "&".join(f"{name}={value}" for name, value in params.items())
    return f"{key}{_PARAM_SEP}{encoded}"


def _text(value: Any, language: str | None) -> Any:
    """Resolve one slot. Anything that is not a key is returned unchanged."""
    if not looks_like_key(value):
        return value
    key, params = _split_params(value)
    return translate(key, language, **params)


def resolve_value(value: Any, language: str | None) -> Any:
    """Public alias of `_text`, for document-level scalars outside a section.

    Same contract as any `SectionData` field: a literal passes through
    unchanged, a `with_params()`-encoded catalog key resolves. Used by
    `localize_document` for the handful of document-level strings (title,
    stakeholder label, …) that are not part of any section.
    """
    return _text(value, language)


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
        # Cells were once exempt, on the grounds that they hold entity labels,
        # concept names and figures — provider data the system does not own.
        # That describes nearly every table and misses one: the benchmark rule
        # table has a status column the system writes itself, where a key
        # rendered verbatim.
        #
        # So a cell now follows the same rule as every other slot: a surface
        # prefix means key, anything else passes through. Provider data is still
        # untouched, and no longer because of which field it happens to sit in.
        return replace(
            block,
            columns=_tuple(block.columns, language),
            rows=tuple(_tuple(row, language) for row in block.rows),
        )
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


def _first_unresolved_key(*values: Any) -> str | None:
    for value in values:
        if looks_like_key(value):
            return value
    return None


def assert_localized_section(section: SectionData) -> None:
    """Raise if `section` still carries an unresolved owned-copy key.

    The check a renderer runs on entry instead of resolving anything itself
    — see `UnresolvedCatalogKeyError`. Cheap and shallow: it inspects the
    same slots `localize_section` writes (title/takeaway/method/blocks), so
    it catches exactly what a skipped `localize_section` call would leave
    behind, including a raw key inside a block (table cell, stat sub, …).
    """
    culprit = _first_unresolved_key(section.title, section.takeaway, section.method)
    if culprit is None:
        for block in section.blocks:
            if isinstance(block, StatGrid):
                for item in block.items:
                    culprit = _first_unresolved_key(item.label, item.sub)
                    if culprit:
                        break
            elif isinstance(block, Table):
                culprit = _first_unresolved_key(*block.columns, *(c for row in block.rows for c in row))
            elif isinstance(block, Narrative):
                culprit = _first_unresolved_key(block.heading, *block.paragraphs)
            elif isinstance(block, Meter):
                culprit = _first_unresolved_key(block.label)
            if culprit:
                break
    if culprit is not None:
        raise UnresolvedCatalogKeyError(
            f"section {section.key!r} reached a renderer with unresolved catalog "
            f"key {culprit!r} — it was never passed through localize_document()/"
            "localize_section()."
        )


def assert_localized_document(doc: LocalizedReportDocument) -> None:
    """Raise if any section or document-level scalar in `doc` is unresolved.

    `LocalizedReportDocument` should be unconstructible with a raw key in it
    — `localize_document` is its only constructor, and localizes everything —
    but this is the belt to that suspenders: the check a document-level
    renderer runs on entry, so a future bypass (a field added to the
    dataclass and populated without going through `localize_document`) fails
    a test immediately instead of shipping a key to a reader.
    """
    culprit = _first_unresolved_key(
        doc.title,
        doc.domain_name,
        doc.stakeholder_label,
        doc.domain_caption,
        doc.generated_caption,
        doc.stakeholder_lens_caption,
        doc.executive_summary_title,
        doc.manual_note_default_title,
        doc.generated_by_caption,
        doc.section_error_prefix,
        doc.disclosure,
    )
    if culprit is not None:
        raise UnresolvedCatalogKeyError(
            f"LocalizedReportDocument carries unresolved catalog key {culprit!r} "
            "in a document-level field."
        )
    for section in doc.sections:
        if isinstance(section, SectionError):
            culprit = _first_unresolved_key(section.title)
            if culprit is not None:
                raise UnresolvedCatalogKeyError(
                    f"LocalizedReportDocument carries an unresolved catalog key "
                    f"{culprit!r} in a section-error title."
                )
        else:
            assert_localized_section(section)


def localize_document(doc: ReportDocument, language: str | None = None) -> LocalizedReportDocument:
    """The one localization transformation every report format funnels through.

    Resolves every section (via `localize_section`) and every document-level
    scalar (via `resolve_value`) into `language`, once. This is the only way
    to construct a `LocalizedReportDocument` — see that type's docstring for
    why that matters — and the result is asserted clean before it is
    returned, so a bug here fails at the source rather than at whichever
    renderer happens to hit the unresolved field first.

    `disclosure` is None for the default language: an English report has no
    language mixture to explain, so there is nothing to disclose (task 8.5).
    """
    sections = tuple(
        replace(s, title=resolve_value(s.title, language))
        if isinstance(s, SectionError)
        else localize_section(s, language)
        for s in doc.sections
    )
    resolved_language = language or DEFAULT_LANGUAGE
    localized = LocalizedReportDocument(
        language=resolved_language,
        domain_id=doc.domain_id,
        domain_name=doc.domain_name,
        title=resolve_value(doc.title, language),
        generated_at=doc.generated_at,
        stakeholder_label=resolve_value(doc.stakeholder_label, language),
        domain_caption=resolve_value("report.cover.domain", language),
        generated_caption=resolve_value("report.cover.generated", language),
        stakeholder_lens_caption=resolve_value("report.stakeholder.lens", language),
        executive_summary_title=resolve_value("report.summary.title", language),
        manual_note_default_title=resolve_value("report.manual.default_title", language),
        generated_by_caption=resolve_value("report.footer.generated_by", language),
        section_error_prefix=resolve_value("report.error.section_prefix", language),
        disclosure=(
            resolve_value("report.disclosure.analysis_language", language)
            if resolved_language != DEFAULT_LANGUAGE
            else None
        ),
        sections=sections,
        # Pass through unchanged: a manual note's title/content is analyst-
        # authored free text, never a catalog key candidate — see
        # document.ManualNote.
        manual_notes=doc.manual_notes,
    )
    assert_localized_document(localized)
    return localized
