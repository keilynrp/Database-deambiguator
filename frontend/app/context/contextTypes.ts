"use client";

export type ContextTab = "snapshot" | "sessions" | "diff" | "tools";

export interface EntityStats {
  total: number;
  enriched: number;
  pct_enriched: number;
}

export interface GapSummary {
  critical: number;
  warning: number;
  ok: number;
}

export interface TopTopic {
  concept: string;
  count: number;
}

export interface Snapshot {
  domain_id: string;
  generated_at: string;
  schema: { name?: string; primary_entity?: string; attributes?: unknown[] };
  entity_stats: EntityStats;
  gaps: GapSummary;
  top_topics: TopTopic[];
}

export interface Session {
  id: number;
  domain_id: string;
  label: string;
  notes: string | null;
  pinned: boolean;
  context_snapshot: string;
  created_at: string;
}

export interface SessionDetail {
  id: number;
  domain_id: string;
  label: string;
  notes: string | null;
  pinned: boolean;
  context_snapshot: Snapshot;
  created_at: string;
}

export interface DeltaValue {
  before: number;
  after: number;
  change: number;
}

export interface DiffResult {
  snapshot_a_domain: string;
  snapshot_b_domain: string;
  snapshot_a_generated: string;
  snapshot_b_generated: string;
  entity_stats: Record<string, DeltaValue>;
  gaps: Record<string, DeltaValue>;
  top_topics: Array<{ concept: string; before: number; after: number; change: number }>;
}

export interface Tool {
  name: string;
  description: string;
  parameters: Record<string, { type: string; default?: unknown }>;
}

export const TAB_LABELS: Record<ContextTab, string> = {
  snapshot: "Live Snapshot",
  sessions: "Saved Sessions",
  diff: "Session Diff",
  tools: "Tool Explorer",
};
