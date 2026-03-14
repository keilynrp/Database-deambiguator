"""
OpenAI Adapter — Phase 5 RAG Engine
Supports: gpt-4o, gpt-4o-mini, text-embedding-3-small/large
Sprint 69C: Agentic tool loop via OpenAI function calling.
"""
import json
import logging
import openai
from typing import Any, Callable, Dict, List
from .base import BaseLLMAdapter

logger = logging.getLogger(__name__)


class OpenAIAdapter(BaseLLMAdapter):

    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        self._client = openai.OpenAI(api_key=api_key)
        self._model_name = model_name
        self._embedding_model = "text-embedding-3-small"

    @property
    def provider_name(self) -> str:
        return "openai"

    def get_embedding(self, text: str) -> List[float]:
        text = text.replace("\n", " ").strip()
        response = self._client.embeddings.create(input=[text], model=self._embedding_model)
        return response.data[0].embedding

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
            response = self._client.chat.completions.create(
                model=self._model_name,
                messages=messages,
                tools=openai_tools,
                tool_choice="auto",
                temperature=0.3,
                max_tokens=1200,
            )
            msg = response.choices[0].message

            if response.choices[0].finish_reason != "tool_calls" or not msg.tool_calls:
                # Final text response
                return {
                    "answer": msg.content or "",
                    "tools_used": tools_used,
                    "iterations": iteration + 1,
                }

            # Append assistant message with tool_calls
            messages.append(msg)

            # Invoke each requested tool
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

        # Exhausted max_iterations — ask for final answer without tools
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
