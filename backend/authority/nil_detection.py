from __future__ import annotations

from dataclasses import dataclass

from backend.authority.base import AuthorityCandidate


@dataclass
class NilDetectionResult:
    detected: bool
    nil_score: float
    nil_reason: str | None = None


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def detect_author_nil(candidates: list[AuthorityCandidate]) -> NilDetectionResult:
    """
    Explicit NIL detector for author resolution.

    This layer is intentionally separate from route selection so we can
    distinguish:
    - no candidates at all
    - insufficient KB coverage
    - unresolved ambiguity
    - conflicting evidence
    """
    if not candidates:
        return NilDetectionResult(detected=True, nil_score=1.0, nil_reason="no_candidates")

    top = candidates[0]
    runner_up = candidates[1] if len(candidates) > 1 else None
    gap = top.confidence - (runner_up.confidence if runner_up else 0.0)

    nil_score = 0.0
    if top.confidence < 0.45:
        nil_score += 0.55
    elif top.confidence < 0.55:
        nil_score += 0.35
    elif top.confidence < 0.65:
        nil_score += 0.15

    if top.resolution_status == "unresolved":
        nil_score += 0.30
    elif top.resolution_status == "ambiguous":
        nil_score += 0.15

    if runner_up:
        if gap <= 0.02:
            nil_score += 0.25
        elif gap <= 0.05:
            nil_score += 0.15

    identifiers = float(top.score_breakdown.get("identifiers", 0.0))
    affiliation = float(top.score_breakdown.get("affiliation", 0.0))
    if identifiers < 0.25 and affiliation < 0.10:
        nil_score += 0.10

    nil_score = round(_clamp(nil_score), 3)

    conflict_flag = any("conflict" in signal.lower() for signal in top.evidence) or (
        len(top.merged_sources) >= 2
        and top.resolution_status == "ambiguous"
        and runner_up is not None
        and gap <= 0.03
    )
    if conflict_flag and nil_score >= 0.55:
        return NilDetectionResult(detected=True, nil_score=max(nil_score, 0.82), nil_reason="conflicting_evidence")

    if runner_up and gap <= 0.02 and top.confidence < 0.62 and top.resolution_status == "ambiguous":
        return NilDetectionResult(detected=True, nil_score=max(nil_score, 0.78), nil_reason="unresolved_ambiguity")

    if top.confidence < 0.45 or (top.resolution_status == "unresolved" and top.confidence < 0.55):
        return NilDetectionResult(detected=True, nil_score=max(nil_score, 0.84), nil_reason="insufficient_coverage")

    return NilDetectionResult(detected=False, nil_score=nil_score, nil_reason=None)
