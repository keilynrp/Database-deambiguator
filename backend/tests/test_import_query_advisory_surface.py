"""An import must say when the provider did not run the query it was given.

Issue #229, second half. The adapter now records what PubMed actually ran and
whether it dropped part of the query; this covers getting that to the operator.

Two surfaces, because they serve different readers:

* `query_translation` — always present when the provider reported one.
  Diagnostic: it answers "what exactly ran?" after the fact.
* `warning` — set only when the provider dropped or ignored part of the query.
  It sits next to `error` in the same response and must never be reported *as*
  an error: the import succeeded, it just succeeded for a narrower query than
  the one on screen.
"""

from __future__ import annotations

import pytest

from backend.routers import api_import


class _Adapter:
    def __init__(self, warning=None, translation=None, error=None):
        self.last_warning = warning
        self.last_query_translation = translation
        self.last_error = error


@pytest.fixture
def job(monkeypatch):
    job_id = "test-job-229"
    monkeypatch.setitem(api_import._jobs, job_id, {"status": "running", "progress": 0.0})
    return job_id


def test_warning_is_carried_onto_the_job(job):
    api_import._record_provider_advisories(
        job, _Adapter(warning="PubMed did not run your query as written. Dropped: crispr")
    )
    assert "crispr" in api_import._jobs[job]["warning"]


def test_query_translation_is_carried_onto_the_job(job):
    api_import._record_provider_advisories(
        job, _Adapter(translation="cancer[Title] AND english[Filter]")
    )
    assert api_import._jobs[job]["query_translation"] == "cancer[Title] AND english[Filter]"


def test_a_clean_query_records_neither(job):
    api_import._record_provider_advisories(job, _Adapter())
    assert api_import._jobs[job].get("warning") is None
    assert api_import._jobs[job].get("query_translation") is None


def test_a_warning_is_not_an_error(job):
    """The distinction the whole issue rests on. A dropped term must not fail
    the import, and must not populate the field that means failure."""
    api_import._record_provider_advisories(job, _Adapter(warning="dropped: zzzz"))

    assert api_import._jobs[job].get("error") is None
    assert api_import._jobs[job].get("status") == "running"


def test_an_adapter_without_the_attributes_is_tolerated(job):
    """Other providers do not report advisories. Absence is normal, not a bug."""
    class _Bare:
        pass

    api_import._record_provider_advisories(job, _Bare())
    assert api_import._jobs[job].get("warning") is None


# ── The API surface ──────────────────────────────────────────────────────────


def test_status_endpoint_returns_warning_and_translation(client, auth_headers, monkeypatch):
    job_id = "test-job-229-api"
    monkeypatch.setitem(api_import._jobs, job_id, {
        "status": "completed",
        "progress": 1.0,
        "records_inserted": 12,
        "total": 12,
        "error": None,
        "warning": "PubMed did not run your query as written. Dropped: crispr",
        "query_translation": "cas9[All Fields]",
    })

    resp = client.get(f"/import/status/{job_id}", headers=auth_headers)

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "completed"
    assert body["error"] is None
    assert "crispr" in body["warning"]
    assert body["query_translation"] == "cas9[All Fields]"


def test_status_endpoint_omits_them_when_absent(client, auth_headers, monkeypatch):
    job_id = "test-job-229-clean"
    monkeypatch.setitem(api_import._jobs, job_id, {
        "status": "completed", "progress": 1.0, "records_inserted": 3, "total": 3,
    })

    body = client.get(f"/import/status/{job_id}", headers=auth_headers).json()

    assert body["warning"] is None
    assert body["query_translation"] is None
