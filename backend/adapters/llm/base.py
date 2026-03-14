"""
Phase 5: Abstract base class for all LLM adapters.
All providers (OpenAI, Anthropic, DeepSeek, xAI, Google, Local) must implement this interface.
"""
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional


class BaseLLMAdapter(ABC):
    """
    A unified, provider-agnostic interface for Large Language Model inference.
    Concrete implementations are injected at runtime based on the active AIIntegration record.
    """

    @abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        """
        Convert a string of text into a dense vector (embedding).
        Used to populate the ChromaDB Vector Database.
        """
        pass

    @abstractmethod
    def chat(self, system_prompt: str, user_query: str, context_chunks: List[str]) -> str:
        """
        Given a system prompt, a user question, and retrieved context documents,
        produce a grounded answer (RAG generation step).
        """
        pass

    def chat_with_tools(
        self,
        system_prompt: str,
        user_query: str,
        context_chunks: List[str],
        tools: List[Dict[str, Any]],
        tool_invoker: Callable[[str, Dict[str, Any]], Any],
        max_iterations: int = 5,
    ) -> Dict[str, Any]:
        """
        Sprint 69C — Agentic Tool Loop.
        Providers that support function calling override this method.
        Default implementation falls back to plain chat() (no tool use).

        Returns:
            {
                "answer": str,          # final LLM text response
                "tools_used": [...],    # list of {tool, params, result} dicts
                "iterations": int,
            }
        """
        answer = self.chat(
            system_prompt=system_prompt,
            user_query=user_query,
            context_chunks=context_chunks,
        )
        return {"answer": answer, "tools_used": [], "iterations": 1}

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider identifier e.g. 'openai'."""
        pass
