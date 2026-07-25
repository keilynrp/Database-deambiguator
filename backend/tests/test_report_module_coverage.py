"""Report coverage for authority, coauthorship and journals
(extend-report-module-coverage).

Each section is authored once against the format-neutral payload from
`unify-report-format-coverage`, so the parity guard proves it reached all four
formats. These tests cover the collectors' semantics: what the section says, what
it must never say, and that it never leaks across tenants.
"""
from backend import models, report_builder
from backend.reporting.section_data import (
    Narrative,
    SectionData,
    StatGrid,
    Table,
)


# ── 1. Authority control ────────────────────────────────────────────────────

def _authority_record(**kw):
    base = dict(
        field_name="brand_capitalized",
        original_value="acme corp",
        canonical_label="ACME Corporation",
        confidence=0.9,
        status="confirmed",
        resolution_status="exact_match",
        review_required=False,
    )
    base.update(kw)
    return models.AuthorityRecord(**base)


def _seed_authority(db, org_id=None) -> None:
    """Two confirmed, three pending review (one ambiguous, two unresolved)."""
    rows = [
        _authority_record(org_id=org_id),
        _authority_record(org_id=org_id, original_value="globex"),
        _authority_record(
            org_id=org_id, original_value="initech", status="pending",
            resolution_status="ambiguous", review_required=True,
            confidence=0.55, nil_reason="multiple_candidates",
        ),
        _authority_record(
            org_id=org_id, original_value="umbrella", status="pending",
            resolution_status="unresolved", review_required=True,
            confidence=0.2, nil_reason="no_candidate_above_threshold",
        ),
        _authority_record(
            org_id=org_id, original_value="soylent", status="pending",
            resolution_status="unresolved", review_required=True,
            confidence=0.1, nil_reason="no_candidate_above_threshold",
        ),
    ]
    for r in rows:
        db.add(r)
    db.commit()


def test_collect_authority_control_reports_counts(db_session):
    """1.1 — total, confirmed and pending-review counts."""
    _seed_authority(db_session)
    section = report_builder.collect_authority_control(db_session, "default", None)

    assert isinstance(section, SectionData)
    assert section.key == "authority_control"

    grid = next(b for b in section.blocks if isinstance(b, StatGrid))
    labels = {i.label: i.value for i in grid.items}
    assert labels["Authority Records"] == "5"
    assert labels["Confirmed"] == "2"
    assert labels["Pending Review"] == "3"
    assert "Mean Confidence" in labels


def test_collect_authority_control_lists_unresolved_conflicts(db_session):
    """1.3 — unresolved conflicts carry their confidence and nil_reason."""
    _seed_authority(db_session)
    section = report_builder.collect_authority_control(db_session, "default", None)

    tables = [b for b in section.blocks if isinstance(b, Table)]
    conflicts = next(t for t in tables if "Value" in t.columns)
    joined = " ".join(" ".join(r) for r in conflicts.rows)
    assert "initech" in joined
    assert "multiple_candidates" in joined          # nil_reason is surfaced
    assert "no_candidate_above_threshold" in joined
    # confirmed records are not conflicts
    assert "globex" not in joined


def test_collect_authority_control_states_reliability_impact(db_session):
    """1.5 — a review backlog produces a prose reliability statement."""
    _seed_authority(db_session)
    section = report_builder.collect_authority_control(db_session, "default", None)

    narrative = next(b for b in section.blocks if isinstance(b, Narrative))
    prose = " ".join(narrative.paragraphs).lower()
    assert "3" in " ".join(narrative.paragraphs)    # the backlog size is stated
    assert "review" in prose


def test_collect_authority_control_empty_state_is_explanatory(db_session):
    """1.7 — no records must read as 'not run', never as 'no conflicts found'.

    Absence of authority data is not evidence of clean identity resolution;
    saying so would be a false reassurance in a decision brief.
    """
    section = report_builder.collect_authority_control(db_session, "default", None)

    narrative = next(b for b in section.blocks if isinstance(b, Narrative))
    prose = " ".join(narrative.paragraphs).lower()
    assert "no authority" in prose or "not been run" in prose or "no records" in prose
    # must NOT claim a clean result
    assert "no conflicts" not in prose


def test_collect_authority_control_is_tenant_scoped(db_session):
    """1.8 — another org's records never appear."""
    _seed_authority(db_session, org_id=1)
    db_session.add(_authority_record(org_id=2, original_value="other-org-secret",
                                     status="pending", resolution_status="unresolved",
                                     review_required=True, confidence=0.3))
    db_session.commit()

    section = report_builder.collect_authority_control(db_session, "default", 1)
    blob = " ".join(
        " ".join(" ".join(r) for r in b.rows) if isinstance(b, Table)
        else " ".join(b.paragraphs) if isinstance(b, Narrative)
        else " ".join(f"{i.label} {i.value}" for i in b.items)
        for b in section.blocks
    )
    assert "other-org-secret" not in blob
    grid = next(b for b in section.blocks if isinstance(b, StatGrid))
    assert {i.label: i.value for i in grid.items}["Authority Records"] == "5"


# ── Section-count ceiling ───────────────────────────────────────────────────

def test_every_public_section_can_be_requested_at_once(client, auth_headers):
    """The request cap must accommodate the whole published vocabulary.

    The picker selects every section by default, so a cap below the number of
    public sections turns "select all + export" into a 422. Pydantic does not
    validate field defaults, so this only breaks for real callers — which is
    exactly why it needs an explicit test rather than trusting the default.
    """
    from backend.routers.reports import _PUBLIC_REPORT_SECTIONS

    resp = client.post(
        "/reports/generate",
        json={"domain_id": "default", "sections": list(_PUBLIC_REPORT_SECTIONS)},
        headers=auth_headers,
    )
    assert resp.status_code == 200, (
        f"requesting all {len(_PUBLIC_REPORT_SECTIONS)} public sections failed: "
        f"{resp.text[:300]}"
    )
