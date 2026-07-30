"""Task 7.4 — read every takeaway against the figures its own section renders.

Prints, per section, the takeaway and every number the section actually puts on
the page, so a claim resting on a figure the reader cannot check is visible. Run
against a populated dataset; against an empty one every section returns its
empty-state sentence and this proves nothing.
"""
import pathlib
import re
import sys

sys.path.insert(0, "D:/universal-knowledge-intelligence-platform")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend import models, report_builder
from backend.database import Base
from backend.reporting.section_data import Meter, Narrative, StatGrid, Table

engine = create_engine("sqlite://", connect_args={"check_same_thread": False},
                       poolclass=StaticPool)
Base.metadata.create_all(bind=engine)
db = sessionmaker(bind=engine)()

for i in range(9):
    db.add(models.RawEntity(
        primary_label=f"Record {i}", domain="default",
        validation_status=("valid" if i % 4 else "pending"),
        enrichment_status=("completed" if i % 3 else "pending"),
        enrichment_concepts="knowledge graph; ontology; semantics; retrieval",
        enrichment_citation_count=40 + i * 30, enrichment_source="openalex",
        secondary_label=("Review" if i % 2 else "Clinical Trial"),
        quality_score=0.71 + (i % 5) * 0.04,
    ))
for step in ("normalize_labels", "dedupe_titles"):
    db.add(models.HarmonizationLog(step_id=step, step_name=step.replace("_", " ").title(),
                                   records_updated=4, fields_modified="primary_label"))
for n, (val, status, conf) in enumerate([
    ("acme corp", "confirmed", 0.94), ("initech", "pending", 0.42),
    ("globex", "pending", 0.55), ("umbrella", "confirmed", 0.88),
]):
    db.add(models.AuthorityRecord(
        field_name="brand_capitalized", original_value=val,
        canonical_label=val.title() if status == "confirmed" else None,
        confidence=conf, status=status,
        resolution_status="exact_match" if status == "confirmed" else "ambiguous",
        review_required=status != "confirmed",
        nil_reason=None if status == "confirmed" else "multiple_candidates",
    ))
for aid, key, name, comm, cent in [
    (1, "a", "Alice Ng", 1, 0.91), (2, "b", "Bob Ito", 1, 0.55),
    (3, "c", "Carol Vex", 2, 0.73), (4, "d", "Dan Roe", 2, 0.31),
]:
    db.add(models.Author(id=aid, name_key=key, display_name=name))
    db.add(models.AuthorStats(author_id=aid, org_id=None, domain_id="default",
                              degree=3, centrality=cent, community_id=comm,
                              publication_count=6))
db.add(models.CoauthorEdge(author_a_id=2, author_b_id=3, org_id=None,
                           domain_id="default", weight=1.0))
db.add(models.CoauthorEdge(author_a_id=1, author_b_id=2, org_id=None,
                           domain_id="default", weight=2.0))
for issn, nm, nif, bayes, lo, hi, works, apc, doaj in [
    ("i1", "Nature Methods", 4.10, 4.05, 3.60, 4.55, 6, 1500, True),
    ("i2", "Sparse Journal", 2.50, None, None, None, 1, None, False),
]:
    db.add(models.JournalMetric(
        org_id=None, issn_l=issn, display_name=nm, normalized_impact_factor=nif,
        nif_field="cs", nif_bayes=bayes, nif_ci_low=lo, nif_ci_high=hi,
        works_2yr=works, apc_usd=apc, is_in_doaj=doaj))
db.commit()

NUM = re.compile(r"\d[\d,]*\.?\d*%?")


def rendered_numbers(payload) -> set[str]:
    out = set()
    for b in payload.blocks:
        if isinstance(b, StatGrid):
            for it in b.items:
                out |= set(NUM.findall(it.value))
                out |= set(NUM.findall(it.sub or ""))
        elif isinstance(b, Table):
            for row in b.rows:
                for cell in row:
                    out |= set(NUM.findall(str(cell)))
        elif isinstance(b, Narrative):
            for p in b.paragraphs:
                out |= set(NUM.findall(p))
        elif isinstance(b, Meter):
            out.add(f"{round(b.pct)}%")
            out.add(str(round(b.pct)))
    return out


sections = [s for s in report_builder.SECTION_COLLECTORS if s != "top_brands"]
for key in sections:
    p = report_builder.collect_section(db, key, "default")
    cited = set(NUM.findall(p.takeaway))
    shown = rendered_numbers(p)
    # A cited figure counts as checkable if it appears verbatim, or without its
    # percent sign, among the numbers the section renders.
    missing = {c for c in cited
               if c not in shown and c.rstrip("%") not in {s.rstrip("%") for s in shown}}
    flag = "  <-- UNCHECKABLE: " + ", ".join(sorted(missing)) if missing else ""
    print(f"\n[{key}] {p.materiality.name}{flag}")
    print(f"   takeaway: {p.takeaway}")
    print(f"   cites:    {sorted(cited)}")
    if missing:
        print(f"   renders:  {sorted(shown)}")
