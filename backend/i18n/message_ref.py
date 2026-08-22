"""A persisted reference to owned copy, resolved at read time (#269).

`catalog.translate()` resolves a key the instant it is called — right for a
report or an API response, built and returned within one request. It is wrong
for a row written to the database: the language active when a background
worker wrote the row is not the language of whoever reads it later, so
translating at write time freezes a locale into storage and discards the key
that would have let a later reader choose differently.

This module is the write-time counterpart: a small, JSON-safe reference that
names a catalog key and its interpolation params without resolving either,
so persistence and resolution stay two separate steps.

**Not `reporting.localize.with_params()`.** That module's `key?a=b&c=d` string
encoding is a reasonable trade for a `SectionData` field, which must stay a
plain `str` because the format-parity contract depends on it — but a `?`- and
`&`-delimited string is exactly the kind of encoding that breaks silently the
day a param value contains one of its own delimiters, and long-lived stored
data does not get a second chance to notice. A JSON-bearing field has no such
constraint, so the reference here is a small explicit object instead: `type`
names the shape (so a foreign dict already living in the same JSON blob is
never mistaken for one of these), `key` is the catalog key, `params` are its
interpolation arguments — always inserted verbatim by `translate()`, never
translated themselves, so provider- or user-authored text passed as a param
can never be misread as owned copy.

Two representations, two field shapes:

  * `make_message_ref` / `is_message_ref` / `resolve_message` /
    `resolve_message_list` — for a JSON-bearing field that may hold a single
    ref, or a list of them (`enrichment_failure.evidence`,
    `.recommendations`).
  * `looks_like_catalog_key` / `resolve_plain_or_key` — for a plain string
    column with no interpolation params, where the value itself can safely be
    the bare catalog key (`CatalogPortal.title`, `.description`).

Both tolerate a legacy value that predates this module — a plain rendered
string, already in the language it was written in — by passing it through
unchanged. Neither ever raises: a malformed ref is a corrupted read, not a
crash, and the failure mode is to degrade the one field, not the response.
"""

from __future__ import annotations

import logging
from typing import Any

from .catalog import SURFACE_PREFIXES, translate

logger = logging.getLogger(__name__)

__all__ = [
    "MESSAGE_REF_TYPE",
    "make_message_ref",
    "is_message_ref",
    "resolve_message",
    "resolve_message_list",
    "looks_like_catalog_key",
    "resolve_plain_or_key",
]

#: The type marker every persisted reference carries. Deliberately not just
#: "the dict has a `key` field" — a foreign JSON object sharing that field
#: name would then silently be treated as owned copy. Versioned by name
#: rather than a separate integer: a future incompatible shape gets its own
#: marker (`"i18n_ref_v2"`) and old rows keep resolving under this one.
MESSAGE_REF_TYPE = "i18n_ref"


def _loggable(value: object, limit: int = 80) -> str:
    """Render an untrusted value safe to put in a log line (`py/log-injection`).

    A persisted ref can carry params sourced from provider data or an
    exception message — text this process did not author — so anything
    derived from one is untrusted the same way a request parameter is.
    """
    text = str(value)[:limit]
    return "".join(char if char.isprintable() else "�" for char in text)


def make_message_ref(key: str, **params: object) -> dict[str, Any]:
    """Build a persisted reference: a catalog key plus its interpolation params.

    Nothing here resolves anything — that is `resolve_message`'s job, once a
    reader knows the language. `params` are stored as given and are never
    treated as keys themselves, so passing a provider's title or an
    exception's message as a param is exactly the safe way to carry it.
    """
    return {"type": MESSAGE_REF_TYPE, "key": key, "params": dict(params)}


def is_message_ref(value: Any) -> bool:
    """True when `value` has the exact shape `make_message_ref` produces.

    Shallow and cheap on purpose: this runs on every field read from
    persisted JSON, most of which are not refs at all (a legacy row, or any
    other key in the same object). A dict missing the marker, or carrying it
    under a different value, is data — not a ref this module owns.
    """
    return (
        isinstance(value, dict)
        and value.get("type") == MESSAGE_REF_TYPE
        and isinstance(value.get("key"), str)
    )


def resolve_message(value: Any, language: str | None) -> Any:
    """Resolve one persisted value into `language`.

    `value` may be a `make_message_ref()` dict (resolved), a legacy plain
    string (returned unchanged — it is already rendered, in whatever
    language it was written in), or anything else (returned unchanged: this
    is not the field this module owns, and passing it through is safer than
    guessing).

    Never raises. A ref whose `key` lacks a backend surface prefix, or whose
    `params` is not a mapping, is a malformed read — logged and resolved to
    the empty string rather than allowed to fail the whole response over one
    corrupted field.
    """
    if not is_message_ref(value):
        return value

    key = value["key"]
    params = value.get("params", {})
    if not isinstance(params, dict) or not key.startswith(SURFACE_PREFIXES):
        logger.warning(
            "i18n: malformed persisted message ref (key=%s): %s",
            _loggable(key),
            _loggable(value),
        )
        return ""

    try:
        return translate(key, language, **params)
    except Exception:  # noqa: BLE001 — a corrupted ref degrades one field, not the response
        logger.warning(
            "i18n: failed to resolve persisted message ref %s", _loggable(key)
        )
        return ""


def resolve_message_list(values: Any, language: str | None) -> Any:
    """`resolve_message`, applied per item, for a field that stores a list.

    `recommendations` is the motivating case: a legacy row holds a list of
    rendered strings, a new one a list of refs, and either can appear
    unchanged if `values` is not a list at all (pass through — not this
    module's field).
    """
    if not isinstance(values, list):
        return values
    return [resolve_message(item, language) for item in values]


def looks_like_catalog_key(value: Any) -> bool:
    """True when a plain string column holds a bare catalog key rather than
    literal text.

    Same test `reporting.localize.looks_like_key()` uses, reimplemented here
    rather than imported: that module is report-specific machinery, and this
    one field shape — a string column with nothing to interpolate — needs
    only the prefix check, not `with_params()`'s param encoding.
    """
    return isinstance(value, str) and value.startswith(SURFACE_PREFIXES)


def resolve_plain_or_key(value: Any, language: str | None) -> Any:
    """Resolve a plain string column that may hold a bare catalog key.

    For `CatalogPortal.title` / `.description`: a new row's value is the key
    itself (no params needed, so no reason to reach for
    `make_message_ref()`'s dict shape on a column that is not JSON to begin
    with); a legacy row's value is already the rendered literal, and is
    returned unchanged. `None` passes through for the nullable columns.
    """
    if not looks_like_catalog_key(value):
        return value
    return translate(value, language)
