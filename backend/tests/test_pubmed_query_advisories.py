"""PubMed tells us the query it ran was not the query we sent — issue #229.

NCBI eSearch returns advisory elements alongside results: `QueryTranslation`
(what it actually ran), `OutputMessage`, `ErrorList`, `WarningList`.
`_esearch` read only `.//IdList/Id` and dropped every one of them, so PubMed
could rewrite a malformed query, run the rewritten one, and the import would
report success for a query the operator never wrote.

Two separate things are recorded, because they answer different questions:

* `last_query_translation` — what PubMed ran. Always captured, for the trace.
  It always differs cosmetically (MeSH expansion, `[All Fields]` suffixes), so
  on its own it is diagnostic material, not a signal.

* `last_warning` — set only when PubMed says it **dropped or ignored** part of
  the query. That is the case where the result set answers a different
  question than the one asked, and the only case worth putting in front of a
  user. A warning derived from raw string difference would fire on every
  query, and a warning that always fires is ignored.
"""

from __future__ import annotations

import pytest

from backend.adapters.enrichment.pubmed import PubMedAdapter


def _esearch_xml(*, ids=("1", "2"), body: str = "") -> str:
    id_list = "".join(f"<Id>{i}</Id>" for i in ids)
    return f"""<?xml version="1.0"?>
<eSearchResult>
  <Count>{len(ids)}</Count>
  <IdList>{id_list}</IdList>
  {body}
</eSearchResult>"""


class _FakeResponse:
    status_code = 200

    def __init__(self, text: str):
        self.text = text


@pytest.fixture
def adapter(monkeypatch):
    a = PubMedAdapter()
    monkeypatch.setattr(a, "_delay", 0)
    return a


def _run(monkeypatch, adapter, xml: str, term: str = "cancer[Title]"):
    import backend.adapters.enrichment.pubmed as mod
    monkeypatch.setattr(mod.time, "sleep", lambda *_: None)
    monkeypatch.setattr(mod.requests, "get", lambda *a, **k: _FakeResponse(xml))
    return adapter._esearch(term, limit=10)


# ── The executed query is always captured ────────────────────────────────────


def test_query_translation_is_recorded(monkeypatch, adapter):
    xml = _esearch_xml(body="<QueryTranslation>cancer[Title] AND english[Filter]</QueryTranslation>")
    ids = _run(monkeypatch, adapter, xml)

    assert ids == ["1", "2"]
    assert adapter.last_query_translation == "cancer[Title] AND english[Filter]"


def test_cosmetic_rewriting_is_not_a_warning(monkeypatch, adapter):
    """PubMed rewrites every query. If that alone warned, nothing would."""
    xml = _esearch_xml(body="<QueryTranslation>\"neoplasms\"[MeSH Terms] OR cancer[All Fields]</QueryTranslation>")
    _run(monkeypatch, adapter, xml)

    assert adapter.last_query_translation
    assert adapter.last_warning is None


# ── OutputMessage: PubMed corrected something, intent preserved ──────────────


def test_output_message_is_recorded_but_does_not_warn(monkeypatch, adapter):
    """The reproduction from the issue: an unmatched quote.

    PubMed dropped the stray quote and ran what the operator meant — the issue
    itself confirms both forms return the same 6375 records. Recording it is
    right; putting it in front of a user is not, because nothing was lost.
    """
    xml = _esearch_xml(body="<OutputMessage>Unmatched double quote ignored.</OutputMessage>")
    _run(monkeypatch, adapter, xml, term='Clinical trial"[Title] AND 2024[PDAT]')

    assert "Unmatched double quote ignored." in (adapter.last_query_notes or "")
    assert adapter.last_warning is None


# ── ErrorList / WarningList: something was dropped ───────────────────────────


@pytest.mark.parametrize(
    "body, expected_fragment",
    [
        ("<ErrorList><PhraseNotFound>zzzznotaterm</PhraseNotFound></ErrorList>", "zzzznotaterm"),
        ("<ErrorList><FieldNotFound>Titel</FieldNotFound></ErrorList>", "Titel"),
        ("<WarningList><QuotedPhraseNotFound>\"gene therapy trial\"</QuotedPhraseNotFound></WarningList>",
         "gene therapy trial"),
        ("<WarningList><PhraseIgnored>and</PhraseIgnored></WarningList>", "and"),
    ],
)
def test_dropped_terms_warn(monkeypatch, adapter, body, expected_fragment):
    _run(monkeypatch, adapter, _esearch_xml(body=body))

    assert adapter.last_warning is not None, "a dropped term must reach the operator"
    assert expected_fragment in adapter.last_warning


def test_warning_names_what_was_dropped_not_just_that_something_was(monkeypatch, adapter):
    """'Part of your query was ignored' is not actionable. Which part is."""
    xml = _esearch_xml(body=(
        "<ErrorList><PhraseNotFound>crispr</PhraseNotFound>"
        "<PhraseNotFound>cas9</PhraseNotFound></ErrorList>"
    ))
    _run(monkeypatch, adapter, xml)

    assert "crispr" in adapter.last_warning
    assert "cas9" in adapter.last_warning


def test_results_are_still_returned_when_a_term_was_dropped(monkeypatch, adapter):
    """This is not a failure. The import succeeds; it just succeeded for a
    narrower query than the operator wrote."""
    xml = _esearch_xml(ids=("7", "8", "9"),
                       body="<ErrorList><PhraseNotFound>zzzz</PhraseNotFound></ErrorList>")
    ids = _run(monkeypatch, adapter, xml)

    assert ids == ["7", "8", "9"]
    assert adapter.last_error is None


# ── State does not leak between searches ─────────────────────────────────────


def test_advisories_reset_between_searches(monkeypatch, adapter):
    """A stale warning would attach a previous query's problem to a clean one."""
    _run(monkeypatch, adapter, _esearch_xml(
        body="<ErrorList><PhraseNotFound>zzzz</PhraseNotFound></ErrorList>"))
    assert adapter.last_warning is not None

    _run(monkeypatch, adapter, _esearch_xml(
        body="<QueryTranslation>clean[All Fields]</QueryTranslation>"))
    assert adapter.last_warning is None
    assert adapter.last_query_translation == "clean[All Fields]"


def test_missing_advisories_are_not_an_error(monkeypatch, adapter):
    """Most responses carry none of these. Absence is the normal case."""
    _run(monkeypatch, adapter, _esearch_xml())

    assert adapter.last_warning is None
    assert adapter.last_query_translation is None
    assert adapter.last_error is None
