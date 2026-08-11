"""`entity_stats` sources its copy from the catalog (#268).

First section migrated onto the localize seam. It carries every field type the
other eighteen use — stat labels, stat sub-labels, table headers, method and an
empty-state takeaway — so getting it right here is what makes the rest
mechanical.

**The composed takeaway is deliberately not migrated.** It bakes English plural
agreement into the f-string, for two counts that inflect independently:

    f"{valid} of {_plural(total, 'entity', 'entities')} "
    f"pass{'es' if valid == 1 else ''} validation "
    f"({pct}%); {pending} remain{'s' if pending == 1 else ''} unresolved"

A catalog key cannot carry that, Spanish inflects differently, and rephrasing to
avoid it would change what English readers see — which task 8.4 of #209 already
established is not an improvement to make silently. It needs a plural-aware
mechanism, which is its own change.
"""

from __future__ import annotations

import pytest

from backend.i18n import catalog as catalog_module
from backend.report_builder import collect_entity_stats
from backend.reporting.localize import localize_section, looks_like_key


@pytest.fixture()
def section(db_session):
    return collect_entity_stats(db_session, "default", None)


class TestTheCollectorEmitsKeys:
    """The seam only works if the collector stops emitting literals."""

    def test_stat_labels_are_keys(self, section):
        grid = next(b for b in section.blocks if hasattr(b, "items"))

        for item in grid.items:
            assert looks_like_key(item.label), f"{item.label!r} is still a literal"

    def test_table_headers_are_keys(self, section):
        table = next(b for b in section.blocks if hasattr(b, "columns"))

        for column in table.columns:
            assert looks_like_key(column), f"{column!r} is still a literal"

    def test_the_method_note_is_a_key(self, section):
        assert looks_like_key(section.method)

    def test_figures_are_not_keys(self, section):
        """A value is data the collector computed, never copy."""
        grid = next(b for b in section.blocks if hasattr(b, "items"))

        for item in grid.items:
            assert not looks_like_key(item.value)


class TestRenderedOutput:
    @pytest.mark.parametrize(
        "language,expected",
        [("en", "Total Entities"), ("es", "Entidades Totales")],
    )
    def test_the_stat_label_follows_the_language(self, section, language, expected):
        out = localize_section(section, language)
        grid = next(b for b in out.blocks if hasattr(b, "items"))

        assert grid.items[0].label == expected

    @pytest.mark.parametrize(
        "language,expected",
        [("en", "Validation Status"), ("es", "Estado de Validación")],
    )
    def test_the_table_header_follows_the_language(self, section, language, expected):
        out = localize_section(section, language)
        table = next(b for b in out.blocks if hasattr(b, "columns"))

        assert table.columns[0] == expected

    def test_english_output_is_unchanged_from_before_the_migration(self, section):
        """Task 8.4's lesson: a migration must not alter what English readers see."""
        out = localize_section(section, "en")
        grid = next(b for b in out.blocks if hasattr(b, "items"))
        table = next(b for b in out.blocks if hasattr(b, "columns"))

        assert [i.label for i in grid.items] == [
            "Total Entities",
            "Valid",
            "Pending",
            "Enriched",
        ]
        assert table.columns == ("Validation Status", "Count", "Distribution")
        assert out.method.startswith("Counts are scoped to this domain and organization.")


class TestInterpolatedSubLabels:
    """`{pct}% of total` interpolates a number, which is language-neutral."""

    @pytest.mark.parametrize("language", ["en", "es"])
    def test_the_placeholder_is_substituted(self, section, language):
        """Asserting `"%" in sub` does not discriminate.

        An unsubstituted `{pct}% of total` also contains a `%`, so that check
        passes whether or not the arguments reach `translate`. Caught by a
        mutation that dropped them: 28 tests stayed green. The placeholder's
        absence is the property that separates the two.
        """
        out = localize_section(section, language)
        grid = next(b for b in out.blocks if hasattr(b, "items"))
        subs = [i.sub for i in grid.items if i.sub]

        assert subs, "the section produced no sub-labels to check"
        for sub in subs:
            assert "{pct}" not in sub, f"{language}: placeholder never substituted: {sub!r}"
            assert not looks_like_key(sub), f"{language}: rendered as a raw key: {sub!r}"
        assert any(s[0].isdigit() for s in subs), (
            f"{language}: no sub-label carries a number: {subs}"
        )


class TestTheTextComesFromTheCatalog:
    def test_output_follows_the_catalog(self, section, monkeypatch):
        sentinel = "SENTINEL-STATS"
        real = catalog_module._load_catalog.__wrapped__("en")
        keys = [k for k in real if k.startswith("report.stat.entity_stats.")]
        assert keys, "no report.stat.entity_stats.* keys in the catalog"
        monkeypatch.setattr(
            catalog_module, "_load_catalog", lambda language: {k: sentinel for k in keys}
        )

        out = localize_section(section, "en")
        grid = next(b for b in out.blocks if hasattr(b, "items"))

        assert grid.items[0].label == sentinel
