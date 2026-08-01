"""Intent routing for the agentic research chat — issue #227.

The resolver used to pick its retrieval mode from three regexes that were
almost entirely Spanish. An English question matched none of them and fell
through to `rag`, so *"How many publications per domain?"* — an aggregate
question that belongs in `nlq` — got answered by semantic retrieval over
documents instead. It did not fail; it answered the wrong way, fluently and
with no signal that the question had been misrouted.

These tests pin the two properties that fix requires:

1. The **decision no longer depends on which words appear in the question**, so
   a third language does not reintroduce the same failure.
2. An unresolvable question stops silently defaulting to `rag`. Guessing is what
   turned a routing miss into a wrong answer.

The classifier is stubbed throughout: what is under test is the routing
contract around it, not the provider's judgement.
"""

from __future__ import annotations

import pytest

from backend import models
from backend.services import agentic_research_chat as svc_module
from backend.services.agentic_research_chat import (
    AgenticChatRequest,
    AgenticResearchChatService,
)


class _FakeIntegration:
    provider_name = "fake-provider"
    model_name = "fake-model"


class _FakeAdapter:
    """Stands in for the LLM already present in the request path."""

    def __init__(self, reply: str):
        self.reply = reply
        self.seen_user_query: str | None = None

    def chat(self, system_prompt: str, user_query: str, context_chunks):
        self.seen_user_query = user_query
        return self.reply


def _ask(db_session, question: str, **overrides):
    user = db_session.query(models.User).filter(models.User.role == "super_admin").first()
    payload_kwargs = {
        "question": question,
        "mode": "auto",
        "domain_id": "science",
        "persist_trace": False,
        **overrides,
    }
    return AgenticResearchChatService.ask(
        db=db_session,
        payload=AgenticChatRequest(**payload_kwargs),
        current_user=user,
        org_id=None,
    )


# ── The intent → mode mapping ────────────────────────────────────────────────


@pytest.mark.parametrize(
    "intents, expected_mode",
    [
        (["aggregate"], "nlq"),
        (["evidence"], "rag"),
        (["exploration"], "hybrid"),
        (["aggregate", "evidence"], "hybrid"),
        (["aggregate", "exploration"], "hybrid"),
        ([], "unclear"),
    ],
)
def test_intents_map_to_modes(monkeypatch, db_session, intents, expected_mode):
    monkeypatch.setattr(
        AgenticResearchChatService,
        "_classify_intents",
        classmethod(lambda cls, question, integration: (set(intents), "llm")),
    )
    result = _ask(db_session, "any question at all")
    assert result["mode_used"] == expected_mode


# ── Language independence ────────────────────────────────────────────────────


def test_routing_ignores_keywords_in_the_question(monkeypatch, db_session):
    """The reason #227 existed: the mode came from matching Spanish tokens.

    "cuantas" was the strongest aggregate keyword in the old table. If the
    resolver still consulted keywords, this question would route to `nlq`
    regardless of the classifier. It must follow the classifier instead.
    """
    monkeypatch.setattr(
        AgenticResearchChatService,
        "_classify_intents",
        classmethod(lambda cls, question, integration: ({"evidence"}, "llm")),
    )
    result = _ask(db_session, "cuantas publicaciones por dominio hay?")
    assert result["mode_used"] == "rag"


def test_same_question_in_two_languages_routes_the_same(monkeypatch, db_session):
    """The reproduction from the issue, with the classifier doing its job.

    Before the fix these two produced different *kinds* of answer: the Spanish
    one aggregated, the English one retrieved documents.
    """
    seen: list[str] = []

    def _classify(cls, question, integration):
        seen.append(question)
        return {"aggregate"}, "llm"

    monkeypatch.setattr(
        AgenticResearchChatService, "_classify_intents", classmethod(_classify)
    )

    es = _ask(db_session, "¿Cuántas publicaciones por dominio?")
    en = _ask(db_session, "How many publications per domain?")

    assert es["mode_used"] == en["mode_used"] == "nlq"
    # The raw question reaches the classifier untouched — no language handling
    # of our own sits in front of it.
    assert seen == ["¿Cuántas publicaciones por dominio?", "How many publications per domain?"]


# ── "unclear" is a real outcome, not a silent fallback ───────────────────────


def test_unclear_runs_neither_branch_and_says_so(monkeypatch, db_session):
    monkeypatch.setattr(
        AgenticResearchChatService,
        "_classify_intents",
        classmethod(lambda cls, question, integration: (set(), "llm")),
    )
    result = _ask(db_session, "asdf qwerty")

    assert result["mode_used"] == "unclear"
    assert result["trace"]["rag_used"] is False
    assert result["trace"]["nlq_used"] is False
    assert result["trace"]["mode_resolution"] == "llm"
    # The user is told the question was not understood, rather than handed a
    # confident answer of the wrong shape.
    assert "no pude determinar" in result["answer"].lower()


# ── No classifier available is an infrastructure state, not an unclear question ──


def test_without_an_llm_it_widens_instead_of_guessing(db_session):
    """The test database has no active integration, so classification is
    impossible. That is not the same as "the question is unclear": we cannot
    ask. Widening to `hybrid` runs both branches rather than silently picking
    the one that happened to be the old default (`rag`), which is precisely how
    an aggregate question got a document answer."""
    result = _ask(db_session, "How many publications per domain?")

    assert result["mode_used"] == "hybrid"
    assert result["trace"]["mode_resolution"] == "no_classifier"


def test_classifier_failure_falls_back_without_raising(monkeypatch, db_session):
    def _boom(cls, question, integration):
        raise RuntimeError("provider exploded")

    monkeypatch.setattr(
        AgenticResearchChatService, "_classify_intents", classmethod(_boom)
    )
    result = _ask(db_session, "How many publications per domain?")

    assert result["mode_used"] == "hybrid"
    assert result["trace"]["mode_resolution"] == "classifier_error"


# ── The classifier itself ────────────────────────────────────────────────────


def test_classifier_parses_the_provider_reply(monkeypatch):
    adapter = _FakeAdapter('{"intents": ["aggregate", "evidence"]}')
    monkeypatch.setattr(svc_module.rag_engine, "_build_adapter", lambda integration: adapter)

    intents, resolution = AgenticResearchChatService._classify_intents(
        "How many publications per domain, and what backs that up?", _FakeIntegration()
    )

    assert intents == {"aggregate", "evidence"}
    assert resolution == "llm"
    assert adapter.seen_user_query == "How many publications per domain, and what backs that up?"


def test_classifier_tolerates_a_fenced_reply(monkeypatch):
    adapter = _FakeAdapter('```json\n{"intents": ["exploration"]}\n```')
    monkeypatch.setattr(svc_module.rag_engine, "_build_adapter", lambda integration: adapter)

    intents, _ = AgenticResearchChatService._classify_intents("whatever", _FakeIntegration())
    assert intents == {"exploration"}


def test_classifier_discards_labels_outside_the_vocabulary(monkeypatch):
    """A provider is free to invent a label. Anything outside the fixed
    vocabulary is dropped rather than mapped onto a mode by accident."""
    adapter = _FakeAdapter('{"intents": ["aggregate", "sentiment", "sql_injection"]}')
    monkeypatch.setattr(svc_module.rag_engine, "_build_adapter", lambda integration: adapter)

    intents, _ = AgenticResearchChatService._classify_intents("whatever", _FakeIntegration())
    assert intents == {"aggregate"}


def test_classifier_reports_unparseable_replies_as_no_intents(monkeypatch):
    adapter = _FakeAdapter("I think this is an aggregate question, honestly")
    monkeypatch.setattr(svc_module.rag_engine, "_build_adapter", lambda integration: adapter)

    intents, resolution = AgenticResearchChatService._classify_intents("whatever", _FakeIntegration())
    assert intents == set()
    assert resolution == "classifier_error"


# ── An explicit mode still bypasses the resolver ─────────────────────────────


def test_explicit_mode_never_calls_the_classifier(monkeypatch, db_session):
    def _should_not_run(cls, question, integration):  # pragma: no cover
        raise AssertionError("the classifier ran for an explicitly requested mode")

    monkeypatch.setattr(
        AgenticResearchChatService, "_classify_intents", classmethod(_should_not_run)
    )
    result = _ask(db_session, "How many publications per domain?", mode="rag")

    assert result["mode_used"] == "rag"
    assert result["trace"]["mode_resolution"] == "explicit"
