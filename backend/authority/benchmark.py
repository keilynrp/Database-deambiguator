from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.authority.author_resolution import summarize_author_resolution
from backend.authority.base import AuthorityCandidate, ResolveContext
from backend.authority.nil_detection import detect_author_nil


DEFAULT_AUTHOR_NIL_BENCHMARK_PATH = (
    Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "author_nil_benchmark.json"
)


def _safe_rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 3)


def _candidate_from_dict(payload: dict[str, Any]) -> AuthorityCandidate:
    return AuthorityCandidate(
        authority_source=payload["authority_source"],
        authority_id=payload["authority_id"],
        canonical_label=payload["canonical_label"],
        aliases=list(payload.get("aliases", [])),
        description=payload.get("description"),
        confidence=float(payload.get("confidence", 0.0)),
        uri=payload.get("uri"),
        score_breakdown=dict(payload.get("score_breakdown", {})),
        evidence=list(payload.get("evidence", [])),
        resolution_status=payload.get("resolution_status", "unresolved"),
        merged_sources=list(payload.get("merged_sources", [])),
    )


def _context_from_dict(payload: dict[str, Any]) -> ResolveContext:
    return ResolveContext(
        affiliation=payload.get("affiliation"),
        orcid_hint=payload.get("orcid_hint"),
        doi=payload.get("doi"),
        year=payload.get("year"),
    )


def load_author_nil_benchmark(path: str | Path = DEFAULT_AUTHOR_NIL_BENCHMARK_PATH) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def evaluate_author_nil_case(case: dict[str, Any]) -> dict[str, Any]:
    candidates = [_candidate_from_dict(item) for item in case.get("candidates", [])]
    context = _context_from_dict(case.get("context", {}))
    nil_result = detect_author_nil(candidates)
    summary = summarize_author_resolution(candidates, context)

    expected = case.get("expected", {})
    predicted_winner_id = candidates[0].authority_id if candidates else None
    expected_winner_id = expected.get("winner_authority_id")
    link_expected = expected_winner_id is not None

    fallback_candidates = [item.lower() for item in case.get("fallback_candidates", [])]
    ancestor_label = expected.get("ancestor_label")
    fallback_available = bool(ancestor_label and ancestor_label.lower() in fallback_candidates)

    return {
        "id": case["id"],
        "category": case["category"],
        "expected": expected,
        "predicted": {
            "nil_detected": nil_result.detected,
            "nil_reason": nil_result.nil_reason,
            "nil_score": nil_result.nil_score,
            "review_required": summary.review_required,
            "resolution_route": summary.resolution_route,
            "complexity_score": summary.complexity_score,
            "winner_authority_id": predicted_winner_id,
            "partial_fallback_available": fallback_available,
        },
        "matches": {
            "nil_detection": nil_result.detected == bool(expected.get("nil_detected")),
            "nil_reason": nil_result.nil_reason == expected.get("nil_reason"),
            "review_required": summary.review_required == bool(expected.get("review_required")),
            "resolution_route": summary.resolution_route == expected.get("resolution_route"),
            "exact_link": (not link_expected) or predicted_winner_id == expected_winner_id,
            "partial_fallback_available": fallback_available == bool(expected.get("partial_fallback_available")),
        },
    }


def evaluate_author_nil_benchmark(dataset: dict[str, Any]) -> dict[str, Any]:
    case_results = [evaluate_author_nil_case(case) for case in dataset.get("cases", [])]
    total_cases = len(case_results)

    expected_nil = sum(1 for item in case_results if item["expected"].get("nil_detected"))
    predicted_nil = sum(1 for item in case_results if item["predicted"]["nil_detected"])
    true_positive_nil = sum(
        1
        for item in case_results
        if item["expected"].get("nil_detected") and item["predicted"]["nil_detected"]
    )

    link_cases = [item for item in case_results if item["expected"].get("winner_authority_id")]
    exact_link_hits = sum(1 for item in link_cases if item["matches"]["exact_link"])

    artificial_nil_cases = [item for item in case_results if item["category"] == "artificial_nil"]
    partial_fallback_hits = sum(1 for item in artificial_nil_cases if item["predicted"]["partial_fallback_available"])

    review_required_count = sum(1 for item in case_results if item["predicted"]["review_required"])
    route_hits = sum(1 for item in case_results if item["matches"]["resolution_route"])
    linkable_review_count = sum(
        1
        for item in link_cases
        if item["predicted"]["review_required"]
    )
    manual_review_count = sum(
        1
        for item in case_results
        if item["predicted"]["resolution_route"] == "manual_review"
    )
    llm_path_count = sum(
        1
        for item in case_results
        if item["predicted"]["resolution_route"] == "llm_path"
    )
    nil_reason_hits = sum(
        1
        for item in case_results
        if item["expected"].get("nil_detected")
        and item["matches"]["nil_reason"]
    )

    predicted_nil_reasons: dict[str, int] = {}
    expected_nil_reasons: dict[str, int] = {}
    category_counts: dict[str, int] = {}
    predicted_routes: dict[str, int] = {}
    expected_routes: dict[str, int] = {}
    for item in case_results:
        category_counts[item["category"]] = category_counts.get(item["category"], 0) + 1
        expected_reason = item["expected"].get("nil_reason")
        predicted_reason = item["predicted"].get("nil_reason")
        expected_route = item["expected"].get("resolution_route")
        predicted_route = item["predicted"].get("resolution_route")
        if expected_reason:
            expected_nil_reasons[expected_reason] = expected_nil_reasons.get(expected_reason, 0) + 1
        if predicted_reason:
            predicted_nil_reasons[predicted_reason] = predicted_nil_reasons.get(predicted_reason, 0) + 1
        if expected_route:
            expected_routes[expected_route] = expected_routes.get(expected_route, 0) + 1
        if predicted_route:
            predicted_routes[predicted_route] = predicted_routes.get(predicted_route, 0) + 1

    return {
        "dataset_name": dataset.get("dataset_name", "unknown_dataset"),
        "version": dataset.get("version", 0),
        "totals": {
            "cases": total_cases,
            "by_category": category_counts,
            "expected_nil_cases": expected_nil,
            "predicted_nil_cases": predicted_nil,
            "review_required_cases": review_required_count,
        },
        "metrics": {
            "nil_precision": _safe_rate(true_positive_nil, predicted_nil),
            "nil_recall": _safe_rate(true_positive_nil, expected_nil),
            "exact_link_accuracy": _safe_rate(exact_link_hits, len(link_cases)),
            "route_accuracy": _safe_rate(route_hits, total_cases),
            "review_load_rate": _safe_rate(review_required_count, total_cases),
            "linkable_review_rate": _safe_rate(linkable_review_count, len(link_cases)),
            "manual_review_rate": _safe_rate(manual_review_count, total_cases),
            "llm_path_rate": _safe_rate(llm_path_count, total_cases),
            "partial_fallback_available_rate": _safe_rate(partial_fallback_hits, len(artificial_nil_cases)),
            "nil_reason_accuracy": _safe_rate(nil_reason_hits, expected_nil),
            "avg_nil_score_on_predicted_nil": round(
                sum(item["predicted"]["nil_score"] for item in case_results if item["predicted"]["nil_detected"])
                / predicted_nil,
                3,
            )
            if predicted_nil
            else 0.0,
            "avg_complexity_score": round(
                sum(item["predicted"]["complexity_score"] for item in case_results) / total_cases,
                3,
            )
            if total_cases
            else 0.0,
        },
        "nil_reasons": {
            "expected": expected_nil_reasons,
            "predicted": predicted_nil_reasons,
        },
        "routes": {
            "expected": expected_routes,
            "predicted": predicted_routes,
        },
        "case_results": case_results,
    }
