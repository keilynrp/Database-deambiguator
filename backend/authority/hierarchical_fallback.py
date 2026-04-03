from __future__ import annotations

import re

from backend.authority.base import AuthorityCandidate
from backend.authority.normalize import normalize_name


_SUPPORTED_ENTITY_TYPES = {"concept", "institution", "organization"}
_SUPPORTED_SOURCES = {"wikidata", "dbpedia", "openalex"}
_STOPWORDS = {
    "a",
    "an",
    "and",
    "de",
    "del",
    "for",
    "in",
    "la",
    "las",
    "los",
    "of",
    "the",
    "y",
}
_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(value: str) -> list[str]:
    normalized = normalize_name(value)
    return [token for token in _TOKEN_RE.findall(normalized) if token and token not in _STOPWORDS]


def apply_hierarchical_fallback(
    value: str,
    entity_type: str,
    candidates: list[AuthorityCandidate],
) -> list[AuthorityCandidate]:
    """
    Mark partial ancestor matches for hierarchy-friendly entity types only.

    The heuristic is intentionally conservative:
    - never applies to person entities
    - only applies to sources with relatively stable graph semantics
    - only applies when the candidate label is a strict lexical subset of the
      original query, suggesting the KB returned a broader concept
    """
    if entity_type not in _SUPPORTED_ENTITY_TYPES or not candidates:
        return candidates

    query_tokens = _tokenize(value)
    if len(query_tokens) < 2:
        return candidates

    query_token_set = set(query_tokens)
    for candidate in candidates:
        if candidate.authority_source not in _SUPPORTED_SOURCES:
            continue
        if candidate.resolution_status == "exact_match":
            continue

        candidate_tokens = _tokenize(candidate.canonical_label)
        if not candidate_tokens:
            continue
        candidate_token_set = set(candidate_tokens)
        if candidate_token_set == query_token_set:
            continue
        if not candidate_token_set.issubset(query_token_set):
            continue

        hierarchy_distance = len(query_token_set - candidate_token_set)
        if hierarchy_distance <= 0 or hierarchy_distance > 3:
            continue
        if len(candidate_token_set) < 1:
            continue
        if candidate.confidence < 0.35:
            continue

        candidate.resolution_status = "partial_ancestor_match"
        candidate.hierarchy_distance = hierarchy_distance
        candidate.evidence = list(dict.fromkeys([
            *candidate.evidence,
            f"hierarchical_fallback:{candidate.authority_source}",
            f"hierarchy_distance:{hierarchy_distance}",
        ]))

    return candidates
