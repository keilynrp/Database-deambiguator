from collections import defaultdict
import json
import re

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend import models
from backend.analyzers.topic_modeling import TopicAnalyzer
from backend.institutional_benchmarks import evaluate_benchmark
from backend.tenant_access import scope_query_to_org


class AnalyticsService:
    """
    Core business logic and complex persistence queries for dashboard KPIs and Analytics.
    Extracted from the HTTP router layer to enable isolated unit testing.
    """

    _YEAR_RE = re.compile(r"\b(20\d{2}|19\d{2})\b")
    _TOP_BRANDS_N = 5
    _TOP_YEARS_N  = 6

    @classmethod
    def _extract_temporal_year(
        cls,
        attributes_json: str | None,
        primary_label: str | None = None,
        secondary_label: str | None = None,
    ) -> int | None:
        """Extract a plausible scientific year from attrs first, then labels."""
        attrs: dict = {}
        if attributes_json:
            try:
                attrs = json.loads(attributes_json) or {}
            except (TypeError, ValueError):
                attrs = {}

        for key in ("publication_year", "year", "creation_date", "published_at", "date"):
            value = attrs.get(key)
            if value is None:
                continue
            match = cls._YEAR_RE.search(str(value))
            if match:
                return int(match.group(1))

        for fallback in (primary_label, secondary_label):
            if not fallback:
                continue
            match = cls._YEAR_RE.search(str(fallback))
            if match:
                return int(match.group(1))

        return None

    @staticmethod
    def build_recommended_actions(snapshot: dict) -> list[dict]:
        """Return a short, deterministic list of explainable next actions."""
        kpis = snapshot.get("kpis", {})
        quality = snapshot.get("quality") or {}
        top_entities = snapshot.get("top_entities") or []
        top_concepts = snapshot.get("top_concepts") or []

        total_entities = int(kpis.get("total_entities") or 0)
        enrichment_pct = float(kpis.get("enrichment_pct") or 0)
        enriched_count = int(kpis.get("enriched_count") or 0)
        avg_quality = quality.get("average")

        actions: list[dict] = []

        if total_entities and enrichment_pct < 40:
            actions.append({
                "id": "bulk_enrichment",
                "title": "Run bulk enrichment before external review",
                "detail": "Coverage is still too shallow to treat this dataset as decision-ready.",
                "evidence": (
                    f"Only {enriched_count:,} of {total_entities:,} entities "
                    f"are enriched ({enrichment_pct:.1f}% coverage)."
                ),
                "priority": "high",
                "category": "coverage",
            })

        if avg_quality is not None and avg_quality < 0.6:
            actions.append({
                "id": "review_low_quality_records",
                "title": "Review low-quality records before briefing stakeholders",
                "detail": "Low-confidence records can distort the first executive readout.",
                "evidence": f"Average quality is {round(avg_quality * 100)}%.",
                "priority": "high" if avg_quality < 0.45 else "medium",
                "category": "quality",
            })

        if top_entities:
            lead_entity = top_entities[0]
            label = lead_entity.get("primary_label") or f"Entity #{lead_entity.get('id')}"
            citations = int(lead_entity.get("citation_count") or 0)
            actions.append({
                "id": "focus_top_impact_entity",
                "title": "Prioritize the top-impact entity for manual analysis",
                "detail": "A quick manual read of the strongest entity usually improves the pilot narrative.",
                "evidence": f"{label} currently leads with {citations:,} citations.",
                "priority": "medium",
                "category": "impact",
            })

        if top_concepts and enrichment_pct >= 40:
            lead_concept = top_concepts[0]
            actions.append({
                "id": "explore_leading_concept_cluster",
                "title": "Explore the leading concept cluster",
                "detail": "The strongest semantic cluster is a good candidate for the next decision lens.",
                "evidence": (
                    f"{lead_concept.get('concept', 'Top concept')} appears "
                    f"{int(lead_concept.get('count') or 0):,} times in the current snapshot."
                ),
                "priority": "medium",
                "category": "semantic",
            })

        return actions[:4]

    @classmethod
    def get_domain_snapshot(
        cls,
        db: Session,
        topic_analyzer: TopicAnalyzer,
        domain_id: str,
        org_id: int | None = None,
        benchmark_profile_id: str | None = None,
        top_n_concepts: int = 10,
        top_n_entities: int = 5
    ) -> dict:
        """Reusable per-domain KPI snapshot — used by dashboard/summary and compare."""
        def _q():
            q = scope_query_to_org(db.query(models.RawEntity), models.RawEntity, org_id)
            if domain_id and domain_id != "all":
                if domain_id == "default":
                    q = q.filter(
                        (models.RawEntity.domain == domain_id)
                        | (models.RawEntity.domain == None)  # noqa: E711
                    )
                else:
                    q = q.filter(models.RawEntity.domain == domain_id)
            return q

        # Hero KPIs
        total_entities = _q().with_entities(func.count(models.RawEntity.id)).scalar() or 0
        enriched_count = (
            _q().with_entities(func.count(models.RawEntity.id))
            .filter(models.RawEntity.enrichment_status == "completed")
            .scalar() or 0
        )
        enrichment_pct = round(enriched_count / total_entities * 100, 1) if total_entities else 0.0
        avg_citations_raw = (
            _q().with_entities(func.avg(models.RawEntity.enrichment_citation_count))
            .filter(models.RawEntity.enrichment_status == "completed")
            .scalar()
        )
        avg_citations = round(float(avg_citations_raw), 1) if avg_citations_raw else 0.0

        # Entity types distribution
        type_rows = (
            _q().with_entities(models.RawEntity.entity_type,
                               func.count(models.RawEntity.id).label("cnt"))
            .filter(models.RawEntity.entity_type != None)
            .group_by(models.RawEntity.entity_type)
            .order_by(func.count(models.RawEntity.id).desc())
            .limit(8).all()
        )
        type_distribution = [{"type": r[0], "count": r[1]} for r in type_rows]

        temporal_rows = (
            _q().with_entities(
                models.RawEntity.attributes_json,
                models.RawEntity.primary_label,
                models.RawEntity.secondary_label,
            ).all()
        )
        entities_by_year_counter = defaultdict(int)
        label_totals = defaultdict(int)
        label_year_raw = defaultdict(lambda: defaultdict(int))
        all_years_set = set()

        for attributes_json, primary_label, secondary_label in temporal_rows:
            year = cls._extract_temporal_year(attributes_json, primary_label, secondary_label)
            if year is None:
                continue

            entities_by_year_counter[year] += 1
            if secondary_label:
                label_totals[secondary_label] += 1
                label_year_raw[secondary_label][year] += 1
                all_years_set.add(year)

        entities_by_year = [
            {"year": year, "count": entities_by_year_counter[year]}
            for year in sorted(entities_by_year_counter)
        ]

        # Top concepts via TopicAnalyzer
        top_concepts = []
        try:
            result = topic_analyzer.top_topics(domain_id, top_n=top_n_concepts, org_id=org_id)
            top_concepts = result.get("topics", [])
        except Exception:
            pass

        emerging_topic_signals = {
            "domain_id": domain_id,
            "is_experimental": True,
            "years_available": [],
            "baseline_years": [],
            "recent_years": [],
            "signals": [],
        }
        try:
            emerging_topic_signals = topic_analyzer.emerging_signals(
                domain_id,
                top_n=4,
                org_id=org_id,
            )
        except Exception:
            pass

        total_concepts = len(top_concepts)

        # Top entities by citation count
        top_entity_rows = (
            _q()
            .with_entities(models.RawEntity.id, models.RawEntity.primary_label,
                           models.RawEntity.enrichment_citation_count,
                           models.RawEntity.enrichment_source)
            .filter(models.RawEntity.enrichment_status == "completed")
            .order_by(models.RawEntity.enrichment_citation_count.desc())
            .limit(top_n_entities)
            .all()
        )
        top_entities = [
            {"id": r.id, "primary_label": r.primary_label,
             "citation_count": r.enrichment_citation_count or 0, "source": r.enrichment_source}
            for r in top_entity_rows
        ]

        # Heatmap: secondary_label x year
        top_labels = sorted(label_totals, key=lambda b: label_totals[b], reverse=True)[:cls._TOP_BRANDS_N]
        heatmap_domains = sorted(all_years_set)[-cls._TOP_YEARS_N:]
        brand_year_matrix = {
            "brands": top_labels, "years": heatmap_domains,
            "matrix": [[label_year_raw[b].get(d, 0) for d in heatmap_domains] for b in top_labels],
        }

        # Quality KPI
        quality_rows = (
            _q()
            .with_entities(models.RawEntity.quality_score)
            .filter(models.RawEntity.quality_score != None)
            .all()
        )
        quality_values = [r[0] for r in quality_rows if r[0] is not None]
        avg_quality = round(sum(quality_values) / len(quality_values), 3) if quality_values else None
        quality_dist = {
            "high":   sum(1 for v in quality_values if v >= 0.7),
            "medium": sum(1 for v in quality_values if 0.3 <= v < 0.7),
            "low":    sum(1 for v in quality_values if v < 0.3),
        }

        snapshot = {
            "domain_id": domain_id,
            "kpis": {
                "total_entities": total_entities,
                "enriched_count": enriched_count,
                "enrichment_pct": enrichment_pct,
                "avg_citations":  avg_citations,
                "total_concepts": total_concepts,
            },
            "type_distribution":  type_distribution,
            "entities_by_year":   entities_by_year,
            "brand_year_matrix":  brand_year_matrix,
            "top_concepts":       top_concepts,
            "emerging_topic_signals": emerging_topic_signals,
            "top_entities":       top_entities,
            "quality": {"average": avg_quality, "distribution": quality_dist},
        }
        snapshot["recommended_actions"] = cls.build_recommended_actions(snapshot)
        snapshot["institutional_benchmark"] = evaluate_benchmark(snapshot, benchmark_profile_id)
        return snapshot

    @staticmethod
    def get_stats(db: Session, org_id: int | None = None) -> dict:
        total_entities = (
            scope_query_to_org(db.query(func.count(models.RawEntity.id)), models.RawEntity, org_id)
            .scalar()
            or 0
        )

        unique_secondary_labels = (
            scope_query_to_org(
                db.query(func.count(func.distinct(models.RawEntity.secondary_label))),
                models.RawEntity,
                org_id,
            )
            .filter(models.RawEntity.secondary_label != None)
            .scalar() or 0
        )
        unique_entity_types = (
            scope_query_to_org(
                db.query(func.count(func.distinct(models.RawEntity.entity_type))),
                models.RawEntity,
                org_id,
            )
            .filter(models.RawEntity.entity_type != None)
            .scalar() or 0
        )

        validation_rows = (
            scope_query_to_org(
                db.query(models.RawEntity.validation_status, func.count(models.RawEntity.id)),
                models.RawEntity,
                org_id,
            )
            .group_by(models.RawEntity.validation_status)
            .all()
        )
        validation_status = {row[0] or "pending": row[1] for row in validation_rows}

        with_canonical_id = (
            scope_query_to_org(db.query(func.count(models.RawEntity.id)), models.RawEntity, org_id)
            .filter(models.RawEntity.canonical_id != None, models.RawEntity.canonical_id != "")
            .scalar() or 0
        )

        top_secondary_labels = (
            scope_query_to_org(
                db.query(models.RawEntity.secondary_label, func.count(models.RawEntity.id).label("count")),
                models.RawEntity,
                org_id,
            )
            .filter(models.RawEntity.secondary_label != None)
            .group_by(models.RawEntity.secondary_label)
            .order_by(func.count(models.RawEntity.id).desc())
            .limit(10)
            .all()
        )
        type_distribution = (
            scope_query_to_org(
                db.query(models.RawEntity.entity_type, func.count(models.RawEntity.id).label("count")),
                models.RawEntity,
                org_id,
            )
            .filter(models.RawEntity.entity_type != None)
            .group_by(models.RawEntity.entity_type)
            .order_by(func.count(models.RawEntity.id).desc())
            .limit(10)
            .all()
        )
        domain_distribution = (
            scope_query_to_org(
                db.query(models.RawEntity.domain, func.count(models.RawEntity.id).label("count")),
                models.RawEntity,
                org_id,
            )
            .filter(models.RawEntity.domain != None)
            .group_by(models.RawEntity.domain)
            .order_by(func.count(models.RawEntity.id).desc())
            .all()
        )

        quality_rows = (
            scope_query_to_org(db.query(models.RawEntity.quality_score), models.RawEntity, org_id)
            .filter(models.RawEntity.quality_score != None)
            .all()
        )
        quality_values = [r[0] for r in quality_rows if r[0] is not None]
        avg_quality = round(sum(quality_values) / len(quality_values), 3) if quality_values else None
        quality_dist = {
            "high":     sum(1 for v in quality_values if v >= 0.7),
            "medium":   sum(1 for v in quality_values if 0.3 <= v < 0.7),
            "low":      sum(1 for v in quality_values if v < 0.3),
            "unscored": (
                scope_query_to_org(db.query(func.count(models.RawEntity.id)), models.RawEntity, org_id)
                .filter(models.RawEntity.quality_score == None)
                .scalar()
                or 0
            ),
        }

        return {
            "total_entities": total_entities,
            "unique_secondary_labels": unique_secondary_labels,
            "unique_entity_types": unique_entity_types,
            "validation_status": validation_status,
            "identifier_coverage": {
                "with_canonical_id": with_canonical_id,
                "total": total_entities,
            },
            "top_secondary_labels": [{"name": b[0], "count": b[1]} for b in top_secondary_labels],
            "type_distribution": [{"name": t[0], "count": t[1]} for t in type_distribution],
            "domain_distribution": [{"name": d[0], "count": d[1]} for d in domain_distribution],
            "quality": {"average": avg_quality, "distribution": quality_dist},
        }
