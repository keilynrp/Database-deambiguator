"use client";

import type { ReactNode } from "react";

type MetaItem = {
  label: string;
  value: ReactNode;
  minWidthClassName?: string;
};

interface RecordResultCardProps {
  title: ReactNode;
  idTag?: ReactNode;
  secondaryLine?: ReactNode;
  statusRow?: ReactNode;
  primaryMeta?: MetaItem[];
  secondaryMeta?: MetaItem[];
  actions?: ReactNode;
  tileLabel: ReactNode;
  leadingSlot?: ReactNode;
  onClick?: () => void;
}

function MetaRow({ items }: { items: MetaItem[] }) {
  if (items.length === 0) return null;

  return (
    <div className="mt-4 flex flex-wrap gap-x-6 gap-y-3 border-t border-gray-100 pt-4 dark:border-gray-800">
      {items.map((item) => (
        <div key={item.label} className={`${item.minWidthClassName ?? "min-w-[10rem]"} flex-1`}>
          <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-500 dark:text-slate-400">
            {item.label}
          </p>
          <div className="mt-1 text-sm text-slate-700 dark:text-slate-300">{item.value}</div>
        </div>
      ))}
    </div>
  );
}

export default function RecordResultCard({
  title,
  idTag,
  secondaryLine,
  statusRow,
  primaryMeta = [],
  secondaryMeta = [],
  actions,
  tileLabel,
  leadingSlot,
  onClick,
}: RecordResultCardProps) {
  return (
    <article
      className={`${onClick ? "cursor-pointer hover:bg-blue-50/30 dark:hover:bg-blue-950/10" : ""} p-4 transition`}
      onClick={onClick}
    >
      <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm transition hover:border-blue-200 hover:shadow-md dark:border-gray-800 dark:bg-gray-950 dark:hover:border-blue-900/40">
        <div className="flex flex-col gap-4 lg:flex-row">
          <div className="flex min-w-0 flex-1 gap-4">
            {leadingSlot}

            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-100 text-center text-xs font-semibold uppercase tracking-[0.12em] text-slate-700 dark:bg-slate-900 dark:text-slate-200">
              {tileLabel}
            </div>

            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="text-lg font-semibold text-slate-900 dark:text-slate-100">{title}</p>
                    {idTag}
                  </div>
                  {secondaryLine ? (
                    <div className="mt-1 flex flex-wrap items-center gap-x-2 gap-y-1 text-sm text-slate-600 dark:text-slate-400">
                      {secondaryLine}
                    </div>
                  ) : null}
                </div>
              </div>

              {statusRow ? <div className="mt-3 flex flex-wrap gap-2">{statusRow}</div> : null}
              <MetaRow items={primaryMeta} />
              <MetaRow items={secondaryMeta} />
            </div>
          </div>

          {actions ? (
            <div className="flex shrink-0 flex-row flex-wrap items-start justify-end gap-2 lg:w-44 lg:flex-col">
              {actions}
            </div>
          ) : null}
        </div>
      </div>
    </article>
  );
}
