"""The localized-document boundary itself (#292), not any one section's copy.

`test_report_render_boundary.py` walks every real report a fixture can produce
and fails on any surface-prefixed string that leaked through. That is the
outcome guard. This is the structural one: it targets the seam directly —
`LocalizedReportDocument` should be unconstructible with a raw key in it, and
every renderer/exporter entry point must refuse to render a payload that
skipped `localize_section`/`localize_document`, rather than resolving keys
itself. A production renderer bypassing the boundary (reading `section.title`
straight off a collector, an exporter inventing its own `translate()` call)
would not necessarily leak a *visible* key — a mistranslated fallback or an
accidental literal could still read as plausible English — so this test does
not rely on scanning rendered text; it asserts the type-level refusal exists
and fires on the exact input a bypass would produce.
"""
from __future__ import annotations

import pytest

from backend.reporting.document import LocalizedReportDocument, ReportDocument
from backend.reporting.excel_renderer import render_excel
from backend.reporting.html_renderer import render_html, render_html_document
from backend.reporting.localize import (
    UnresolvedCatalogKeyError,
    assert_localized_document,
    assert_localized_section,
    localize_document,
    with_params,
)
from backend.reporting.pptx_renderer import render_pptx
from backend.reporting.section_data import SectionData


def _raw_section(**overrides) -> SectionData:
    base = dict(
        key="entity_stats",
        title="report.section.entity_stats",  # never resolved
        takeaway="30 of 40 entities pass validation.",
        method="Counts are scoped to this domain.",
    )
    base.update(overrides)
    return SectionData(**base)


def _raw_document(**overrides) -> ReportDocument:
    base = dict(
        domain_id="default",
        domain_name="default",
        title=with_params("report.cover.title", domain="default"),
        generated_at="2026-01-01 00:00 UTC",
        stakeholder_label="report.stakeholder.leadership.label",
        sections=(_raw_section(),),
    )
    base.update(overrides)
    return ReportDocument(**base)


class TestLocalizeDocumentProducesACleanBoundary:
    def test_every_owned_string_resolves(self):
        doc = localize_document(_raw_document(), "en")
        # Would raise if anything survived — this is the assertion, not just a
        # setup step, since localize_document already calls it internally.
        assert_localized_document(doc)

    def test_the_result_is_the_boundary_type(self):
        doc = localize_document(_raw_document(), "en")
        assert isinstance(doc, LocalizedReportDocument)


class TestTheGuardCatchesEveryBypassShape:
    """Each case starves the guard of the one thing localize_document would
    have provided, so a renderer/exporter that skipped it hits this exact
    failure rather than shipping a key silently.
    """

    def test_an_unlocalized_section_fails_its_own_assertion(self):
        with pytest.raises(UnresolvedCatalogKeyError):
            assert_localized_section(_raw_section())

    def test_a_key_buried_in_a_table_cell_fails(self):
        from backend.reporting.section_data import Table

        section = _raw_section(
            title="Entity Statistics",
            blocks=(Table(columns=("Status",), rows=(("report.status.passed",),)),),
        )
        with pytest.raises(UnresolvedCatalogKeyError):
            assert_localized_section(section)

    def test_html_render_html_refuses_a_raw_section(self):
        with pytest.raises(UnresolvedCatalogKeyError):
            render_html(_raw_section())

    def test_excel_render_excel_refuses_a_raw_section(self):
        import openpyxl

        with pytest.raises(UnresolvedCatalogKeyError):
            render_excel(_raw_section(), openpyxl.Workbook())

    def test_pptx_render_pptx_refuses_a_raw_section(self):
        from pptx import Presentation
        from pptx.dml.color import RGBColor

        with pytest.raises(UnresolvedCatalogKeyError):
            render_pptx(_raw_section(), Presentation(), RGBColor(0x63, 0x66, 0xF1))

    def test_a_smuggled_document_level_key_fails_document_assembly(self):
        """Not just a section field: a bypass could also hand-construct the
        document-level scalars (title, captions, …) without localizing them.
        """
        with pytest.raises(UnresolvedCatalogKeyError):
            assert_localized_document(
                LocalizedReportDocument(
                    language="en",
                    domain_id="default",
                    domain_name="default",
                    title="report.cover.title",  # smuggled in unresolved
                    generated_at="2026-01-01 00:00 UTC",
                    stakeholder_label="Leadership",
                    domain_caption="Domain",
                    generated_caption="Generated",
                    stakeholder_lens_caption="Stakeholder lens",
                    executive_summary_title="Executive Summary",
                    manual_note_default_title="Analyst Note",
                    disclosure=None,
                    sections=(),
                )
            )

    def test_html_render_html_document_refuses_a_smuggled_document(self):
        with pytest.raises(UnresolvedCatalogKeyError):
            render_html_document(
                LocalizedReportDocument(
                    language="en",
                    domain_id="default",
                    domain_name="default",
                    title="Cover title",
                    generated_at="2026-01-01 00:00 UTC",
                    stakeholder_label="Leadership",
                    domain_caption="Domain",
                    generated_caption="Generated",
                    stakeholder_lens_caption="Stakeholder lens",
                    executive_summary_title="Executive Summary",
                    manual_note_default_title="Analyst Note",
                    disclosure=None,
                    sections=(_raw_section(),),  # title is still a raw key
                    errors=(),
                )
            )
