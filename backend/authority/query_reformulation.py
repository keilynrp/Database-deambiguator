from __future__ import annotations

import json
import os
from dataclasses import dataclass

from backend.authority.author_resolution import AuthorResolutionSummary, summarize_author_resolution
from backend.authority.base import AuthorityCandidate, ResolveContext
from backend.llm_agent import generate_query_reformulations


@dataclass
class ReformulationTrace:
    enabled: bool = False
    attempted: bool = False
    applied: bool = False
    provider: str | None = None
    model: str | None = None
    generated_queries: list[str] | None = None
    selected_query: str | None = None
    retrieval_gain: int = 0
    candidate_count_before: int = 0
    candidate_count_after: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    estimated_cost_usd: float = 0.0

    def to_json(self) -> str:
        return json.dumps(
            {
                "enabled": self.enabled,
                "attempted": self.attempted,
                "applied": self.applied,
                "provider": self.provider,
                "model": self.model,
                "generated_queries": self.generated_queries or [],
                "selected_query": self.selected_query,
                "retrieval_gain": self.retrieval_gain,
                "candidate_count_before": self.candidate_count_before,
                "candidate_count_after": self.candidate_count_after,
                "prompt_tokens": self.prompt_tokens,
                "completion_tokens": self.completion_tokens,
                "estimated_cost_usd": round(self.estimated_cost_usd, 6),
            },
            ensure_ascii=True,
        )


def _feature_flag_enabled() -> bool:
    return os.environ.get("UKIP_ENABLE_LLM_QUERY_REFORMULATION", "").strip().lower() in {"1", "true", "yes", "on"}


def _max_variants() -> int:
    try:
        return max(1, min(5, int(os.environ.get("UKIP_LLM_QUERY_REFORMULATION_MAX_VARIANTS", "3"))))
    except ValueError:
        return 3


def _model_name() -> str:
    return os.environ.get("UKIP_LLM_QUERY_REFORMULATION_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"


def _estimated_cost_usd(prompt_tokens: int, completion_tokens: int) -> float:
    # Conservative flat estimate for experiment telemetry only, not billing.
    return round((prompt_tokens * 0.00000015) + (completion_tokens * 0.0000006), 6)


def _should_attempt(summary: AuthorResolutionSummary, candidates: list[AuthorityCandidate]) -> bool:
    if not candidates:
        return True
    if summary.nil_reason in {"insufficient_coverage", "unresolved_ambiguity", "conflicting_evidence"}:
        return True
    top_conf = candidates[0].confidence if candidates else 0.0
    return summary.review_required and top_conf < 0.7


def _route_rank(summary: AuthorResolutionSummary) -> int:
    return {
        "fast_path": 4,
        "hybrid_path": 3,
        "llm_path": 2,
        "manual_review": 1,
    }.get(summary.resolution_route, 0)


def _is_better_result(
    base_candidates: list[AuthorityCandidate],
    base_summary: AuthorResolutionSummary,
    new_candidates: list[AuthorityCandidate],
    new_summary: AuthorResolutionSummary,
) -> bool:
    if base_summary.nil_reason and not new_summary.nil_reason:
        return True
    if new_summary.nil_reason and not base_summary.nil_reason:
        return False
    if _route_rank(new_summary) > _route_rank(base_summary):
        return True
    if _route_rank(new_summary) < _route_rank(base_summary):
        return False

    base_top = base_candidates[0].confidence if base_candidates else 0.0
    new_top = new_candidates[0].confidence if new_candidates else 0.0
    if new_top > base_top + 0.05:
        return True
    if len(new_candidates) > len(base_candidates) and new_top >= base_top:
        return True
    return False


def run_author_query_reformulation(
    *,
    value: str,
    context: ResolveContext,
    base_candidates: list[AuthorityCandidate],
    base_summary: AuthorResolutionSummary,
    resolver_fn,
) -> tuple[list[AuthorityCandidate], AuthorResolutionSummary, ReformulationTrace]:
    trace = ReformulationTrace(
        enabled=_feature_flag_enabled(),
        candidate_count_before=len(base_candidates),
    )
    if not trace.enabled or not _should_attempt(base_summary, base_candidates):
        return base_candidates, base_summary, trace

    trace.attempted = True
    reformulation = generate_query_reformulations(
        value,
        context={
            "affiliation": context.affiliation,
            "orcid_hint": context.orcid_hint,
            "doi": context.doi,
            "year": context.year,
        },
        max_variants=_max_variants(),
        model_name=_model_name(),
    )
    trace.provider = reformulation.provider
    trace.model = reformulation.model
    trace.generated_queries = reformulation.variants
    trace.prompt_tokens = reformulation.prompt_tokens
    trace.completion_tokens = reformulation.completion_tokens
    trace.estimated_cost_usd = _estimated_cost_usd(reformulation.prompt_tokens, reformulation.completion_tokens)

    best_candidates = base_candidates
    best_summary = base_summary

    for query in reformulation.variants:
        alt_candidates = resolver_fn(query, "person", context)
        alt_summary = summarize_author_resolution(alt_candidates, context)
        if _is_better_result(best_candidates, best_summary, alt_candidates, alt_summary):
            best_candidates = alt_candidates
            best_summary = alt_summary
            trace.applied = True
            trace.selected_query = query

    trace.candidate_count_after = len(best_candidates)
    trace.retrieval_gain = trace.candidate_count_after - trace.candidate_count_before

    return best_candidates, best_summary, trace
