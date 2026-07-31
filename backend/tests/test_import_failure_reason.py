"""A failed import job must say why — issue #217.

`GET /import/status/{job_id}` returned a bare `"failed"` with no reason; the
cause reached the server log only. In production this cost a full extra round
trip to discover that a query used unsupported syntax rather than that the
provider was down.

The second half is subtler and is guarded here too. The provider adapters
swallow transport, HTTP and parse failures and return `[]`, so a provider outage
arrived as a *successful* job that imported zero records — indistinguishable
from a query that genuinely matched nothing. A silent wrong success is worse
than a mute failure, so "zero records" must state which of the two it was.

Reasons are operator-facing text, never a traceback: an unrecognised failure
gets a generic message rather than leaking internals to an API response.
"""

from __future__ import annotations

import pytest

from backend.routers import api_import


@pytest.fixture(autouse=True)
def _clean_jobs():
    api_import._jobs.clear()
    yield
    api_import._jobs.clear()


class _FakeAdapter:
    """Stands in for a provider adapter: returns records, or fails, on demand."""

    def __init__(self, records=None, raises=None, last_error=None):
        self._records = records or []
        self._raises = raises
        self.last_error = last_error

    def search_bulk(self, *args, **kwargs):
        if self._raises:
            raise self._raises
        return self._records


def _run_pubmed(monkeypatch, adapter, db_factory):
    monkeypatch.setattr(api_import, "PubMedAdapter", lambda: adapter)
    job_id = "job-under-test"
    api_import._jobs[job_id] = {"status": "queued", "progress": 0.0, "records_inserted": 0, "total": 10}
    # The runner takes a generator and calls next() on it, mirroring get_db();
    # the db_factory fixture hands back a Session directly.
    api_import._run_pubmed_import(job_id, "cancer", 10, "science", None, iter([db_factory()]))
    return api_import._jobs[job_id]


# ── A failure carries a reason ───────────────────────────────────────────────


class TestFailureReason:
    def test_failed_job_records_a_reason(self, monkeypatch, db_factory):
        job = _run_pubmed(monkeypatch, _FakeAdapter(raises=RuntimeError("boom")), db_factory)
        assert job["status"] == "failed"
        assert job.get("error"), "a failed job must say why"

    def test_reason_does_not_leak_internals(self, monkeypatch, db_factory):
        secret = "psycopg2.OperationalError: password authentication failed for user 'ukip'"
        job = _run_pubmed(monkeypatch, _FakeAdapter(raises=RuntimeError(secret)), db_factory)
        assert "password" not in job["error"]
        assert "psycopg2" not in job["error"]
        assert "Traceback" not in job["error"]

    def test_status_endpoint_exposes_the_reason(self, client, auth_headers, monkeypatch, db_factory):
        job = _run_pubmed(monkeypatch, _FakeAdapter(raises=RuntimeError("boom")), db_factory)
        assert job["status"] == "failed"
        resp = client.get("/import/status/job-under-test", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["error"], "the reason must reach the caller, not just the log"


# ── Zero records is not automatically success ────────────────────────────────


class TestEmptyResultIsDisambiguated:
    def test_provider_failure_behind_an_empty_result_is_a_failure(
        self, monkeypatch, db_factory
    ):
        """The adapter swallows transport errors and returns []. Without this,
        an outage is reported as a successful import of nothing."""
        adapter = _FakeAdapter(records=[], last_error="PubMed eSearch returned HTTP 503")
        job = _run_pubmed(monkeypatch, adapter, db_factory)
        assert job["status"] == "failed"
        assert job.get("error")

    def test_genuinely_empty_result_still_succeeds(self, monkeypatch, db_factory):
        adapter = _FakeAdapter(records=[], last_error=None)
        job = _run_pubmed(monkeypatch, adapter, db_factory)
        assert job["status"] == "done"
        assert job["records_inserted"] == 0

    def test_genuinely_empty_result_says_so(self, monkeypatch, db_factory):
        adapter = _FakeAdapter(records=[], last_error=None)
        job = _run_pubmed(monkeypatch, adapter, db_factory)
        assert job.get("error"), (
            "zero matches is a legitimate outcome, but the operator still needs "
            "to be told it was zero matches rather than a silent failure"
        )


# ── The success path is unchanged ────────────────────────────────────────────


class TestSuccessPathUntouched:
    def test_successful_import_carries_no_error(self, monkeypatch, db_factory):
        from backend.schemas_enrichment import EnrichedRecord

        rec = EnrichedRecord(
            id="W1", doi="10.1234/reason-test", title="A paper", authors=["Doe, J"],
            citation_count=0, publication_year=2024, source_api="PubMed",
        )
        job = _run_pubmed(monkeypatch, _FakeAdapter(records=[rec]), db_factory)
        assert job["status"] == "done"
        assert not job.get("error")
