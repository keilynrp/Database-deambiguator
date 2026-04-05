"use client";

export interface Stats {
  domain_id: string;
  domain_name: string;
  total_records: number;
  distributions: Record<string, { label: string; value: number }[]>;
  cube_metrics: Record<string, unknown>;
}

export interface EnrichStats {
  total_entities: number;
  enriched_count: number;
  pending_count: number;
  failed_count: number;
  none_count: number;
  enrichment_coverage_pct: number;
  top_concepts: { concept: string; count: number }[];
  citations: {
    average: number;
    max: number;
    total: number;
    distribution: Record<string, number>;
  };
}
