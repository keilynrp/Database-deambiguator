"""
Report Builder — generates self-contained HTML reports per domain.
No external template dependencies; uses f-strings with inline CSS.
"""
from __future__ import annotations

import json
import os
from html import escape
from datetime import datetime, timezone
from typing import List, TypedDict

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend import models
from backend.analyzers.topic_modeling import TopicAnalyzer
from backend.schema_registry import registry
from backend.services.analytics_service import AnalyticsService
from backend.services.pattern_discovery import PatternDiscoveryService
from backend.tenant_access import scope_query_to_org

_STAKEHOLDER_PROFILES = {
    "leadership": {
        "label": "Leadership / Strategy",
        "focus": "decision readiness, strategic risk, and institutional positioning",
        "brief_hint": "Use this lens when the audience needs a concise readout of readiness, confidence, and next executive moves.",
        "attention_points": [
            "benchmark readiness and whether the current portfolio supports a defendable executive conversation",
            "main confidence risks that could weaken institutional positioning if shared too early",
            "one concrete next move that improves decision readiness quickly",
        ],
        "narrative_goal": "Keep the story concise, directional, and anchored in readiness, confidence, and near-term institutional action.",
    },
    "research_office": {
        "label": "Research Office",
        "focus": "portfolio quality, benchmark progress, and operational follow-through",
        "brief_hint": "Use this lens when the audience needs to understand what to improve in the dataset and which actions strengthen research reporting.",
        "attention_points": [
            "coverage and quality gaps that most directly hold back reporting confidence",
            "which benchmark rules already pass and which still need operational attention",
            "the most practical next actions for strengthening the portfolio baseline",
        ],
        "narrative_goal": "Frame the brief as an operational readout: what is already usable, what still needs work, and where the office should focus next.",
    },
    "library": {
        "label": "Library / Metadata",
        "focus": "metadata quality, authority control, and catalog reliability",
        "brief_hint": "Use this lens when the audience cares most about normalization quality, authority review, and trust in the underlying records.",
        "attention_points": [
            "record quality and authority issues that still affect trust in the dataset",
            "whether metadata consistency is strong enough for downstream analytics and reporting",
            "where curation effort will most improve catalog reliability",
        ],
        "narrative_goal": "Tell the story through trust in the record layer: what is stable, what remains ambiguous, and what curation work matters most.",
    },
    "innovation": {
        "label": "Innovation / Transfer",
        "focus": "high-impact entities, signals worth following, and portfolio narratives that support opportunity scanning",
        "brief_hint": "Use this lens when the audience wants a faster read on standout outputs, concentration areas, and next exploratory opportunities.",
        "attention_points": [
            "high-impact outputs that can anchor opportunity scanning or partner conversations",
            "concept clusters that point to concentration areas worth exploring further",
            "the next exploratory move that could turn signal into action",
        ],
        "narrative_goal": "Keep the brief opportunity-oriented: highlight standout outputs, concentration areas, and the most promising next exploratory path.",
    },
}


class ManualReportSection(TypedDict, total=False):
    title: str
    content: str


def _stakeholder_profile(profile_id: str | None) -> dict[str, str]:
    return _STAKEHOLDER_PROFILES.get(profile_id or "leadership", _STAKEHOLDER_PROFILES["leadership"])


def _section_manual_note(title: str, content: str) -> str:
    safe_title = escape(title.strip() or "Analyst Note")
    paragraphs = [
        f"<p>{escape(part.strip())}</p>"
        for part in content.split("\n\n")
        if part.strip()
    ]
    if not paragraphs:
        return ""
    return f"""<section>
    <h2>{safe_title}</h2>
    <div class="analyst-note">
        {"".join(paragraphs)}
    </div>
</section>"""


def collect_stakeholder_reading(
    db: Session,
    domain_id: str,
    org_id: int | None,
    benchmark_profile_id: str | None = None,
    benchmark_org: models.Organization | None = None,
    stakeholder_profile: str | None = None,
) -> "SectionData":
    """Format-neutral stakeholder lens: a single Narrative framing the brief for
    the chosen audience. Migrated onto the shared payload (phase 3.11). The
    attention-point bullets flatten to paragraphs and the bold labels become
    plain text, consistent with the earlier migrations.
    """
    from backend.reporting.section_data import Narrative, SectionData

    snapshot = AnalyticsService.get_domain_snapshot(
        db,
        TopicAnalyzer(),
        domain_id,
        org_id=org_id,
        benchmark_org=benchmark_org,
        benchmark_profile_id=benchmark_profile_id,
        top_n_concepts=5,
        top_n_entities=3,
    )
    stakeholder = _stakeholder_profile(stakeholder_profile)
    benchmark = snapshot.get("institutional_benchmark") or {}
    quality = snapshot.get("quality") or {}
    kpis = snapshot.get("kpis") or {}
    actions = snapshot.get("recommended_actions") or []
    top_entity = (snapshot.get("top_entities") or [None])[0]
    impact_projection = snapshot.get("impact_projection") or {}

    benchmark_status = benchmark.get("status", "watch")
    readiness_pct = round(float(benchmark.get("readiness_pct") or 0))
    quality_avg = round(float(quality.get("average") or 0))
    coverage_pct = round(float(kpis.get("enrichment_pct") or 0))
    impact_score = round(float(impact_projection.get("score") or 0))
    impact_range = impact_projection.get("range") or {}

    if benchmark_status == "ready":
        stance = "The dataset is already in a comparatively strong position for a first stakeholder-facing conversation."
    elif benchmark_status == "watch":
        stance = "The dataset already supports directional interpretation, but it still carries enough uncertainty that the audience should treat this brief as an informed internal read rather than a final position."
    else:
        stance = "The dataset is best treated as an early baseline. It already surfaces useful directional patterns, but it is not yet robust enough for a high-confidence external narrative."

    action_text = actions[0]["title"] if actions else "Continue strengthening enrichment coverage and record quality before broad circulation."

    paragraphs: list[str] = [
        f'This brief is being framed for {stakeholder["focus"]}. {stakeholder["brief_hint"]}',
        stance,
        f"Current benchmark readiness is {readiness_pct}%, average quality is {quality_avg}%, and enrichment coverage is {coverage_pct}%.",
        f'The current Monte Carlo impact projection is {impact_score}/100, with a probable range of {impact_range.get("p10", 0)}–{impact_range.get("p90", 0)}.',
    ]
    if top_entity:
        entity_label = top_entity.get("entity_name") or top_entity.get("primary_label") or "the current lead record"
        paragraphs.append(
            f"The highest-impact visible entity right now is {entity_label}, which can anchor a concrete stakeholder discussion."
        )
    paragraphs.append(f"Recommended emphasis: {action_text}")

    # Readiness caveat: an identity-resolution backlog sitting underneath the
    # dataset must qualify readiness language, so a brief cannot call the data
    # decision-ready while thousands of unresolved identity conflicts wait below.
    # The ratio is ALWAYS disclosed; the qualifier is added only above threshold.
    pending_authority, total_authority = _authority_backlog_ratio(db, org_id)
    if total_authority:
        backlog_pct = round(pending_authority / total_authority * 100)
        disclosure = (
            f"Identity resolution: {pending_authority:,} of {total_authority:,} "
            f"authority records ({backlog_pct}%) are awaiting human review."
        )
        if pending_authority / total_authority >= _authority_backlog_threshold():
            disclosure += (
                " That backlog is material, so entity identity is not settled: read "
                "the readiness above as provisional to that extent until the review "
                "queue is worked down."
            )
        paragraphs.append(disclosure)

    attention_points = stakeholder.get("attention_points", [])
    if attention_points:
        paragraphs.append("How to read this brief for this audience:")
        paragraphs.extend(attention_points)
    paragraphs.append(f'Narrative goal: {stakeholder["narrative_goal"]}')

    reading = Narrative(heading=stakeholder["label"], paragraphs=tuple(paragraphs))
    return SectionData(key="stakeholder_reading", title="Stakeholder Reading", blocks=(reading,))


def _section_stakeholder_reading(
    db: Session,
    domain_id: str,
    org_id: int | None,
    benchmark_profile_id: str | None = None,
    benchmark_org: models.Organization | None = None,
    stakeholder_profile: str | None = None,
) -> str:
    from backend.reporting.html_renderer import render_html
    return render_html(
        collect_stakeholder_reading(
            db, domain_id, org_id, benchmark_profile_id, benchmark_org, stakeholder_profile
        )
    )

# ── CSS (inline, print-friendly) ─────────────────────────────────────────────

_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
       font-size: 14px; color: #111827; background: #fff; padding: 32px; }
.cover { text-align: center; padding: 60px 0 48px; border-bottom: 2px solid #e5e7eb; margin-bottom: 40px; }
.cover .logo { display: inline-flex; align-items: center; gap: 10px; margin-bottom: 16px; }
.cover .logo-icon { width: 40px; height: 40px; background: #2563eb; border-radius: 10px;
                    display: flex; align-items: center; justify-content: center; }
.cover .logo-icon svg { width: 24px; height: 24px; color: #fff; stroke: #fff; }
.cover h1 { font-size: 28px; font-weight: 700; color: #111827; margin-bottom: 8px; }
.cover .meta { font-size: 13px; color: #6b7280; }
section { margin-bottom: 40px; }
section h2 { font-size: 17px; font-weight: 600; color: #1d4ed8; margin-bottom: 16px;
             padding-bottom: 8px; border-bottom: 1px solid #dbeafe; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 16px; margin-bottom: 16px; }
.stat-card { background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 10px; padding: 16px; }
.stat-card .label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: .05em; color: #6b7280; }
.stat-card .value { font-size: 26px; font-weight: 700; color: #111827; margin-top: 4px; }
.stat-card .sub { font-size: 12px; color: #9ca3af; margin-top: 2px; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th { text-align: left; padding: 8px 12px; background: #f3f4f6;
     font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: .05em; color: #6b7280;
     border-bottom: 1px solid #e5e7eb; }
td { padding: 9px 12px; border-bottom: 1px solid #f3f4f6; color: #374151; }
tr:last-child td { border-bottom: none; }
.bar-wrap { display: flex; align-items: center; gap: 8px; }
.bar { height: 8px; background: #2563eb; border-radius: 4px; }
.bar-bg { flex: 1; background: #e5e7eb; border-radius: 4px; height: 8px; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 9999px; font-size: 11px; font-weight: 600; }
.badge-blue   { background: #dbeafe; color: #1d4ed8; }
.badge-green  { background: #d1fae5; color: #065f46; }
.badge-amber  { background: #fef3c7; color: #92400e; }
.badge-gray   { background: #f3f4f6; color: #6b7280; }
.badge-red    { background: #fee2e2; color: #991b1b; }
.chip { display: inline-block; margin: 2px; padding: 3px 10px; border-radius: 9999px;
        font-size: 12px; background: #eff6ff; color: #1d4ed8; }
.callout { border-radius: 12px; padding: 16px; margin: 16px 0; border: 1px solid #e5e7eb; background: #f9fafb; }
.callout h3 { font-size: 13px; font-weight: 700; color: #111827; margin-bottom: 6px; }
.callout p { font-size: 13px; color: #4b5563; line-height: 1.6; }
.analyst-note { border-left: 4px solid #2563eb; background: #f8fafc; padding: 16px 18px; border-radius: 0 10px 10px 0; }
.analyst-note p { font-size: 14px; color: #1f2937; line-height: 1.7; margin-bottom: 10px; white-space: pre-wrap; }
.analyst-note p:last-child { margin-bottom: 0; }
footer { margin-top: 48px; padding-top: 16px; border-top: 1px solid #e5e7eb;
         font-size: 12px; color: #9ca3af; text-align: center; }
/* ── Paged media ───────────────────────────────────────────────────────────
   This stylesheet is shared: build() produces the one HTML that both the HTML
   and the PDF export render (routers/reports.py). Everything below is scoped
   to @page / @media print so the HTML view is untouched. */

@page {
  size: A4;
  margin: 22mm 16mm 18mm;
  @top-left     { content: string(doctitle); font-size: 8pt; color: #6b7280; }
  @top-right    { content: string(docmeta);  font-size: 8pt; color: #9ca3af; }
  @bottom-right { content: counter(page) " / " counter(pages);
                  font-size: 8pt; color: #9ca3af; }
}
/* The cover carries its own title; a running header would repeat it. */
@page :first {
  @top-left  { content: none; }
  @top-right { content: none; }
}

@media print {
  /* @page supplies the margins; body padding on top of it double-counts. */
  body { padding: 0; }

  /* Pull the cover's own text up into the running header on later pages. */
  .cover      { padding: 34mm 0 24mm; border-bottom: none; break-after: page; }
  .cover h1   { string-set: doctitle content(); }
  .cover .meta{ string-set: docmeta content(); }

  /* `section { break-inside: avoid }` was counterproductive: a section longer
     than a page cannot honour it, and the engine then breaks it worse than if
     left alone. Keep sections breakable and protect the units that actually
     read badly when split. */
  section        { break-inside: auto; margin-bottom: 32px; }
  section h2     { break-after: avoid; }
  thead          { display: table-header-group; }
  tr             { break-inside: avoid; }
  .stat-card,
  .callout,
  .analyst-note  { break-inside: avoid; }
  p, td          { orphans: 3; widows: 3; }

  footer { margin-top: 24px; }
}
"""

# ── Section builders ──────────────────────────────────────────────────────────

def _entities_query(db: Session, domain_id: str, org_id: int | None):
    query = scope_query_to_org(db.query(models.RawEntity), models.RawEntity, org_id)
    if domain_id:
        query = query.filter(models.RawEntity.domain == domain_id)
    return query


def _harmonization_query(db: Session, org_id: int | None):
    return scope_query_to_org(db.query(models.HarmonizationLog), models.HarmonizationLog, org_id)


def collect_entity_stats(db: Session, domain_id: str, org_id: int | None) -> "SectionData":
    """Format-neutral entity statistics: KPI cards + validation distribution.

    First section migrated onto the shared section payload; every format renders
    from this one collector rather than re-querying and re-formatting.
    """
    from backend.reporting.section_data import (
        SectionData, StatGrid, StatItem, Table,
    )

    query = _entities_query(db, domain_id, org_id)
    total = query.with_entities(func.count(models.RawEntity.id)).scalar() or 0
    by_status = query.with_entities(
        models.RawEntity.validation_status,
        func.count(models.RawEntity.id),
    ).group_by(models.RawEntity.validation_status).all()
    by_enrich = query.with_entities(
        models.RawEntity.enrichment_status,
        func.count(models.RawEntity.id),
    ).group_by(models.RawEntity.enrichment_status).all()

    status_map = {r[0]: r[1] for r in by_status}
    enrich_map = {r[0]: r[1] for r in by_enrich}

    valid_pct = round(status_map.get("valid", 0) / total * 100) if total else 0
    enriched = enrich_map.get("completed", 0)
    enrich_pct = round(enriched / total * 100) if total else 0

    grid = StatGrid(items=(
        StatItem(label="Total Entities", value=f"{total:,}"),
        StatItem(label="Valid", value=f"{status_map.get('valid', 0):,}", sub=f"{valid_pct}% of total"),
        StatItem(label="Pending", value=f"{status_map.get('pending', 0):,}", sub="awaiting validation"),
        StatItem(label="Enriched", value=f"{enriched:,}", sub=f"{enrich_pct}% coverage"),
    ))

    rows = tuple(
        (
            s or "—",
            f"{c:,}",
            f"{round(c / total * 100) if total else 0}%",
        )
        for s, c in sorted(by_status, key=lambda x: -x[1])
    )
    table = Table(
        columns=("Validation Status", "Count", "Distribution"),
        rows=rows,
        bar_column=2,
    )
    return SectionData(key="entity_stats", title="Entity Statistics", blocks=(grid, table))


def _section_entity_stats(db: Session, domain_id: str, org_id: int | None) -> str:
    from backend.reporting.html_renderer import render_html
    return render_html(collect_entity_stats(db, domain_id, org_id))


def collect_enrichment_coverage(db: Session, domain_id: str, org_id: int | None) -> "SectionData":
    """Format-neutral enrichment coverage: coverage/avg-citation KPIs plus the
    top enriched entities. Migrated onto the shared section payload (phase 3.2).
    """
    from backend.reporting.section_data import (
        SectionData, StatGrid, StatItem, Table,
    )

    query = _entities_query(db, domain_id, org_id)
    total = query.with_entities(func.count(models.RawEntity.id)).scalar() or 0
    completed = query.with_entities(func.count(models.RawEntity.id))\
        .filter(models.RawEntity.enrichment_status == "completed").scalar() or 0
    avg_cit = query.with_entities(func.avg(models.RawEntity.enrichment_citation_count))\
        .filter(models.RawEntity.enrichment_status == "completed").scalar() or 0
    top = query.with_entities(
        models.RawEntity.primary_label,
        models.RawEntity.enrichment_citation_count,
        models.RawEntity.enrichment_source,
    ).filter(
        models.RawEntity.enrichment_status == "completed"
    ).order_by(
        models.RawEntity.enrichment_citation_count.desc()
    ).limit(8).all()

    pct = round(completed / total * 100) if total else 0

    grid = StatGrid(items=(
        StatItem(label="Coverage", value=f"{pct}%", sub=f"{completed:,} of {total:,} entities"),
        StatItem(label="Avg Citations", value=f"{round(avg_cit or 0):,}", sub="enriched entities only"),
    ))
    rows = tuple(
        (r[0] or "—", f"{r[1] or 0:,}", r[2] or "—")
        for r in top
    )
    table = Table(columns=("Entity", "Citations", "Source"), rows=rows)
    return SectionData(key="enrichment_coverage", title="Enrichment Coverage", blocks=(grid, table))


def _section_enrichment_coverage(db: Session, domain_id: str, org_id: int | None) -> str:
    from backend.reporting.html_renderer import render_html
    return render_html(collect_enrichment_coverage(db, domain_id, org_id))


def collect_top_secondary_labels(db: Session, domain_id: str, org_id: int | None) -> "SectionData":
    """Format-neutral top secondary labels: a share table where each row's bar is
    drawn relative to the most common label. Migrated onto the shared payload
    (phase 3.3).
    """
    from backend.reporting.section_data import SectionData, Table

    rows_q = _entities_query(db, domain_id, org_id).with_entities(
        models.RawEntity.secondary_label,
        func.count(models.RawEntity.id).label("n"),
    )\
        .filter(models.RawEntity.secondary_label.isnot(None))\
        .group_by(models.RawEntity.secondary_label)\
        .order_by(func.count(models.RawEntity.id).desc()).limit(15).all()
    max_n = rows_q[0][1] if rows_q else 1
    rows = tuple(
        (r[0], f"{r[1]:,}", f"{round(r[1] / max_n * 100)}%")
        for r in rows_q
    )
    table = Table(columns=("Label", "Entities", "Share"), rows=rows, bar_column=2)
    return SectionData(
        key="top_secondary_labels",
        title="Top Secondary Labels / Classifications",
        blocks=(table,),
    )


def _section_top_brands(db: Session, domain_id: str, org_id: int | None) -> str:
    from backend.reporting.html_renderer import render_html
    return render_html(collect_top_secondary_labels(db, domain_id, org_id))


#: One limit, applied in the payload, because no renderer truncates — whatever
#: this collector returns is what every format shows verbatim. So the number has
#: to be legible in the worst case, a PPTX slide, not just in a spreadsheet.
#:
#: It replaces four different numbers that had drifted apart: Excel fetched 50,
#: PPTX 20, and HTML fetched 15 while drawing 15 chips and a 10-row table. Same
#: section key, four answers. Excel readers lose detail here (50 -> 20); raising
#: it again means teaching the PPTX renderer to truncate with a visible
#: "showing N of M", which is a change to every section's tables, not just this
#: one.
_TOPIC_CAP = 20


def collect_topic_clusters(db: Session, domain_id: str, org_id: int | None) -> "SectionData":
    """Format-neutral top concepts (report-presentation, task 3.4).

    Note the section key says "clusters" and this returns most-frequent
    concepts. That was already true of all three previous implementations;
    reconciling the name is task 3.6, deliberately separate because renaming a
    section a caller can request is a visible API change.
    """
    from backend.reporting.section_data import (
        Materiality,
        Narrative,
        SectionData,
        Table,
    )

    method = (
        "Most frequent enriched concepts for this domain, ranked by occurrence "
        f"and capped at the top {_TOPIC_CAP}. Frequency counts concept "
        "occurrences across enriched records, not distinct entities, so one "
        "record contributes more than once when it carries a concept repeatedly."
    )

    try:
        result = TopicAnalyzer().top_topics(domain_id=domain_id, top_n=_TOPIC_CAP, org_id=org_id)
        topics = result.get("topics", []) or []
    except Exception:
        # An analyzer failure is reported as an empty section rather than a
        # broken report; the empty-state takeaway says so explicitly.
        topics = []

    if not topics:
        return SectionData(
            key="topic_clusters",
            title="Top Concepts",
            blocks=(
                Narrative(
                    heading="No concepts available",
                    paragraphs=("No enriched concepts found — run enrichment first.",),
                ),
            ),
            takeaway="No enriched concepts to report; enrichment has not produced any for this domain.",
            method=method,
            materiality=Materiality.EMPTY,
        )

    max_count = topics[0]["count"] or 1
    total = sum(t["count"] for t in topics)
    lead = topics[0]
    lead_share = round(lead["count"] / total * 100) if total else 0

    rows = tuple(
        (t["concept"], f'{t["count"]:,}', f'{round(t["count"] / max_count * 100)}%')
        for t in topics
    )

    return SectionData(
        key="topic_clusters",
        title="Top Concepts",
        blocks=(
            Table(
                columns=("Concept", "Frequency", "Relative weight"),
                rows=rows,
                bar_column=2,
            ),
        ),
        takeaway=(
            f'"{lead["concept"]}" is the most frequent concept, accounting for '
            f'{lead_share}% of the top {len(topics)}'
        ),
        method=method,
        # Concentration is the finding worth reading; an even spread is not.
        materiality=Materiality.NOTABLE if lead_share >= 25 else Materiality.ROUTINE,
    )


def _section_topic_clusters(db: Session, domain_id: str, org_id: int | None) -> str:
    from backend.reporting.html_renderer import render_html
    return render_html(collect_topic_clusters(db, domain_id, org_id))


def collect_harmonization_log(db: Session, domain_id: str, org_id: int | None) -> "SectionData":
    """Format-neutral harmonization log: the recent harmonization steps as a
    table. Migrated onto the shared payload (phase 3.5, HTML + PPTX). The
    Applied/Reverted status badge becomes a plain Status column. Excel keeps its
    bespoke "Harmonization" sheet until the cleanup phase de-dups it.
    """
    from backend.reporting.section_data import SectionData, Table

    logs = _harmonization_query(db, org_id)\
        .order_by(models.HarmonizationLog.executed_at.desc()).limit(10).all()
    rows = tuple(
        (
            l.step_name or l.step_id,
            f"{l.records_updated or 0:,}",
            "Reverted" if l.reverted else "Applied",
            l.executed_at.strftime("%Y-%m-%d %H:%M") if l.executed_at else "—",
        )
        for l in logs
    )
    table = Table(
        columns=("Step", "Records Updated", "Status", "Executed"),
        rows=rows,
    )
    return SectionData(key="harmonization_log", title="Harmonization Log", blocks=(table,))


def _section_harmonization_log(db: Session, domain_id: str, org_id: int | None) -> str:
    from backend.reporting.html_renderer import render_html
    return render_html(collect_harmonization_log(db, domain_id, org_id))


def collect_decision_recommendations(
    db: Session,
    domain_id: str,
    org_id: int | None,
    benchmark_org: models.Organization | None = None,
) -> "SectionData":
    """Format-neutral suggested next actions: a prioritized recommendation table.
    Migrated onto the shared payload (phase 3.9). The per-card priority badge
    becomes a plain Priority column so every format renders the same rows.
    """
    from backend.reporting.section_data import SectionData, Table

    snapshot = AnalyticsService.get_domain_snapshot(
        db,
        TopicAnalyzer(),
        domain_id,
        org_id=org_id,
        benchmark_org=benchmark_org,
        top_n_concepts=10,
        top_n_entities=5,
    )
    actions = snapshot.get("recommended_actions") or []
    rows = tuple(
        (
            str(action.get("priority", "")).title(),
            str(action.get("category", "")).replace("_", " "),
            action.get("title", ""),
            action.get("detail", ""),
            action.get("evidence", ""),
        )
        for action in actions
    )
    table = Table(
        columns=("Priority", "Category", "Recommendation", "Detail", "Evidence"),
        rows=rows,
    )
    return SectionData(
        key="decision_recommendations",
        title="Suggested Next Actions",
        blocks=(table,),
    )


def _section_decision_recommendations(
    db: Session,
    domain_id: str,
    org_id: int | None,
    benchmark_org: models.Organization | None = None,
) -> str:
    from backend.reporting.html_renderer import render_html
    return render_html(collect_decision_recommendations(db, domain_id, org_id, benchmark_org))


def collect_impact_projection(
    db: Session,
    domain_id: str,
    org_id: int | None,
    benchmark_org: models.Organization | None = None,
) -> "SectionData":
    """Format-neutral impact projection: KPI cards, an executive-interpretation
    narrative, and one Meter per projection driver. Migrated onto the shared
    payload (phase 3.7); first section to exercise the Narrative and Meter
    primitives in a real migration.
    """
    from backend.reporting.section_data import (
        Meter, Narrative, SectionData, StatGrid, StatItem,
    )

    snapshot = AnalyticsService.get_domain_snapshot(
        db,
        TopicAnalyzer(),
        domain_id,
        org_id=org_id,
        benchmark_org=benchmark_org,
        top_n_concepts=10,
        top_n_entities=10,
    )
    projection = snapshot.get("impact_projection") or {}
    score = int(projection.get("score") or 0)
    p10 = int((projection.get("range") or {}).get("p10") or 0)
    p50 = int((projection.get("range") or {}).get("p50") or score)
    p90 = int((projection.get("range") or {}).get("p90") or 0)
    confidence = str(projection.get("confidence") or "low").title()
    confidence_score = int(projection.get("confidence_score") or 0)
    drivers = projection.get("drivers") or {}

    grid = StatGrid(items=(
        StatItem(label="Expected Impact", value=f"{score}/100", sub="Monte Carlo median projection"),
        StatItem(label="Probable Range", value=f"{p10}–{p90}", sub=f"P10 to P90 · expected {p50}"),
        StatItem(label="Confidence", value=confidence, sub=f"{confidence_score}/100 stability score"),
    ))
    interpretation = Narrative(
        heading="Executive interpretation",
        paragraphs=(
            projection.get("recommendation", "No impact projection is available yet."),
            f'Brief angle: {projection.get("brief_angle", "Use this as a directional signal only.")}',
            projection.get("explanation", ""),
        ),
    )

    def _pct(value: float) -> float:
        return max(0, min(100, round(float(value or 0))))

    meters = tuple(
        Meter(label=label, pct=_pct(drivers.get(key, 0)))
        for label, key in (
            ("Coverage", "coverage"),
            ("Quality", "quality"),
            ("Citation signal", "citation_signal"),
            ("Concentration", "concentration"),
        )
    )
    return SectionData(
        key="impact_projection",
        title="Impact Projection",
        blocks=(grid, interpretation, *meters),
    )


def _section_impact_projection(
    db: Session,
    domain_id: str,
    org_id: int | None,
    benchmark_org: models.Organization | None = None,
) -> str:
    from backend.reporting.html_renderer import render_html
    return render_html(collect_impact_projection(db, domain_id, org_id, benchmark_org))


def collect_hidden_patterns(
    db: Session,
    domain_id: str,
    org_id: int | None,
    benchmark_org: models.Organization | None = None,
) -> "SectionData":
    """Format-neutral hidden patterns: an executive-reading narrative plus a
    table of discovered signals, the impact score drawn as a bar. Migrated onto
    the shared payload (phase 3.8). The per-card confidence badge becomes a plain
    Confidence column.
    """
    from backend.reporting.section_data import Narrative, SectionData, Table

    result = PatternDiscoveryService.discover(
        db,
        domain_id=domain_id,
        org_id=org_id,
        limit=6,
    )
    patterns = result.get("patterns") or []

    reading = Narrative(
        heading="Executive reading",
        paragraphs=(
            "UKIP scanned the portfolio for non-obvious concentrations, outliers, "
            "quality risks, source imbalance and graph bridge signals.",
        ),
    )
    rows = tuple(
        (
            str(pattern.get("type", "")).replace("_", " "),
            str(pattern.get("confidence", "")).title(),
            pattern.get("label", ""),
            pattern.get("evidence", ""),
            pattern.get("recommended_action", ""),
            f'{int(pattern.get("impact_score") or 0)}',
        )
        for pattern in patterns
    )
    table = Table(
        columns=("Pattern", "Confidence", "Signal", "Evidence", "Action", "Impact"),
        rows=rows,
        bar_column=5,
    )
    return SectionData(
        key="hidden_patterns",
        title="Hidden Patterns",
        blocks=(reading, table),
    )


def _section_hidden_patterns(
    db: Session,
    domain_id: str,
    org_id: int | None,
    benchmark_org: models.Organization | None = None,
) -> str:
    from backend.reporting.html_renderer import render_html
    return render_html(collect_hidden_patterns(db, domain_id, org_id, benchmark_org))


def collect_institutional_benchmark(
    db: Session,
    domain_id: str,
    org_id: int | None,
    benchmark_profile_id: str | None = None,
    benchmark_org: models.Organization | None = None,
) -> "SectionData":
    """Format-neutral institutional benchmark: readiness KPIs, an executive
    reading, and gap/rule tables. Migrated onto the shared payload (phase 3.6).
    The status/priority/pass badges become plain text so every format renders
    the same content.
    """
    from backend.reporting.section_data import (
        Narrative, SectionData, StatGrid, StatItem, Table,
    )

    snapshot = AnalyticsService.get_domain_snapshot(
        db,
        TopicAnalyzer(),
        domain_id,
        org_id=org_id,
        benchmark_org=benchmark_org,
        benchmark_profile_id=benchmark_profile_id,
        top_n_concepts=10,
        top_n_entities=5,
    )
    benchmark = snapshot.get("institutional_benchmark") or {}
    top_gaps = benchmark.get("top_gaps") or []
    rules = benchmark.get("rules") or []

    status = benchmark.get("status", "watch")
    readiness_pct = round(float(benchmark.get("readiness_pct") or 0))
    passed_rules = benchmark.get("passed_rules", 0)
    total_rules = benchmark.get("total_rules", 0)

    if status == "ready":
        benchmark_summary = (
            "This benchmark profile is currently in a ready state. "
            "The dataset is strong enough for a first stakeholder-facing interpretation with relatively limited benchmark risk."
        )
    elif status == "watch":
        benchmark_summary = (
            "This benchmark profile is in a watch state. "
            "The dataset already supports early interpretation, but important gaps still make the benchmark better suited for internal review than final external positioning."
        )
    else:
        benchmark_summary = (
            "This benchmark profile is currently showing a material gap. "
            "The benchmark is still useful as a directional baseline, but the current dataset should not be treated as fully decision-ready without additional enrichment or cleanup."
        )

    paragraphs = [benchmark_summary]
    if top_gaps:
        lead_gap = top_gaps[0]
        paragraphs.append(
            f"The main constraint right now is {lead_gap['label'].lower()}, "
            f"with evidence: {lead_gap['evidence']}"
        )

    grid = StatGrid(items=(
        StatItem(
            label="Benchmark Profile",
            value=benchmark.get("profile_name", "Institutional Benchmark"),
            sub=benchmark.get("description", "") or None,
        ),
        StatItem(
            label="Readiness",
            value=f"{readiness_pct}%",
            sub=f"{passed_rules} of {total_rules} rules satisfied",
        ),
        StatItem(
            label="Status",
            value=str(status).title(),
            sub="Baseline evaluation for the current dataset",
        ),
    ))
    reading = Narrative(heading="Executive reading", paragraphs=tuple(paragraphs))
    gap_table = Table(
        columns=("Gap", "Priority", "Evidence"),
        rows=tuple(
            (gap.get("label", ""), str(gap.get("priority", "")), gap.get("evidence", ""))
            for gap in top_gaps
        ),
    )
    rule_table = Table(
        columns=("Rule", "Observed", "Threshold", "Status", "Interpretation"),
        rows=tuple(
            (
                rule.get("label", ""),
                str(rule.get("observed", "")),
                str(rule.get("threshold", "")),
                "Passed" if rule.get("passed") else "Below threshold",
                rule.get("message", ""),
            )
            for rule in rules
        ),
    )
    return SectionData(
        key="institutional_benchmark",
        title="Institutional Benchmark",
        blocks=(grid, reading, gap_table, rule_table),
    )


def _section_institutional_benchmark(
    db: Session,
    domain_id: str,
    org_id: int | None,
    benchmark_profile_id: str | None = None,
    benchmark_org: models.Organization | None = None,
) -> str:
    from backend.reporting.html_renderer import render_html
    return render_html(
        collect_institutional_benchmark(
            db, domain_id, org_id, benchmark_profile_id, benchmark_org
        )
    )


def collect_agentic_trace(db: Session, domain_id: str, org_id: int | None) -> "SectionData":
    """Format-neutral saved agentic-chat traces (report-presentation, task 3.5).

    Migrating this fixed two defects the bespoke HTML builder carried. It styled
    its cards with `class="card"` and `class="muted"`, neither of which exists
    in the report stylesheet, so the section had been rendering unstyled; and
    its standing intro paragraph was hard-coded Spanish inside an
    otherwise-English report. Both disappear by going through the shared
    renderer, and the intro is where it belonged all along — the method
    disclosure.
    """
    from backend.reporting.section_data import Materiality, Narrative, SectionData

    method = (
        "AI-generated answers saved from the research assistant, not verified "
        "findings about the corpus. Each entry records the tools invoked and "
        "the sources cited so the answer can be audited; the answer itself has "
        "not been reviewed. Shows the 5 most recent saved traces."
    )

    traces = (
        db.query(models.AnalysisContext)
        .filter(
            models.AnalysisContext.domain_id == domain_id,
            models.AnalysisContext.label.like("agentic-chat:%"),
        )
        .order_by(models.AnalysisContext.created_at.desc())
        .limit(5)
        .all()
    )

    if not traces:
        return SectionData(
            key="agentic_trace",
            title="Agentic Research Trace",
            blocks=(
                Narrative(
                    heading="No saved traces",
                    paragraphs=(
                        "No saved agentic chat traces are available yet. Ask a question "
                        "from the research assistant and save the trace to include it here.",
                    ),
                ),
            ),
            takeaway="No agentic research traces have been saved for this domain.",
            method=method,
            materiality=Materiality.EMPTY,
        )

    blocks: list[Narrative] = []
    tools_seen: set[str] = set()
    for trace in traces:
        try:
            payload = json.loads(trace.context_snapshot or "{}")
        except Exception:
            payload = {}
        question = payload.get("question") or trace.label.replace("agentic-chat:", "").strip()
        answer = (payload.get("answer") or "")[:900]
        trace_meta = payload.get("trace") or {}
        sources = payload.get("sources") or []

        tools = trace_meta.get("tools_used") or []
        tools_seen.update(tools)
        tool_list = ", ".join(tools) or "No tools"
        source_list = ", ".join(
            str(s.get("label") or s.get("entity_id") or "source")
            for s in sources[:4]
            if isinstance(s, dict)
        ) or "No explicit sources"

        blocks.append(
            Narrative(
                heading=question or "Saved question",
                paragraphs=tuple(
                    p for p in (answer, f"Tools: {tool_list}", f"Sources: {source_list}") if p
                ),
            )
        )

    return SectionData(
        key="agentic_trace",
        title="Agentic Research Trace",
        blocks=tuple(blocks),
        takeaway=(
            f"{len(traces)} saved agentic answer{'s' if len(traces) != 1 else ''} "
            f"in this brief, drawing on {len(tools_seen) or 'no'} distinct tool"
            f"{'s' if len(tools_seen) != 1 else ''}"
        ),
        method=method,
        # Never leads: these are generated answers, not findings about the data.
        materiality=Materiality.ROUTINE,
    )


def _section_agentic_trace(db: Session, domain_id: str, org_id: int | None) -> str:
    from backend.reporting.html_renderer import render_html
    return render_html(collect_agentic_trace(db, domain_id, org_id))


# ── Authority / coauthorship / journals (extend-report-module-coverage) ──────
# Explicit cap on the conflicts table: a brief lists the worst offenders, it is
# not an export of the review queue (production holds ~9.4k pending records).
_AUTHORITY_CONFLICT_LIMIT = 10
# Fraction of authority records awaiting review at or above which the stakeholder
# reading gains an explicit backlog caveat, so readiness language cannot silently
# contradict a known identity-resolution backlog sitting underneath it. This is a
# starting point for judgement, NOT a derived constant — override per deployment
# via UKIP_REPORT_AUTHORITY_BACKLOG_THRESHOLD (declared in docker-compose.prod.yml).
_DEFAULT_AUTHORITY_BACKLOG_THRESHOLD = 0.15


def _authority_backlog_threshold() -> float:
    raw = os.environ.get("UKIP_REPORT_AUTHORITY_BACKLOG_THRESHOLD")
    if raw is None:
        return _DEFAULT_AUTHORITY_BACKLOG_THRESHOLD
    try:
        return max(0.0, min(1.0, float(raw)))
    except ValueError:
        return _DEFAULT_AUTHORITY_BACKLOG_THRESHOLD


def _authority_backlog_ratio(db: Session, org_id: int | None) -> tuple[int, int]:
    """(pending_review, total) authority records for this org. (0, 0) when none."""
    query = scope_query_to_org(
        db.query(models.AuthorityRecord), models.AuthorityRecord, org_id
    )
    total = query.with_entities(func.count(models.AuthorityRecord.id)).scalar() or 0
    if not total:
        return 0, 0
    pending = query.with_entities(func.count(models.AuthorityRecord.id))\
        .filter(models.AuthorityRecord.review_required.is_(True)).scalar() or 0
    return pending, total


def collect_authority_control(db: Session, domain_id: str, org_id: int | None) -> "SectionData":
    """Format-neutral authority-control reading: resolution status, review
    backlog, and what that backlog means for the report's own reliability.

    `domain_id` is accepted for signature consistency with the other collectors
    but is not a filter — `AuthorityRecord` is scoped per organisation, not per
    domain.
    """
    from backend.reporting.section_data import (
        Narrative, SectionData, StatGrid, StatItem, Table,
    )

    query = scope_query_to_org(
        db.query(models.AuthorityRecord), models.AuthorityRecord, org_id
    )
    total = query.with_entities(func.count(models.AuthorityRecord.id)).scalar() or 0

    if not total:
        # Absence of authority data is NOT evidence of clean identity
        # resolution. Saying "no conflicts" here would be a false reassurance.
        return SectionData(
            key="authority_control",
            title="Authority Control",
            blocks=(
                Narrative(
                    heading="Authority resolution not available",
                    paragraphs=(
                        "No authority records exist for this workspace, so identity "
                        "resolution has not been run over it.",
                        "This is not a finding of zero conflicts: unresolved duplicates "
                        "and identity collisions may still be present and simply have not "
                        "been looked for. Run authority resolution before treating entity "
                        "identity in this brief as settled.",
                    ),
                ),
            ),
        )

    confirmed = query.with_entities(func.count(models.AuthorityRecord.id))\
        .filter(models.AuthorityRecord.status == "confirmed").scalar() or 0
    pending = query.with_entities(func.count(models.AuthorityRecord.id))\
        .filter(models.AuthorityRecord.review_required.is_(True)).scalar() or 0
    mean_confidence = query.with_entities(
        func.avg(models.AuthorityRecord.confidence)
    ).scalar() or 0.0
    backlog_pct = round(pending / total * 100) if total else 0

    grid = StatGrid(items=(
        StatItem(label="Authority Records", value=f"{total:,}"),
        StatItem(label="Confirmed", value=f"{confirmed:,}",
                 sub=f"{round(confirmed / total * 100)}% of total"),
        StatItem(label="Pending Review", value=f"{pending:,}",
                 sub=f"{backlog_pct}% awaiting a human decision"),
        StatItem(label="Mean Confidence", value=f"{round(float(mean_confidence) * 100)}%",
                 sub="across all resolution attempts"),
    ))

    by_resolution = query.with_entities(
        models.AuthorityRecord.resolution_status,
        func.count(models.AuthorityRecord.id),
    ).group_by(models.AuthorityRecord.resolution_status).all()
    distribution = Table(
        columns=("Resolution Status", "Records", "Share"),
        rows=tuple(
            (status or "unknown", f"{count:,}", f"{round(count / total * 100)}%")
            for status, count in sorted(by_resolution, key=lambda r: -r[1])
        ),
        bar_column=2,
    )

    # Lowest-confidence unresolved items first: those are the ones a reader
    # should not assume were decided correctly.
    conflicts = query.with_entities(
        models.AuthorityRecord.original_value,
        models.AuthorityRecord.field_name,
        models.AuthorityRecord.resolution_status,
        models.AuthorityRecord.confidence,
        models.AuthorityRecord.nil_reason,
    ).filter(
        models.AuthorityRecord.review_required.is_(True)
    ).order_by(
        models.AuthorityRecord.confidence.asc()
    ).limit(_AUTHORITY_CONFLICT_LIMIT).all()
    conflicts_table = Table(
        columns=("Value", "Field", "Resolution", "Confidence", "Reason"),
        rows=tuple(
            (
                r[0] or "—",
                r[1] or "—",
                r[2] or "unresolved",
                f"{round(float(r[3] or 0) * 100)}%",
                r[4] or "—",
            )
            for r in conflicts
        ),
    )

    reliability = [
        f"{pending:,} of {total:,} authority records ({backlog_pct}%) are awaiting "
        f"human review.",
    ]
    if pending:
        reliability.append(
            "Entity identity in this brief should be read as provisional to that "
            "extent: unreviewed records may merge distinct entities or split a single "
            "one, which shifts counts and rankings elsewhere in the report."
        )
        if len(conflicts) == _AUTHORITY_CONFLICT_LIMIT:
            reliability.append(
                f"The table above lists the {_AUTHORITY_CONFLICT_LIMIT} lowest-confidence "
                "cases only; it is a sample of the backlog, not the whole queue."
            )
    else:
        reliability.append(
            "No records are awaiting review, so identity resolution is settled for "
            "the records that were processed."
        )

    return SectionData(
        key="authority_control",
        title="Authority Control",
        blocks=(
            grid,
            distribution,
            conflicts_table,
            Narrative(heading="Reliability reading", paragraphs=tuple(reliability)),
        ),
    )


def _section_authority_control(db: Session, domain_id: str, org_id: int | None) -> str:
    from backend.reporting.html_renderer import render_html
    return render_html(collect_authority_control(db, domain_id, org_id))


# How many top authors / bridges a brief lists. A reading, not a graph export.
_COLLAB_TOP_LIMIT = 10
# Author stats older than this read as stale; the section says so rather than
# presenting a months-old collaboration structure as current.
_COLLAB_STALENESS_DAYS = 30


def collect_collaboration_graph(db: Session, domain_id: str, org_id: int | None) -> "SectionData":
    """Format-neutral collaboration-graph reading from PRECOMPUTED `AuthorStats`
    and `CoauthorEdge`: author/edge/community counts, the most central authors,
    and bridge authors spanning communities.

    Reads columns only — it never invokes the coauthorship recompute or graph
    analytics path, so a brief stays cheap and reflects the last computed state.
    `domain_id` is not a filter here (org-scoped like the rest of the graph).
    """
    from datetime import datetime, timezone

    from backend.reporting.section_data import (
        Narrative, SectionData, StatGrid, StatItem, Table,
    )

    stats_q = scope_query_to_org(
        db.query(models.AuthorStats), models.AuthorStats, org_id
    )
    author_count = stats_q.with_entities(
        func.count(func.distinct(models.AuthorStats.author_id))
    ).scalar() or 0

    if not author_count:
        return SectionData(
            key="collaboration_graph",
            title="Collaboration Graph",
            blocks=(
                Narrative(
                    heading="Collaboration graph not available",
                    paragraphs=(
                        "No author statistics exist for this workspace, so the "
                        "coauthorship graph has not been computed over it.",
                        "Run coauthorship analysis to surface collaboration structure "
                        "— central authors, communities and the bridges between them.",
                    ),
                ),
            ),
        )

    edge_count = scope_query_to_org(
        db.query(models.CoauthorEdge), models.CoauthorEdge, org_id
    ).with_entities(func.count(models.CoauthorEdge.author_a_id)).scalar() or 0
    community_count = stats_q.with_entities(
        func.count(func.distinct(models.AuthorStats.community_id))
    ).filter(models.AuthorStats.community_id.isnot(None)).scalar() or 0

    grid = StatGrid(items=(
        StatItem(label="Authors", value=f"{author_count:,}"),
        StatItem(label="Collaborations", value=f"{edge_count:,}",
                 sub="coauthorship edges"),
        StatItem(label="Communities", value=f"{community_count:,}",
                 sub="detected clusters"),
    ))

    central = stats_q.with_entities(
        models.Author.display_name,
        models.AuthorStats.degree,
        models.AuthorStats.centrality,
        models.AuthorStats.publication_count,
    ).join(
        models.Author, models.Author.id == models.AuthorStats.author_id
    ).order_by(
        models.AuthorStats.centrality.desc().nullslast(),
        models.AuthorStats.degree.desc().nullslast(),
    ).limit(_COLLAB_TOP_LIMIT).all()
    central_table = Table(
        columns=("Author", "Degree", "Centrality", "Publications"),
        rows=tuple(
            (
                r[0] or "—",
                f"{r[1] or 0:,}",
                f"{float(r[2] or 0):.3f}",
                f"{r[3] or 0:,}",
            )
            for r in central
        ),
    )

    # Bridge authors = endpoints of an edge whose two authors sit in different
    # communities. Read entirely from the precomputed community_id column — no
    # graph traversal. Alias AuthorStats twice to compare the two endpoints.
    from sqlalchemy.orm import aliased
    stats_a = aliased(models.AuthorStats)
    stats_b = aliased(models.AuthorStats)
    cross_edges = scope_query_to_org(
        db.query(models.CoauthorEdge), models.CoauthorEdge, org_id
    ).join(
        stats_a, stats_a.author_id == models.CoauthorEdge.author_a_id
    ).join(
        stats_b, stats_b.author_id == models.CoauthorEdge.author_b_id
    ).filter(
        stats_a.community_id.isnot(None),
        stats_b.community_id.isnot(None),
        stats_a.community_id != stats_b.community_id,
    ).with_entities(
        models.CoauthorEdge.author_a_id,
        stats_a.community_id,
        models.CoauthorEdge.author_b_id,
        stats_b.community_id,
    ).all()
    # Collect each bridging author with the two communities it links.
    bridge_links: dict[int, set] = {}
    for a_id, a_comm, b_id, b_comm in cross_edges:
        bridge_links.setdefault(a_id, set()).update((a_comm, b_comm))
        bridge_links.setdefault(b_id, set()).update((a_comm, b_comm))
    bridge_names = {
        a.id: a.display_name
        for a in db.query(models.Author).filter(models.Author.id.in_(bridge_links.keys())).all()
    } if bridge_links else {}
    bridges_table = Table(
        columns=("Bridge Author", "Communities Linked"),
        rows=tuple(
            (bridge_names.get(aid, "—"), ", ".join(str(c) for c in sorted(comms)))
            for aid, comms in sorted(bridge_links.items(), key=lambda kv: -len(kv[1]))
        ),
    )

    blocks = [grid, central_table, bridges_table]

    # Staleness: the reader must know if this structure is old or uncomputed.
    latest_computed = stats_q.with_entities(
        func.max(models.AuthorStats.computed_at)
    ).scalar()
    if latest_computed is None:
        blocks.append(Narrative(
            heading="Staleness",
            paragraphs=(
                "These statistics have no computation timestamp, so the collaboration "
                "structure may be stale — treat it as indicative, not current.",
            ),
        ))
    else:
        if latest_computed.tzinfo is None:
            latest_computed = latest_computed.replace(tzinfo=timezone.utc)
        age_days = (datetime.now(timezone.utc) - latest_computed).days
        if age_days >= _COLLAB_STALENESS_DAYS:
            blocks.append(Narrative(
                heading="Staleness",
                paragraphs=(
                    f"The collaboration graph was last computed {age_days} days ago "
                    f"({latest_computed.strftime('%Y-%m-%d')}); it may be stale relative "
                    "to recent imports. Recompute before relying on the structure.",
                ),
            ))

    return SectionData(
        key="collaboration_graph",
        title="Collaboration Graph",
        blocks=tuple(blocks),
    )


def _section_collaboration_graph(db: Session, domain_id: str, org_id: int | None) -> str:
    from backend.reporting.html_renderer import render_html
    return render_html(collect_collaboration_graph(db, domain_id, org_id))


_JOURNAL_TOP_LIMIT = 12


def _bayes_with_interval(bayes, ci_low, ci_high) -> str:
    """Render the Bayesian NIF *only* bound to its credible interval.

    The point estimate exists because raw NIF is unstable for low-volume
    journals; showing it without the interval would hide the very uncertainty
    the estimator expresses. So the estimate and its bounds are formatted into a
    single cell — there is no code path that emits one without the other. When
    the interval is missing, the estimate is withheld entirely.
    """
    if bayes is None or ci_low is None or ci_high is None:
        return "—"
    return f"{float(bayes):.2f} [{float(ci_low):.2f}, {float(ci_high):.2f}]"


def collect_journal_portfolio(db: Session, domain_id: str, org_id: int | None) -> "SectionData":
    """Format-neutral journal-portfolio reading from `JournalMetric`: where the
    work was published, at what open-access cost, and with what field-normalized
    standing — the Bayesian estimate always carried with its credible interval.

    `domain_id` is not a filter (org-scoped like the other new sections).
    """
    from backend.reporting.section_data import (
        Narrative, SectionData, StatGrid, StatItem, Table,
    )

    query = scope_query_to_org(
        db.query(models.JournalMetric), models.JournalMetric, org_id
    )
    total = query.with_entities(func.count(models.JournalMetric.id)).scalar() or 0

    if not total:
        return SectionData(
            key="journal_portfolio",
            title="Journal Portfolio",
            blocks=(
                Narrative(
                    heading="Journal metrics not available",
                    paragraphs=(
                        "No journal metrics exist for this workspace, so the publication "
                        "portfolio — where the work was published, at what open-access cost, "
                        "and with what field-normalized standing — cannot be reported yet.",
                        "Run journal enrichment to populate it.",
                    ),
                ),
            ),
        )

    in_doaj = query.with_entities(func.count(models.JournalMetric.id))\
        .filter(models.JournalMetric.is_in_doaj.is_(True)).scalar() or 0
    with_apc = query.with_entities(func.count(models.JournalMetric.id))\
        .filter(models.JournalMetric.apc_usd.isnot(None),
                models.JournalMetric.apc_usd > 0).scalar() or 0
    doaj_pct = round(in_doaj / total * 100) if total else 0

    grid = StatGrid(items=(
        StatItem(label="Journals", value=f"{total:,}", sub="distinct venues"),
        StatItem(label="In DOAJ", value=f"{doaj_pct}%",
                 sub=f"{in_doaj:,} of {total:,} open-access listed"),
        StatItem(label="Charging APC", value=f"{with_apc:,}",
                 sub="venues with a publication fee"),
    ))

    top = query.with_entities(
        models.JournalMetric.display_name,
        models.JournalMetric.normalized_impact_factor,
        models.JournalMetric.nif_bayes,
        models.JournalMetric.nif_ci_low,
        models.JournalMetric.nif_ci_high,
        models.JournalMetric.works_2yr,
        models.JournalMetric.apc_usd,
        models.JournalMetric.is_in_doaj,
    ).order_by(
        models.JournalMetric.normalized_impact_factor.desc().nullslast()
    ).limit(_JOURNAL_TOP_LIMIT).all()
    table = Table(
        columns=(
            "Journal",
            "NIF (field-normalized)",
            "Bayesian NIF [95% CI]",
            "Local works (2yr)",
            "APC (USD)",
            "DOAJ",
        ),
        rows=tuple(
            (
                r[0] or "—",
                f"{float(r[1]):.2f}" if r[1] is not None else "—",
                _bayes_with_interval(r[2], r[3], r[4]),
                f"{r[5] or 0:,}",
                f"${int(r[6]):,}" if r[6] else "—",
                "Yes" if r[7] else "No",
            )
            for r in top
        ),
    )

    note = Narrative(
        heading="How to read these metrics",
        paragraphs=(
            "NIF is a field-normalized open proxy for journal standing (two-year mean "
            "citedness, normalized within field). It is NOT a Journal Impact Factor and "
            "must not be read as one.",
            "The Bayesian NIF is the shrunk estimate for low-volume journals and is always "
            "shown with its 95% credible interval; a point estimate without the interval "
            "would misrepresent its uncertainty.",
            "\"Local works (2yr)\" counts the works in THIS workspace, not the journal's "
            "global two-year output — it is local coverage, not a global volume.",
        ),
    )

    return SectionData(
        key="journal_portfolio",
        title="Journal Portfolio",
        blocks=(grid, table, note),
    )


def _section_journal_portfolio(db: Session, domain_id: str, org_id: int | None) -> str:
    from backend.reporting.html_renderer import render_html
    return render_html(collect_journal_portfolio(db, domain_id, org_id))


# ── Public API ────────────────────────────────────────────────────────────────

SECTION_BUILDERS = {
    "entity_stats": _section_entity_stats,
    "enrichment_coverage": _section_enrichment_coverage,
    "decision_recommendations": _section_decision_recommendations,
    "impact_projection": _section_impact_projection,
    "hidden_patterns": _section_hidden_patterns,
    "agentic_trace": _section_agentic_trace,
    "institutional_benchmark": _section_institutional_benchmark,
    "top_secondary_labels": _section_top_brands,
    "top_brands": _section_top_brands,
    "topic_clusters": _section_topic_clusters,
    "harmonization_log": _section_harmonization_log,
    "authority_control": _section_authority_control,
    "collaboration_graph": _section_collaboration_graph,
    "journal_portfolio": _section_journal_portfolio,
}

SECTION_LABELS = {
    "entity_stats": "Entity Statistics",
    "enrichment_coverage": "Enrichment Coverage",
    "decision_recommendations": "Suggested Next Actions",
    "impact_projection": "Impact Projection",
    "hidden_patterns": "Hidden Patterns",
    "agentic_trace": "Agentic Research Trace",
    "institutional_benchmark": "Institutional Benchmark",
    "top_secondary_labels": "Top Secondary Labels / Classifications",
    "top_brands": "Top Secondary Labels / Classifications",
    # Key stays `topic_clusters` — it is part of the vocabulary GET
    # /reports/sections returns and the generated SDKs expose, so renaming it
    # would break callers. The label says what the section actually shows
    # (report-presentation 3.6): most frequent concepts, never clusters.
    "topic_clusters": "Top Concepts",
    "harmonization_log": "Harmonization Log",
    "authority_control": "Authority Control",
    "collaboration_graph": "Collaboration Graph",
    "journal_portfolio": "Journal Portfolio",
}

# Deprecated section ids mapped to the public id that GET /reports/sections
# returns. Renderers must match on canonical ids only — a gate keyed on a
# deprecated alias silently drops the section for any client using the
# documented vocabulary. Run section lists through canonical_sections() at
# every renderer boundary so no renderer matches raw request strings.
SECTION_ALIASES = {
    "top_brands": "top_secondary_labels",
}


def canonical_sections(sections: list[str]) -> list[str]:
    """Resolve deprecated section aliases to their public ids, order preserved."""
    return [SECTION_ALIASES.get(section, section) for section in sections]


def build(
    db: Session,
    domain_id: str,
    sections: List[str],
    title: str | None = None,
    org_id: int | None = None,
    benchmark_profile_id: str | None = None,
    benchmark_org: models.Organization | None = None,
    stakeholder_profile: str | None = None,
    manual_sections: List[ManualReportSection] | None = None,
) -> str:
    """Return a complete, self-contained HTML report string."""
    domain_name = domain_id
    try:
        d = registry.get_domain(domain_id)
        domain_name = d.name if d else domain_id
    except Exception:
        pass

    report_title = title or f"UKIP Report — {domain_name}"
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    stakeholder = _stakeholder_profile(stakeholder_profile)

    logo_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4"/>
    </svg>"""

    cover = f"""<div class="cover">
        <div class="logo">
            <div class="logo-icon">{logo_svg}</div>
            <span style="font-size:20px;font-weight:700;color:#111827">UKIP</span>
        </div>
        <h1>{report_title}</h1>
        <p class="meta">Domain: <b>{domain_name}</b> &nbsp;·&nbsp; Generated: <b>{generated_at}</b></p>
        <p class="meta" style="margin-top:8px">Stakeholder lens: <b>{stakeholder["label"]}</b></p>
    </div>"""

    body_sections = [
        _section_stakeholder_reading(
            db,
            domain_id,
            org_id,
            benchmark_profile_id=benchmark_profile_id,
            benchmark_org=benchmark_org,
            stakeholder_profile=stakeholder_profile,
        )
    ]
    for manual in manual_sections or []:
        manual_html = _section_manual_note(
            str(manual.get("title") or "Analyst Note"),
            str(manual.get("content") or ""),
        )
        if manual_html:
            body_sections.append(manual_html)
    for sec in sections:
        builder = SECTION_BUILDERS.get(sec)
        if builder:
            try:
                if sec == "institutional_benchmark":
                    rendered = builder(db, domain_id, org_id, benchmark_profile_id, benchmark_org)
                elif sec in {"decision_recommendations", "impact_projection", "hidden_patterns"}:
                    rendered = builder(db, domain_id, org_id, benchmark_org)
                else:
                    rendered = builder(db, domain_id, org_id)
                if not isinstance(rendered, str):
                    raise TypeError(f"section builder returned {type(rendered).__name__}, expected str")
                body_sections.append(rendered)
            except Exception as exc:
                body_sections.append(f'<section><h2>{SECTION_LABELS.get(sec, sec)}</h2>'
                                     f'<p style="color:#ef4444">Error building section: {exc}</p></section>')

    footer = f'<footer>Generated by UKIP &nbsp;·&nbsp; {generated_at}</footer>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{report_title}</title>
  <style>{_CSS}</style>
</head>
<body>
  {cover}
  {"".join(body_sections)}
  {footer}
</body>
</html>"""
