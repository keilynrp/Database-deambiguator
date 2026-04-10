"""
Scientific literature import endpoints.
  GET  /scientific/sources              — list available sources
  POST /scientific/search               — search without importing
  POST /scientific/import               — search + save as RawEntity (201)
  POST /scientific/dois                 — batch DOI resolver + save (201)
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.auth import get_current_user, require_role
from backend.database import get_db
from backend import models
from backend.adapters.scientific import get_scientific_adapter, list_sources
from backend.adapters.scientific.base import ScientificRecord
from backend.parsers.science_mapper import science_record_to_entity
from backend.tenant_access import resolve_request_org_id, persisted_org_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/scientific", tags=["scientific-import"])


class SearchRequest(BaseModel):
    source: str
    query: str = Field(min_length=1, max_length=500)
    max_results: int = Field(default=20, ge=1, le=100)
    config: dict = Field(default_factory=dict)


class DoiBatchRequest(BaseModel):
    dois: list[str] = Field(min_length=1, max_length=200)
    source: str = Field(default="crossref")
    config: dict = Field(default_factory=dict)


def _record_to_dict(r: ScientificRecord) -> dict:
    return {
        "title": r.title,
        "doi": r.doi,
        "authors": r.authors,
        "year": r.year,
        "abstract": r.abstract,
        "journal": r.journal,
        "publisher": r.publisher,
        "concepts": r.concepts,
        "citation_count": r.citation_count,
        "is_open_access": r.is_open_access,
        "url": r.url,
        "source_api": r.source_api,
        "external_id": r.external_id,
    }


def _save_records(records: list, db: Session, org_id: Optional[int]) -> dict:
    """Convert ScientificRecords → RawEntity rows. Skips duplicates by DOI."""
    imported = 0
    skipped = 0
    for rec in records:
        if rec.doi:
            exists = db.query(models.RawEntity).filter_by(enrichment_doi=rec.doi).first()
            if exists:
                skipped += 1
                continue
        entity_kwargs = science_record_to_entity({
            "title": rec.title,
            "authors": "; ".join(rec.authors) if rec.authors else None,
            "doi": rec.doi,
            "keywords": ", ".join(rec.concepts) if rec.concepts else None,
            "year": str(rec.year) if rec.year else None,
            "abstract": rec.abstract,
            "journal": rec.journal,
            "publisher": rec.publisher,
        })
        entity_kwargs["enrichment_doi"] = rec.doi
        entity_kwargs["enrichment_citation_count"] = rec.citation_count or 0
        entity_kwargs["enrichment_source"] = rec.source_api
        entity_kwargs["source"] = "scientific_import"
        stored_org = persisted_org_id(org_id)
        if stored_org is not None:
            entity_kwargs["org_id"] = stored_org
        db.add(models.RawEntity(**entity_kwargs))
        imported += 1
    db.commit()
    return {"imported": imported, "skipped": skipped}


@router.get("/sources")
def get_sources(_=Depends(get_current_user)):
    return list_sources()


@router.post("/search")
def search_scientific(body: SearchRequest, _=Depends(get_current_user)):
    try:
        adapter = get_scientific_adapter(body.source, body.config)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    try:
        records = adapter.search(body.query, max_results=body.max_results)
    except Exception as e:
        logger.exception("Scientific search failed for source=%s", body.source)
        raise HTTPException(status_code=502, detail=f"Source unavailable: {e}")
    return [_record_to_dict(r) for r in records]


@router.post("/import", status_code=201)
def import_scientific(
    body: SearchRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("super_admin", "admin", "editor")),
):
    try:
        adapter = get_scientific_adapter(body.source, body.config)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    try:
        records = adapter.search(body.query, max_results=body.max_results)
    except Exception as e:
        logger.exception("Scientific import failed for source=%s", body.source)
        raise HTTPException(status_code=502, detail=f"Source unavailable: {e}")
    org_id = resolve_request_org_id(db, current_user)
    return _save_records(records, db, org_id)


@router.post("/dois", status_code=201)
def import_dois(
    body: DoiBatchRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("super_admin", "admin", "editor")),
):
    try:
        adapter = get_scientific_adapter(body.source, body.config)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    try:
        records = adapter.fetch_batch_dois(body.dois)
    except Exception as e:
        logger.exception("DOI batch failed for source=%s", body.source)
        raise HTTPException(status_code=502, detail=f"Source unavailable: {e}")
    org_id = resolve_request_org_id(db, current_user)
    return _save_records(records, db, org_id)
