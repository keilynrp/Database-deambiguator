"""
Pure-Python RIS (Research Information Systems) file parser.
RIS format: each record is a series of two-letter tag lines ending with ER --.

Reference: https://en.wikipedia.org/wiki/RIS_(file_format)
"""
from typing import Any

# RIS type code → human-readable entity_type
_TYPE_MAP = {
    "JOUR": "journal_article",
    "JFULL": "journal_article",
    "ABST": "journal_article",
    "BOOK": "book",
    "CHAP": "book_chapter",
    "CONF": "conference_paper",
    "CPAPER": "conference_paper",
    "THES": "thesis",
    "RPRT": "technical_report",
    "MGZN": "magazine_article",
    "NEWS": "news",
    "ELEC": "website",
    "PATENT": "patent",
    "PCOMM": "personal_communication",
    "DATA": "dataset",
    "MISC": "other",
    "GEN": "other",
}

# Maps RIS two-letter tags → internal field names
_TAG_MAP = {
    "TI": "title",
    "T1": "title",
    "CT": "title",
    "BT": "title",
    "AU": "authors",
    "A1": "authors",
    "A2": "editors",
    "A3": "authors",
    "A4": "authors",
    "PY": "year",
    "Y1": "year",
    "DO": "doi",
    "JO": "journal",
    "JF": "journal",
    "J2": "journal",
    "T2": "journal",
    "AB": "abstract",
    "N2": "abstract",
    "KW": "keywords",
    "VL": "volume",
    "IS": "issue",
    "SP": "start_page",
    "EP": "end_page",
    "SN": "issn",
    "UR": "url",
    "L2": "url",
    "PB": "publisher",
    "CY": "address",
    "AD": "institution",
    "LA": "language",
    "N1": "note",
    "ID": "_cite_key",
}

# Tags that can appear multiple times (joined with "; ")
_MULTI_VALUE_TAGS = {"AU", "A1", "A2", "A3", "A4", "KW"}


def parse_ris(content: str) -> list[dict[str, Any]]:
    """Parse a full RIS file and return a list of record dicts."""
    records: list[dict[str, Any]] = []
    current: dict[str, Any] = {}
    multi_buffers: dict[str, list[str]] = {}

    for raw_line in content.splitlines():
        line = raw_line.rstrip()

        # End of record
        if line.startswith("ER") and "  -" in line:
            if current:
                # Flush multi-value fields
                for tag, vals in multi_buffers.items():
                    field = _TAG_MAP.get(tag, tag.lower())
                    current[field] = "; ".join(vals)
                records.append(current)
            current = {}
            multi_buffers = {}
            continue

        # Parse tag line: "XX  - value"
        if len(line) >= 6 and line[2:6] == "  - ":
            tag = line[:2].strip()
            value = line[6:].strip()

            if not value:
                continue

            if tag == "TY":
                current["entity_type"] = _TYPE_MAP.get(value, value.lower())
                current["_ris_type"] = value
            elif tag in _MULTI_VALUE_TAGS:
                multi_buffers.setdefault(tag, []).append(value)
            else:
                mapped = _TAG_MAP.get(tag)
                if mapped:
                    current[mapped] = value

    # Handle file without final ER
    if current:
        for tag, vals in multi_buffers.items():
            field = _TAG_MAP.get(tag, tag.lower())
            current[field] = "; ".join(vals)
        records.append(current)

    return records
