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


@lru_cache(maxsize=None)
def _load_catalog(language: str) -> dict[str, str]:
    """Read one language's projection. Cached — the file never changes at runtime.

    The whitelist is not redundant with `_resolve_language`. `language` reaches
    this function from `?language=` and `Accept-Language`, and it is
    interpolated into a filesystem path; that every current caller sanitises it
    first is a **non-local** invariant — true because of a function elsewhere,
    invisible to a reader of this one, and one direct call away from being
    false. CodeQL flagged the flow as `py/path-injection` and was right to.
    Checking here makes the path underivable from anything but a known language.
    """
    if language not in LANGUAGES:
        logger.warning(
            "i18n: refusing to load a catalog for unsupported language %r",
            language,
        )
        return {}

    path = CATALOG_DIR / f"catalog.{language}.json"
    if not path.exists():
        logger.warning(
            "i18n catalog missing for language %r at %s; falling back to keys",
            language,
            path,
        )
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_language(language: str | None) -> str:
    if language is None:
        return DEFAULT_LANGUAGE
    if language in LANGUAGES:
        return language
    logger.warning(
        "i18n: unsupported language %r requested; rendering in %r instead",
        language,
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
                "i18n: key %r missing in %r; served %r instead",
                key,
                resolved,
                DEFAULT_LANGUAGE,
            )

    if template is None:
        logger.warning("i18n: key %r is not in the catalog; rendering the key itself", key)
        return key

    return _interpolate(template, params) if params else template
