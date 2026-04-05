"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { apiFetch } from "@/lib/api";

import type { DiffResult, Session, SessionDetail, Snapshot, Tool } from "./contextTypes";

export function useContextPageController(activeDomainId: string | null) {
  const [tab, setTab] = useState<"snapshot" | "sessions" | "diff" | "tools">("snapshot");

  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [loadingSnap, setLoadingSnap] = useState(false);
  const [saveLabel, setSaveLabel] = useState("");
  const [saving, setSaving] = useState(false);
  const [snapError, setSnapError] = useState<string | null>(null);

  const [sessions, setSessions] = useState<Session[]>([]);
  const [loadingSessions, setLoadingSessions] = useState(false);
  const [selectedSession, setSelectedSession] = useState<SessionDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [editingNotes, setEditingNotes] = useState<Record<number, string>>({});
  const [savingNotes, setSavingNotes] = useState<Record<number, boolean>>({});

  const [sessionInsights, setSessionInsights] = useState<Record<number, string>>({});
  const [loadingInsights, setLoadingInsights] = useState<Record<number, boolean>>({});
  const [diffInsights, setDiffInsights] = useState<string | null>(null);
  const [loadingDiffInsights, setLoadingDiffInsights] = useState(false);
  const [insightsError, setInsightsError] = useState<string | null>(null);

  const [diffA, setDiffA] = useState<number | "">("");
  const [diffB, setDiffB] = useState<number | "">("");
  const [diffResult, setDiffResult] = useState<DiffResult | null>(null);
  const [diffLoading, setDiffLoading] = useState(false);
  const [diffError, setDiffError] = useState<string | null>(null);

  const [tools, setTools] = useState<Tool[]>([]);
  const [loadingTools, setLoadingTools] = useState(false);
  const [selectedTool, setSelectedTool] = useState("");
  const [toolParams, setToolParams] = useState<Record<string, string>>({});
  const [toolResult, setToolResult] = useState<unknown>(null);
  const [invoking, setInvoking] = useState(false);
  const [toolError, setToolError] = useState<string | null>(null);

  const fetchSnapshot = useCallback(async () => {
    if (!activeDomainId) {
      return;
    }
    setLoadingSnap(true);
    setSnapError(null);
    try {
      const response = await apiFetch(`/context/snapshot/${activeDomainId}`);
      if (!response.ok) {
        setSnapError(await response.text());
        return;
      }
      setSnapshot(await response.json());
    } catch {
      setSnapError("Network error");
    } finally {
      setLoadingSnap(false);
    }
  }, [activeDomainId]);

  useEffect(() => {
    if (tab === "snapshot") {
      void fetchSnapshot();
    }
  }, [tab, fetchSnapshot]);

  const fetchSessions = useCallback(async () => {
    setLoadingSessions(true);
    try {
      const response = await apiFetch("/context/sessions");
      if (response.ok) {
        setSessions(await response.json());
      }
    } finally {
      setLoadingSessions(false);
    }
  }, []);

  useEffect(() => {
    if (tab === "sessions" || tab === "diff") {
      void fetchSessions();
    }
  }, [tab, fetchSessions]);

  const fetchTools = useCallback(async () => {
    if (tools.length) {
      return;
    }
    setLoadingTools(true);
    try {
      const response = await apiFetch("/context/tools");
      if (response.ok) {
        const data: Tool[] = await response.json();
        setTools(data);
        if (data.length > 0) {
          const defaults: Record<string, string> = {};
          Object.entries(data[0].parameters).forEach(([key, value]) => {
            defaults[key] = String(value.default ?? "");
          });
          setSelectedTool(data[0].name);
          setToolParams({ ...defaults, domain_id: activeDomainId || "default" });
        }
      }
    } finally {
      setLoadingTools(false);
    }
  }, [tools.length, activeDomainId]);

  useEffect(() => {
    if (tab === "tools") {
      void fetchTools();
    }
  }, [tab, fetchTools]);

  const saveSnapshot = async () => {
    if (!activeDomainId) {
      return;
    }
    setSaving(true);
    try {
      await apiFetch("/context/sessions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ domain_id: activeDomainId, label: saveLabel || "" }),
      });
      setSaveLabel("");
      if (tab === "sessions") {
        await fetchSessions();
      }
    } finally {
      setSaving(false);
    }
  };

  const fetchSessionDetail = async (id: number) => {
    setLoadingDetail(true);
    setSelectedSession(null);
    try {
      const response = await apiFetch(`/context/sessions/${id}`);
      if (response.ok) {
        setSelectedSession(await response.json());
      }
    } finally {
      setLoadingDetail(false);
    }
  };

  const deleteSession = async (id: number) => {
    await apiFetch(`/context/sessions/${id}`, { method: "DELETE" });
    setSessions((current) => current.filter((session) => session.id !== id));
    if (selectedSession?.id === id) {
      setSelectedSession(null);
    }
  };

  const patchSession = async (id: number, patch: { label?: string; notes?: string; pinned?: boolean }) => {
    setSavingNotes((current) => ({ ...current, [id]: true }));
    try {
      await apiFetch(`/context/sessions/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(patch),
      });
      setSessions((current) => current.map((session) => (session.id === id ? { ...session, ...patch } : session)));
      setSelectedSession((current) => (current && current.id === id ? { ...current, ...patch } : current));
    } finally {
      setSavingNotes((current) => ({ ...current, [id]: false }));
    }
  };

  const sortedSessions = useMemo(
    () =>
      [...sessions].sort(
        (a, b) =>
          Number(b.pinned) - Number(a.pinned) ||
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
      ),
    [sessions],
  );

  const fetchSessionInsights = async (id: number) => {
    setLoadingInsights((current) => ({ ...current, [id]: true }));
    setInsightsError(null);
    try {
      const response = await apiFetch(`/context/sessions/${id}/insights`, { method: "POST" });
      const data = await response.json();
      if (!response.ok) {
        setInsightsError(data.detail ?? "Failed to get insights");
        return;
      }
      setSessionInsights((current) => ({ ...current, [id]: data.analysis }));
    } catch {
      setInsightsError("Network error");
    } finally {
      setLoadingInsights((current) => ({ ...current, [id]: false }));
    }
  };

  const fetchDiffInsights = async () => {
    if (!diffA || !diffB) {
      return;
    }
    setLoadingDiffInsights(true);
    setDiffInsights(null);
    setInsightsError(null);
    try {
      const response = await apiFetch(`/context/sessions/diff/insights?a=${diffA}&b=${diffB}`, {
        method: "POST",
      });
      const data = await response.json();
      if (!response.ok) {
        setInsightsError(data.detail ?? "Failed to get insights");
        return;
      }
      setDiffInsights(data.analysis);
    } catch {
      setInsightsError("Network error");
    } finally {
      setLoadingDiffInsights(false);
    }
  };

  const runDiff = async () => {
    if (!diffA || !diffB) {
      return;
    }
    setDiffLoading(true);
    setDiffError(null);
    setDiffResult(null);
    try {
      const response = await apiFetch(`/context/sessions/diff?a=${diffA}&b=${diffB}`);
      if (!response.ok) {
        setDiffError(await response.text());
        return;
      }
      setDiffResult(await response.json());
    } catch {
      setDiffError("Network error");
    } finally {
      setDiffLoading(false);
    }
  };

  const onSelectTool = (name: string) => {
    setSelectedTool(name);
    setToolResult(null);
    setToolError(null);
    const tool = tools.find((item) => item.name === name);
    if (tool) {
      const defaults: Record<string, string> = {};
      Object.entries(tool.parameters).forEach(([key, value]) => {
        defaults[key] = String(value.default ?? "");
      });
      setToolParams({ ...defaults, domain_id: activeDomainId || "default" });
    }
  };

  const invokeTool = async () => {
    setInvoking(true);
    setToolResult(null);
    setToolError(null);
    try {
      const params: Record<string, unknown> = {};
      Object.entries(toolParams).forEach(([key, value]) => {
        params[key] = Number.isNaN(Number(value)) ? value : Number(value);
      });
      const response = await apiFetch("/context/invoke", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tool: selectedTool, params }),
      });
      const data = await response.json();
      if (!response.ok) {
        setToolError(data.detail ?? JSON.stringify(data));
        return;
      }
      setToolResult(data.result);
    } catch {
      setToolError("Network error");
    } finally {
      setInvoking(false);
    }
  };

  return {
    tab,
    setTab,
    snapshot,
    loadingSnap,
    saveLabel,
    setSaveLabel,
    saving,
    snapError,
    fetchSnapshot,
    saveSnapshot,
    sessions,
    loadingSessions,
    selectedSession,
    loadingDetail,
    editingNotes,
    setEditingNotes,
    savingNotes,
    sessionInsights,
    loadingInsights,
    diffInsights,
    loadingDiffInsights,
    insightsError,
    fetchSessionDetail,
    deleteSession,
    patchSession,
    sortedSessions,
    fetchSessionInsights,
    diffA,
    setDiffA,
    diffB,
    setDiffB,
    diffResult,
    diffLoading,
    diffError,
    runDiff,
    fetchDiffInsights,
    tools,
    loadingTools,
    selectedTool,
    toolParams,
    setToolParams,
    toolResult,
    invoking,
    toolError,
    onSelectTool,
    invokeTool,
  };
}
