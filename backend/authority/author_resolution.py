from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from backend.authority.base import AuthorityCandidate, ResolveContext


@dataclass
class AuthorResolutionSummary:
    resolution_route: str
    complexity_score: float
    review_required: bool
    nil_reason: Optional[str] = None


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def summarize_author_resolution(
    candidates: list[AuthorityCandidate],
    context: ResolveContext,
) -> AuthorResolutionSummary:
    """
    Heuristic author-only routing for the first Decision Engine baseline.

    The route intentionally stays deterministic and explainable:
    - fast_path for very strong exact matches
    - hybrid_path for probable, safely-ranked matches
    - llm_path for ambiguous close calls
    - manual_review / NIL for missing or weak evidence
    """
    if not candidates:
        return AuthorResolutionSummary(
            resolution_route="manual_review",
            complexity_score=1.0,
            review_required=True,
            nil_reason="no_candidates",
        )

    top = candidates[0]
    runner_up = candidates[1] if len(candidates) > 1 else None
    gap = round(top.confidence - (runner_up.confidence if runner_up else 0.0), 3)

    complexity = 0.55
    if context.orcid_hint:
        complexity -= 0.20
    if context.affiliation:
        complexity -= 0.05
    if top.resolution_status == "exact_match":
        complexity -= 0.20
    elif top.resolution_status == "probable_match":
        complexity -= 0.05
    elif top.resolution_status == "ambiguous":
        complexity += 0.10
    else:
        complexity += 0.20

    if top.confidence >= 0.92:
        complexity -= 0.15
    elif top.confidence < 0.72:
        complexity += 0.10

    if gap >= 0.15:
        complexity -= 0.15
    elif gap <= 0.05:
        complexity += 0.15

    if len(candidates) >= 5:
        complexity += 0.10

    complexity = round(_clamp(complexity), 3)

    if top.confidence >= 0.92 and top.resolution_status == "exact_match" and gap >= 0.12:
        return AuthorResolutionSummary(
            resolution_route="fast_path",
            complexity_score=complexity,
            review_required=False,
        )

    if top.confidence >= 0.78 and gap >= 0.10 and top.resolution_status in {"exact_match", "probable_match"}:
        return AuthorResolutionSummary(
            resolution_route="hybrid_path",
            complexity_score=complexity,
            review_required=False,
        )

    if top.confidence >= 0.55 and top.resolution_status in {"probable_match", "ambiguous"}:
        return AuthorResolutionSummary(
            resolution_route="llm_path",
            complexity_score=complexity,
            review_required=True,
        )

    return AuthorResolutionSummary(
        resolution_route="manual_review",
        complexity_score=complexity,
        review_required=True,
        nil_reason="low_confidence",
    )
