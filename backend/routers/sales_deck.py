"""
Sprint 84 — Demo-Readiness: Executive Sales Deck & Narrative PDF
  GET /exports/sales-deck        — live HTML narrative (printable to PDF)
  GET /exports/sales-deck/data   — JSON data payload used by the interactive page
"""
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Response
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend import models
from backend.auth import get_current_user
from backend.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(tags=["demo"])


@router.get("/exports/sales-deck/data")
def sales_deck_data(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """JSON payload for the interactive sales page."""
    total = db.query(func.count(models.RawEntity.id)).scalar() or 0
    enriched = (
        db.query(func.count(models.RawEntity.id))
        .filter(models.RawEntity.enrichment_status == "completed")
        .scalar() or 0
    )
    enrichment_pct = round(enriched / total * 100, 1) if total else 0.0

    quality_rows = (
        db.query(models.RawEntity.quality_score)
        .filter(models.RawEntity.quality_score.isnot(None))
        .all()
    )
    quality_values = [r[0] for r in quality_rows]
    avg_quality = round(sum(quality_values) / len(quality_values) * 100, 1) if quality_values else 0.0

    domains = (
        db.query(models.RawEntity.domain, func.count(models.RawEntity.id))
        .filter(models.RawEntity.domain.isnot(None))
        .group_by(models.RawEntity.domain)
        .order_by(func.count(models.RawEntity.id).desc())
        .limit(6)
        .all()
    )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "kpis": {
            "total_entities": total,
            "enriched_count": enriched,
            "enrichment_pct": enrichment_pct,
            "avg_quality_pct": avg_quality,
            "domains_count": len(domains),
        },
        "domain_breakdown": [{"domain": d, "count": c} for d, c in domains],
        "value_props": [
            {"icon": "⚡", "title": "3 months → 1 hour", "desc": "Reduce analysis time from quarters to minutes with AI-powered entity enrichment and OLAP analytics."},
            {"icon": "🎯", "title": "80%+ auto-enriched", "desc": "Platform auto-enriches records via OpenAlex, Wikidata, VIAF and more — only edge cases need human review."},
            {"icon": "📊", "title": "175+ API endpoints", "desc": "Full REST API with API key auth, webhooks and scheduled exports — integrates with any enterprise stack."},
            {"icon": "🔒", "title": "Enterprise RBAC", "desc": "4-role access control (super_admin / admin / editor / viewer), audit log, and account lockout."},
            {"icon": "🤖", "title": "NLQ + Semantic RAG", "desc": "Ask your data anything in plain English — AI translates to OLAP queries and retrieves semantically relevant records."},
            {"icon": "📬", "title": "Automated delivery", "desc": "Scheduled reports by email (PDF/Excel/HTML), Slack/Teams/Discord alerts, and custom dashboard builder."},
        ],
    }


@router.get("/exports/sales-deck", response_class=Response)
def sales_deck_html(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """
    Returns a self-contained, print-ready HTML executive narrative.
    Open in browser → File → Print → Save as PDF for a polished sales deck.
    """
    data = sales_deck_data(db=db, _=_)
    kpis = data["kpis"]
    domains = data["domain_breakdown"]
    value_props = data["value_props"]

    domain_rows = "".join(
        f'<tr><td style="padding:8px 12px;border-bottom:1px solid #f0f0f0">{d["domain"]}</td>'
        f'<td style="padding:8px 12px;border-bottom:1px solid #f0f0f0;text-align:right;font-weight:600">{d["count"]:,}</td></tr>'
        for d in domains
    )
    vp_cards = "".join(
        f'''<div style="background:#f8faff;border:1px solid #dce7ff;border-radius:12px;padding:20px">
          <div style="font-size:28px;margin-bottom:8px">{vp["icon"]}</div>
          <div style="font-weight:700;color:#1e40af;font-size:15px;margin-bottom:6px">{vp["title"]}</div>
          <div style="color:#6b7280;font-size:13px;line-height:1.5">{vp["desc"]}</div>
        </div>'''
        for vp in value_props
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>UKIP Executive Sales Deck</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #111827; background: #fff; }}
  @media print {{
    .no-print {{ display: none !important; }}
    body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  }}
  .page {{ max-width: 960px; margin: 0 auto; padding: 48px 40px; }}
  .hero {{ background: linear-gradient(135deg, #1e40af 0%, #4f46e5 100%); color: white; border-radius: 20px; padding: 52px 48px; margin-bottom: 40px; }}
  .hero h1 {{ font-size: 38px; font-weight: 800; margin-bottom: 12px; }}
  .hero p {{ font-size: 17px; opacity: 0.85; max-width: 600px; line-height: 1.6; }}
  .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 40px; }}
  .kpi {{ background: #f8faff; border: 1px solid #dce7ff; border-radius: 14px; padding: 24px; text-align: center; }}
  .kpi-number {{ font-size: 36px; font-weight: 800; color: #1e40af; line-height: 1; }}
  .kpi-label {{ font-size: 12px; color: #6b7280; margin-top: 8px; text-transform: uppercase; letter-spacing: 0.05em; }}
  h2 {{ font-size: 22px; font-weight: 700; color: #111827; margin-bottom: 20px; }}
  .section {{ margin-bottom: 40px; }}
  .vp-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }}
  table {{ width: 100%; border-collapse: collapse; border-radius: 12px; overflow: hidden; border: 1px solid #e5e7eb; }}
  thead {{ background: #f9fafb; }}
  thead th {{ padding: 10px 12px; text-align: left; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: #6b7280; }}
  .timeline {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; margin-bottom: 40px; }}
  .step {{ text-align: center; padding: 16px 8px; }}
  .step-num {{ width: 32px; height: 32px; border-radius: 50%; background: #1e40af; color: white; font-weight: 700; font-size: 14px; display: flex; align-items: center; justify-content: center; margin: 0 auto 8px; }}
  .step-title {{ font-size: 12px; font-weight: 600; color: #111827; margin-bottom: 4px; }}
  .step-time {{ font-size: 11px; color: #6b7280; }}
  .step-arrow {{ display: flex; align-items: center; justify-content: center; color: #9ca3af; font-size: 20px; padding-top: 16px; }}
  .footer {{ border-top: 2px solid #1e40af; padding-top: 24px; text-align: center; color: #6b7280; font-size: 13px; }}
  .print-btn {{ position: fixed; top: 20px; right: 20px; background: #1e40af; color: white; border: none; border-radius: 8px; padding: 10px 20px; font-size: 14px; cursor: pointer; font-weight: 600; }}
  .print-btn:hover {{ background: #1e3a8a; }}
</style>
</head>
<body>
<button class="no-print print-btn" onclick="window.print()">🖨 Print / Save PDF</button>
<div class="page">

  <!-- Hero -->
  <div class="hero">
    <h1>Universal Knowledge Intelligence Platform</h1>
    <p>Enterprise-grade master data management, enrichment, and analytics — from raw Excel to strategic intelligence in minutes.</p>
    <div style="margin-top:24px;font-size:14px;opacity:0.7">Generated {datetime.now(timezone.utc).strftime("%B %d, %Y")} &nbsp;·&nbsp; Confidential</div>
  </div>

  <!-- KPIs from live data -->
  <div class="section">
    <h2>Platform at a Glance (Live Data)</h2>
    <div class="kpi-grid">
      <div class="kpi">
        <div class="kpi-number">{kpis["total_entities"]:,}</div>
        <div class="kpi-label">Entities managed</div>
      </div>
      <div class="kpi">
        <div class="kpi-number">{kpis["enrichment_pct"]}%</div>
        <div class="kpi-label">Auto-enriched</div>
      </div>
      <div class="kpi">
        <div class="kpi-number">{kpis["avg_quality_pct"]}%</div>
        <div class="kpi-label">Avg quality score</div>
      </div>
      <div class="kpi">
        <div class="kpi-number">{kpis["domains_count"]}</div>
        <div class="kpi-label">Active domains</div>
      </div>
    </div>
  </div>

  <!-- Value Props -->
  <div class="section">
    <h2>Why UKIP?</h2>
    <div class="vp-grid">{vp_cards}</div>
  </div>

  <!-- Domain breakdown -->
  {f'''<div class="section">
    <h2>Domain Breakdown</h2>
    <table>
      <thead><tr><th>Domain</th><th style="text-align:right">Entities</th></tr></thead>
      <tbody>{domain_rows}</tbody>
    </table>
  </div>''' if domains else ''}

  <!-- Typical workflow timeline -->
  <div class="section">
    <h2>Typical Analyst Workflow — With UKIP</h2>
    <div class="timeline">
      <div class="step"><div class="step-num">1</div><div class="step-title">Import</div><div class="step-time">2 min</div></div>
      <div class="step-arrow">→</div>
      <div class="step"><div class="step-num">2</div><div class="step-title">Auto-Enrich</div><div class="step-time">30 min (auto)</div></div>
      <div class="step-arrow">→</div>
      <div class="step"><div class="step-num">3</div><div class="step-title">Analyze</div><div class="step-time">5 min</div></div>
      <div class="step-arrow">→</div>
      <div class="step"><div class="step-num">4</div><div class="step-title">Project</div><div class="step-time">2 min</div></div>
      <div class="step-arrow">→</div>
      <div class="step"><div class="step-num">5</div><div class="step-title">Export</div><div class="step-time">1 min</div></div>
    </div>
    <p style="color:#6b7280;font-size:14px;text-align:center">Total: ~40 minutes &nbsp;vs.&nbsp; 3 months of manual analyst work</p>
  </div>

  <!-- Sprints roadmap snapshot -->
  <div class="section">
    <h2>Platform Capabilities (82 Sprints Delivered)</h2>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
      {"".join(f'<div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;padding:12px 16px;font-size:13px"><span style="color:#1e40af;font-weight:600">✓</span> {cap}</div>' for cap in [
        "Multi-domain entity management",
        "AI enrichment (OpenAlex, Wikidata, VIAF, ORCID, DBpedia)",
        "OLAP Cube Explorer (DuckDB)",
        "Natural Language Query (NLQ)",
        "Executive Dashboard + KPIs",
        "Topic Modeling & Correlation Analysis",
        "Data Harmonization Pipeline",
        "Authority Control & Disambiguation",
        "Knowledge Graph Export (GraphML, Cytoscape, JSON-LD)",
        "Scheduled Reports (PDF / Excel / HTML by email)",
        "Alert Channels (Slack / Teams / Discord / webhook)",
        "Public API Keys + webhooks (175+ endpoints)",
        "Custom Dashboard Builder (drag-and-drop widgets)",
        "Semantic RAG + Context Engineering",
        "Audit Log + RBAC (4 roles) + Account Lockout",
      ])}
    </div>
  </div>

  <div class="footer">
    <strong>Universal Knowledge Intelligence Platform</strong> &nbsp;·&nbsp; Built with FastAPI + Next.js + DuckDB + ChromaDB<br/>
    This document was auto-generated from live platform data.
  </div>
</div>
</body>
</html>"""

    return Response(content=html, media_type="text/html")
