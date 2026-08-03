"""Backend message catalog — the JSON projection of the frontend catalog.

`frontend/app/i18n/translations.ts` is the single source of truth for every
user-facing string in the system. It is TypeScript, so the backend cannot
import it; `scripts/generate-i18n-projection.mjs` emits the JSON files in this
package, and a CI gate fails when they disagree with their source.

This module deliberately exposes only where the catalog lives and which
languages exist. Lookup (`translate`) arrives with the catalog module in phase
3 of the backend-i18n-message-catalog change.
"""

from pathlib import Path

CATALOG_DIR = Path(__file__).resolve().parent

#: English is the reference language: keys are English-derived, and the parity
#: gate checks every other language against it.
LANGUAGES = ("en", "es")

DEFAULT_LANGUAGE = "en"

__all__ = ["CATALOG_DIR", "LANGUAGES", "DEFAULT_LANGUAGE"]
