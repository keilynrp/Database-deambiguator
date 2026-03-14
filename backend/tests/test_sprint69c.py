"""
Sprint 69C — Agentic Tool Loop (Function Calling) tests.

Covers:
- BaseLLMAdapter.chat_with_tools() default fallback implementation
- OpenAIAdapter._to_openai_tools() format conversion
- AnthropicAdapter._to_anthropic_tools() format conversion
- LocalAdapter._to_openai_tools() format conversion
- OpenAIAdapter.chat_with_tools() multi-turn loop (mocked client)
- AnthropicAdapter.chat_with_tools() multi-turn loop (mocked client)
- LocalAdapter.chat_with_tools() fallback on tool-calling failure
- query_catalog_agentic() in rag_engine.py (mocked adapter + vector store)
- /rag/query endpoint with use_tools=True (mocked)
- /rag/query endpoint with use_tools=False stays on non-agentic path
- Response shape: answer, tools_used, iterations, agentic flag
- max_iterations guard
"""
import json
import pytest
from unittest.mock import MagicMock, patch, call


# ── Tool format helpers ────────────────────────────────────────────────────────

_SAMPLE_TOOLS = [
    {
        "name": "get_entity_stats",
        "description": "Returns entity stats for a domain.",
        "parameters": {
            "domain_id": {"type": "string", "default": "default"},
        },
    },
    {
        "name": "get_gaps",
        "description": "Returns gap analysis.",
        "parameters": {
            "domain_id": {"type": "string", "default": "default"},
        },
    },
]


class TestOpenAIToolFormat:
    def test_converts_to_openai_format(self):
        from backend.adapters.llm.openai_adapter import OpenAIAdapter
        result = OpenAIAdapter._to_openai_tools(_SAMPLE_TOOLS)
        assert len(result) == 2
        assert result[0]["type"] == "function"
        assert result[0]["function"]["name"] == "get_entity_stats"
        assert "description" in result[0]["function"]
        assert result[0]["function"]["parameters"]["type"] == "object"

    def test_properties_preserved(self):
        from backend.adapters.llm.openai_adapter import OpenAIAdapter
        result = OpenAIAdapter._to_openai_tools(_SAMPLE_TOOLS)
        props = result[0]["function"]["parameters"]["properties"]
        assert "domain_id" in props

    def test_required_is_empty_list(self):
        from backend.adapters.llm.openai_adapter import OpenAIAdapter
        result = OpenAIAdapter._to_openai_tools(_SAMPLE_TOOLS)
        assert result[0]["function"]["parameters"]["required"] == []

    def test_empty_tools_list(self):
        from backend.adapters.llm.openai_adapter import OpenAIAdapter
        result = OpenAIAdapter._to_openai_tools([])
        assert result == []


class TestAnthropicToolFormat:
    def test_converts_to_anthropic_format(self):
        from backend.adapters.llm.anthropic_adapter import AnthropicAdapter
        result = AnthropicAdapter._to_anthropic_tools(_SAMPLE_TOOLS)
        assert len(result) == 2
        assert result[0]["name"] == "get_entity_stats"
        assert "input_schema" in result[0]
        assert result[0]["input_schema"]["type"] == "object"

    def test_input_schema_has_properties(self):
        from backend.adapters.llm.anthropic_adapter import AnthropicAdapter
        result = AnthropicAdapter._to_anthropic_tools(_SAMPLE_TOOLS)
        assert "domain_id" in result[0]["input_schema"]["properties"]

    def test_no_type_field_at_top_level(self):
        # Anthropic format has no "type": "function" wrapper
        from backend.adapters.llm.anthropic_adapter import AnthropicAdapter
        result = AnthropicAdapter._to_anthropic_tools(_SAMPLE_TOOLS)
        assert "type" not in result[0]


class TestLocalToolFormat:
    def test_converts_to_openai_format(self):
        from backend.adapters.llm.local_adapter import LocalAdapter
        result = LocalAdapter._to_openai_tools(_SAMPLE_TOOLS)
        assert len(result) == 2
        assert result[0]["type"] == "function"
        assert result[0]["function"]["name"] == "get_entity_stats"


# ── Base fallback ──────────────────────────────────────────────────────────────

class TestBaseFallback:
    def test_default_fallback_calls_chat(self):
        """BaseLLMAdapter default chat_with_tools() falls back to chat()."""
        from backend.adapters.llm.base import BaseLLMAdapter

        class DummyAdapter(BaseLLMAdapter):
            def get_embedding(self, text): return [0.0]
            def chat(self, system_prompt, user_query, context_chunks): return "plain answer"
            @property
            def provider_name(self): return "dummy"

        adapter = DummyAdapter()
        result = adapter.chat_with_tools(
            system_prompt="sys",
            user_query="hello",
            context_chunks=[],
            tools=_SAMPLE_TOOLS,
            tool_invoker=lambda n, p: {},
        )
        assert result["answer"] == "plain answer"
        assert result["tools_used"] == []
        assert result["iterations"] == 1

    def test_fallback_ignores_tool_invoker(self):
        from backend.adapters.llm.base import BaseLLMAdapter
        invoked = []

        class DummyAdapter(BaseLLMAdapter):
            def get_embedding(self, text): return []
            def chat(self, system_prompt, user_query, context_chunks): return "ok"
            @property
            def provider_name(self): return "dummy"

        adapter = DummyAdapter()
        invoker = lambda n, p: invoked.append(n) or {}
        adapter.chat_with_tools("sys", "q", [], _SAMPLE_TOOLS, invoker)
        assert invoked == []


# ── OpenAI agentic loop ────────────────────────────────────────────────────────

def _make_openai_text_response(text="Final answer."):
    msg = MagicMock()
    msg.content = text
    msg.tool_calls = None
    choice = MagicMock()
    choice.finish_reason = "stop"
    choice.message = msg
    resp = MagicMock()
    resp.choices = [choice]
    return resp


def _make_openai_tool_call_response(tool_name="get_entity_stats", args=None, call_id="call_1"):
    tc = MagicMock()
    tc.id = call_id
    tc.function.name = tool_name
    tc.function.arguments = json.dumps(args or {"domain_id": "default"})
    msg = MagicMock()
    msg.content = None
    msg.tool_calls = [tc]
    choice = MagicMock()
    choice.finish_reason = "tool_calls"
    choice.message = msg
    resp = MagicMock()
    resp.choices = [choice]
    return resp


class TestOpenAIAgenticLoop:
    def _adapter(self):
        from backend.adapters.llm.openai_adapter import OpenAIAdapter
        adapter = OpenAIAdapter.__new__(OpenAIAdapter)
        adapter._model_name = "gpt-4o-mini"
        adapter._client = MagicMock()
        return adapter

    def test_no_tool_calls_returns_direct_answer(self):
        adapter = self._adapter()
        adapter._client.chat.completions.create.return_value = _make_openai_text_response("Hello!")
        result = adapter.chat_with_tools("sys", "q", [], _SAMPLE_TOOLS, lambda n, p: {})
        assert result["answer"] == "Hello!"
        assert result["tools_used"] == []
        assert result["iterations"] == 1

    def test_single_tool_call_then_answer(self):
        adapter = self._adapter()
        adapter._client.chat.completions.create.side_effect = [
            _make_openai_tool_call_response("get_entity_stats"),
            _make_openai_text_response("Based on stats: all good."),
        ]
        invoker_calls = []
        def invoker(name, params):
            invoker_calls.append(name)
            return {"total": 42, "pct_enriched": 80.0}
        result = adapter.chat_with_tools("sys", "q", [], _SAMPLE_TOOLS, invoker)
        assert result["answer"] == "Based on stats: all good."
        assert len(result["tools_used"]) == 1
        assert result["tools_used"][0]["tool"] == "get_entity_stats"
        assert result["tools_used"][0]["result"]["total"] == 42
        assert result["iterations"] == 2
        assert invoker_calls == ["get_entity_stats"]

    def test_tool_result_appended_to_messages(self):
        adapter = self._adapter()
        adapter._client.chat.completions.create.side_effect = [
            _make_openai_tool_call_response("get_gaps"),
            _make_openai_text_response("Gap analysis done."),
        ]
        adapter.chat_with_tools("sys", "q", [], _SAMPLE_TOOLS, lambda n, p: {"gaps": []})
        # Second call should include tool role message
        second_call_messages = adapter._client.chat.completions.create.call_args_list[1][1]["messages"]
        tool_msgs = [m for m in second_call_messages if isinstance(m, dict) and m.get("role") == "tool"]
        assert len(tool_msgs) == 1

    def test_max_iterations_guard(self):
        adapter = self._adapter()
        # Always returns tool_calls — never text
        adapter._client.chat.completions.create.return_value = _make_openai_tool_call_response()
        result = adapter.chat_with_tools("sys", "q", [], _SAMPLE_TOOLS, lambda n, p: {}, max_iterations=2)
        # After 2 tool calls it does one final plain call
        assert adapter._client.chat.completions.create.call_count == 3  # 2 tool + 1 final
        assert result["iterations"] == 2

    def test_invoker_exception_captured(self):
        adapter = self._adapter()
        adapter._client.chat.completions.create.side_effect = [
            _make_openai_tool_call_response("get_entity_stats"),
            _make_openai_text_response("Sorry, tool failed."),
        ]
        def bad_invoker(name, params):
            raise ValueError("DB error")
        result = adapter.chat_with_tools("sys", "q", [], _SAMPLE_TOOLS, bad_invoker)
        assert result["tools_used"][0]["result"]["error"] == "DB error"


# ── Anthropic agentic loop ─────────────────────────────────────────────────────

def _make_anthropic_text_response(text="Anthropic answer."):
    block = MagicMock()
    block.type = "text"
    block.text = text
    resp = MagicMock()
    resp.stop_reason = "end_turn"
    resp.content = [block]
    return resp


def _make_anthropic_tool_use_response(tool_name="get_entity_stats", tool_input=None, block_id="tu_1"):
    block = MagicMock()
    block.type = "tool_use"
    block.name = tool_name
    block.input = tool_input or {"domain_id": "default"}
    block.id = block_id
    resp = MagicMock()
    resp.stop_reason = "tool_use"
    resp.content = [block]
    return resp


class TestAnthropicAgenticLoop:
    def _adapter(self):
        from backend.adapters.llm.anthropic_adapter import AnthropicAdapter
        adapter = AnthropicAdapter.__new__(AnthropicAdapter)
        adapter._model_name = "claude-3-5-haiku-latest"
        adapter._client = MagicMock()
        return adapter

    def test_no_tool_calls_returns_text(self):
        adapter = self._adapter()
        adapter._client.messages.create.return_value = _make_anthropic_text_response("Direct answer.")
        result = adapter.chat_with_tools("sys", "q", [], _SAMPLE_TOOLS, lambda n, p: {})
        assert result["answer"] == "Direct answer."
        assert result["tools_used"] == []
        assert result["iterations"] == 1

    def test_single_tool_call_then_answer(self):
        adapter = self._adapter()
        adapter._client.messages.create.side_effect = [
            _make_anthropic_tool_use_response("get_entity_stats"),
            _make_anthropic_text_response("Stats retrieved."),
        ]
        invoker = lambda n, p: {"total": 5}
        result = adapter.chat_with_tools("sys", "q", [], _SAMPLE_TOOLS, invoker)
        assert result["answer"] == "Stats retrieved."
        assert result["tools_used"][0]["tool"] == "get_entity_stats"
        assert result["tools_used"][0]["result"]["total"] == 5
        assert result["iterations"] == 2

    def test_tool_result_sent_as_user_message(self):
        adapter = self._adapter()
        adapter._client.messages.create.side_effect = [
            _make_anthropic_tool_use_response("get_gaps"),
            _make_anthropic_text_response("Done."),
        ]
        adapter.chat_with_tools("sys", "q", [], _SAMPLE_TOOLS, lambda n, p: {"gaps": []})
        second_call_messages = adapter._client.messages.create.call_args_list[1][1]["messages"]
        # Last message should be user role with tool_result content
        last_msg = second_call_messages[-1]
        assert last_msg["role"] == "user"
        content = last_msg["content"]
        assert any(item.get("type") == "tool_result" for item in content)

    def test_max_iterations_guard(self):
        adapter = self._adapter()
        adapter._client.messages.create.return_value = _make_anthropic_tool_use_response()
        result = adapter.chat_with_tools("sys", "q", [], _SAMPLE_TOOLS, lambda n, p: {}, max_iterations=2)
        # 2 tool turns + 1 final call
        assert adapter._client.messages.create.call_count == 3
        assert result["iterations"] == 2


# ── query_catalog_agentic ──────────────────────────────────────────────────────

_AGENTIC_RETURN = {
    "answer": "Agentic answer.",
    "tools_used": [{"tool": "get_entity_stats", "params": {}, "result": {"total": 3}}],
    "iterations": 2,
}


class TestQueryCatalogAgentic:
    def test_returns_answer(self, db_session):
        mock_adapter = MagicMock()
        mock_adapter.get_embedding.return_value = [0.1] * 10
        mock_adapter.chat_with_tools.return_value = _AGENTIC_RETURN.copy()
        with patch("backend.analytics.rag_engine._build_adapter", return_value=mock_adapter), \
             patch("backend.analytics.rag_engine.VectorStoreService.query",
                   return_value=[{"text": "E", "id": "e1", "metadata": {}, "similarity_score": 0.9}]):
            from backend.analytics import rag_engine
            result = rag_engine.query_catalog_agentic("How many?", MagicMock(), db_session)
        assert result["answer"] == "Agentic answer."

    def test_agentic_flag_true(self, db_session):
        mock_adapter = MagicMock()
        mock_adapter.get_embedding.return_value = [0.1] * 10
        mock_adapter.chat_with_tools.return_value = _AGENTIC_RETURN.copy()
        with patch("backend.analytics.rag_engine._build_adapter", return_value=mock_adapter), \
             patch("backend.analytics.rag_engine.VectorStoreService.query",
                   return_value=[{"text": "E", "id": "e1", "metadata": {}, "similarity_score": 0.9}]):
            from backend.analytics import rag_engine
            result = rag_engine.query_catalog_agentic("Q?", MagicMock(), db_session)
        assert result["agentic"] is True

    def test_tools_used_in_result(self, db_session):
        mock_adapter = MagicMock()
        mock_adapter.get_embedding.return_value = [0.1] * 10
        mock_adapter.chat_with_tools.return_value = _AGENTIC_RETURN.copy()
        with patch("backend.analytics.rag_engine._build_adapter", return_value=mock_adapter), \
             patch("backend.analytics.rag_engine.VectorStoreService.query",
                   return_value=[{"text": "E", "id": "e1", "metadata": {}, "similarity_score": 0.9}]):
            from backend.analytics import rag_engine
            result = rag_engine.query_catalog_agentic("Q?", MagicMock(), db_session)
        assert "tools_used" in result
        assert result["tools_used"][0]["tool"] == "get_entity_stats"

    def test_iterations_in_result(self, db_session):
        mock_adapter = MagicMock()
        mock_adapter.get_embedding.return_value = [0.1] * 10
        mock_adapter.chat_with_tools.return_value = _AGENTIC_RETURN.copy()
        with patch("backend.analytics.rag_engine._build_adapter", return_value=mock_adapter), \
             patch("backend.analytics.rag_engine.VectorStoreService.query",
                   return_value=[{"text": "E", "id": "e1", "metadata": {}, "similarity_score": 0.9}]):
            from backend.analytics import rag_engine
            result = rag_engine.query_catalog_agentic("Q?", MagicMock(), db_session)
        assert result["iterations"] == 2

    def test_no_adapter_returns_error(self, db_session):
        with patch("backend.analytics.rag_engine._build_adapter", return_value=None):
            from backend.analytics import rag_engine
            result = rag_engine.query_catalog_agentic("Q?", None, db_session)
        assert "error" in result

    def test_empty_vector_store_returns_gracefully(self, db_session):
        mock_adapter = MagicMock()
        mock_adapter.get_embedding.return_value = [0.1] * 10
        with patch("backend.analytics.rag_engine._build_adapter", return_value=mock_adapter), \
             patch("backend.analytics.rag_engine.VectorStoreService.query", return_value=[]):
            from backend.analytics import rag_engine
            result = rag_engine.query_catalog_agentic("Q?", MagicMock(), db_session)
        assert "answer" in result
        assert result["tools_used"] == []


# ── /rag/query endpoint ────────────────────────────────────────────────────────

class TestRagQueryEndpoint:
    def test_use_tools_false_calls_standard_path(self, client, auth_headers):
        mock_result = {"answer": "Normal answer", "sources": [], "provider": "openai", "model": "gpt-4o-mini"}
        with patch("backend.routers.ai_rag.rag_engine.query_catalog", return_value=mock_result) as mock_std, \
             patch("backend.routers.ai_rag.rag_engine.query_catalog_agentic") as mock_ag:
            resp = client.post("/rag/query", json={"question": "Hello?", "use_tools": False}, headers=auth_headers)
        assert resp.status_code == 200
        mock_std.assert_called_once()
        mock_ag.assert_not_called()

    def test_use_tools_true_calls_agentic_path(self, client, auth_headers):
        mock_result = {
            "answer": "Agentic!", "sources": [], "provider": "openai", "model": "gpt-4o-mini",
            "tools_used": [], "iterations": 1, "agentic": True,
        }
        with patch("backend.routers.ai_rag.rag_engine.query_catalog_agentic", return_value=mock_result) as mock_ag, \
             patch("backend.routers.ai_rag.rag_engine.query_catalog") as mock_std:
            resp = client.post("/rag/query", json={"question": "Give me stats", "use_tools": True}, headers=auth_headers)
        assert resp.status_code == 200
        mock_ag.assert_called_once()
        mock_std.assert_not_called()

    def test_agentic_response_has_tools_used(self, client, auth_headers):
        mock_result = {
            "answer": "Done", "sources": [], "provider": "openai", "model": "gpt-4o-mini",
            "tools_used": [{"tool": "get_gaps", "params": {}, "result": []}],
            "iterations": 2, "agentic": True,
        }
        with patch("backend.routers.ai_rag.rag_engine.query_catalog_agentic", return_value=mock_result):
            resp = client.post("/rag/query", json={"question": "Any gaps?", "use_tools": True}, headers=auth_headers)
        assert resp.json()["tools_used"][0]["tool"] == "get_gaps"

    def test_agentic_flag_passed_through(self, client, auth_headers):
        mock_result = {
            "answer": "x", "sources": [], "provider": "openai", "model": "m",
            "tools_used": [], "iterations": 1, "agentic": True,
        }
        with patch("backend.routers.ai_rag.rag_engine.query_catalog_agentic", return_value=mock_result):
            resp = client.post("/rag/query", json={"question": "q", "use_tools": True}, headers=auth_headers)
        assert resp.json()["agentic"] is True

    def test_context_injected_field_present(self, client, auth_headers):
        mock_result = {"answer": "A", "sources": [], "provider": "openai", "model": "m"}
        with patch("backend.routers.ai_rag.rag_engine.query_catalog", return_value=mock_result):
            resp = client.post("/rag/query", json={"question": "q"}, headers=auth_headers)
        assert "context_injected" in resp.json()

    def test_use_tools_requires_auth(self, client):
        resp = client.post("/rag/query", json={"question": "q", "use_tools": True})
        assert resp.status_code in (401, 403)
