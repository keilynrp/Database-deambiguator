"""Report-surface strings come from the catalog, not from literals.

Phase 6 group A. These modules feed generated reports, which default to English
by decision (2026-07-31) and ignore `Accept-Language`, so migrating them changes
nothing a reader sees today — it moves the text into the catalog so phase 8 can
select a language.

The tests assert two separable things:

* the rendered output is **English**, which is the observable change;
* the text **came from the catalog**, which is the point of the migration.

The second needs its own assertion. A module that simply had its Spanish
literals rewritten in English would satisfy the first and none of the intent, so
each module is also exercised with the catalog monkeypatched — if the output
does not follow, the call site is still hard-coded.
"""

import pytest

from backend.i18n import catalog as catalog_module
from backend.services.impact_projection import ImpactProjectionService

#: The service reads `kpis` / `quality` / `top_entities`, not flat fields. A flat
#: fixture yields `total_entities == 0` and silently takes the empty branch, so a
#: test claiming to exercise a populated portfolio would exercise neither.
_SNAPSHOT_STRONG = {
    "domain_id": 1,
    "kpis": {"total_entities": 500, "enrichment_pct": 96.0, "avg_citations": 40.0},
    "quality": {"average": 0.92},
    "top_entities": [{"id": i, "citation_count": 400 - i} for i in range(10)],
}
_SNAPSHOT_EMPTY = {"kpis": {"total_entities": 0}, "quality": {}, "top_entities": []}

_SPANISH_MARKERS = (
    "proyección",
    "portafolio",
    "Importa",
    "enriquece",
    "señal",
    "línea base",
    "brechas",
    "supuestos",
    "registros",
)


def _projection_text(snapshot: dict) -> str:
    result = ImpactProjectionService.build_from_snapshot(snapshot)
    return " ".join(
        str(result.get(field, "")) for field in ("recommendation", "brief_angle", "explanation")
    )


class TestImpactProjectionIsEnglish:
    @pytest.mark.parametrize(
        "snapshot,label", [(_SNAPSHOT_STRONG, "populated"), (_SNAPSHOT_EMPTY, "empty")]
    )
    def test_no_spanish_remains(self, snapshot, label):
        text = _projection_text(snapshot)

        found = [marker for marker in _SPANISH_MARKERS if marker.lower() in text.lower()]
        assert not found, f"the {label} projection still reads Spanish: {found} in {text!r}"

    def test_every_field_is_populated(self):
        """A migration that silently emptied a field would pass a Spanish check."""
        result = ImpactProjectionService.build_from_snapshot(_SNAPSHOT_STRONG)

        for field in ("recommendation", "brief_angle", "explanation"):
            assert result.get(field), f"{field} is empty after the migration"


class TestImpactProjectionReadsTheCatalog:
    """The assertion that distinguishes migration from translation-in-place."""

    def test_output_follows_the_catalog(self, monkeypatch):
        sentinel = "SENTINEL-FROM-CATALOG"
        # Captured before patching: inside the replacement, the attribute is the
        # replacement itself and the real loader is no longer reachable.
        real_keys = [
            key
            for key in catalog_module._load_catalog.__wrapped__("en")
            if key.startswith("report.impact_projection.")
        ]
        monkeypatch.setattr(
            catalog_module,
            "_load_catalog",
            lambda language: {key: sentinel for key in real_keys},
        )

        text = _projection_text(_SNAPSHOT_STRONG)

        assert sentinel in text, (
            "changing the catalog did not change the output — the call site still "
            "holds a literal, so the strings were rewritten rather than migrated"
        )

    def test_the_keys_this_module_uses_exist_in_both_languages(self):
        for language in ("en", "es"):
            catalog = catalog_module._load_catalog.__wrapped__(language)
            keys = [k for k in catalog if k.startswith("report.impact_projection.")]
            assert len(keys) == 10, (
                f"expected 10 report.impact_projection.* keys in {language}, found {len(keys)}"
            )
