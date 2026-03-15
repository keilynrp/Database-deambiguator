"use client";

import Link from "next/link";
import { ReactNode } from "react";

// ── Preset icons ───────────────────────────────────────────────────────────

const ICONS: Record<string, ReactNode> = {
  entities: (
    <svg className="h-10 w-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.25} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
    </svg>
  ),
  search: (
    <svg className="h-10 w-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.25} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
    </svg>
  ),
  chart: (
    <svg className="h-10 w-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.25} d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
    </svg>
  ),
  sparkles: (
    <svg className="h-10 w-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.25} d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
    </svg>
  ),
  bell: (
    <svg className="h-10 w-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.25} d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0" />
    </svg>
  ),
  key: (
    <svg className="h-10 w-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.25} d="M15.75 5.25a3 3 0 013 3m3 0a6 6 0 01-7.029 5.912c-.563-.097-1.159.026-1.563.43L10.5 17.25H8.25v2.25H6v2.25H2.25v-2.818c0-.597.237-1.17.659-1.591l6.499-6.499c.404-.404.527-1 .43-1.563A6 6 0 1121.75 8.25z" />
    </svg>
  ),
  users: (
    <svg className="h-10 w-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.25} d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
    </svg>
  ),
  bolt: (
    <svg className="h-10 w-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.25} d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
    </svg>
  ),
  document: (
    <svg className="h-10 w-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.25} d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
    </svg>
  ),
};

// ── CTA type ───────────────────────────────────────────────────────────────

type CtaItem =
  | { label: string; href: string; variant?: "primary" | "secondary" }
  | { label: string; onClick: () => void; variant?: "primary" | "secondary" };

// ── Color schemes for the icon container ──────────────────────────────────

type ColorScheme = "blue" | "violet" | "emerald" | "amber" | "slate" | "rose";

const COLOR_CLASSES: Record<ColorScheme, { container: string; icon: string }> = {
  blue:    { container: "bg-blue-50 dark:bg-blue-900/20",    icon: "text-blue-500 dark:text-blue-400" },
  violet:  { container: "bg-violet-50 dark:bg-violet-900/20", icon: "text-violet-500 dark:text-violet-400" },
  emerald: { container: "bg-emerald-50 dark:bg-emerald-900/20", icon: "text-emerald-500 dark:text-emerald-400" },
  amber:   { container: "bg-amber-50 dark:bg-amber-900/20",  icon: "text-amber-500 dark:text-amber-400" },
  slate:   { container: "bg-slate-100 dark:bg-slate-800",    icon: "text-slate-400 dark:text-slate-500" },
  rose:    { container: "bg-rose-50 dark:bg-rose-900/20",    icon: "text-rose-500 dark:text-rose-400" },
};

// ── Main component ─────────────────────────────────────────────────────────

interface EmptyStateProps {
  icon?: keyof typeof ICONS | ReactNode;
  title: string;
  description?: string;
  cta?: CtaItem | CtaItem[];
  color?: ColorScheme;
  /** Use "page" for full-page empty states, "card" for inline in a section */
  size?: "page" | "card" | "compact";
  className?: string;
}

export default function EmptyState({
  icon = "entities",
  title,
  description,
  cta,
  color = "slate",
  size = "card",
  className = "",
}: EmptyStateProps) {
  const colors = COLOR_CLASSES[color];
  const iconNode = typeof icon === "string" ? ICONS[icon] ?? ICONS.entities : icon;
  const ctas = cta ? (Array.isArray(cta) ? cta : [cta]) : [];

  const paddingClass =
    size === "page"    ? "py-24" :
    size === "compact" ? "py-8"  :
                         "py-14";

  return (
    <div className={`flex flex-col items-center justify-center text-center ${paddingClass} ${className}`}>
      {/* Icon bubble */}
      <div className={`flex h-20 w-20 items-center justify-center rounded-full ${colors.container} ${colors.icon} mb-5`}>
        {iconNode}
      </div>

      {/* Text */}
      <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100">{title}</h3>
      {description && (
        <p className="mt-2 max-w-sm text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
          {description}
        </p>
      )}

      {/* CTAs */}
      {ctas.length > 0 && (
        <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
          {ctas.map((c, i) => {
            const isPrimary = c.variant !== "secondary";
            const btnClass = isPrimary
              ? "inline-flex items-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
              : "inline-flex items-center rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700";

            if ("href" in c) {
              return (
                <Link key={i} href={c.href} className={btnClass}>
                  {c.label}
                </Link>
              );
            }
            return (
              <button key={i} onClick={c.onClick} className={btnClass}>
                {c.label}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
