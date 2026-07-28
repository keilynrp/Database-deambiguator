"""Format-neutral section payload types (unify-report-format-coverage, phase 1).

A section is authored once as a `SectionData` of format-neutral blocks; each
renderer turns those blocks into HTML / Excel / PPTX. These tests pin the
construction and validation contract of the payload before any renderer or
migration depends on it.
"""
import pytest

from backend.reporting.section_data import (
    Materiality,
    Meter,
    Narrative,
    SectionData,
    StatGrid,
    StatItem,
    Table,
)


def test_statgrid_holds_labelled_items():
    grid = StatGrid(items=(
        StatItem(label="Total", value="1,240"),
        StatItem(label="Enriched", value="60%", sub="744 of 1,240"),
    ))
    assert grid.items[1].sub == "744 of 1,240"


def test_table_rows_must_match_column_count():
    Table(columns=("Journal", "NIF"), rows=(("Nature", "9.1"), ("Cell", "8.3")))
    with pytest.raises(ValueError):
        Table(columns=("Journal", "NIF"), rows=(("Nature",),))


def test_table_bar_column_must_be_in_range():
    Table(columns=("A", "B"), rows=(("1", "2"),), bar_column=1)
    with pytest.raises(ValueError):
        Table(columns=("A", "B"), rows=(("1", "2"),), bar_column=2)


def test_meter_pct_is_bounded():
    Meter(label="Coverage", pct=0)
    Meter(label="Coverage", pct=100)
    with pytest.raises(ValueError):
        Meter(label="Coverage", pct=101)
    with pytest.raises(ValueError):
        Meter(label="Coverage", pct=-1)


def test_narrative_requires_a_heading():
    Narrative(heading="Executive reading", paragraphs=("A.", "B."))
    with pytest.raises(ValueError):
        Narrative(heading="", paragraphs=("A.",))


def test_section_data_carries_key_title_and_blocks():
    section = SectionData(
        key="entity_stats",
        title="Entity Statistics",
        blocks=(
            StatGrid(items=(StatItem(label="Total", value="10"),)),
            Narrative(heading="Reading", paragraphs=("All good.",)),
        ),
    )
    assert section.key == "entity_stats"
    assert len(section.blocks) == 2


def test_section_data_rejects_empty_key():
    with pytest.raises(ValueError):
        SectionData(key="", title="X", blocks=())


def test_blocks_are_immutable():
    item = StatItem(label="Total", value="10")
    with pytest.raises(Exception):
        item.value = "20"  # frozen


# ── Presentation contract (report-presentation) ───────────────────────────────


def test_materiality_orders_lead_above_everything():
    """The executive summary sorts by materiality, so the ordinal has to sort."""
    assert Materiality.LEAD > Materiality.NOTABLE > Materiality.ROUTINE > Materiality.EMPTY


def test_materiality_sorts_lead_first_when_reversed():
    levels = [Materiality.ROUTINE, Materiality.LEAD, Materiality.EMPTY, Materiality.NOTABLE]
    assert sorted(levels, reverse=True)[0] is Materiality.LEAD
    assert sorted(levels, reverse=True)[-1] is Materiality.EMPTY


def test_section_carries_takeaway_method_and_materiality():
    section = SectionData(
        key="authority_control",
        title="Authority Control",
        blocks=(),
        takeaway="912 of 1,000 authority records confirmed; 88 await review",
        method="Counts scoped to this domain and organization, as of the last resolution run.",
        materiality=Materiality.LEAD,
    )
    assert section.takeaway.startswith("912 of 1,000")
    assert "as of" in section.method
    assert section.materiality is Materiality.LEAD


def test_presentation_fields_default_so_unmigrated_collectors_still_construct():
    """The eleven pre-contract collectors must keep working during migration.

    Blank-rejection lands with task 3.7, when the defaults come off; asserting
    it here would fail every collector that has not been migrated yet.
    """
    section = SectionData(key="entity_stats", title="Entity Statistics", blocks=())
    assert section.takeaway == ""
    assert section.method == ""
    assert section.materiality is Materiality.ROUTINE


def test_has_presentation_distinguishes_migrated_from_default():
    bare = SectionData(key="k", title="T", blocks=())
    assert bare.has_presentation is False

    partial = SectionData(key="k", title="T", blocks=(), takeaway="Something happened")
    assert partial.has_presentation is False, "a takeaway without a method is not the contract"

    whitespace = SectionData(key="k", title="T", blocks=(), takeaway="  ", method="  ")
    assert whitespace.has_presentation is False, "whitespace is not a disclosure"

    full = SectionData(key="k", title="T", blocks=(), takeaway="A finding", method="A source")
    assert full.has_presentation is True


def test_presentation_fields_are_immutable():
    section = SectionData(key="k", title="T", blocks=(), takeaway="A finding")
    with pytest.raises(Exception):
        section.takeaway = "something else"  # frozen
