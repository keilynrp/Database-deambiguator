"""
Knowledge Gap Detector — Phase 10 (Artifact Studio)
Scans a domain and returns a prioritized list of actionable data gaps.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List

from sqlalchemy.orm import Session

from backend import models
from backend.schema_registry import SchemaRegistry

_registry = SchemaRegistry()


@dataclass
class GapItem:
    category: str        # "enrichment" | "authority" | "concepts" | "dimensions"
    severity: str        # "critical" | "warning" | "ok"
    title: str
    description: str
    affected_count: int
    total_count: int
    pct: float           # affected / total * 100
    action: str


class GapAnalyzer:
    """Runs all gap checks and returns results sorted by severity then impact."""

    def analyze(self, domain_id: str, db: Session) -> List[GapItem]:
        gaps: List[GapItem] = []
        gaps += self._enrichment_gaps(db)
        gaps += self._authority_gaps(db)
        gaps += self._concept_density(db)
        gaps += self._dimension_completeness(domain_id, db)
        # Sort: critical first, then by pct desc within each severity
        _order = {"critical": 0, "warning": 1, "ok": 2}
        return sorted(gaps, key=lambda g: (_order.get(g.severity, 3), -g.pct))

    # ── 1. Enrichment coverage ────────────────────────────────────────────────

    def _enrichment_gaps(self, db: Session) -> List[GapItem]:
        total = db.query(models.RawEntity).count()
        if total == 0:
            return []
        not_done = (
            db.query(models.RawEntity)
            .filter(models.RawEntity.enrichment_status != "done")
            .count()
        )
        pct = not_done / total * 100
        if pct > 40:
            severity = "critical"
        elif pct > 10:
            severity = "warning"
        else:
            severity = "ok"
        return [GapItem(
            category="enrichment",
            severity=severity,
            title="Enrichment Coverage Gap",
            description=f"{not_done} of {total} entities ({pct:.1f}%) have not been enriched with external metadata.",
            affected_count=not_done,
            total_count=total,
            pct=pct,
            action=f"Run enrichment on {not_done} pending entities to improve citation coverage.",
        )]

    # ── 2. Authority resolution backlog ──────────────────────────────────────

    def _authority_gaps(self, db: Session) -> List[GapItem]:
        total = db.query(models.AuthorityRecord).count()
        if total == 0:
            return []
        pending = (
            db.query(models.AuthorityRecord)
            .filter(models.AuthorityRecord.status == "pending")
            .count()
        )
        if pending == 0:
            return []
        pct = pending / total * 100
        return [GapItem(
            category="authority",
            severity="warning",
            title="Authority Resolution Backlog",
            description=f"{pending} of {total} authority records ({pct:.1f}%) are still pending review.",
            affected_count=pending,
            total_count=total,
            pct=pct,
            action="Review pending authority records in Authority Control to confirm or reject candidates.",
        )]

    # ── 3. Concept density ────────────────────────────────────────────────────

    def _concept_density(self, db: Session) -> List[GapItem]:
        enriched = (
            db.query(models.RawEntity)
            .filter(models.RawEntity.enrichment_status == "done")
            .all()
        )
        if not enriched:
            return []
        sparse = [
            e for e in enriched
            if not e.enrichment_concepts or len(e.enrichment_concepts.split(",")) <= 1
        ]
        pct = len(sparse) / len(enriched) * 100
        if pct <= 15:
            return []
        severity = "critical" if pct > 50 else "warning"
        return [GapItem(
            category="concepts",
            severity=severity,
            title="Low Concept Density",
            description=(
                f"{len(sparse)} enriched entities ({pct:.1f}%) have ≤1 concept tag, "
                "limiting semantic search and topic modeling quality."
            ),
            affected_count=len(sparse),
            total_count=len(enriched),
            pct=pct,
            action="Re-enrich sparse entities or review enrichment source quality to improve concept coverage.",
        )]

    # ── 4. Dimension completeness ─────────────────────────────────────────────

    def _dimension_completeness(self, domain_id: str, db: Session) -> List[GapItem]:
        domain = _registry.get_domain(domain_id)
        if not domain:
            return []
        total = db.query(models.RawEntity).count()
        if total == 0:
            return []

        _EMPTY = {"", "unknown", "n/a", "none", "null", "-", "sin datos"}
        gaps: List[GapItem] = []

        string_fields = [a for a in domain.attributes if a.type == "string" and a.is_core]
        for attr in string_fields:
            col = getattr(models.RawEntity, attr.name, None)
            if col is None:
                continue
            rows = db.query(col).all()
            missing = sum(
                1 for (v,) in rows
                if v is None or str(v).strip().lower() in _EMPTY
            )
            pct = missing / total * 100
            if pct < 20:
                continue
            severity = "critical" if pct > 60 else "warning"
            gaps.append(GapItem(
                category="dimensions",
                severity=severity,
                title=f"Missing Values: {attr.label}",
                description=f"{missing} of {total} entities ({pct:.1f}%) have no value for '{attr.label}'.",
                affected_count=missing,
                total_count=total,
                pct=pct,
                action=f"Populate the '{attr.label}' field to improve OLAP query coverage and filtering accuracy.",
            ))
        return gaps
