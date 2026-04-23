"""
Parser for OpenAlex/Web of Science-style plaintext exports.

These files are line-oriented, use two-character tags, and delimit records with
`ER`. A typical file starts with `FN` and `VR` header lines and then contains
records like:

PT J
AU Author Name
   Second Author
TI Paper title
...
ER
"""
from __future__ import annotations

import re
from typing import Any


_ENTITY_TYPE_MAP = {
    "article": "journal_article",
    "book": "book",
    "book-chapter": "book_chapter",
    "book chapter": "book_chapter",
    "conference-paper": "conference_paper",
    "conference paper": "conference_paper",
    "proceedings-article": "conference_paper",
    "review": "journal_article",
    "dataset": "dataset",
    "thesis": "thesis",
    "report": "technical_report",
    "preprint": "preprint",
}

_MULTI_VALUE_TAGS = {"AU", "AF", "C1", "C3", "RI", "OI"}


def looks_like_wos_plaintext(content: str) -> bool:
    """Heuristic detector for the plaintext bibliographic format."""
    if not content.strip():
        return False

    lines = [line.rstrip() for line in content.splitlines() if line.strip()]
    if len(lines) < 4:
        return False

    joined = "\n".join(lines[:40])
    has_header = "FN " in joined and "VR " in joined
    has_record_markers = "\nPT " in f"\n{joined}" and "\nER" in f"\n{content}"
    has_core_fields = any(token in joined for token in ("\nAU ", "\nAF ", "\nTI ", "\nSO "))
    return has_header and has_record_markers and has_core_fields


def _collapse(values: list[str]) -> str | None:
    cleaned = [value.strip() for value in values if value and value.strip()]
    return "; ".join(cleaned) if cleaned else None


def _first(values: list[str]) -> str | None:
    for value in values:
        value = value.strip()
        if value:
            return value
    return None


def _parse_int(value: str | None) -> int | None:
    if not value:
        return None
    digits = re.sub(r"[^\d]", "", value)
    return int(digits) if digits else None


def _map_entity_type(document_type: str | None) -> str:
    if not document_type:
        return "publication"
    normalized = document_type.strip().lower()
    return _ENTITY_TYPE_MAP.get(normalized, "publication")


def _normalize_record(raw: dict[str, list[str]], source_name: str | None) -> dict[str, Any]:
    record: dict[str, Any] = {}

    title = _first(raw.get("TI", []))
    if title:
        record["title"] = title

    authors = _collapse(raw.get("AU", []))
    if authors:
        record["authors"] = authors

    full_authors = _collapse(raw.get("AF", []))
    if full_authors:
        record["full_authors"] = full_authors

    journal = _first(raw.get("SO", []))
    if journal:
        record["journal"] = journal

    language = _first(raw.get("LA", []))
    if language:
        record["language"] = language

    document_type = _first(raw.get("DT", []))
    record["entity_type"] = _map_entity_type(document_type)
    if document_type:
        record["document_type"] = document_type

    institution = _collapse(raw.get("C3", [])) or _collapse(raw.get("C1", []))
    if institution:
        record["institution"] = institution

    corresponding_author = _first(raw.get("RP", []))
    if corresponding_author:
        record["corresponding_author"] = corresponding_author

    researcher_ids = _collapse(raw.get("RI", []))
    if researcher_ids:
        record["researcher_ids"] = researcher_ids

    orcids = _collapse(raw.get("OI", []))
    if orcids:
        record["orcids"] = orcids

    funding = _collapse(raw.get("FU", []))
    if funding:
        record["funding"] = funding

    year = _first(raw.get("PY", []))
    if year:
        record["year"] = year

    volume = _first(raw.get("VL", []))
    if volume:
        record["volume"] = volume

    issue = _first(raw.get("IS", []))
    if issue:
        record["issue"] = issue

    start_page = _first(raw.get("BP", []))
    if start_page:
        record["start_page"] = start_page

    end_page = _first(raw.get("EP", []))
    if end_page:
        record["end_page"] = end_page

    pages = _first(raw.get("PG", []))
    if pages:
        record["pages"] = pages

    publisher = _first(raw.get("PU", []))
    if publisher:
        record["publisher"] = publisher

    issn = _first(raw.get("SN", []))
    if issn:
        record["issn"] = issn

    eissn = _first(raw.get("EI", []))
    if eissn:
        record["eissn"] = eissn

    doi = _first(raw.get("DI", []))
    if doi:
        record["doi"] = doi

    pub_month = _first(raw.get("PD", []))
    if pub_month:
        record["month"] = pub_month

    pubmed_id = _first(raw.get("PM", []))
    if pubmed_id:
        record["pubmed_id"] = pubmed_id

    open_access = _first(raw.get("OA", []))
    if open_access:
        record["open_access"] = open_access

    retrieved_at = _first(raw.get("DA", []))
    if retrieved_at:
        record["retrieved_at"] = retrieved_at

    citation_count = _parse_int(_first(raw.get("CT", [])))
    if citation_count is not None:
        record["citation_count"] = citation_count

    reference_count = _parse_int(_first(raw.get("NR", [])))
    if reference_count is not None:
        record["reference_count"] = reference_count

    pub_type = _first(raw.get("PT", []))
    if pub_type:
        record["_plaintext_type"] = pub_type

    if source_name:
        record["_source_name"] = source_name

    source_version = _first(raw.get("VR", []))
    if source_version:
        record["_source_version"] = source_version

    # Preserve every original tag so exports, detail views, and future mappers
    # can recover the full plaintext payload without reparsing the source file.
    for tag, values in raw.items():
        collapsed = _collapse(values)
        if collapsed:
            record[f"raw_{tag.lower()}"] = collapsed

    return record


def parse_wos_plaintext(content: str) -> list[dict[str, Any]]:
    """Parse a plaintext bibliographic export into normalized science records."""
    source_name: str | None = None
    current: dict[str, list[str]] = {}
    current_tag: str | None = None
    records: list[dict[str, Any]] = []

    for raw_line in content.splitlines():
        line = raw_line.rstrip("\r\n")

        if not line.strip():
            continue

        if line.startswith("ER"):
            if current:
                records.append(_normalize_record(current, source_name))
            current = {}
            current_tag = None
            continue

        if line[:2] in {"FN", "VR"} and len(line) >= 3 and line[2].isspace():
            tag = line[:2]
            value = line[3:].strip()
            if tag == "FN":
                source_name = value or source_name
            if value:
                current.setdefault(tag, []).append(value)
            continue

        if line.startswith("   ") and current_tag:
            value = line.strip()
            if value:
                current.setdefault(current_tag, []).append(value)
            continue

        if len(line) >= 3 and line[:2].isalnum() and line[2].isspace():
            tag = line[:2]
            value = line[3:].strip()
            current_tag = tag
            if value or tag in _MULTI_VALUE_TAGS:
                current.setdefault(tag, []).append(value)

    if current:
        records.append(_normalize_record(current, source_name))

    return records
