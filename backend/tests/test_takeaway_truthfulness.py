"""A takeaway may only cite figures its own section renders.

The presentation contract requires this, and it is the requirement that stops a
report asserting something a reader cannot check. Enforcing that a takeaway
*exists* is a type concern and lives in `section_data`; enforcing that it is
*supportable* needs data, which is what this module supplies.

That distinction is the whole point. Run against an empty database, every
section returns its empty-state takeaway, cites no figures, and passes — a test
that cannot fail. The fixtures below exist so the assertion has something to
bite on. When this was first written against the default fixtures it reported
thirteen passes and had verified nothing; populating the database immediately
surfaced a real violation in `top_secondary_labels`.
"""
import re

import pytest

from backend import models
from backend.reporting.section_data import Meter, Narrative, StatGrid, Table

_NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")


def _figures(text) -> set[str]:
    """Numeric tokens in a string, comma separators removed."""
    return {token.replace(",", "") for token in _NUMBER.findall(str(text))}


def _rendered_figures(section) -> set[str]:
    """Every number a reader can see in the section's own blocks."""
    seen: set[str] = set()
    for block in section.blocks:
        if isinstance(block, StatGrid):
            for item in block.items:
                seen |= _figures(item.value) | _figures(item.sub or "")
        elif isinstance(block, Table):
            for row in block.rows:
                for cell in row:
                    seen |= _figures(cell)
        elif isinstance(block, Narrative):
            seen |= _figures(block.heading)
            for paragraph in block.paragraphs:
                seen |= _figures(paragraph)
        elif isinstance(block, Meter):
            seen |= _figures(block.pct) | _figures(round(block.pct))
    return seen


def _collect(db, key: str):
    from backend import report_builder as rb

    collect = rb.SECTION_COLLECTORS[key]
    if key == "institutional_benchmark":
        return collect(db, "default", None, None, None)
    if key in rb._BENCHMARK_ORG_SECTIONS:
        return collect(db, "default", None, None)
    return collect(db, "default", None)


@pytest.fixture
def populated(db_session):
    """Enough data that the metric-bearing sections have something to report.

    Deliberately uneven: 30 of 40 valid, 22 enriched, and three classifications
    at 25/10/5 so concentration is a real figure rather than a tie.
    """
    for i in range(40):
        db_session.add(
            models.RawEntity(
                primary_label=f"Entity {i}",
                secondary_label="Alpha" if i < 25 else "Beta" if i < 35 else "Gamma",
                domain="default",
                source="test",
                validation_status="valid" if i < 30 else "pending",
                enrichment_status="completed" if i < 22 else "pending",
                enrichment_citation_count=i * 3 if i < 22 else None,
            )
        )
    db_session.commit()
    return db_session


@pytest.fixture
def populated_records(db_session):
    """The sections backed by their own tables rather than by RawEntity.

    Separate from `populated` because these need no entities at all, and mixing
    them would make a failure ambiguous about which seed caused it.
    """
    import json
    from datetime import datetime, timezone

    # 7 authority records: 4 confirmed, 3 pending, so the backlog is a real
    # figure and confirmed != pending.
    for i in range(7):
        db_session.add(
            models.AuthorityRecord(
                field_name="author",
                original_value=f"Author {i}",
                authority_source="test",
                authority_id=f"A{i}",
                canonical_label=f"Canonical {i}",
                confidence=0.9 if i < 4 else 0.4,
                status="confirmed" if i < 4 else "pending",
            )
        )

    # 5 journals: 3 in DOAJ, 2 charging an APC.
    for i in range(5):
        db_session.add(
            models.JournalMetric(
                issn_l=f"1234-000{i}",
                display_name=f"Journal {i}",
                two_yr_mean_citedness=1.5 + i,
                is_in_doaj=i < 3,
                apc_usd=1200 if i >= 3 else None,
            )
        )

    for i in range(4):
        db_session.add(
            models.HarmonizationLog(
                step_id=f"step-{i}",
                step_name=f"Normalise field {i}",
                records_updated=10 * (i + 1),
                executed_at=datetime.now(timezone.utc),
            )
        )

    db_session.add(
        models.AnalysisContext(
            domain_id="default",
            label="agentic-chat:What is the coverage?",
            context_snapshot=json.dumps(
                {
                    "question": "What is the coverage?",
                    "answer": "Coverage is 55%.",
                    "trace": {"tools_used": ["search", "analytics"]},
                    "sources": [{"label": "Entity 1"}],
                }
            ),
        )
    )
    db_session.commit()
    return db_session


_DATA_BEARING = [
    "entity_stats",
    "enrichment_coverage",
    "top_secondary_labels",
]

#: Sections seeded from their own tables. Kept as a separate list so a missing
#: fixture surfaces as a failure here rather than as a silently skipped section.
_RECORD_BACKED = [
    "authority_control",
    "journal_portfolio",
    "harmonization_log",
    "agentic_trace",
]


@pytest.mark.parametrize("key", _DATA_BEARING)
def test_takeaway_cites_only_rendered_figures(populated, key):
    section = _collect(populated, key)
    orphans = _figures(section.takeaway) - _rendered_figures(section)
    assert not orphans, (
        f"{key}: takeaway cites {sorted(orphans)}, which the section does not "
        f"render — a reader cannot check it.\n"
        f"  takeaway: {section.takeaway}\n"
        f"  rendered: {sorted(_rendered_figures(section))}"
    )


@pytest.mark.parametrize("key", _DATA_BEARING)
def test_populated_sections_actually_cite_something(populated, key):
    """Guard the guard.

    Without this, a takeaway that stopped citing figures — or a fixture that
    stopped populating — would make the test above vacuously true, which is the
    failure mode this suite has hit more than once.
    """
    section = _collect(populated, key)
    assert _figures(section.takeaway), (
        f"{key}: takeaway cites no figures on populated data, so the "
        f"truthfulness check above proves nothing: {section.takeaway!r}"
    )


@pytest.mark.parametrize("key", _DATA_BEARING)
def test_empty_sections_state_absence_and_rank_lowest(db_session, key):
    """The empty path is a separate assertion, not the default one."""
    from backend.reporting.section_data import Materiality

    section = _collect(db_session, key)
    assert section.materiality is Materiality.EMPTY
    assert section.takeaway.strip()
    assert not _figures(section.takeaway) - _rendered_figures(section)


def test_share_of_classified_is_rendered_not_only_asserted(populated):
    """Regression: the takeaway once cited a share the section never showed.

    The table had a column called "Share" holding each label's proportion of the
    *largest* label — so the top row always read 100% — while the takeaway used
    the proportion of *all classified entities*. Two quantities, one word, and
    the figure that led the sentence appeared nowhere a reader could check.
    """
    section = _collect(populated, "top_secondary_labels")
    table = next(b for b in section.blocks if isinstance(b, Table))
    assert "Share of classified" in table.columns
    assert "Relative weight" in table.columns

    share_idx = table.columns.index("Share of classified")
    weight_idx = table.columns.index("Relative weight")
    # The distinction is the point: relative weight tops out at 100% by
    # construction, share of classified does not.
    assert table.rows[0][weight_idx] == "100%"
    assert table.rows[0][share_idx] != "100%"
    assert table.rows[0][share_idx].rstrip("%") in section.takeaway


@pytest.mark.parametrize("key", _RECORD_BACKED)
def test_record_backed_takeaway_cites_only_rendered_figures(populated_records, key):
    section = _collect(populated_records, key)
    orphans = _figures(section.takeaway) - _rendered_figures(section)
    assert not orphans, (
        f"{key}: takeaway cites {sorted(orphans)}, which the section does not "
        f"render, so a reader cannot check it. "
        f"takeaway={section.takeaway!r} "
        f"rendered={sorted(_rendered_figures(section))}"
    )


@pytest.mark.parametrize("key", _RECORD_BACKED)
def test_record_backed_sections_actually_cite_something(populated_records, key):
    section = _collect(populated_records, key)
    assert _figures(section.takeaway), (
        f"{key}: takeaway cites no figures on populated data, so the check "
        f"above proves nothing: {section.takeaway!r}"
    )
