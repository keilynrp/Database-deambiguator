"""A Spanish report renders Spanish copy, not English that resolved cleanly.

`test_report_render_boundary.py` says this in its own docstring: it catches an
unresolved KEY, not untranslated English, and a key replaced by an English
literal keeps it green. That is exactly how the stakeholder reading shipped —
its copy moved into the catalog in #284, every key resolved without leaking,
and the whole section still rendered in English because the renderer was never
told which language to resolve into.

So this asserts the complement, and does it from the catalog rather than from
hardcoded sentences: for each migrated key, the Spanish copy must appear in a
Spanish report and the English copy must not. Hardcoding the sentences would
make the test pass on a wording it agrees with rather than on the catalog the
report actually reads.

Params are stripped before comparison — `translate()` substitutes them, so the
rendered text contains numbers where the catalog holds `{placeholders}`. What
both sides share is the literal text between placeholders; the longest such run
is the anchor, because several of these sentences open with a placeholder and
would otherwise anchor on the empty string.

**Two cases corroborate rather than isolate.** The authority backlog sentence is
a strict substring of the stakeholder one — deliberately, they say the same
thing — so no anchor can distinguish them by searching the whole document.
Dropping the language argument makes both fail, and the stakeholder section is
the culprit in each. Read a failure in `report.narrative.authority.backlog.*`
as "one of these two sections is wrong", not as a location.

Mutation-checked: removing `language=` from the stakeholder call in `build()`
fails two of these cases. It leaves `test_report_render_boundary.py` entirely
green, which is the gap this file exists to close.

#268 final residual pass added a second, hand-run mutation check: reverting
`collect_topic_clusters`'s takeaway to its pre-#268 raw f-string (the exact
literal this batch replaced with `_counted("report.takeaway.topics", ...)`)
fails `test_the_spanish_copy_is_what_renders[report.takeaway.topics.other]`
— the Spanish anchor `"» es el concepto más frecuente, con el"` never
appears, because the mutated payload carries the English sentence verbatim
regardless of language. `TestCountAgreement` below pins the same defect as an
always-on regression test, since a hand-run mutation is not something CI can
repeat on its own.
"""

from __future__ import annotations

import json
import re

import pytest

from backend import models, report_builder
from backend.i18n.catalog import translate
from backend.reporting.localize import resolve_value

pytestmark = pytest.mark.reporting

#: Sections needed for the keys below to render at all. Two of them —
#: topic_clusters and collaboration_graph — are absent from the render-boundary
#: guard's own list, which is why nothing checked their copy until now.
_SECTIONS = [
    "entity_stats",
    "enrichment_coverage",
    "impact_projection",
    "authority_control",
    "topic_clusters",
    "collaboration_graph",
    # #268 final residual pass: harmonization_log, institutional_benchmark,
    # journal_portfolio and agentic_trace all carried owned copy that was
    # still a raw f-string (or, for agentic_trace's method, not a catalog key
    # at all) rather than something localize_section could resolve.
    "harmonization_log",
    "institutional_benchmark",
    "journal_portfolio",
    "agentic_trace",
    "top_secondary_labels",
]

#: Keys this batch migrated, each of which renders with the fixture below.
_MIGRATED = [
    "report.takeaway.enrichment_coverage",
    "report.method.topic_clusters",
    "report.takeaway.impact",
    "report.stat.impact.sub.range",
    "report.stat.impact.sub.stability",
    "report.narrative.authority.backlog.other",
    "report.narrative.authority.provisional",
    "report.stakeholder.identity_backlog.other",
    # #268 final residual pass.
    "report.takeaway.topics.other",
    "report.status.harmonization.applied",
    "report.col.harmonization_log.step",
    "report.col.harmonization_log.status",
    "report.stat.benchmark.sub.rules_satisfied.other",
    "report.col.authority.share",
    "report.stat.authority.sub.awaiting_decision",
    "report.bool.yes",
    "report.stat.journal.sub.open_access_listed.one",
    "report.method.trace",
    "report.takeaway.trace",
    "report.col.top_secondary_labels.label",
]


def _literal_anchor(key: str, language: str) -> str:
    """The longest run of literal text in a catalog entry.

    Not the leading run: several of these sentences open with a placeholder
    ("{count} de {total} registros …"), where a prefix is the empty string and
    an assertion on it passes against any output at all. The longest segment
    between placeholders is both non-empty and distinctive, and it is free of
    the substitution that makes a rendered sentence differ from its catalog
    form.
    """
    segments = re.split(r"\{[^}]*\}", translate(key, language))
    return max(segments, key=len).strip()


def _seed(db) -> None:
    for idx in range(4):
        db.add(models.RawEntity(
            primary_label=f"Record {idx}", domain="default",
            validation_status="valid" if idx else "pending",
            enrichment_status="completed",
            enrichment_concepts="knowledge graph; ontology",
            enrichment_citation_count=100 + idx,
            enrichment_source="openalex",
            secondary_label="Review",
            quality_score=0.8,
        ))
    # `pending` counts review_required, not status — seeding status alone leaves
    # the branch that carries the reliability prose unreached, and the test
    # passes without ever rendering what it claims to check.
    for idx in range(3):
        db.add(models.AuthorityRecord(
            org_id=None, field_name="primary_label",
            original_value=f"Record {idx}", authority_source="wikidata",
            authority_id=f"Q{idx}", canonical_label=f"Canonical {idx}",
            confidence=0.30 + idx / 100, status="pending",
            resolution_status="ambiguous", review_required=True,
        ))
    # harmonization_log / journal_portfolio / agentic_trace (#268): each of
    # these needs its own table populated, or its section renders its empty
    # state and never reaches the copy this batch migrated.
    db.add(models.HarmonizationLog(
        step_id="normalize_labels", step_name="Normalize labels",
        records_updated=4, fields_modified="primary_label",
    ))
    db.add(models.JournalMetric(
        org_id=None, issn_l="issn-x", display_name="Nature Methods",
        normalized_impact_factor=4.10, nif_field="cs",
        nif_bayes=4.05, nif_ci_low=3.60, nif_ci_high=4.55,
        works_2yr=8, apc_usd=1500, is_in_doaj=True,
    ))
    db.add(models.AnalysisContext(
        domain_id="default",
        label="agentic-chat:What is the coverage?",
        context_snapshot=json.dumps({
            "question": "What is the coverage?",
            "answer": "Coverage is 55%.",
            "trace": {"tools_used": ["search", "analytics"]},
            "sources": [{"label": "Entity 1"}],
        }),
    ))
    db.commit()


@pytest.fixture
def spanish_report(db_session) -> str:
    _seed(db_session)
    return report_builder.build(
        db_session, "default", _SECTIONS, org_id=None, language="es"
    )


@pytest.mark.parametrize("key", _MIGRATED)
def test_the_spanish_copy_is_what_renders(spanish_report, key):
    spanish = _literal_anchor(key, "es")
    assert spanish, f"{key} has no literal text to anchor on"
    assert spanish in spanish_report, (
        f"{key} did not render its Spanish copy. The key resolved — the "
        f"render-boundary guard would not see this — but into the wrong "
        f"language.\nExpected to find: {spanish!r}"
    )


@pytest.mark.parametrize("key", _MIGRATED)
def test_the_english_copy_does_not_survive(spanish_report, key):
    english = _literal_anchor(key, "en")
    spanish = _literal_anchor(key, "es")
    if english == spanish:
        pytest.skip(f"{key} reads identically in both languages")
    assert english not in spanish_report, (
        f"{key} rendered its English copy inside a Spanish report.\n"
        f"Found: {english!r}"
    )


class TestCountAgreement:
    """#268 final residual pass — three sentences gained `.one`/`.other`
    variants where none existed before (`report.takeaway.topics`,
    `report.stat.benchmark.sub.rules_satisfied`,
    `report.stat.journal.sub.open_access_listed`). Spanish inflects the noun
    on the count in each ("resultado" -> "principales", "regla" -> "reglas",
    "catalogada" -> "catalogadas"); English does not, which is exactly why a
    key-leak or key-presence test cannot catch picking the wrong variant.

    Exercised directly against `_counted()` and the catalog rather than
    through a full collector fixture: the governing count is a collector-
    internal quantity (a benchmark's rule count, a topic list's length) that
    is not worth reverse-engineering a database fixture for when the
    contract this batch has to satisfy is about the catalog's grammar, not
    about a collector's arithmetic — that arithmetic is unchanged by this
    batch and already covered by `test_takeaway_truthfulness.py`.
    """

    @pytest.mark.parametrize(
        "stem,params,singular_only,plural_only",
        [
            (
                "report.takeaway.topics",
                {"concept": "X", "pct": 50},
                "único resultado",
                "principales",
            ),
            (
                "report.stat.benchmark.sub.rules_satisfied",
                {"passed": 1},
                "regla cumplida",
                "reglas cumplidas",
            ),
            (
                "report.stat.journal.sub.open_access_listed",
                {"in_doaj": 1},
                "catalogada en acceso abierto",
                "catalogadas en acceso abierto",
            ),
        ],
    )
    def test_spanish_picks_the_grammatically_correct_variant(
        self, stem, params, singular_only, plural_only
    ):
        one = resolve_value(report_builder._counted(stem, 1, **params), "es")
        other = resolve_value(report_builder._counted(stem, 3, **params), "es")

        assert singular_only in one, f"count=1 should read {singular_only!r}, got {one!r}"
        assert plural_only not in one, f"count=1 wrongly used the plural form: {one!r}"
        assert plural_only in other, f"count=3 should read {plural_only!r}, got {other!r}"
        assert singular_only not in other, f"count=3 wrongly used the singular form: {other!r}"

    def test_a_mutation_back_to_the_former_english_literal_is_caught(
        self, db_session, monkeypatch
    ):
        """Contract-required mutation check, pinned as a regression test rather
        than a one-off manual run: reverting `collect_topic_clusters`'s
        takeaway to the pre-#268 raw f-string must be caught by
        `test_the_english_copy_does_not_survive`'s own assertion, not pass
        silently.

        Patches `SECTION_COLLECTORS["topic_clusters"]` — the single dispatch
        `assemble_report_document()` reads (report_builder.py's own docstring
        on why there is exactly one such map) — so the mutation reaches
        `report_builder.build()` exactly the way a real regression would,
        rather than asserting against the collector in isolation.
        """
        from dataclasses import replace as _replace

        from backend.reporting.section_data import Table

        real_collect = report_builder.collect_topic_clusters

        def mutated(db, domain_id, org_id):
            section = real_collect(db, domain_id, org_id)
            table = next(b for b in section.blocks if isinstance(b, Table))
            if not table.rows:
                return section
            # The exact literal `collect_topic_clusters` built by hand before #268.
            pre_268_literal = (
                f'"{table.rows[0][0]}" is the most frequent concept, accounting for '
                f'{table.rows[0][2]} of the top {len(table.rows)}'
            )
            return _replace(section, takeaway=pre_268_literal)

        monkeypatch.setitem(report_builder.SECTION_COLLECTORS, "topic_clusters", mutated)

        _seed(db_session)
        mutated_report = report_builder.build(
            db_session, "default", ["topic_clusters"], org_id=None, language="es"
        )

        # Quote-free: the executive summary HTML-escapes the literal's leading
        # `"` to `&quot;`, which would make a straight-quote anchor a silent
        # false negative regardless of the mutation — the Spanish catalog
        # copy uses guillemets («»), not straight quotes, so that escaping
        # never affects the real positive/negative tests above.
        english = "is the most frequent concept, accounting for"
        assert english in mutated_report, (
            "the mutation did not reproduce the pre-#268 defect — this test's "
            "setup is stale, not the migration"
        )
        with pytest.raises(AssertionError):
            assert english not in mutated_report, (
                f"report.takeaway.topics rendered its English copy inside a "
                f"Spanish report.\nFound: {english!r}"
            )
