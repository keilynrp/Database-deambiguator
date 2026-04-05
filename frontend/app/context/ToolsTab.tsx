"use client";

import type { Tool } from "./contextTypes";

export function ToolsTab({
  tools,
  loadingTools,
  selectedTool,
  toolParams,
  toolResult,
  invoking,
  toolError,
  onSelectTool,
  onToolParamChange,
  onInvokeTool,
}: {
  tools: Tool[];
  loadingTools: boolean;
  selectedTool: string;
  toolParams: Record<string, string>;
  toolResult: unknown;
  invoking: boolean;
  toolError: string | null;
  onSelectTool: (name: string) => void;
  onToolParamChange: (key: string, value: string) => void;
  onInvokeTool: () => void;
}) {
  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-[260px_1fr]">
      <div className="space-y-2">
        {loadingTools && <div className="h-48 animate-pulse rounded-xl bg-gray-100 dark:bg-gray-800" />}
        {tools.map((tool) => (
          <button
            key={tool.name}
            type="button"
            onClick={() => onSelectTool(tool.name)}
            className={`w-full rounded-xl border p-4 text-left transition-all ${
              selectedTool === tool.name
                ? "border-blue-300 bg-blue-50 dark:border-blue-500/40 dark:bg-blue-500/10"
                : "border-gray-200 bg-white hover:border-gray-300 dark:border-gray-700 dark:bg-gray-900"
            }`}
          >
            <p className="font-mono text-sm font-medium text-gray-900 dark:text-white">{tool.name}</p>
            <p className="mt-1 line-clamp-2 text-xs text-gray-500 dark:text-gray-400">{tool.description}</p>
          </button>
        ))}
      </div>

      {selectedTool &&
        (() => {
          const tool = tools.find((item) => item.name === selectedTool);
          if (!tool) {
            return null;
          }
          return (
            <div className="space-y-4 rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-900">
              <h3 className="font-mono text-sm font-semibold text-gray-900 dark:text-white">{tool.name}</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">{tool.description}</p>
              <div className="space-y-3">
                {Object.entries(tool.parameters).map(([key, value]) => (
                  <div key={key}>
                    <label className="mb-1 block text-xs font-medium text-gray-600 dark:text-gray-400">
                      {key} <span className="text-gray-400">({value.type})</span>
                    </label>
                    <input
                      type="text"
                      value={toolParams[key] ?? String(value.default ?? "")}
                      onChange={(e) => onToolParamChange(key, e.target.value)}
                      className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 font-mono text-sm text-gray-900 focus:border-blue-500 focus:outline-none dark:border-gray-600 dark:bg-gray-800 dark:text-white"
                    />
                  </div>
                ))}
              </div>
              <button
                type="button"
                onClick={onInvokeTool}
                disabled={invoking}
                className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
              >
                {invoking ? "Running..." : "Run Tool"}
              </button>
              {toolError && (
                <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-800 dark:bg-red-900/20 dark:text-red-400">
                  {toolError}
                </div>
              )}
              {toolResult !== null && (
                <div className="rounded-xl border border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-800">
                  <p className="border-b border-gray-200 px-4 py-2 text-xs font-medium text-gray-500 dark:border-gray-700 dark:text-gray-400">
                    Result
                  </p>
                  <pre className="max-h-64 overflow-auto p-4 text-xs text-gray-800 dark:text-gray-200">
                    {JSON.stringify(toolResult, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          );
        })()}
    </div>
  );
}
