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
from backend.reporting.localize import localize_section, with_params
from backend.schema_registry import registry
from backend.services.analytics_service import AnalyticsService
from backend.services.pattern_discovery import PatternDiscoveryService
from backend.tenant_access import scope_query_to_org

# Every field here is a catalog key, resolved at the render boundary like any
# other section copy. `focus` and `brief_hint` were two literals joined by an
# f-string into one sentence; they are one key now, because translate() does not
# translate its params — a translated fragment interpolated into a translated
# sentence would arrive in the wrong language. For the same reason `takeaway`
# is per-profile rather than one template taking the label as a parameter.
_STAKEHOLDER_PROFILES = {
    "leadership": {
        "label": "report.stakeholder.leadership.label",
        "framing": "report.stakeholder.leadership.framing",
        "attention_points": [
            "report.stakeholder.leadership.attention.readiness",
            "report.stakeholder.leadership.attention.confidence",
            "report.stakeholder.leadership.attention.next_move",
        ],
        "narrative_goal": "report.stakeholder.leadership.narrative_goal",
        "takeaway": "report.stakeholder.leadership.takeaway",
    },
    "research_office": {
        "label": "report.stakeholder.research_office.label",
        "framing": "report.stakeholder.research_office.framing",
        "attention_points": [
            "report.stakeholder.research_office.attention.gaps",
            "report.stakeholder.research_office.attention.rules",
            "report.stakeholder.research_office.attention.next_actions",
        ],
        "narrative_goal": "report.stakeholder.research_office.narrative_goal",
        "takeaway": "report.stakeholder.research_office.takeaway",
    },
    "library": {
        "label": "report.stakeholder.library.label",
        "framing": "report.stakeholder.library.framing",
        "attention_points": [
            "report.stakeholder.library.attention.quality",
            "report.stakeholder.library.attention.consistency",
            "report.stakeholder.library.attention.curation",
        ],
        "narrative_goal": "report.stakeholder.library.narrative_goal",
        "takeaway": "report.stakeholder.library.takeaway",
    },
    "innovation": {
        "label": "report.stakeholder.innovation.label",
        "framing": "report.stakeholder.innovation.framing",
        "attention_points": [
            "report.stakeholder.innovation.attention.outputs",
            "report.stakeholder.innovation.attention.clusters",
            "report.stakeholder.innovation.attention.next_move",
        ],
        "narrative_goal": "report.stakeholder.innovation.narrative_goal",
        "takeaway": "report.stakeholder.innovation.takeaway",
    },
}


class ManualReportSection(TypedDict, total=False):
    title: str
    content: str


def _stakeholder_profile(profile_id: str | None) -> dict[str, str]:
    return _STAKEHOLDER_PROFILES.get(profile_id or "leadership", _STAKEHOLDER_PROFILES["leadership"])


def _section_manual_note(title: str, content: str, language: str | None = None) -> str:
    # Raw HTML, not SectionData, so localize_section never sees it: the default
    # title has to be resolved here.
    safe_title = escape(title.strip() or translate("report.manual.default_title", language))
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
    # `quality.average` is a 0–1 fraction (its own distribution buckets at 0.7 /
    # 0.3 say so), and both figures below render it as a percentage. Without the
    # scaling a real average of 0.82 was reported as "quality 1%" — every other
    # consumer of this field multiplies: impact_projection and both dashboards.
    quality_avg = round(float(quality.get("average") or 0) * 100)
    coverage_pct = round(float(kpis.get("enrichment_pct") or 0))
    impact_score = round(float(impact_projection.get("score") or 0))
    impact_range = impact_projection.get("range") or {}

    if benchmark_status == "ready":
        stance = "report.stakeholder.stance.ready"
    elif benchmark_status == "watch":
        stance = "report.stakeholder.stance.watch"
    else:
        stance = "report.stakeholder.stance.gap"

    paragraphs: list[str] = [
        stakeholder["framing"],
        stance,
        with_params(
            "report.stakeholder.figures",
            readiness=readiness_pct,
            quality=quality_avg,
            coverage=coverage_pct,
        ),
        with_params(
            "report.stakeholder.projection",
            score=impact_score,
            p10=impact_range.get("p10", 0),
            p90=impact_range.get("p90", 0),
        ),
    ]
    if top_entity:
        # A provider-supplied name is data and goes in as a parameter. With no
        # name there is nothing to parametrise, and the fallback phrase has to
        # be part of the sentence — a key passed as a param would be
        # substituted, not translated.
        entity_label = top_entity.get("entity_name") or top_entity.get("primary_label")
        paragraphs.append(
            with_params("report.stakeholder.top_entity", entity=entity_label)
            if entity_label
            else "report.stakeholder.top_entity.unnamed"
        )
    # Same shape: a recommendation title is data, its absence is copy.
    paragraphs.append(
        with_params("report.stakeholder.emphasis", emphasis=actions[0]["title"])
        if actions
        else "report.stakeholder.emphasis.default"
    )

    # Readiness caveat: an identity-resolution backlog sitting underneath the
    # dataset must qualify readiness language, so a brief cannot call the data
    # decision-ready while thousands of unresolved identity conflicts wait below.
    # The ratio is ALWAYS disclosed; the qualifier is added only above threshold.
    pending_authority, total_authority = _authority_backlog_ratio(db, org_id)
    if total_authority:
        backlog_pct = round(pending_authority / total_authority * 100)
        # The qualifier used to be concatenated onto the sentence. Two keys
        # cannot be concatenated — the collector holds keys, and only the
        # renderer knows the language — so the material case is a key carrying
        # both sentences. That keeps this one paragraph, as it renders today.
        material = pending_authority / total_authority >= _authority_backlog_threshold()
        paragraphs.append(
            with_params(
                "report.stakeholder.identity_backlog.material"
                if material
                else "report.stakeholder.identity_backlog",
                pending=f"{pending_authority:,}",
                total=f"{total_authority:,}",
                pct=backlog_pct,
            )
        )

    attention_points = stakeholder.get("attention_points", [])
    if attention_points:
        paragraphs.append("report.stakeholder.how_to_read")
        paragraphs.extend(attention_points)
    paragraphs.append(stakeholder["narrative_goal"])

    reading = Narrative(heading=stakeholder["label"], paragraphs=tuple(paragraphs))
    return SectionData(
        key="stakeholder_reading",
        title="Stakeholder Reading",
        blocks=(reading,),
        takeaway=with_params(
            stakeholder["takeaway"],
            readiness=readiness_pct,
            quality=quality_avg,
            coverage=coverage_pct,
        ),
        method=(
            "report.method.stakeholder"
        ),
    )


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
/* The eyebrow above a section heading: exhibit ordinal + dataset label. The
   heading itself states the finding, so the label sits here — quieter, but still
   there, because a report you cannot scan by section name is worse than one that
   only names its sections. */
.exhibit-label { font-size: 11px; font-weight: 600; text-transform: uppercase;
                 letter-spacing: .06em; color: #6b7280; margin-bottom: 6px; }
.exhibit-label .ord { color: #1d4ed8; font-variant-numeric: tabular-nums; }
/* Source, as-of date and caveat, under the figures they qualify. */
.method { margin-top: 14px; padding-top: 10px; border-top: 1px dashed #e5e7eb;
          font-size: 11px; color: #6b7280; line-height: 1.6; }
.summary-list { list-style: none; padding-left: 0; }
.summary-list li { padding: 7px 0; border-bottom: 1px solid #f3f4f6; line-height: 1.6; }
.summary-list li:last-child { border-bottom: none; }
.summary-list .ord { color: #1d4ed8; font-weight: 600;
                     font-variant-numeric: tabular-nums; white-space: nowrap; }
/* Computed, and unremarkable. De-emphasized rather than dropped: that a section
   ran and found nothing is itself information. */
.summary-list li.muted,
.summary-list li.muted .ord { color: #9ca3af; }
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
  /* The eyebrow is a label for what follows; stranded at a page bottom it
     labels nothing. The method qualifies the figures above it, so it has to
     land on the page that carries them. */
  .exhibit-label { break-after: avoid; }
  .method        { break-before: avoid; break-inside: avoid; }
  .summary-list li { break-inside: avoid; }
  thead          { display: table-header-group; }
  tr             { break-inside: avoid; }
  .stat-card,
  .callout,
  .analyst-note  { break-inside: avoid; }

  /* WeasyPrint 69 does support CSS Grid, but not `repeat(auto-fill, minmax(…))`
     — measured, not assumed: with auto-fill or auto-fit every card lands on its
     own row at full width, while explicit `repeat(4, 1fr)` lays out one row
     correctly. So the KPI grid was degrading to one full-width card per line in
     the PDF only, which is most of why an eleven-page report was eleven pages.

     The fallback is a table row rather than explicit columns, because the column
     count is not fixed: sections carry two, three or four cards, and
     `repeat(4, 1fr)` would leave a two-card section at quarter width. A table
     distributes across however many cards there are, and WeasyPrint's table
     layout is its strongest.

     Print-scoped legitimately: this compensates for an engine limitation, not a
     design decision. On screen the responsive grid is correct and stays. */
  .grid          { display: table; width: 100%; border-spacing: 8px 0; }
  .stat-card     { display: table-cell; }
  p, td          { orphans: 3; widows: 3; }

  footer { margin-top: 24px; }
}
"""

# ── Section builders ──────────────────────────────────────────────────────────

def _counted(stem: str, count: int, **params) -> str:
    """A catalog key whose variant agrees with `count`, carrying its arguments.

    `3 patterns` / `1 pattern` used to be built here, in English, by appending an
    "s". A catalog cannot work that way: Spanish agrees in the verb as well as
    the noun, so the choice is not "which suffix" but "which whole sentence".
    Each variant is therefore a complete sentence in the catalog, which leaves
    the translator free to inflect however the language requires while this
    function only decides *which* of the two to ask for.

    Three sentences do not fit even this: they inflect on two or three
    independent counts, which is 4 and 8 variants of one line. Those were
    rephrased so no word depends on a number — see the keys without .one/.other.
    """
    return with_params(
        f"{stem}.{'one' if count == 1 else 'other'}", count=f"{count:,}", **params
    )


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

    # Labels and sub-labels are catalog keys; values stay as computed. The
    # renderer resolves them — see backend/reporting/localize.py.
    grid = StatGrid(items=(
        StatItem(label="report.stat.entity_stats.total", value=f"{total:,}"),
        StatItem(
            label="report.stat.entity_stats.valid",
            value=f"{status_map.get('valid', 0):,}",
            sub=with_params("report.stat.entity_stats.sub.pct_of_total", pct=valid_pct),
        ),
        StatItem(
            label="report.stat.entity_stats.pending",
            value=f"{status_map.get('pending', 0):,}",
            sub="report.stat.entity_stats.sub.awaiting",
        ),
        StatItem(
            label="report.stat.entity_stats.enriched",
            value=f"{enriched:,}",
            sub=with_params("report.stat.entity_stats.sub.pct_coverage", pct=enrich_pct),
        ),
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
        columns=(
            "report.col.entity_stats.status",
            "report.col.entity_stats.count",
            "report.col.entity_stats.distribution",
        ),
        rows=rows,
        bar_column=2,
    )
    from backend.reporting.section_data import Materiality

    pending = status_map.get("pending", 0)
    if not total:
        takeaway = "report.takeaway.entity_stats.empty"
        materiality = Materiality.EMPTY
    else:
        # Both verbs agree with the count in front of them, not with `total`:
        # the subject of "pass" is the valid count and the subject of "remain" is
        # the pending one, so the two can disagree with each other in one
        # sentence and still both be right.
        valid = int(status_map.get("valid", 0))
        takeaway = with_params(
            "report.takeaway.entity_stats",
            valid=f"{valid:,}", total=f"{total:,}", pct=valid_pct,
            pending=f"{pending:,}",
        )
        materiality = (
            Materiality.LEAD if valid_pct < 85
            else Materiality.NOTABLE if pending
            else Materiality.ROUTINE
        )

    return SectionData(
        key="entity_stats",
        title="Entity Statistics",
        blocks=(grid, table),
        takeaway=takeaway,
        method="report.method.entity_stats",
        materiality=materiality,
    )


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
        StatItem(
            label="report.stat.enrichment_coverage.coverage",
            value=f"{pct}%",
            sub=with_params(
                "report.stat.enrichment_coverage.sub.of_entities",
                done=f"{completed:,}",
                total=f"{total:,}",
            ),
        ),
        StatItem(
            label="report.stat.enrichment_coverage.avg_citations",
            value=f"{round(avg_cit or 0):,}",
            sub="report.stat.enrichment_coverage.sub.enriched_only",
        ),
    ))
    rows = tuple(
        (r[0] or "—", f"{r[1] or 0:,}", r[2] or "—")
        for r in top
    )
    table = Table(
        columns=(
            "report.col.enrichment_coverage.entity",
            "report.col.enrichment_coverage.citations",
            "report.col.enrichment_coverage.source",
        ),
        rows=rows,
    )
    from backend.reporting.section_data import Materiality

    if not total:
        takeaway = "report.empty.enrichment_coverage"
        materiality = Materiality.EMPTY
    else:
        takeaway = (
            f"Enrichment covers {pct}% of records ({completed:,} of {total:,}); "
            f"mean citation count {round(avg_cit or 0):,}"
        )
        materiality = (
            Materiality.LEAD if pct < 60
            else Materiality.NOTABLE if pct < 85
            else Materiality.ROUTINE
        )

    return SectionData(
        key="enrichment_coverage",
        title="Enrichment Coverage",
        blocks=(grid, table),
        takeaway=takeaway,
                method="report.method.enrichment_coverage",
        materiality=materiality,
    )


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
    # Two different percentages, previously both called "report.col.authority.share": the bar is drawn
    # relative to the largest label (so the top row is always 100%), while the
    # finding a reader cares about is each label's share of all classified
    # entities. Naming them apart, and rendering the second, is what lets the
    # takeaway cite a figure the reader can actually check — "Relative weight"
    # matches what topic_clusters already calls the same device.
    classified_total = sum(r[1] for r in rows_q) or 1
    rows = tuple(
        (
            r[0],
            f"{r[1]:,}",
            f"{round(r[1] / classified_total * 100)}%",
            f"{round(r[1] / max_n * 100)}%",
        )
        for r in rows_q
    )
    table = Table(
        columns=("Label", "report.col.top_secondary_labels.entities", "report.col.top_secondary_labels.share", "report.col.top_secondary_labels.weight"),
        rows=rows,
        bar_column=3,
    )
    from backend.reporting.section_data import Materiality, StatGrid, StatItem

    # Read back from the rendered rows rather than recomputing: the takeaway may
    # only cite figures the section shows, and reading the same cells the reader
    # sees is what makes that true by construction rather than by coincidence.
    classified = classified_total if rows_q else 0
    top_share = int(rows[0][2].rstrip("%")) if rows else 0

    # The denominator belongs on the page. Task 7.4 caught the takeaway citing
    # "N classified entities" while the section rendered only the per-label counts
    # — a reader had to add up the rows to check the sentence above them. Same
    # reasoning, and the same remedy, as the "Operations Applied" card in
    # harmonization_log.
    #
    # The truthfulness test did not catch it: with its fixture the total (40)
    # happened to equal an unrelated relative-weight cell (10/25 = 40%), so the
    # assertion was satisfied by a coincidence of the data rather than by the
    # section rendering its own denominator.
    totals = StatGrid(items=(
        StatItem(
            label="report.stat.top_secondary_labels.classified",
            value=f"{classified:,}",
            sub=_counted("report.stat.top_secondary_labels.across", len(rows_q)),
        ),
    ))
    return SectionData(
        takeaway=(
            _counted(
                "report.takeaway.secondary_labels", classified,
                top=rows[0][0], pct=top_share,
            )
            if rows else "report.empty.secondary_labels"
        ),
                method="report.method.top_secondary_labels",
        materiality=(
            Materiality.NOTABLE if top_share > 60
            else Materiality.ROUTINE if rows
            else Materiality.EMPTY
        ),
        key="top_secondary_labels",
        title="Top Secondary Labels / Classifications",
        blocks=(totals, table),
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
                    heading="report.narrative.topics.unavailable",
                    paragraphs=("report.narrative.topics.empty.p1",),
                ),
            ),
            takeaway="report.takeaway.topics.empty",
            method=method,
            materiality=Materiality.EMPTY,
        )

    max_count = topics[0]["count"] or 1
    total = sum(t["count"] for t in topics)
    lead = topics[0]
    lead_share = round(lead["count"] / total * 100) if total else 0

    # Two percentages, as in top_secondary_labels: the bar is drawn against the
    # most frequent concept (so the top row is always 100%), while the figure the
    # takeaway cites is each concept's share of the top N. Rendering only the
    # first left the sentence's number nowhere a reader could check it.
    rows = tuple(
        (
            t["concept"],
            f'{t["count"]:,}',
            f'{round(t["count"] / total * 100)}%',
            f'{round(t["count"] / max_count * 100)}%',
        )
        for t in topics
    )

    return SectionData(
        key="topic_clusters",
        title="Top Concepts",
        blocks=(
            Table(
                columns=("report.col.topics.concept", "report.col.topics.frequency", "report.col.topics.share_of_top", "report.col.topics.relative_weight"),
                rows=rows,
                bar_column=3,
            ),
        ),
        takeaway=(
            f'"{rows[0][0]}" is the most frequent concept, accounting for '
            f'{rows[0][2]} of the top {len(topics)}'
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
        columns=("Step", "report.col.harmonization_log.updated", "Status", "report.col.harmonization_log.executed"),
        rows=rows,
    )
    from backend.reporting.section_data import Materiality, StatGrid, StatItem

    # The count leads the takeaway, so it belongs on the page: a reader should
    # not have to count table rows to check the sentence above them.
    summary = StatGrid(items=(
        StatItem(label="report.stat.harmonization_log.applied", value=f"{len(logs):,}", sub="report.stat.harmonization_log.sub.recent_first"),
    ))
    return SectionData(
        key="harmonization_log",
        title="Harmonization Log",
        blocks=(summary, table),
        takeaway=(
            _counted("report.takeaway.harmonization", len(logs), recent=rows[0][0])
            if rows else "report.empty.harmonization"
        ),
        method="report.method.harmonization",
        materiality=Materiality.ROUTINE if rows else Materiality.EMPTY,
    )


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
        columns=("report.col.actions.priority", "report.col.actions.category", "report.col.actions.recommendation", "report.col.actions.detail", "report.col.actions.evidence"),
        rows=rows,
    )
    from backend.reporting.section_data import Materiality

    high = sum(
        1 for a in actions
        if str(a.get("priority", "")).lower() in {"high", "critical"}
    )
    from backend.reporting.section_data import StatGrid, StatItem

    action_summary = StatGrid(items=(
        StatItem(label="report.stat.actions.recommended", value=f"{len(actions):,}"),
        StatItem(label="report.stat.actions.high_priority", value=f"{high:,}", sub="report.stat.actions.sub.of_those"),
    ))
    return SectionData(
        takeaway=(
            _counted("report.takeaway.decisions", len(actions), high=high)
            if actions else "report.empty.decision_recommendations"
        ),
        method=(
            "report.method.actions"
        ),
        materiality=(
            Materiality.LEAD if high
            else Materiality.NOTABLE if actions
            else Materiality.EMPTY
        ),
        key="decision_recommendations",
        title="Suggested Next Actions",
        blocks=(action_summary, table),
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
        StatItem(label="report.stat.impact.expected", value=f"{score}/100", sub="report.stat.impact.sub.monte_carlo_median"),
        StatItem(label="report.stat.impact.probable_range", value=f"{p10}–{p90}", sub=f"P10 to P90 · expected {p50}"),
        StatItem(label="report.col.authority.confidence", value=confidence, sub=f"{confidence_score}/100 stability score"),
    ))
    interpretation = Narrative(
        heading="report.narrative.impact.exec_interpretation",
        paragraphs=(
            projection.get("recommendation") or "report.empty.impact_projection",
            with_params("report.narrative.impact.brief_angle", angle=projection["brief_angle"])
            if projection.get("brief_angle")
            else "report.narrative.impact.brief_angle.default",
            projection.get("explanation", ""),
        ),
    )

    def _pct(value: float) -> float:
        return max(0, min(100, round(float(value or 0))))

    meters = tuple(
        Meter(label=label, pct=_pct(drivers.get(key, 0)))
        for label, key in (
            ("report.meter.coverage", "coverage"),
            ("report.meter.quality", "quality"),
            ("report.meter.citation_signal", "citation_signal"),
            ("report.meter.concentration", "concentration"),
        )
    )
    from backend.reporting.section_data import Materiality

    spread = (p90 or 0) - (p10 or 0)
    return SectionData(
        takeaway=f"Projected impact {score}/100, probable range {p10}-{p90}",
        method=(
            "report.method.impact"
        ),
        # Never LEAD. A wide range is low information, and letting it head the
        # summary sells uncertainty as a finding.
        materiality=Materiality.NOTABLE if spread <= 30 else Materiality.ROUTINE,
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
        heading="report.narrative.patterns.exec_reading",
        paragraphs=(
            "report.narrative.patterns.scan",
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
        columns=("report.col.patterns.pattern", "report.col.patterns.confidence", "report.col.patterns.signal", "report.col.patterns.evidence", "report.col.patterns.action", "report.col.patterns.impact"),
        rows=rows,
        bar_column=5,
    )
    from backend.reporting.section_data import Materiality

    from backend.reporting.section_data import StatGrid, StatItem

    # The count leads the takeaway, so it has to be visible: checking the
    # sentence should not mean counting table rows.
    pattern_summary = StatGrid(items=(
        StatItem(label="report.stat.patterns.detected", value=f"{len(patterns):,}"),
    ))
    return SectionData(
        takeaway=(
            _counted("report.takeaway.patterns", len(patterns), top=rows[0][0])
            if rows else "report.empty.hidden_patterns"
        ),
        method=(
            "report.method.patterns"
        ),
        # Capped below LEAD unconditionally: the section name invites a causal
        # reading its method cannot support.
        materiality=Materiality.NOTABLE if patterns else Materiality.EMPTY,
        key="hidden_patterns",
        title="Hidden Patterns",
        blocks=(pattern_summary, reading, table),
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
        benchmark_summary = "report.benchmark.state.ready"
    elif status == "watch":
        benchmark_summary = "report.benchmark.state.watch"
    else:
        benchmark_summary = "report.benchmark.state.gap"

    paragraphs = [benchmark_summary]
    if top_gaps:
        lead_gap = top_gaps[0]
        paragraphs.append(
            with_params(
                "report.benchmark.lead_gap",
                gap=lead_gap["label"].lower(),
                evidence=lead_gap["evidence"],
            )
        )

    grid = StatGrid(items=(
        StatItem(
            label="report.stat.benchmark.profile",
            value=benchmark.get("profile_name", "Institutional Benchmark"),
            sub=benchmark.get("description", "") or None,
        ),
        StatItem(
            label="report.stat.benchmark.readiness",
            value=f"{readiness_pct}%",
            sub=f"{passed_rules} of {total_rules} rules satisfied",
        ),
        StatItem(
            label="report.col.benchmark.status",
            value=str(status).title(),
            sub="report.stat.benchmark.sub.baseline",
        ),
    ))
    reading = Narrative(heading="report.narrative.benchmark.exec_reading", paragraphs=tuple(paragraphs))
    gap_table = Table(
        columns=("report.col.benchmark.gap", "report.col.benchmark.priority", "report.col.benchmark.evidence"),
        rows=tuple(
            (gap.get("label", ""), str(gap.get("priority", "")), gap.get("evidence", ""))
            for gap in top_gaps
        ),
    )
    rule_table = Table(
        columns=("report.col.benchmark.rule", "report.col.benchmark.observed", "report.col.benchmark.threshold", "report.stat.benchmark.status", "report.col.benchmark.interpretation"),
        rows=tuple(
            (
                rule.get("label", ""),
                str(rule.get("observed", "")),
                str(rule.get("threshold", "")),
                "report.status.passed" if rule.get("passed") else "report.status.below_threshold",
                rule.get("message", ""),
            )
            for rule in rules
        ),
    )
    from backend.reporting.section_data import Materiality

    return SectionData(
        key="institutional_benchmark",
        title="Institutional Benchmark",
        blocks=(grid, reading, gap_table, rule_table),
        takeaway=(
            _counted(
                "report.takeaway.benchmark", total_rules,
                readiness=readiness_pct, passed=passed_rules, status=status,
            )
        ),
        method=(
            "report.method.benchmark"
        ),
        materiality=Materiality.LEAD if status != "ready" else Materiality.NOTABLE,
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
                    heading="report.narrative.trace.unavailable",
                    paragraphs=(
                        "report.narrative.trace.empty.p1",
                    ),
                ),
            ),
            takeaway="report.takeaway.trace.empty",
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
        tool_list = ", ".join(tools)
        source_list = ", ".join(
            str(s.get("label") or s.get("entity_id") or "source")
            for s in sources[:4]
            if isinstance(s, dict)
        )

        blocks.append(
            Narrative(
                heading=question or "report.trace.saved_question",
                paragraphs=tuple(
                    p for p in (
                        answer,
                        with_params("report.trace.tools", tools=tool_list)
                        if tool_list else "report.trace.tools.none",
                        with_params("report.trace.sources", sources=source_list)
                        if source_list else "report.trace.sources.none",
                    ) if p
                ),
            )
        )

    # Same reason as harmonization_log: the takeaway rolls the per-trace tool
    # lists up into a distinct count, which appears nowhere unless stated.
    from backend.reporting.section_data import StatGrid, StatItem

    summary = StatGrid(items=(
        StatItem(label="report.stat.trace.saved_answers", value=f"{len(traces):,}"),
        StatItem(label="report.stat.trace.distinct_tools", value=f"{len(tools_seen):,}", sub="report.stat.trace.sub.across_answers"),
    ))
    return SectionData(
        key="agentic_trace",
        title="Agentic Research Trace",
        blocks=(summary, *blocks),
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
#: Shared by both return paths of collect_authority_control so the empty case
#: discloses the same thing as the populated one.
_JOURNAL_METHOD = "report.method.journal"
_COLLAB_METHOD = "report.method.collab"
_AUTHORITY_METHOD = "report.method.authority"

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
        from backend.reporting.section_data import Materiality

        return SectionData(
            takeaway=(
                "report.takeaway.authority.empty"
            ),
            method=_AUTHORITY_METHOD,
            materiality=Materiality.EMPTY,
            key="authority_control",
            title="Authority Control",
            blocks=(
                Narrative(
                    heading="report.narrative.authority.unavailable",
                    paragraphs=(
                        "report.narrative.authority.empty.p1",
                        "report.narrative.authority.empty.p2",
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
        StatItem(label="report.stat.authority.records", value=f"{total:,}"),
        StatItem(label="report.stat.authority.confirmed", value=f"{confirmed:,}",
                 sub=f"{round(confirmed / total * 100)}% of total"),
        StatItem(label="report.stat.authority.pending", value=f"{pending:,}",
                 sub=f"{backlog_pct}% awaiting a human decision"),
        StatItem(label="report.stat.authority.mean_confidence", value=f"{round(float(mean_confidence) * 100)}%",
                 sub="report.stat.authority.sub.all_attempts"),
    ))

    by_resolution = query.with_entities(
        models.AuthorityRecord.resolution_status,
        func.count(models.AuthorityRecord.id),
    ).group_by(models.AuthorityRecord.resolution_status).all()
    distribution = Table(
        columns=("report.col.authority.resolution_status", "report.col.authority.records", "Share"),
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
        columns=("report.col.authority.value", "report.col.authority.field", "report.col.authority.resolution", "Confidence", "report.col.authority.reason"),
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
            "report.empty.authority_review"
        )

    from backend.reporting.section_data import Materiality

    return SectionData(
        key="authority_control",
        title="Authority Control",
        blocks=(
            grid,
            distribution,
            conflicts_table,
            Narrative(heading="report.narrative.authority.reliability", paragraphs=tuple(reliability)),
        ),
        takeaway=(
            with_params(
                "report.takeaway.authority",
                confirmed=f"{confirmed:,}", total=f"{total:,}",
                pending=f"{pending:,}",
                confidence=round(float(mean_confidence or 0) * 100),
            )
        ),
        method=_AUTHORITY_METHOD,
        # A backlog larger than the confirmed set is the finding, not a footnote.
        materiality=(
            Materiality.LEAD if pending > confirmed
            else Materiality.NOTABLE if pending
            else Materiality.ROUTINE
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
        from backend.reporting.section_data import Materiality

        return SectionData(
            takeaway="report.takeaway.collab.empty",
            method=_COLLAB_METHOD,
            materiality=Materiality.EMPTY,
            key="collaboration_graph",
            title="Collaboration Graph",
            blocks=(
                Narrative(
                    heading="report.narrative.collab.unavailable",
                    paragraphs=(
                        "report.narrative.collab.empty.p1",
                        "report.narrative.collab.empty.p2"
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
        StatItem(label="report.stat.collab.authors", value=f"{author_count:,}"),
        StatItem(label="report.stat.collab.collaborations", value=f"{edge_count:,}",
                 sub="report.stat.collab.sub.edges"),
        StatItem(label="report.stat.collab.communities", value=f"{community_count:,}",
                 sub="report.stat.collab.sub.clusters"),
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
        columns=("report.col.collab.author", "report.col.collab.degree", "report.col.collab.centrality", "report.col.collab.publications"),
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
        columns=("report.col.collab.bridge_author", "report.col.collab.communities_linked"),
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
            heading="report.narrative.collab.staleness",
            paragraphs=(
                "report.narrative.collab.stale_warning"
            ),
        ))
    else:
        if latest_computed.tzinfo is None:
            latest_computed = latest_computed.replace(tzinfo=timezone.utc)
        age_days = (datetime.now(timezone.utc) - latest_computed).days
        if age_days >= _COLLAB_STALENESS_DAYS:
            blocks.append(Narrative(
                heading="report.narrative.collab.staleness",
                paragraphs=(
                    f"The collaboration graph was last computed {age_days} days ago "
                    f"({latest_computed.strftime('%Y-%m-%d')}); it may be stale relative "
                    "to recent imports. Recompute before relying on the structure.",
                ),
            ))

    from backend.reporting.section_data import Materiality

    return SectionData(
        key="collaboration_graph",
        title="Collaboration Graph",
        blocks=tuple(blocks),
        takeaway=(
            with_params(
                "report.takeaway.collab",
                authors=f"{author_count:,}", communities=f"{community_count:,}",
                collaborations=f"{edge_count:,}",
            )
        ),
        method=_COLLAB_METHOD,
        materiality=Materiality.NOTABLE if community_count > 1 else Materiality.ROUTINE,
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
        from backend.reporting.section_data import Materiality

        return SectionData(
            takeaway="report.takeaway.journal.empty",
            method=_JOURNAL_METHOD,
            materiality=Materiality.EMPTY,
            key="journal_portfolio",
            title="Journal Portfolio",
            blocks=(
                Narrative(
                    heading="report.narrative.journal.unavailable",
                    paragraphs=(
                        "report.narrative.journal.empty.p1",
                        "report.narrative.journal.empty.p2",
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
        StatItem(label="report.stat.journal.journals", value=f"{total:,}", sub="report.stat.journal.sub.distinct_venues"),
        StatItem(label="report.stat.journal.in_doaj", value=f"{doaj_pct}%",
                 sub=f"{in_doaj:,} of {total:,} open-access listed"),
        StatItem(label="report.stat.journal.charging_apc", value=f"{with_apc:,}",
                 sub="report.stat.journal.sub.publication_fee"),
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
            "report.col.journal.journal",
            "report.col.journal.nif",
            "report.col.journal.nif_bayes",
            "report.col.journal.local_works",
            "report.col.journal.apc",
            "report.col.journal.doaj",
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
        heading="report.narrative.journal.how_to_read",
        paragraphs=(
            "report.narrative.journal.nif",
            "report.narrative.journal.bayes",
            "report.narrative.journal.local_works"
        ),
    )

    from backend.reporting.section_data import Materiality

    return SectionData(
        key="journal_portfolio",
        title="Journal Portfolio",
        blocks=(grid, table, note),
        takeaway=(
            _counted(
                "report.takeaway.journal", total,
                doaj=doaj_pct, apc=f"{with_apc:,}",
            )
        ),
        method=_JOURNAL_METHOD,
        materiality=Materiality.NOTABLE if doaj_pct < 50 else Materiality.ROUTINE,
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

#: Collectors that take `benchmark_org` in addition to the common three.
#: `institutional_benchmark` takes `benchmark_profile_id` as well and is handled
#: separately; keeping the shapes named rather than inline stops the dispatch
#: from being copied out of step in a fourth place.
_BENCHMARK_ORG_SECTIONS = frozenset(
    {"decision_recommendations", "impact_projection", "hidden_patterns"}
)

#: What `build()` assembles from. Mirrors SECTION_BUILDERS key for key, including
#: the deprecated `top_brands` alias, but yields SectionData rather than markup —
#: which is what lets assembly attach exhibit ordinals and compose an executive
#: summary. SECTION_BUILDERS is retained for callers that still want a single
#: section as HTML.
SECTION_COLLECTORS = {
    "entity_stats": collect_entity_stats,
    "enrichment_coverage": collect_enrichment_coverage,
    "decision_recommendations": collect_decision_recommendations,
    "impact_projection": collect_impact_projection,
    "hidden_patterns": collect_hidden_patterns,
    "agentic_trace": collect_agentic_trace,
    "institutional_benchmark": collect_institutional_benchmark,
    "top_secondary_labels": collect_top_secondary_labels,
    "top_brands": collect_top_secondary_labels,
    "topic_clusters": collect_topic_clusters,
    "harmonization_log": collect_harmonization_log,
    "authority_control": collect_authority_control,
    "collaboration_graph": collect_collaboration_graph,
    "journal_portfolio": collect_journal_portfolio,
}

def collect_section(
    db: Session,
    section: str,
    domain_id: str,
    org_id: int | None = None,
    benchmark_profile_id: str | None = None,
    benchmark_org: models.Organization | None = None,
):
    """Collect one section's payload, resolving its collector signature.

    Collectors come in three shapes and the caller cannot know which without
    consulting this dispatch. Extracted from `build()` so there is exactly one
    copy of it: this codebase has already paid for two section maps drifting
    apart (task 4.7), and a dispatch duplicated into a test drifts the same way —
    silently, and in the direction of the test agreeing with itself.

    Returns None for an unknown section rather than raising, so a caller
    iterating a requested list can skip what it does not recognise.
    """
    collect = SECTION_COLLECTORS.get(section)
    if collect is None:
        return None
    if section == "institutional_benchmark":
        return collect(db, domain_id, org_id, benchmark_profile_id, benchmark_org)
    if section in _BENCHMARK_ORG_SECTIONS:
        return collect(db, domain_id, org_id, benchmark_org)
    return collect(db, domain_id, org_id)


def _executive_summary(collected: list) -> str:
    """Every collected section's takeaway, ordered by materiality.

    Ordered, not filtered. A reader can see that a section was computed and had
    nothing notable to say — which is itself information — while the findings
    that matter lead. Non-material entries are de-emphasized rather than
    dropped.

    Ties break on exhibit order so the sequence is stable for a given
    selection rather than depending on dict iteration.
    """
    from backend.reporting.section_data import Materiality

    if not collected:
        return ""

    ranked = sorted(
        collected,
        key=lambda s: (-int(s.materiality), s.exhibit or 0),
    )

    items = []
    for section in ranked:
        muted = ' class="muted"' if section.materiality <= Materiality.ROUTINE else ""
        items.append(
            f"<li{muted}>"
            f'<span class="ord">Exhibit {section.exhibit}</span>&nbsp;·&nbsp;'
            f"{escape(section.takeaway)}"
            f"</li>"
        )

    return (
        "<section>"
        "<h2>Executive Summary</h2>"
        f'<ul class="summary-list">{"".join(items)}</ul>'
        "</section>"
    )


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
    language: str | None = None,
) -> str:
    """Return a complete, self-contained HTML report string.

    `language` selects catalog-sourced text only — section titles and the
    disclosure. Analysis prose and provider-supplied names stay English by
    decision, which is why a non-English report carries a disclosure saying so
    rather than leaving a reader to interpret the mixture as a defect.
    """
    from backend.i18n import DEFAULT_LANGUAGE
    from backend.i18n.catalog import translate
    from backend.i18n.locale import resolve_report_language

    # Reports never consult Accept-Language: resolve_report_language takes no
    # header argument, so the operator's browser cannot decide the language of
    # a document produced for someone else.
    language = resolve_report_language(language)
    domain_name = domain_id
    try:
        d = registry.get_domain(domain_id)
        domain_name = d.name if d else domain_id
    except Exception:
        pass

    report_title = title or translate("report.cover.title", language, domain=domain_name)
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
        <p class="meta">{translate("report.cover.domain", language)}: <b>{domain_name}</b> &nbsp;·&nbsp; {translate("report.cover.generated", language)}: <b>{generated_at}</b></p>
        <p class="meta" style="margin-top:8px">{translate("report.stakeholder.lens", language)}: <b>{translate(stakeholder["label"], language)}</b></p>
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
            str(manual.get("title") or ""),
            str(manual.get("content") or ""),
            language,
        )
        if manual_html:
            body_sections.append(manual_html)
    # Assembly runs on the collectors, not the string builders. HTML/PDF was the
    # last format still assembling from rendered markup, which is why exhibit
    # ordinals and the executive summary could not be built: this function never
    # held a SectionData to attach them to. Excel and PPTX already work this way.
    #
    # Output is intended to be byte-identical to the builder path — every
    # `_section_*` was already a thin `render_html(collect_*(...))` wrapper, so
    # this removes one level of indirection rather than changing what renders.
    from dataclasses import replace as _replace

    from backend.reporting.html_renderer import render_html

    collected: list = []
    exhibit_no = 0

    for sec in sections:
        if sec in SECTION_COLLECTORS:
            try:
                payload = collect_section(
                    db, sec, domain_id, org_id,
                    benchmark_profile_id=benchmark_profile_id,
                    benchmark_org=benchmark_org,
                )
                # Numbered only once a section has actually collected, so a
                # section that errors below does not consume an ordinal and
                # leave a gap in the sequence a reader would notice.
                exhibit_no += 1
                # Titles are translated here rather than in each collector: the
                # section id is canonical and this is the one place every
                # section passes through, so a new section cannot forget to.
                payload = _replace(
                    payload,
                    exhibit=exhibit_no,
                    title=translate(f"report.section.{sec}", language),
                )
                # Resolve here, where the payload forks. Every renderer localizes
                # what it is handed, but the executive summary is not a renderer:
                # it reads `takeaway` off the collected payload directly, so a
                # migrated takeaway reached it as a raw catalog key. Doing it once
                # at the fork covers both consumers; localize_section is
                # idempotent, so the renderers' own pass stays a no-op.
                payload = localize_section(payload, language)
                collected.append(payload)
                body_sections.append(render_html(payload, language))
            except Exception as exc:
                # Per-section error boundary: one failing collector degrades its
                # own section, it does not take the report down.
                body_sections.append(f'<section><h2>{translate(f"report.section.{sec}", language)}</h2>'
                                     f'<p style="color:#ef4444">Error building section: {exc}</p></section>')

    # Built after the loop but placed before it: the summary states the findings
    # and cannot know them until every section has been collected.
    summary = _executive_summary(collected)
    if summary:
        body_sections.insert(0, summary)

    # Task 8.5. Only a non-English artefact needs it: an English report has no
    # mixture to explain. Placed first so a reader meets the limitation before
    # the text it applies to, rather than discovering it as an apparent defect.
    if language != DEFAULT_LANGUAGE:
        body_sections.insert(
            0,
            '<section class="ukip-language-disclosure"><p>'
            f'{translate("report.disclosure.analysis_language", language)}'
            "</p></section>",
        )

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
