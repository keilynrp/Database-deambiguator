"""
UKIP Transformation Engine — safe mini-language for bulk field edits.

Supported expressions (case-insensitive function names):
  value.trim()
  value.upper()
  value.lower()
  value.title()
  value.split(",")[0]        — first token by delimiter
  value.replace("old","new") — literal substring replacement
  value.prefix("Dr. ")       — prepend string
  value.suffix(" PhD")       — append string
  value.strip_html()         — remove <tag> patterns
  value.to_number()          — cast to numeric string, or empty on failure
  value.slice(0,10)          — substring [start:end]
  value.strip("chars")       — strip specific characters

No eval(), no exec(), no import. Pure regex parse + dispatch.
"""
import re
import html
from typing import Any, Optional


# ── Expression parsing ─────────────────────────────────────────────────────────

# Matches: value.funcname(args)
_EXPR_RE = re.compile(
    r"^value\s*\.\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*)\)\s*$",
    re.DOTALL,
)

# Matches: ["..."] or [N] subscript after base expression
_SUBSCRIPT_RE = re.compile(r'^(.*)\[([^\]]+)\]\s*$', re.DOTALL)

# Matches quoted string: "..." or '...'
_QSTR_RE = re.compile(r'^["\'](.*)["\']\s*$', re.DOTALL)

# Matches integer
_INT_RE = re.compile(r'^-?\d+$')


class TransformError(ValueError):
    """Raised for invalid expressions or unsupported functions."""


def _parse_str_arg(raw: str) -> str:
    """Strip surrounding quotes from a string argument."""
    raw = raw.strip()
    m = _QSTR_RE.match(raw)
    if not m:
        raise TransformError(f"Expected a quoted string, got: {raw!r}")
    return m.group(1)


def _parse_int_arg(raw: str) -> int:
    raw = raw.strip()
    if not _INT_RE.match(raw):
        raise TransformError(f"Expected an integer, got: {raw!r}")
    return int(raw)


def _split_args(raw: str) -> list[str]:
    """Split comma-separated args respecting quoted strings."""
    args = []
    depth = 0
    current = []
    in_quote = None
    for ch in raw:
        if ch in ('"', "'") and in_quote is None:
            in_quote = ch
            current.append(ch)
        elif ch == in_quote:
            in_quote = None
            current.append(ch)
        elif ch == ',' and in_quote is None and depth == 0:
            args.append("".join(current).strip())
            current = []
        else:
            if ch == '(' and in_quote is None:
                depth += 1
            elif ch == ')' and in_quote is None:
                depth -= 1
            current.append(ch)
    if current:
        args.append("".join(current).strip())
    return args


def _apply_func(func_name: str, args_raw: str, value: str) -> str:
    """Dispatch a single function call on value."""
    fn = func_name.lower()
    args = _split_args(args_raw) if args_raw.strip() else []

    if fn == "trim":
        return value.strip()
    elif fn == "upper":
        return value.upper()
    elif fn == "lower":
        return value.lower()
    elif fn == "title":
        return value.title()
    elif fn == "replace":
        if len(args) != 2:
            raise TransformError("replace() requires exactly 2 arguments: replace('old','new')")
        old = _parse_str_arg(args[0])
        new = _parse_str_arg(args[1])
        return value.replace(old, new)
    elif fn == "prefix":
        if len(args) != 1:
            raise TransformError("prefix() requires exactly 1 argument")
        pfx = _parse_str_arg(args[0])
        return pfx + value if not value.startswith(pfx) else value
    elif fn == "suffix":
        if len(args) != 1:
            raise TransformError("suffix() requires exactly 1 argument")
        sfx = _parse_str_arg(args[0])
        return value + sfx if not value.endswith(sfx) else value
    elif fn == "strip_html":
        text = re.sub(r'<[^>]+>', '', value)
        return html.unescape(text).strip()
    elif fn == "to_number":
        cleaned = re.sub(r'[^\d.\-]', '', value)
        try:
            float(cleaned)
            return cleaned
        except ValueError:
            return ""
    elif fn == "slice":
        if len(args) not in (1, 2):
            raise TransformError("slice() requires 1 or 2 integer arguments: slice(start) or slice(start,end)")
        start = _parse_int_arg(args[0])
        end = _parse_int_arg(args[1]) if len(args) == 2 else None
        return value[start:end]
    elif fn == "split":
        if len(args) != 1:
            raise TransformError("split() requires exactly 1 argument: split(',')")
        delim = _parse_str_arg(args[0])
        # Returns the full list as a pipe-joined string; subscript applied after
        return delim.join(value.split(delim))  # returns original — subscript handles indexing
    elif fn == "strip":
        if len(args) == 0:
            return value.strip()
        chars = _parse_str_arg(args[0])
        return value.strip(chars)
    else:
        raise TransformError(
            f"Unknown function '{func_name}'. Supported: trim, upper, lower, title, "
            "replace, prefix, suffix, strip_html, to_number, slice, split, strip"
        )


def apply_expression(expr: str, value: Any) -> str:
    """
    Parse and evaluate a transformation expression on a single value.
    Returns the transformed string.
    Raises TransformError on invalid expressions.
    """
    if value is None:
        return ""
    value = str(value)

    expr = expr.strip()

    # Check for subscript: value.split(",")[0]
    sub_match = _SUBSCRIPT_RE.match(expr)
    subscript_index: Optional[int] = None
    if sub_match:
        inner_expr = sub_match.group(1).strip()
        idx_raw = sub_match.group(2).strip()
        subscript_index = _parse_int_arg(idx_raw)
        expr = inner_expr

    # Parse main expression: value.funcname(args)
    m = _EXPR_RE.match(expr)
    if not m:
        raise TransformError(
            f"Invalid expression: {expr!r}. Must be value.function(args) — "
            "e.g. value.trim(), value.replace('old','new')"
        )

    func_name = m.group(1)
    args_raw = m.group(2)

    # For split with subscript, handle specially
    if func_name.lower() == "split" and subscript_index is not None:
        args = _split_args(args_raw)
        if len(args) != 1:
            raise TransformError("split() requires exactly 1 argument")
        delim = _parse_str_arg(args[0])
        parts = value.split(delim)
        try:
            return parts[subscript_index].strip()
        except IndexError:
            return ""

    result = _apply_func(func_name, args_raw, value)

    # Apply subscript to generic result (list-like operations)
    if subscript_index is not None:
        parts = result.split()  # fallback
        try:
            return parts[subscript_index]
        except IndexError:
            return ""

    return result


def validate_expression(expr: str) -> None:
    """
    Validate an expression without applying it.
    Raises TransformError if invalid.
    """
    apply_expression(expr, "test_value")


# ── ALLOWED FIELDS (columns on RawEntity that can be transformed) ─────────────

TRANSFORMABLE_FIELDS = {
    "primary_label", "secondary_label", "canonical_id",
    "entity_type", "domain", "validation_status",
    "enrichment_source", "enrichment_concepts",
}
