"""
Anthropic (Claude) Adapter — Phase 5 RAG Engine
Supports: claude-3-5-sonnet-latest, claude-3-haiku-20240307
Embeddings: Falls back to sentence-transformers (Anthropic has no native embedding API).
Sprint 69C: Agentic tool loop via Anthropic tool_use.
"""
import json
import logging
from typing import Any, Callable, Dict, List
from .base import BaseLLMAdapter
from .local_adapter import LocalAdapter  # Reuse sentence-transformers for embeddings

logger = logging.getLogger(__name__)


class AnthropicAdapter(BaseLLMAdapter):

    def __init__(self, api_key: str, model_name: str = "claude-3-5-haiku-latest"):
        import anthropic
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model_name = model_name
        # Claude has no embedding API — use local sentence-transformers as fallback
        self._embed_fallback = LocalAdapter(model_name="all-MiniLM-L6-v2")

    @property
    def provider_name(self) -> str:
        return "anthropic"

    def get_embedding(self, text: str) -> List[float]:
        # Route to local sentence-transformers (free, no API cost)
        return self._embed_fallback.get_embedding(text)

    def chat(self, system_prompt: str, user_query: str, context_chunks: List[str]) -> str:
        context_block = "\n\n---\n\n".join(context_chunks)
        user_content = f"CONTEXT FROM CATALOG:\n{context_block}\n\nQUESTION: {user_query}"

        response = self._client.messages.create(
            model=self._model_name,
            max_tokens=1200,
            system=system_prompt,
            messages=[{"role": "user", "content": user_content}]
        )
        return response.content[0].text

    # ── Sprint 69C ─────────────────────────────────────────────────────────────

    @staticmethod
    def _to_anthropic_tools(tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert UKIP tool registry format → Anthropic tool_use format."""
        result = []
        for t in tools:
            result.append({
                "name": t["name"],
                "description": t.get("description", ""),
                "input_schema": {
                    "type": "object",
                    "properties": t.get("parameters", {}),
                    "required": [],
                },
            })
        return result

    def chat_with_tools(
        self,
        system_prompt: str,
        user_query: str,
        context_chunks: List[str],
        tools: List[Dict[str, Any]],
        tool_invoker: Callable[[str, Dict[str, Any]], Any],
        max_iterations: int = 5,
    ) -> Dict[str, Any]:
        context_block = "\n\n---\n\n".join(context_chunks)
        messages: List[Dict[str, Any]] = [
            {"role": "user", "content": f"CONTEXT FROM CATALOG:\n{context_block}\n\nQUESTION: {user_query}"},
        ]
        anthropic_tools = self._to_anthropic_tools(tools)
        tools_used: List[Dict[str, Any]] = []

        for iteration in range(max_iterations):
            response = self._client.messages.create(
                model=self._model_name,
                max_tokens=1200,
                system=system_prompt,
                tools=anthropic_tools,
                messages=messages,
            )

            if response.stop_reason != "tool_use":
                # Final text response — extract text block
                text = next(
                    (block.text for block in response.content if hasattr(block, "text")),
                    "",
                )
                return {"answer": text, "tools_used": tools_used, "iterations": iteration + 1}

            # Append assistant turn
            messages.append({"role": "assistant", "content": response.content})

            # Collect tool results
            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                fn_name = block.name
                fn_args = block.input if isinstance(block.input, dict) else {}
                try:
                    tool_result = tool_invoker(fn_name, fn_args)
                except Exception as exc:
                    tool_result = {"error": str(exc)}
                tools_used.append({"tool": fn_name, "params": fn_args, "result": tool_result})
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(tool_result, default=str),
                })

            messages.append({"role": "user", "content": tool_results})

        # Exhausted iterations — one final call without tools
        messages.append({"role": "user", "content": [{"type": "text", "text": "Please provide your final answer based on the information gathered."}]})
        final = self._client.messages.create(
            model=self._model_name,
            max_tokens=1200,
            system=system_prompt,
            messages=messages,
        )
        text = next(
            (block.text for block in final.content if hasattr(block, "text")),
            "",
        )
        return {"answer": text, "tools_used": tools_used, "iterations": max_iterations}
