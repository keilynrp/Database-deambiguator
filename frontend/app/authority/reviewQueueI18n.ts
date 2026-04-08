"use client";

type Translate = (key: string) => string;

const ROUTE_KEYS: Record<string, string> = {
    fast_path: "page.authority.route_fast_path",
    hybrid_path: "page.authority.route_hybrid_path",
    llm_path: "page.authority.route_llm_path",
    manual_review: "page.authority.route_manual_review",
    legacy: "page.authority.route_legacy",
};

const NIL_REASON_KEYS: Record<string, string> = {
    no_candidates: "page.authority.nil_reason_no_candidates",
    insufficient_coverage: "page.authority.nil_reason_insufficient_coverage",
    unresolved_ambiguity: "page.authority.nil_reason_unresolved_ambiguity",
    conflicting_evidence: "page.authority.nil_reason_conflicting_evidence",
};

const ENTITY_TYPE_KEYS: Record<string, string> = {
    general: "page.authority.entity_type_general",
    person: "page.authority.entity_type_person",
    organization: "page.authority.entity_type_organization",
    concept: "page.authority.entity_type_concept",
    institution: "page.authority.entity_type_institution",
};

const RESOLUTION_STATUS_KEYS: Record<string, string> = {
    exact_match: "page.authority.resolution_exact_match",
    probable_match: "page.authority.resolution_probable_match",
    ambiguous: "page.authority.resolution_ambiguous",
    unresolved: "page.authority.resolution_unresolved",
    partial_ancestor_match: "page.authority.resolution_partial_ancestor_match",
    internal_nil: "page.authority.resolution_internal_nil",
};

function humanizeKey(value: string) {
    return value.replaceAll("_", " ");
}

export function getRouteLabel(route: string | null | undefined, t: Translate) {
    if (!route) {
        return t("page.authority.route_legacy");
    }
    return ROUTE_KEYS[route] ? t(ROUTE_KEYS[route]) : humanizeKey(route);
}

export function getNilReasonLabel(reason: string | null | undefined, t: Translate) {
    if (!reason) {
        return null;
    }
    return NIL_REASON_KEYS[reason] ? t(NIL_REASON_KEYS[reason]) : humanizeKey(reason);
}

export function getEntityTypeLabel(entityType: string, t: Translate) {
    return ENTITY_TYPE_KEYS[entityType] ? t(ENTITY_TYPE_KEYS[entityType]) : humanizeKey(entityType);
}

export function getResolutionStatusLabel(status: string | null | undefined, t: Translate) {
    if (!status) {
        return "--";
    }
    return RESOLUTION_STATUS_KEYS[status] ? t(RESOLUTION_STATUS_KEYS[status]) : humanizeKey(status);
}

export function getStatusLabel(status: string, t: Translate) {
    if (status === "pending") {
        return t("page.authority.status_pending");
    }
    if (status === "confirmed") {
        return t("page.authority.status_confirmed");
    }
    if (status === "rejected") {
        return t("page.authority.status_rejected");
    }
    return humanizeKey(status);
}
