"use client";

import { TAB_LABELS, type ContextTab } from "./contextTypes";

export function ContextTabs({
  tab,
  onChange,
}: {
  tab: ContextTab;
  onChange: (tab: ContextTab) => void;
}) {
  return (
    <div className="flex gap-1 rounded-xl border border-gray-200 bg-gray-50 p-1 dark:border-gray-700 dark:bg-gray-800">
      {(Object.keys(TAB_LABELS) as ContextTab[]).map((nextTab) => (
        <button
          key={nextTab}
          type="button"
          onClick={() => onChange(nextTab)}
          className={`flex-1 rounded-lg px-4 py-2 text-sm font-medium transition-all ${
            tab === nextTab
              ? "bg-white text-gray-900 shadow-sm dark:bg-gray-900 dark:text-white"
              : "text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          }`}
        >
          {TAB_LABELS[nextTab]}
        </button>
      ))}
    </div>
  );
}
