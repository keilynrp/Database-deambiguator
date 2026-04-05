"use client";

import { PageHeader } from "../components/ui";
import { useDomain } from "../contexts/DomainContext";

import { ContextTabs } from "./ContextTabs";
import { DiffTab } from "./DiffTab";
import { SessionsTab } from "./SessionsTab";
import { SnapshotTab } from "./SnapshotTab";
import { ToolsTab } from "./ToolsTab";
import { useContextPageController } from "./useContextPageController";

export default function ContextPage() {
  const { activeDomainId } = useDomain();
  const controller = useContextPageController(activeDomainId);

  return (
    <div className="space-y-6">
      <PageHeader
        breadcrumbs={[{ label: "Home", href: "/" }, { label: "Context Engineering" }]}
        title="Context Engineering"
        description="Domain context snapshots, memory sessions, diff analysis, and tool invocations"
      />

      <ContextTabs tab={controller.tab} onChange={controller.setTab} />

      {controller.tab === "snapshot" && (
        <SnapshotTab
          snapshot={controller.snapshot}
          loading={controller.loadingSnap}
          error={controller.snapError}
          saveLabel={controller.saveLabel}
          saving={controller.saving}
          onSaveLabelChange={controller.setSaveLabel}
          onSave={controller.saveSnapshot}
          onRefresh={controller.fetchSnapshot}
        />
      )}

      {controller.tab === "sessions" && (
        <SessionsTab
          loadingSessions={controller.loadingSessions}
          sessions={controller.sessions}
          sortedSessions={controller.sortedSessions}
          selectedSession={controller.selectedSession}
          loadingDetail={controller.loadingDetail}
          editingNotes={controller.editingNotes}
          savingNotes={controller.savingNotes}
          sessionInsights={controller.sessionInsights}
          loadingInsights={controller.loadingInsights}
          insightsError={controller.insightsError}
          onFetchDetail={controller.fetchSessionDetail}
          onFetchInsights={controller.fetchSessionInsights}
          onDeleteSession={controller.deleteSession}
          onPatchSession={controller.patchSession}
          onEditingNotesChange={(id, value) =>
            controller.setEditingNotes((current) => ({ ...current, [id]: value }))
          }
        />
      )}

      {controller.tab === "diff" && (
        <DiffTab
          sortedSessions={controller.sortedSessions}
          diffA={controller.diffA}
          diffB={controller.diffB}
          diffResult={controller.diffResult}
          diffLoading={controller.diffLoading}
          diffError={controller.diffError}
          diffInsights={controller.diffInsights}
          loadingDiffInsights={controller.loadingDiffInsights}
          insightsError={controller.insightsError}
          onDiffAChange={controller.setDiffA}
          onDiffBChange={controller.setDiffB}
          onRunDiff={controller.runDiff}
          onFetchDiffInsights={controller.fetchDiffInsights}
        />
      )}

      {controller.tab === "tools" && (
        <ToolsTab
          tools={controller.tools}
          loadingTools={controller.loadingTools}
          selectedTool={controller.selectedTool}
          toolParams={controller.toolParams}
          toolResult={controller.toolResult}
          invoking={controller.invoking}
          toolError={controller.toolError}
          onSelectTool={controller.onSelectTool}
          onToolParamChange={(key, value) =>
            controller.setToolParams((current) => ({ ...current, [key]: value }))
          }
          onInvokeTool={controller.invokeTool}
        />
      )}
    </div>
  );
}
