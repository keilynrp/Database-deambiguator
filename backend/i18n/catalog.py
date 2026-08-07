"""Message catalog lookup.

The catalog is the JSON projection of `frontend/app/i18n/translations.ts`
committed under this package by `scripts/generate-i18n-projection.mjs`. One key
space is shared with the frontend; the backend owns the part of it carrying a
surface prefix, so a report can never accidentally render a sidebar label.

Two failure modes are deliberately different:

* **A missing key is data.** It renders as its own key and logs a warning.
  Raising would turn a cosmetic defect into a failed report — an artefact that
  is expensive to regenerate — and half-translated output still delivers.
* **A malformed key is a defect at the call site.** It raises, because it is
  deterministic: any test exercising that path fails, every time, before the
  code reaches a reader.
"""

from __future__ import annotations

import json
import logging
from functools import lru_cache

from . import CATALOG_DIR, DEFAULT_LANGUAGE, LANGUAGES

logger = logging.getLogger(__name__)

#: The backend owns these namespaces inside the shared key space. A key without
#: one of them belongs to the frontend, and rendering it server-side would put
#: UI chrome into a PDF.
#:
#: One prefix per surface the backend actually serves, rather than one blanket
#: `backend.`: the guard's job is to keep frontend chrome out of server-rendered
#: artefacts, and a key that names its surface also says whether it is allowed
#: to reach a PDF. The first three came from the report-and-email framing of
#: #209; the rest were added in phase 6, when migrating the strings showed that
#: framing covered only 18 of 70.
SURFACE_PREFIXES = (
    "report.",  # PDF / PPTX / Excel artefact text
    "email.",  # outbound mail subjects and bodies
    "validation.",  # record-level failure reasons and remediation hints
    "field.",  # field labels, help and examples served to the import wizard
    "chat.",  # agentic chat replies and suggested follow-ups
    "dashboard.",  # dashboard titles and descriptions served over the API
    "preset.",  # audience preset names, descriptions and export CTAs
)

__all__ = ["translate", "SURFACE_PREFIXES"]


#: Every catalog path this module will ever open, built from the LANGUAGES
#: constant and nothing else. A request value is only ever used as a *key* into
#: this map — it never reaches path construction, so there is no flow to taint.
#:
#: The first attempt was a whitelist (`if language not in LANGUAGES: return {}`)
#: immediately before `CATALOG_DIR / f"catalog.{language}.json"`. It closed the
#: hole but CodeQL still reported `py/path-injection`, correctly: the parameter
#: still reached the path expression, and a guard several lines up is an
#: argument about reachability rather than a structural impossibility. It also
#: made things worse in one respect — the rejection branch logged the hostile
#: value, adding a fifth `py/log-injection` finding.
_CATALOG_PATHS = {language: CATALOG_DIR / f"catalog.{language}.json" for language in LANGUAGES}


def _loggable(value: object, limit: int = 80) -> str:
    """Render an untrusted value safe to put in a log line.

    A key or language arrives from the request, and a newline in it forges a
    second log record — `py/log-injection`. `%r` already escapes newlines, but
    relying on the format specifier means the protection disappears the moment
    someone switches it to `%s`. Doing it here makes it a property of the value.
    """
    text = str(value)[:limit]
    return "".join(char if char.isprintable() else "�" for char in text)


@lru_cache(maxsize=None)
def _load_catalog(language: str) -> dict[str, str]:
    """Read one language's projection. Cached — the file never changes at runtime."""
    path = _CATALOG_PATHS.get(language)
    if path is None:
        logger.warning(
            "i18n: no catalog for unsupported language '%s'", _loggable(language)
        )
        return {}

    if not path.exists():
        logger.warning(
            "i18n catalog missing for language '%s'; falling back to keys",
            _loggable(language),
        )
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_language(language: str | None) -> str:
    if language is None:
        return DEFAULT_LANGUAGE
    if language in LANGUAGES:
        return language
    logger.warning(
        "i18n: unsupported language '%s' requested; rendering in '%s' instead",
        _loggable(language),
        DEFAULT_LANGUAGE,
    )
    return DEFAULT_LANGUAGE


def _interpolate(template: str, params: dict[str, object]) -> str:
    """Replace each `{name}` the caller supplied, and nothing else.

    Deliberately not `str.format`. That would raise on a placeholder the caller
    did not supply, and would also choke on any catalog string containing a
    literal brace. This mirrors the frontend's `replaceAll` so the same message
    renders identically on both sides, and an unsupplied placeholder stays
    visible instead of failing the render.
    """
    for name, value in params.items():
        template = template.replace("{" + name + "}", str(value))
    return template


def translate(key: str, language: str | None = None, **params: object) -> str:
    """Return the catalog text for `key` in `language`, interpolating `params`.

    Interpolated values are inserted verbatim: a concept name, a journal title
    or a provider name is data supplied by someone else, not copy this system
    owns, and translating it would misattribute words to a provider.

    Raises:
        ValueError: if `key` carries no backend surface prefix.
    """
    if not isinstance(key, str) or not key.startswith(SURFACE_PREFIXES):
        raise ValueError(
            f"i18n key {key!r} has no backend surface prefix; expected one of "
            f"{', '.join(SURFACE_PREFIXES)}. Keys outside these namespaces belong "
            f"to the frontend and must not be rendered server-side."
        )

    resolved = _resolve_language(language)
    template = _load_catalog(resolved).get(key)

    if template is None and resolved != DEFAULT_LANGUAGE:
        # One-sided keys are a CI failure in the parity gate, not a runtime
        # crash: serve the reference language rather than the raw key.
        template = _load_catalog(DEFAULT_LANGUAGE).get(key)
        if template is not None:
            logger.warning(
                "i18n: key '%s' missing in '%s'; served '%s' instead",
                _loggable(key),
                _loggable(resolved),
                DEFAULT_LANGUAGE,
            )

    if template is None:
        logger.warning(
            "i18n: key '%s' is not in the catalog; rendering the key itself",
            _loggable(key),
        )
        return key

    return _interpolate(template, params) if params else template
