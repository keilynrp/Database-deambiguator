from __future__ import annotations

from copy import deepcopy
import json


DEFAULT_BENCHMARK_PROFILE_ID = "research_portfolio_baseline"


_BUILTIN_PROFILES = [
    {
        "id": "research_portfolio_baseline",
        "name": "Research Portfolio Baseline",
        "description": "General readiness baseline for institutional research portfolio reviews.",
        "region": "generic",
        "rules": [
            {
                "id": "coverage_min",
                "label": "Enrichment coverage",
                "metric": "enrichment_pct",
                "threshold": 60,
                "priority": "high",
                "pass_text": "Coverage is strong enough for a first institutional review.",
                "fail_text": "Coverage is still too low for a confident institutional benchmark.",
            },
            {
                "id": "quality_min",
                "label": "Average quality",
                "metric": "quality_pct",
                "threshold": 65,
                "priority": "high",
                "pass_text": "Average quality supports stakeholder-facing interpretation.",
                "fail_text": "Average quality is still below the baseline for external interpretation.",
            },
            {
                "id": "concept_depth_min",
                "label": "Concept depth",
                "metric": "total_concepts",
                "threshold": 8,
                "priority": "medium",
                "pass_text": "The dataset shows enough semantic depth for comparative review.",
                "fail_text": "Semantic depth is still shallow for a broad institutional reading.",
            },
        ],
    },
    {
        "id": "ref_readiness_baseline",
        "name": "REF Readiness Baseline",
        "description": "Conservative proxy baseline for UK-style portfolio review readiness.",
        "region": "uk",
        "rules": [
            {
                "id": "coverage_min",
                "label": "Enrichment coverage",
                "metric": "enrichment_pct",
                "threshold": 70,
                "priority": "high",
                "pass_text": "Coverage supports a more robust review cut.",
                "fail_text": "Coverage is not yet strong enough for a REF-style baseline review.",
            },
            {
                "id": "quality_min",
                "label": "Average quality",
                "metric": "quality_pct",
                "threshold": 70,
                "priority": "high",
                "pass_text": "Quality is within an acceptable baseline range.",
                "fail_text": "Quality remains below the REF-style baseline threshold.",
            },
            {
                "id": "citations_min",
                "label": "Average citations",
                "metric": "avg_citations",
                "threshold": 20,
                "priority": "medium",
                "pass_text": "Citation intensity supports comparative positioning.",
                "fail_text": "Citation intensity is still weak for comparative review.",
            },
        ],
    },
    {
        "id": "sni_readiness_baseline",
        "name": "SNI Readiness Baseline",
        "description": "Conservative proxy baseline for Mexico SNI-oriented portfolio screening.",
        "region": "mx",
        "rules": [
            {
                "id": "coverage_min",
                "label": "Enrichment coverage",
                "metric": "enrichment_pct",
                "threshold": 65,
                "priority": "high",
                "pass_text": "Coverage is sufficient for a first SNI-style screening.",
                "fail_text": "Coverage should improve before relying on this screening.",
            },
            {
                "id": "portfolio_size_min",
                "label": "Portfolio size",
                "metric": "total_entities",
                "threshold": 25,
                "priority": "medium",
                "pass_text": "Portfolio volume is enough for a first screening view.",
                "fail_text": "Portfolio volume is still too low for a meaningful screening baseline.",
            },
            {
                "id": "quality_min",
                "label": "Average quality",
                "metric": "quality_pct",
                "threshold": 60,
                "priority": "high",
                "pass_text": "Quality supports a first-pass evaluation.",
                "fail_text": "Quality remains below a safe screening threshold.",
            },
        ],
    },
]


def _org_default_profile_id(org) -> str:
    return getattr(org, "benchmark_profile_id", None) or DEFAULT_BENCHMARK_PROFILE_ID


def _org_profile_overrides(org) -> dict:
    raw = getattr(org, "benchmark_profile_overrides", None)
    if not raw:
        return {}
    if isinstance(raw, dict):
        return raw
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else {}
    except (TypeError, ValueError, json.JSONDecodeError):
        return {}


def _apply_org_profile_overrides(profile: dict, org) -> dict:
    overrides = _org_profile_overrides(org)
    profile_override = (overrides.get("profiles") or {}).get(profile["id"]) or {}
    if not profile_override:
        return profile

    merged = deepcopy(profile)
    for field in ("name", "description", "region"):
        if profile_override.get(field):
            merged[field] = profile_override[field]

    rule_overrides = profile_override.get("rules") or {}
    for rule in merged["rules"]:
        override = rule_overrides.get(rule["id"]) or {}
        for field in ("label", "threshold", "priority", "pass_text", "fail_text"):
            if field in override and override[field] is not None:
                rule[field] = override[field]
    return merged


def list_benchmark_profiles(org=None) -> list[dict]:
    default_profile_id = _org_default_profile_id(org)
    return [
        {
            "id": merged_profile["id"],
            "name": merged_profile["name"],
            "description": merged_profile["description"],
            "region": merged_profile["region"],
            "rules_count": len(merged_profile["rules"]),
            "is_default": merged_profile["id"] == default_profile_id,
        }
        for profile in _BUILTIN_PROFILES
        for merged_profile in [_apply_org_profile_overrides(deepcopy(profile), org)]
    ]


def get_benchmark_profile(profile_id: str | None, org=None) -> dict | None:
    wanted = profile_id or _org_default_profile_id(org)
    for profile in _BUILTIN_PROFILES:
        if profile["id"] == wanted:
            return _apply_org_profile_overrides(deepcopy(profile), org)
    return None


def evaluate_benchmark(snapshot: dict, profile_id: str | None = None, org=None) -> dict:
    profile = get_benchmark_profile(profile_id, org=org)
    if profile is None:
        raise ValueError(f"Unknown benchmark profile: {profile_id}")

    kpis = snapshot.get("kpis", {})
    quality = snapshot.get("quality") or {}
    avg_quality = quality.get("average")
    metrics = {
        "enrichment_pct": float(kpis.get("enrichment_pct") or 0),
        "quality_pct": round(float(avg_quality) * 100, 1) if avg_quality is not None else 0.0,
        "total_concepts": int(kpis.get("total_concepts") or 0),
        "avg_citations": float(kpis.get("avg_citations") or 0),
        "total_entities": int(kpis.get("total_entities") or 0),
    }

    evaluated_rules = []
    failed_rules = []
    passed_count = 0

    for rule in profile["rules"]:
        observed = metrics[rule["metric"]]
        passed = observed >= rule["threshold"]
        evaluated = {
            "id": rule["id"],
            "label": rule["label"],
            "metric": rule["metric"],
            "priority": rule["priority"],
            "threshold": rule["threshold"],
            "observed": observed,
            "passed": passed,
            "message": rule["pass_text"] if passed else rule["fail_text"],
            "evidence": f"{rule['label']}: observed {observed}, expected at least {rule['threshold']}.",
        }
        evaluated_rules.append(evaluated)
        if passed:
            passed_count += 1
        else:
            failed_rules.append(evaluated)

    total_rules = len(evaluated_rules)
    readiness_pct = round((passed_count / total_rules) * 100, 1) if total_rules else 0.0
    high_failures = sum(1 for rule in failed_rules if rule["priority"] == "high")
    if readiness_pct >= 80 and high_failures == 0:
        status = "ready"
    elif readiness_pct >= 50:
        status = "watch"
    else:
        status = "gap"

    return {
        "profile_id": profile["id"],
        "profile_name": profile["name"],
        "description": profile["description"],
        "region": profile["region"],
        "status": status,
        "readiness_pct": readiness_pct,
        "passed_rules": passed_count,
        "total_rules": total_rules,
        "rules": evaluated_rules,
        "top_gaps": failed_rules[:3],
    }
