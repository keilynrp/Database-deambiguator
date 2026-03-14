"""
Pure-Python BibTeX parser.
Supports the most common entry types: article, book, inproceedings, conference,
phdthesis, mastersthesis, techreport, misc.

Returns a list of dicts with normalized keys.
"""
import re
from typing import Any

# BibTeX entry type → human-readable entity_type
_ENTRY_TYPES = {
    "article":        "journal_article",
    "book":           "book",
    "inproceedings":  "conference_paper",
    "conference":     "conference_paper",
    "proceedings":    "proceedings",
    "phdthesis":      "phd_thesis",
    "mastersthesis":  "masters_thesis",
    "techreport":     "technical_report",
    "incollection":   "book_chapter",
    "misc":           "other",
}

# Maps BibTeX field keys → our internal field names
_FIELD_MAP = {
    "title":       "title",
    "author":      "authors",
    "editor":      "editors",
    "year":        "year",
    "journal":     "journal",
    "booktitle":   "journal",
    "publisher":   "publisher",
    "doi":         "doi",
    "url":         "url",
    "eprint":      "url",
    "abstract":    "abstract",
    "keywords":    "keywords",
    "volume":      "volume",
    "number":      "issue",
    "pages":       "pages",
    "issn":        "issn",
    "isbn":        "isbn",
    "address":     "address",
    "month":       "month",
    "note":        "note",
    "school":      "institution",
    "institution": "institution",
}


def _strip_braces(value: str) -> str:
    """Remove outer braces and LaTeX commands from a BibTeX value."""
    value = value.strip()
    # Remove outer quotes or braces
    if (value.startswith('"') and value.endswith('"')) or \
       (value.startswith('{') and value.endswith('}')):
        value = value[1:-1]
    # Remove nested braces but keep content
    value = re.sub(r'\{([^{}]*)\}', r'\1', value)
    # Collapse multiple whitespace
    value = re.sub(r'\s+', ' ', value).strip()
    return value


def _parse_entry(entry_text: str) -> dict[str, Any] | None:
    """Parse a single BibTeX entry block into a dict."""
    # Match @type{key, ...}
    header_match = re.match(r'@(\w+)\s*\{\s*([^,\s]*)\s*,', entry_text, re.IGNORECASE)
    if not header_match:
        return None

    entry_type = header_match.group(1).lower()
    cite_key = header_match.group(2).strip()

    # Parse key = value pairs — handle nested braces
    fields: dict[str, str] = {}
    body = entry_text[header_match.end():]

    # State machine to extract key = value pairs
    i = 0
    while i < len(body):
        # Skip whitespace and commas
        while i < len(body) and body[i] in ' \t\n\r,':
            i += 1
        if i >= len(body) or body[i] == '}':
            break

        # Read key
        key_match = re.match(r'(\w+)\s*=\s*', body[i:])
        if not key_match:
            i += 1
            continue
        key = key_match.group(1).lower()
        i += key_match.end()

        # Read value (handle braces and quotes)
        if i >= len(body):
            break
        if body[i] == '{':
            depth = 0
            start = i
            while i < len(body):
                if body[i] == '{':
                    depth += 1
                elif body[i] == '}':
                    depth -= 1
                    if depth == 0:
                        i += 1
                        break
                i += 1
            value = body[start:i].strip()
        elif body[i] == '"':
            i += 1
            start = i
            while i < len(body) and body[i] != '"':
                i += 1
            value = '"' + body[start:i] + '"'
            i += 1
        else:
            # Bare word / number
            start = i
            while i < len(body) and body[i] not in ',}\n':
                i += 1
            value = body[start:i].strip()

        if value:
            fields[key] = _strip_braces(value)

    result: dict[str, Any] = {
        "_cite_key":   cite_key,
        "_entry_type": entry_type,
        "entity_type": _ENTRY_TYPES.get(entry_type, entry_type),
    }
    for bib_key, val in fields.items():
        mapped = _FIELD_MAP.get(bib_key, bib_key)
        result[mapped] = val

    return result


def parse_bibtex(content: str) -> list[dict[str, Any]]:
    """Parse a full BibTeX file and return a list of record dicts."""
    entries = []

    # Split on @type{ boundaries (keep the @ delimiter)
    raw_blocks = re.split(r'(?=@\w+\s*\{)', content)

    for block in raw_blocks:
        block = block.strip()
        if not block or not block.startswith('@'):
            continue
        # Skip @comment, @preamble, @string
        if re.match(r'@(comment|preamble|string)\b', block, re.IGNORECASE):
            continue
        try:
            entry = _parse_entry(block)
            if entry:
                entries.append(entry)
        except Exception:
            continue  # skip malformed entries

    return entries
