"""Per-request locale resolution.

Two resolvers, deliberately not one.

`resolve_language` is the general API chain: an explicit parameter, then
`Accept-Language`, then the configured default.

`resolve_report_language` **cannot see the header** — it does not take one. A
report is produced for an audience, not for whoever pressed the button, so
honouring the operator's browser locale would leak their language into someone
else's document without anyone asking for it. Making that structural rather
than a convention matters: a resolver that accepted the header and chose not to
read it is one refactor away from reading it.

Nothing consults these yet. Report generation gains its parameter in phase 8 of
the backend-i18n-message-catalog change, and email in phase 7.
"""

from __future__ import annotations

import logging

from fastapi import Header, Query

from . import DEFAULT_LANGUAGE, LANGUAGES

logger = logging.getLogger(__name__)

__all__ = ["resolve_language", "resolve_report_language", "language_dependency"]

#: RFC 9110 caps quality values at three decimal places in the range 0–1.
_MAX_QUALITY = 1.0


def _normalise(tag: str) -> str:
    """`es-MX` and `ES` both mean `es` here — we carry no regional variants."""
    return tag.strip().lower().split("-", 1)[0]


def _parse_accept_language(header: str) -> list[str]:
    """Return supported languages, best first.

    The header is attacker-controllable and arrives malformed often enough that
    parsing it must never raise: anything unreadable is skipped rather than
    failing the request. An entry with `q=0` means *not acceptable* and is
    dropped rather than ranked last.
    """
    candidates: list[tuple[float, int, str]] = []

    for position, part in enumerate(header.split(",")):
        segments = part.split(";")
        tag = _normalise(segments[0])
        if not tag or tag not in LANGUAGES:
            continue

        quality = _MAX_QUALITY
        for segment in segments[1:]:
            name, _, raw = segment.partition("=")
            if name.strip().lower() != "q":
                continue
            try:
                quality = float(raw.strip())
            except ValueError:
                # A malformed q is not a reason to discard an otherwise valid
                # tag; treat it as unspecified.
                quality = _MAX_QUALITY
            break

        if quality <= 0:
            continue
        candidates.append((quality, -position, tag))

    # Highest quality first; ties keep the order the client wrote them in.
    return [tag for _, _, tag in sorted(candidates, reverse=True)]


def resolve_language(explicit: str | None, accept_language: str | None) -> str:
    """Resolve a language for a general API request.

    Order: explicit parameter, then `Accept-Language`, then the default.

    An explicit but unsupported language resolves to the default and does
    **not** fall through to the header. Falling through would answer a question
    the caller did not ask — they named a language, and it is unavailable —
    hiding that behind a plausible-looking result.
    """
    if explicit:
        candidate = _normalise(explicit)
        if candidate in LANGUAGES:
            return candidate
        logger.warning(
            "i18n: unsupported language %r requested; using %r instead",
            explicit,
            DEFAULT_LANGUAGE,
        )
        return DEFAULT_LANGUAGE

    if accept_language:
        for tag in _parse_accept_language(accept_language):
            return tag

    return DEFAULT_LANGUAGE


def resolve_report_language(explicit: str | None) -> str:
    """Resolve the language of a generated report.

    Takes no header, by design — see the module docstring. Omitting the
    parameter yields the configured default, which preserves the behaviour of
    every caller written before the parameter existed.
    """
    if explicit:
        candidate = _normalise(explicit)
        if candidate in LANGUAGES:
            return candidate
        logger.warning(
            "i18n: unsupported report language %r requested; generating in %r instead",
            explicit,
            DEFAULT_LANGUAGE,
        )
    return DEFAULT_LANGUAGE


def language_dependency(
    language: str | None = Query(
        default=None,
        description="Language for catalog-sourced text (en, es). Falls back to Accept-Language, then English.",
        max_length=35,
    ),
    accept_language: str | None = Header(default=None),
) -> str:
    """FastAPI dependency exposing the general precedence chain to routes."""
    return resolve_language(explicit=language, accept_language=accept_language)
