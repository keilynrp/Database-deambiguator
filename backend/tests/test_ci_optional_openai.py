import builtins
import sys

import pytest

from backend.schema_registry import AttributeSchema, DomainSchema


def _sample_domain() -> DomainSchema:
    return DomainSchema(
        id="default",
        name="Default",
        description="",
        primary_entity="entity",
        attributes=[
            AttributeSchema(
                name="name",
                type="string",
                label="Name",
                required=False,
                is_core=True,
            )
        ],
    )


def test_llm_agent_falls_back_without_openai_sdk(monkeypatch):
    from backend import llm_agent

    monkeypatch.setattr(llm_agent, "OpenAI", None)
    monkeypatch.setattr(llm_agent, "client", None)

    result = llm_agent.disambiguate_entity({"name": "Acme"}, _sample_domain(), api_key="test-key")

    assert result.attributes == {"name": "Acme"}
    assert result.extended_payload["simulated"] is True


def test_openai_adapter_imports_without_sdk_until_init(monkeypatch):
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "openai":
            raise ModuleNotFoundError("No module named 'openai'")
        return real_import(name, *args, **kwargs)

    monkeypatch.delitem(sys.modules, "openai", raising=False)
    monkeypatch.setattr(builtins, "__import__", fake_import)

    from backend.adapters.llm.openai_adapter import OpenAIAdapter

    with pytest.raises(RuntimeError, match="OpenAI SDK is not installed"):
        OpenAIAdapter(api_key="test-key")


def test_query_reformulation_falls_back_without_openai_sdk(monkeypatch):
    from backend import llm_agent

    monkeypatch.setattr(llm_agent, "OpenAI", None)
    monkeypatch.setattr(llm_agent, "client", None)

    result = llm_agent.generate_query_reformulations("Gabriel Garcia Marquez")

    assert result.variants == []
    assert result.provider is None
    assert result.model is None
