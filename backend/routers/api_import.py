"""
API-based scientific import endpoints.
  POST /import/openalex  — bulk import from OpenAlex
  POST /import/pubmed    — bulk import from PubMed/NCBI
  GET  /import/status/{job_id} — poll async import job progress
"""
from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Annotated, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import AfterValidator, BaseModel, Field
from sqlalchemy.orm import Session

from backend import models
from backend.adapters.enrichment.openalex import OpenAlexAdapter
from backend.adapters.enrichment.pubmed import PubMedAdapter
from backend.auth import get_current_user, require_role
from backend.database import get_db
from backend.schema_registry import registry
from backend.schemas_enrichment import EnrichedRecord
from backend.tenant_access import persisted_org_id, resolve_request_org_id

logger = logging.getLogger(__name__)

router = APIRouter(tags=["api-import"])

# ---------------------------------------------------------------------------
# In-memory job store
# ---------------------------------------------------------------------------

_jobs: Dict[str, dict] = {}


def _update_job(job_id: str, **kwargs: object) -> None:
    if job_id in _jobs:
        _jobs[job_id].update(kwargs)


# ---------------------------------------------------------------------------
# Shared ingestion helper
# ---------------------------------------------------------------------------


def _ingest_records(
    db: Session,
    records: List[EnrichedRecord],
    domain: str,
    source: str,
    org_id: Optional[int] = None,
) -> int:
    """
    Create RawEntity rows from EnrichedRecord objects.
    Skips records whose DOI already exists within the same org scope.
    Returns number of new rows inserted.
    """
    existing_dois: set[str] = set()
    dois_in_batch = [r.doi for r in records if r.doi]
    if dois_in_batch:
        query = db.query(models.RawEntity.enrichment_doi).filter(
            models.RawEntity.enrichment_doi.in_(dois_in_batch)
        )
        if org_id is not None:
            query = query.filter(models.RawEntity.org_id == org_id)
        existing_dois = {row[0] for row in query.all() if row[0]}

    inserted = 0
    batch: list[models.RawEntity] = []
    for rec in records:
        if rec.doi and rec.doi in existing_dois:
            continue

        attrs = {}
        if rec.authors:
            attrs["authors"] = ", ".join(rec.authors)
        if rec.publication_year:
            attrs["year"] = rec.publication_year
        if rec.affiliations:
            attrs["affiliation"] = "; ".join(rec.affiliations)
            attrs["affiliations"] = rec.affiliations
        if rec.publisher:
            attrs["publisher"] = rec.publisher
        if rec.venue:
            attrs["venue"] = rec.venue

        # Journal display name for the OLAP `journal` dimension. Prefer the
        # resolved JournalMetrics name, fall back to the raw venue string.
        journal_meta = getattr(rec, "journal", None)
        journal_name = getattr(journal_meta, "display_name", None) if journal_meta else None
        journal_name = journal_name or rec.venue
        if isinstance(journal_name, str) and journal_name.strip():
            attrs["journal"] = journal_name.strip()

        # Task 2.2 — persist structured affiliation metadata
        canonical_affs = getattr(rec, "canonical_affiliations", None)
        if canonical_affs:
            attrs["canonical_affiliations"] = [
                a.model_dump() if hasattr(a, "model_dump") else (a if isinstance(a, dict) else {})
                for a in canonical_affs
            ]
        author_affs = getattr(rec, "author_affiliations", None)
        if author_affs:
            attrs["author_affiliations"] = [
                a.model_dump() if hasattr(a, "model_dump") else (a if isinstance(a, dict) else {})
                for a in author_affs
            ]

        entity = models.RawEntity(
            primary_label=rec.title,
            secondary_label=", ".join(rec.authors[:3]) if rec.authors else None,
            canonical_id=rec.doi,
            entity_type="publication",
            domain=domain,
            source=source,
            enrichment_doi=rec.doi,
            enrichment_citation_count=rec.citation_count or 0,
            enrichment_concepts=", ".join(rec.concepts) if rec.concepts else None,
            enrichment_source=rec.source_api,
            enrichment_status="pending",
            attributes_json=json.dumps(attrs, ensure_ascii=False) if attrs else "{}",
            org_id=persisted_org_id(org_id),
        )
        batch.append(entity)
        if rec.doi:
            existing_dois.add(rec.doi)

        if len(batch) >= 500:
            db.add_all(batch)
            db.commit()
            inserted += len(batch)
            batch = []

    if batch:
        db.add_all(batch)
        db.commit()
        inserted += len(batch)

    return inserted


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------


def _must_be_registered_domain(value: str) -> str:
    """Reject domains the schema registry does not know about.

    ``RawEntity.domain`` is written verbatim from the payload and never
    re-derived, so an unvalidated value silently produces records that no
    schema, facet, dashboard, or report can reach.
    """
    if registry.get_domain(value) is None:
        available = ", ".join(sorted(registry.domains)) or "(none registered)"
        raise ValueError(
            f"Unknown domain {value!r}. Available domains: {available}."
        )
    return value


RegisteredDomain = Annotated[str, AfterValidator(_must_be_registered_domain)]

#: Why ``domain`` is required rather than defaulted.
#:
#: It defaulted to ``"science"``, so a caller that never considered the field
#: got a permanent answer to a question they did not know was being asked —
#: which is the failure the field was added to prevent, not a mitigation of it.
#: ``RawEntity.domain`` is write-once and no re-filing path exists, so a wrong
#: value costs a delete-and-reimport. A 422 costs one line in the request.
_DOMAIN_FIELD = Field(
    ...,
    description=(
        "Registered domain the imported records are filed under. Required: this "
        "is written once at ingest and cannot be changed afterwards."
    ),
)


class OpenAlexImportRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    limit: int = Field(default=100, ge=1, le=1000)
    filters: Optional[Dict[str, str]] = None
    domain: RegisteredDomain = _DOMAIN_FIELD
    preview: bool = False


class PubMedImportRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    limit: int = Field(default=100, ge=1, le=500)
    domain: RegisteredDomain = _DOMAIN_FIELD
    preview: bool = False


class ImportJobResponse(BaseModel):
    job_id: str
    status: str
    record_count: int = 0


class ImportStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: float = 0.0
    records_inserted: int = 0
    total: int = 0
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Operator-facing failure reasons
# ---------------------------------------------------------------------------

_GENERIC_FAILURE = (
    "The import failed for an unexpected reason. Check the server logs for details."
)

# Substrings that identify a failure class, mapped to text safe to hand back over
# the API. Matched against the exception's type name, never its message: a
# message can carry a connection string, a credential, or a row of user data.
_FAILURE_CLASSES: List[tuple[tuple[str, ...], str]] = [
    (("Timeout", "ReadTimeout", "ConnectTimeout"),
     "The provider did not respond in time. Try again, or reduce the number of records."),
    (("ConnectionError", "ConnectError", "RequestError", "SSLError"),
     "Could not reach the provider. Check network access to the external API."),
    (("HTTPStatusError", "HTTPError"),
     "The provider rejected the request. Check the query syntax and the record limit."),
    (("ParseError", "JSONDecodeError", "ValueError"),
     "The provider returned a response that could not be read."),
    (("OperationalError", "IntegrityError", "DatabaseError", "SQLAlchemyError"),
     "The records were retrieved but could not be saved. Check the server logs."),
]


_NO_MATCHES = "The query returned no records. Try broadening it."

_PROVIDER_UNAVAILABLE = (
    "The provider returned no records because the request to it failed. "
    "This is not an empty result — try again shortly."
)

_PARTIAL_RESULT = (
    "The provider failed part-way, so fewer records were imported than requested. "
    "Re-run the import to collect the rest."
)


def _abort_on_swallowed_provider_error(job_id: str, adapter, records, provider: str) -> bool:
    """Fail the job when an empty result is actually a provider failure.

    The adapters catch transport, HTTP and parse errors and return ``[]`` — the
    right degradation for the enrichment worker, which must move on, but it
    turns a provider outage into a *successful* import of nothing. A silent
    wrong success is worse than a mute failure, so the import path asks the
    adapter whether the empty list means "no matches" or "the call failed".

    Returns True when the job was failed and the caller should stop.
    """
    last_error = getattr(adapter, "last_error", None)
    if not last_error:
        return False
    if records:
        # Partial result: the provider failed part-way and the adapter returned
        # what it had. Keeping the records is right; reporting a clean success
        # is not, because the caller cannot tell the page was cut short.
        logger.warning("%s import job %s: partial result after provider error: %s",
                       provider, job_id, last_error)
        _update_job(job_id, error=_PARTIAL_RESULT)
        return False
    logger.error("%s import job %s: empty result masked a provider error: %s",
                 provider, job_id, last_error)
    _update_job(job_id, status="failed", progress=0.0, error=_PROVIDER_UNAVAILABLE)
    return True


def _completion_error(job_id: str, inserted: int) -> Optional[str]:
    """The note a completed job carries, if any.

    A partial-result warning already recorded by
    ``_abort_on_swallowed_provider_error`` outranks the empty-query note and
    must not be overwritten when the job finishes.
    """
    existing = _jobs.get(job_id, {}).get("error")
    if existing:
        return existing
    return None if inserted else _NO_MATCHES


def _failure_reason(exc: BaseException) -> str:
    """Map an exception to text an operator can act on.

    Deliberately keyed on the exception *type*, not its message. A message may
    contain a DSN, a credential or a fragment of user data, and this value is
    returned over the API — see issue #217.
    """
    name = type(exc).__name__
    for markers, message in _FAILURE_CLASSES:
        if any(marker in name for marker in markers):
            return message
    return _GENERIC_FAILURE


# ---------------------------------------------------------------------------
# Background task runners
# ---------------------------------------------------------------------------


def _run_openalex_import(
    job_id: str,
    query: str,
    filters: Optional[Dict[str, str]],
    limit: int,
    domain: str,
    org_id: Optional[int],
    db_factory,
) -> None:
    _update_job(job_id, status="running", progress=0.0, error=None)
    try:
        adapter = OpenAlexAdapter()
        records = adapter.search_bulk(query, filters=filters, limit=limit)
        if _abort_on_swallowed_provider_error(job_id, adapter, records, "OpenAlex"):
            return
        _update_job(job_id, total=len(records), progress=0.5)

        db = next(db_factory)
        try:
            inserted = _ingest_records(db, records, domain, "openalex", org_id)
        finally:
            db.close()

        _update_job(
            job_id, status="done", progress=1.0, records_inserted=inserted,
            error=_completion_error(job_id, inserted),
        )
    except Exception as exc:
        logger.error("OpenAlex import job %s failed: %s", job_id, exc)
        _update_job(job_id, status="failed", progress=0.0, error=_failure_reason(exc))


def _run_pubmed_import(
    job_id: str,
    query: str,
    limit: int,
    domain: str,
    org_id: Optional[int],
    db_factory,
) -> None:
    _update_job(job_id, status="running", progress=0.0, error=None)
    try:
        adapter = PubMedAdapter()
        records = adapter.search_bulk(query, limit=limit)
        if _abort_on_swallowed_provider_error(job_id, adapter, records, "PubMed"):
            return
        _update_job(job_id, total=len(records), progress=0.5)

        db = next(db_factory)
        try:
            inserted = _ingest_records(db, records, domain, "pubmed", org_id)
        finally:
            db.close()

        _update_job(
            job_id, status="done", progress=1.0, records_inserted=inserted,
            error=_completion_error(job_id, inserted),
        )
    except Exception as exc:
        logger.error("PubMed import job %s failed: %s", job_id, exc)
        _update_job(job_id, status="failed", progress=0.0, error=_failure_reason(exc))


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/import/openalex", status_code=202, response_model=ImportJobResponse)
def import_openalex(
    payload: OpenAlexImportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("super_admin", "admin", "editor")),
):
    org_id = resolve_request_org_id(db, current_user)

    if payload.preview:
        adapter = OpenAlexAdapter()
        records = adapter.search_bulk(
            payload.query, filters=payload.filters, limit=min(payload.limit, 10)
        )
        inserted = _ingest_records(db, records, payload.domain, "openalex", org_id)
        return ImportJobResponse(job_id="preview", status="done", record_count=inserted)

    job_id = str(uuid.uuid4())
    _jobs[job_id] = {
        "status": "queued",
        "progress": 0.0,
        "records_inserted": 0,
        "total": payload.limit,
    }

    from backend.database import get_db as db_factory
    background_tasks.add_task(
        _run_openalex_import,
        job_id,
        payload.query,
        payload.filters,
        payload.limit,
        payload.domain,
        org_id,
        db_factory(),
    )

    return ImportJobResponse(job_id=job_id, status="queued", record_count=0)


@router.post("/import/pubmed", status_code=202, response_model=ImportJobResponse)
def import_pubmed(
    payload: PubMedImportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("super_admin", "admin", "editor")),
):
    org_id = resolve_request_org_id(db, current_user)

    if payload.preview:
        adapter = PubMedAdapter()
        records = adapter.search_bulk(payload.query, limit=min(payload.limit, 10))
        inserted = _ingest_records(db, records, payload.domain, "pubmed", org_id)
        return ImportJobResponse(job_id="preview", status="done", record_count=inserted)

    job_id = str(uuid.uuid4())
    _jobs[job_id] = {
        "status": "queued",
        "progress": 0.0,
        "records_inserted": 0,
        "total": payload.limit,
    }

    from backend.database import get_db as db_factory
    background_tasks.add_task(
        _run_pubmed_import,
        job_id,
        payload.query,
        payload.limit,
        payload.domain,
        org_id,
        db_factory(),
    )

    return ImportJobResponse(job_id=job_id, status="queued", record_count=0)


@router.get("/import/status/{job_id}", response_model=ImportStatusResponse)
def import_status(
    job_id: str,
    _: models.User = Depends(get_current_user),
):
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Import job not found")

    job = _jobs[job_id]
    return ImportStatusResponse(
        job_id=job_id,
        status=job.get("status", "unknown"),
        progress=job.get("progress", 0.0),
        records_inserted=job.get("records_inserted", 0),
        total=job.get("total", 0),
        error=job.get("error"),
    )
