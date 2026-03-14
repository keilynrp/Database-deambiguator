"""
OpenAI-Compatible Adapter — Phase 5 RAG Engine
Works for ANY OpenAI-compatible API: DeepSeek, xAI (Grok), Google (Gemini via proxy),
and Local servers like Ollama, vLLM, or LMStudio.

The adapter detects whether it's using a remote cloud URL or a local endpoint.
Local usage also generates embeddings via sentence-transformers (free, offline).
Sprint 69C: Agentic tool loop via OpenAI function calling format.
"""
import json
import logging
from typing import Any, Callable, Dict, List, Optional
from .base import BaseLLMAdapter

logger = logging.getLogger(__name__)


class LocalAdapter(BaseLLMAdapter):
    """
    Versatile OpenAI-compatible adapter.
    - Local: Ollama (http://localhost:11434/v1), LMStudio, vLLM
    - Cloud: DeepSeek (https://api.deepseek.com), xAI (https://api.x.ai/v1),
             Google (https://generativelanguage.googleapis.com/v1beta/openai)
    Embeddings are always computed via sentence-transformers locally.
    """
    _embedding_model = None  # Lazy loaded singleton

    def __init__(self, base_url: str = "http://localhost:11434/v1", api_key: str = "not-needed", model_name: str = "llama3"):
        import openai
        self._client = openai.OpenAI(base_url=base_url, api_key=api_key)
        self._model_name = model_name
        self._base_url = base_url

    @property
    def provider_name(self) -> str:
        return "local"

    def get_embedding(self, text: str) -> List[float]:
        """Uses sentence-transformers locally — no API calls, no cost."""
        if LocalAdapter._embedding_model is None:
            from sentence_transformers import SentenceTransformer
            LocalAdapter._embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        text = text.replace("\n", " ").strip()
        vector = LocalAdapter._embedding_model.encode(text).tolist()
        return vector

    def chat(self, system_prompt: str, user_query: str, context_chunks: List[str]) -> str:
        context_block = "\n\n---\n\n".join(context_chunks)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"CONTEXT FROM CATALOG:\n{context_block}\n\nQUESTION: {user_query}"}
        ]
        response = self._client.chat.completions.create(
            model=self._model_name,
            messages=messages,
            temperature=0.3,
            max_tokens=1200
        )
        return response.choices[0].message.content

    # ── Sprint 69C ─────────────────────────────────────────────────────────────

    @staticmethod
    def _to_openai_tools(tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert UKIP tool registry format → OpenAI function calling format."""
        result = []
        for t in tools:
            result.append({
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "parameters": {
                        "type": "object",
                        "properties": t.get("parameters", {}),
                        "required": [],
                    },
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
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"CONTEXT FROM CATALOG:\n{context_block}\n\nQUESTION: {user_query}"},
        ]
        openai_tools = self._to_openai_tools(tools)
        tools_used: List[Dict[str, Any]] = []

        for iteration in range(max_iterations):
            try:
                response = self._client.chat.completions.create(
                    model=self._model_name,
                    messages=messages,
                    tools=openai_tools,
                    tool_choice="auto",
                    temperature=0.3,
                    max_tokens=1200,
                )
            except Exception:
                # Provider may not support tool calling — fall back to plain chat
                fallback = self._client.chat.completions.create(
                    model=self._model_name,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=1200,
                )
                return {
                    "answer": fallback.choices[0].message.content or "",
                    "tools_used": tools_used,
                    "iterations": iteration + 1,
                }

            msg = response.choices[0].message

            if response.choices[0].finish_reason != "tool_calls" or not msg.tool_calls:
                return {
                    "answer": msg.content or "",
                    "tools_used": tools_used,
                    "iterations": iteration + 1,
                }

            messages.append(msg)

            for tc in msg.tool_calls:
                fn_name = tc.function.name
                try:
                    fn_args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    fn_args = {}
                try:
                    tool_result = tool_invoker(fn_name, fn_args)
                except Exception as exc:
                    tool_result = {"error": str(exc)}
                tools_used.append({"tool": fn_name, "params": fn_args, "result": tool_result})
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(tool_result, default=str),
                })

        messages.append({"role": "user", "content": "Please provide your final answer based on the information gathered."})
        final = self._client.chat.completions.create(
            model=self._model_name,
            messages=messages,
            temperature=0.3,
            max_tokens=1200,
        )
        return {
            "answer": final.choices[0].message.content or "",
            "tools_used": tools_used,
            "iterations": max_iterations,
        }
