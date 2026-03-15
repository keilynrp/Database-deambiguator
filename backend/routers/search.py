"""
Phase 12 Sprint 53 — Full-Text Search
  GET  /search          — global search across entities + authority + annotations
  POST /search/rebuild  — rebuild FTS index (admin+)

Dialect support
---------------
SQLite  : FTS5 virtual table with MATCH + prefix wildcards
PostgreSQL : regular table with GIN tsvector index + plainto_tsquery
"""
import logging
import re

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend import models
from backend.auth import get_current_user, require_role
from backend.database import get_db, SQLALCHEMY_DATABASE_URL

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])

_IS_SQLITE = SQLALCHEMY_DATABASE_URL.startswith("sqlite")

# ── FTS helpers (SQLite / FTS5) ───────────────────────────────────────────────

_UNSAFE_RE = re.compile(r'[^\w\s\-]', re.UNICODE)


def _fts_query(raw: str) -> str:
    """
    Convert a raw user string into a safe FTS5 MATCH expression.
    - Strips characters that could break the FTS5 parser.
    - Appends '*' to every token for prefix matching (autocomplete feel).
    """
    cleaned = _UNSAFE_RE.sub(" ", raw).strip()
    tokens  = [t for t in cleaned.split() if t]
    if not tokens:
        return '""'
    return " ".join(f'"{t}"*' for t in tokens)


# ── Common INSERT helpers ─────────────────────────────────────────────────────

def _rebuild(db: Session) -> int:
    """Drop + repopulate the search_index table. Returns indexed row count."""
    db.execute(text("DELETE FROM search_index"))

    db.execute(text("""
        INSERT INTO search_index (doc_type, doc_id, title, body, href)
        SELECT
            'entity',
            id,
            COALESCE(primary_label, ''),
            COALESCE(canonical_id, '') || ' ' ||
            COALESCE(secondary_label, '') || ' ' ||
            COALESCE(enrichment_concepts, ''),
            '/entities/' || id
        FROM raw_entities
    """))

    db.execute(text("""
        INSERT INTO search_index (doc_type, doc_id, title, body, href)
        SELECT
            'authority',
            id,
            COALESCE(canonical_label, original_value, ''),
            COALESCE(description, '') || ' ' || COALESCE(original_value, ''),
            '/authority'
        FROM authority_records
    """))

    db.execute(text("""
        INSERT INTO search_index (doc_type, doc_id, title, body, href)
        SELECT
            'annotation',
            id,
            COALESCE(content, ''),
            '',
            '/disambiguation'
        FROM annotations
    """))

    db.commit()

    row = db.execute(text("SELECT COUNT(*) FROM search_index")).fetchone()
    return row[0] if row else 0


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("")
def global_search(
    q:     str = Query(min_length=1, max_length=300),
    limit: int = Query(default=20, ge=1, le=100),
    skip:  int = Query(default=0, ge=0),
    doc_type: str | None = Query(default=None, description="entity | authority | annotation"),
    db:    Session      = Depends(get_db),
    _:     models.User  = Depends(get_current_user),
):
    """
    Full-text search across entities, authority records, and annotations.
    Returns ranked results with navigation hrefs.
    Dialect-aware: FTS5 on SQLite, tsvector on PostgreSQL.
    """
    params: dict = {}
    type_filter = ""

    if doc_type:
        type_filter = "AND doc_type = :doc_type"
        params["doc_type"] = doc_type

    params["limit"] = limit
    params["skip"]  = skip

    try:
        if _IS_SQLITE:
            # ── SQLite FTS5 ───────────────────────────────────────────────────
            fts_expr = _fts_query(q)
            params["expr"] = fts_expr

            count_sql = text(f"""
                SELECT COUNT(*)
                FROM search_index
                WHERE search_index MATCH :expr {type_filter}
            """)
            rows_sql = text(f"""
                SELECT doc_type, doc_id, title, body, href, rank
                FROM search_index
                WHERE search_index MATCH :expr {type_filter}
                ORDER BY rank
                LIMIT :limit OFFSET :skip
            """)
        else:
            # ── PostgreSQL tsvector ───────────────────────────────────────────
            params["q"] = q
            _vec = "to_tsvector('english', COALESCE(title,'') || ' ' || COALESCE(body,''))"
            _qry = "plainto_tsquery('english', :q)"

            count_sql = text(f"""
                SELECT COUNT(*)
                FROM search_index
                WHERE {_vec} @@ {_qry} {type_filter}
            """)
            rows_sql = text(f"""
                SELECT doc_type, doc_id, title, body, href
                FROM search_index
                WHERE {_vec} @@ {_qry} {type_filter}
                ORDER BY ts_rank({_vec}, {_qry}) DESC
                LIMIT :limit OFFSET :skip
            """)

        total = db.execute(count_sql, params).fetchone()[0]
        rows  = db.execute(rows_sql,  params).fetchall()

    except Exception as exc:
        logger.warning("Search query failed for %r: %s", q, exc)
        raise HTTPException(status_code=422, detail=f"Invalid search query: {exc}")

    items = [
        {
            "doc_type": r[0],
            "doc_id":   r[1],
            "title":    r[2],
            "snippet":  (r[3] or "")[:120],
            "href":     r[4],
        }
        for r in rows
    ]

    return {"total": total, "skip": skip, "limit": limit, "items": items}


@router.post("/rebuild", status_code=200)
def rebuild_index(
    db: Session    = Depends(get_db),
    _:  models.User = Depends(require_role("super_admin", "admin")),
):
    """Force a full rebuild of the search index. Admin+ only."""
    count = _rebuild(db)
    return {"indexed": count}
