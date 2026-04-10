"""
Report builder endpoints.
  POST /reports/generate
  GET  /reports/sections
  POST /exports/pdf
  POST /exports/excel
"""
import logging
from importlib import import_module
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend import models
from backend import report_builder as _report_builder
from backend.auth import get_current_user, require_role
from backend.database import get_db
from backend.exporters.excel_exporter import EnterpriseExcelExporter
from backend.exporters.pptx_exporter import generate_pptx as _generate_pptx
from backend.tenant_access import resolve_request_org_id

logger = logging.getLogger(__name__)

def _load_weasyprint_html():
    module = import_module("weasyprint")
    return module.HTML


# WeasyPrint is imported lazily so the app starts even without it installed.
def _make_pdf(html: str) -> bytes:
    try:
        _WPHTML = _load_weasyprint_html()
        return _WPHTML(string=html).write_pdf()
    except ImportError as exc:
        raise HTTPException(
            status_code=501,
            detail="PDF export requires weasyprint. Install it with: pip install weasyprint",
        ) from exc
    except OSError as exc:
        raise HTTPException(
            status_code=501,
            detail=(
                "PDF export requires native WeasyPrint runtime libraries. "
                "On Windows, install the GTK runtime (or run PDF export from Docker/Linux) and restart the backend."
            ),
        ) from exc

router = APIRouter(tags=["reports"])

_ALL_REPORT_SECTIONS = list(_report_builder.SECTION_LABELS.keys())


class _ReportRequest(BaseModel):
    domain_id: str          = Field(default="default", min_length=1, max_length=64)
    sections:  List[str]    = Field(default=_ALL_REPORT_SECTIONS, min_length=1, max_length=10)
    title:     Optional[str] = Field(default=None, max_length=200)
    benchmark_profile_id: Optional[str] = Field(default=None, max_length=80)


@router.post("/reports/generate", tags=["reports"])
def generate_report(
    payload: _ReportRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("super_admin", "admin", "editor")),
):
    """Generate a self-contained HTML report and return it as a downloadable file."""
    org_id = resolve_request_org_id(db, current_user)
    invalid = [s for s in payload.sections if s not in _report_builder.SECTION_BUILDERS]
    if invalid:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown sections: {invalid}. Valid: {_ALL_REPORT_SECTIONS}",
        )
    html = _report_builder.build(
        db,
        payload.domain_id,
        payload.sections,
        payload.title,
        org_id=org_id,
        benchmark_profile_id=payload.benchmark_profile_id,
    )
    filename = (
        f"ukip_report_{payload.domain_id}_"
        f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.html"
    )
    return Response(
        content=html,
        media_type="text/html",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/reports/sections", tags=["reports"])
def list_report_sections(_: models.User = Depends(get_current_user)):
    """Return available report sections."""
    return [{"id": k, "label": v} for k, v in _report_builder.SECTION_LABELS.items()]


# ── Enterprise Export Endpoints ────────────────────────────────────────────────

@router.post("/exports/pdf", tags=["exports"])
def export_pdf(
    payload: _ReportRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("super_admin", "admin", "editor")),
):
    """Generate a professional PDF report via WeasyPrint."""
    org_id = resolve_request_org_id(db, current_user)
    invalid = [s for s in payload.sections if s not in _report_builder.SECTION_BUILDERS]
    if invalid:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown sections: {invalid}. Valid: {_ALL_REPORT_SECTIONS}",
        )
    html = _report_builder.build(
        db,
        payload.domain_id,
        payload.sections,
        payload.title,
        org_id=org_id,
        benchmark_profile_id=payload.benchmark_profile_id,
    )
    pdf_bytes = _make_pdf(html)
    filename = (
        f"ukip_report_{payload.domain_id}_"
        f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.pdf"
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/exports/excel", tags=["exports"])
def export_excel(
    payload: _ReportRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("super_admin", "admin", "editor")),
):
    """Generate a branded multi-sheet Excel workbook."""
    org_id = resolve_request_org_id(db, current_user)
    xlsx_bytes = EnterpriseExcelExporter().build(
        db,
        payload.domain_id,
        payload.sections,
        org_id=org_id,
    )
    filename = (
        f"ukip_export_{payload.domain_id}_"
        f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.xlsx"
    )
    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/exports/pptx", tags=["exports"])
def export_pptx(
    payload: _ReportRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("super_admin", "admin", "editor")),
):
    """Generate a branded PowerPoint presentation (python-pptx)."""
    org_id = resolve_request_org_id(db, current_user)
    invalid = [s for s in payload.sections if s not in _report_builder.SECTION_BUILDERS]
    if invalid:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown sections: {invalid}. Valid: {_ALL_REPORT_SECTIONS}",
        )
    # Fetch branding settings (use defaults if singleton not yet created)
    from backend.routers.branding import _get_or_create_settings as _branding_settings
    branding = _branding_settings(db)
    branding_dict = {
        "platform_name": branding.platform_name,
        "logo_url":       branding.logo_url,
        "accent_color":   branding.accent_color,
        "footer_text":    branding.footer_text,
    }
    try:
        pptx_bytes = _generate_pptx(
            db=db,
            domain_id=payload.domain_id,
            sections=payload.sections,
            title=payload.title,
            branding=branding_dict,
            org_id=org_id,
        )
    except ImportError as exc:
        raise HTTPException(
            status_code=501,
            detail="PowerPoint export requires python-pptx. Install with: pip install python-pptx",
        ) from exc
    filename = (
        f"ukip_report_{payload.domain_id}_"
        f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.pptx"
    )
    return Response(
        content=pptx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
