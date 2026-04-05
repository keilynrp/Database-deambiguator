from __future__ import annotations

from backend.authority.benchmark import evaluate_author_nil_benchmark, load_author_nil_benchmark


def test_author_nil_benchmark_dataset_is_reproducible():
    dataset = load_author_nil_benchmark()

    assert dataset["dataset_name"] == "ukip_author_nil_benchmark_v2"
    assert dataset["version"] == 2
    assert len(dataset["cases"]) == 12


def test_author_nil_benchmark_metrics_match_current_engine_baseline():
    dataset = load_author_nil_benchmark()
    results = evaluate_author_nil_benchmark(dataset)

    assert results["totals"]["cases"] == 12
    assert results["totals"]["by_category"] == {
        "in_kb": 4,
        "ambiguous": 2,
        "real_nil": 4,
        "artificial_nil": 2,
    }
    assert results["metrics"] == {
        "nil_precision": 1.0,
        "nil_recall": 1.0,
        "exact_link_accuracy": 1.0,
        "route_accuracy": 1.0,
        "review_load_rate": 0.75,
        "linkable_review_rate": 0.5,
        "manual_review_rate": 0.583,
        "llm_path_rate": 0.167,
        "partial_fallback_available_rate": 0.5,
        "nil_reason_accuracy": 1.0,
        "avg_nil_score_on_predicted_nil": 0.908,
        "avg_complexity_score": 0.642,
    }
    assert results["nil_reasons"] == {
        "expected": {
            "no_candidates": 1,
            "insufficient_coverage": 3,
            "conflicting_evidence": 1,
            "unresolved_ambiguity": 1,
        },
        "predicted": {
            "no_candidates": 1,
            "insufficient_coverage": 3,
            "conflicting_evidence": 1,
            "unresolved_ambiguity": 1,
        },
    }
    assert results["routes"] == {
        "expected": {
            "fast_path": 1,
            "hybrid_path": 2,
            "llm_path": 2,
            "manual_review": 7,
        },
        "predicted": {
            "fast_path": 1,
            "hybrid_path": 2,
            "llm_path": 2,
            "manual_review": 7,
        },
    }
