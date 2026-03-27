"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch } from "../../lib/api";

interface OnboardingStep {
  key: string;
  label: string;
  description: string;
  href: string;
  icon: string;
  completed: boolean;
}

interface CommercialMvp {
  key: string;
  label: string;
  summary: string;
  ideal_customer: string;
  initial_dataset: string;
  time_to_first_value: string;
  primary_outcomes: string[];
}

interface JourneyStep {
  key: string;
  label: string;
  description: string;
  href: string;
}

interface RecommendedStep {
  key: string;
  label: string;
  description: string;
  href: string;
  reason: string;
}

interface OnboardingStatus {
  steps: OnboardingStep[];
  completed: number;
  total: number;
  percent: number;
  all_done: boolean;
  commercial_mvp: CommercialMvp;
  journey: JourneyStep[];
  next_recommended_step: RecommendedStep | null;
}

const DISMISSED_KEY = "ukip_onboarding_dismissed_v1";

function StepIcon({ icon, completed }: { icon: string; completed: boolean }) {
  const iconMap: Record<string, React.ReactNode> = {
    upload: (
      <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
      </svg>
    ),
    sparkles: (
      <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
      </svg>
    ),
    adjustments: (
      <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.5 6h9.75M10.5 6a1.5 1.5 0 11-3 0m3 0a1.5 1.5 0 10-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-9.75 0h9.75" />
      </svg>
    ),
    bolt: (
      <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
      </svg>
    ),
    chart: (
      <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
      </svg>
    ),
  };

  if (completed) {
    return (
      <div className="flex h-7 w-7 items-center justify-center rounded-full bg-emerald-100 text-emerald-600">
        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M4.5 12.75l6 6 9-13.5" />
        </svg>
      </div>
    );
  }

  return (
    <div className="flex h-7 w-7 items-center justify-center rounded-full bg-slate-100 text-slate-400">
      {iconMap[icon] || iconMap.chart}
    </div>
  );
}

export default function OnboardingChecklist({ token }: { token: string | null }) {
  const [status, setStatus] = useState<OnboardingStatus | null>(null);
  const [collapsed, setCollapsed] = useState(false);
  const [dismissed, setDismissed] = useState(() => {
    if (typeof window === "undefined") return false;
    return localStorage.getItem(DISMISSED_KEY) === "1";
  });

  const load = useCallback(async () => {
    if (!token) return;
    try {
      const response = await apiFetch("/onboarding/status");
      if (response.ok) {
        setStatus(await response.json());
      }
    } catch {
      // non-critical
    }
  }, [token]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void load();
    }, 0);
    return () => window.clearTimeout(timer);
  }, [load]);

  const dismiss = () => {
    localStorage.setItem(DISMISSED_KEY, "1");
    setDismissed(true);
  };

  if (dismissed || !status || status.all_done) return null;

  return (
    <div className="overflow-hidden rounded-xl border border-violet-200 bg-white shadow-sm">
      <div
        className="flex cursor-pointer select-none items-center justify-between px-5 py-4"
        onClick={() => setCollapsed((current) => !current)}
      >
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-violet-100 text-sm font-bold text-violet-600">
            {status.completed}/{status.total}
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-900">Getting started</p>
            <p className="text-xs text-slate-400">{status.percent}% complete</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="hidden h-1.5 w-24 overflow-hidden rounded-full bg-slate-100 sm:block">
            <div
              className="h-full rounded-full bg-violet-500 transition-all"
              style={{ width: `${status.percent}%` }}
            />
          </div>
          <svg
            className={`h-4 w-4 text-slate-400 transition-transform ${collapsed ? "" : "rotate-180"}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      {!collapsed && (
        <div className="border-t border-slate-100">
          <div className="grid gap-4 bg-slate-50/80 px-5 py-5 lg:grid-cols-[1.2fr_0.8fr]">
            <div className="rounded-xl border border-slate-200 bg-white px-4 py-4">
              <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-sky-600">
                Initial commercial focus
              </p>
              <h3 className="mt-2 text-base font-semibold text-slate-900">
                {status.commercial_mvp.label}
              </h3>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                {status.commercial_mvp.summary}
              </p>
              <div className="mt-4 grid gap-3 sm:grid-cols-3">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Ideal customer
                  </p>
                  <p className="mt-1 text-sm text-slate-700">{status.commercial_mvp.ideal_customer}</p>
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                    First dataset
                  </p>
                  <p className="mt-1 text-sm text-slate-700">{status.commercial_mvp.initial_dataset}</p>
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Time to first value
                  </p>
                  <p className="mt-1 text-sm text-slate-700">{status.commercial_mvp.time_to_first_value}</p>
                </div>
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                {status.commercial_mvp.primary_outcomes.map((outcome) => (
                  <span
                    key={outcome}
                    className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600"
                  >
                    {outcome}
                  </span>
                ))}
              </div>
            </div>

            <div className="space-y-3">
              {status.next_recommended_step && (
                <div className="rounded-xl border border-violet-200 bg-violet-50 px-4 py-4">
                  <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-violet-600">
                    Recommended next
                  </p>
                  <h3 className="mt-2 text-sm font-semibold text-slate-900">
                    {status.next_recommended_step.label}
                  </h3>
                  <p className="mt-1 text-sm text-slate-600">
                    {status.next_recommended_step.reason}
                  </p>
                  <Link
                    href={status.next_recommended_step.href}
                    className="mt-3 inline-flex items-center gap-2 rounded-lg bg-violet-600 px-3 py-2 text-sm font-medium text-white transition-colors hover:bg-violet-700"
                  >
                    Go now
                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.5 4.5l6 7.5-6 7.5M19.5 12h-15" />
                    </svg>
                  </Link>
                </div>
              )}

              <div className="rounded-xl border border-slate-200 bg-white px-4 py-4">
                <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-emerald-600">
                  Fast path
                </p>
                <div className="mt-3 space-y-3">
                  {status.journey.map((step, index) => (
                    <div key={step.key} className="flex items-start gap-3">
                      <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-xs font-semibold text-emerald-700">
                        {index + 1}
                      </div>
                      <div>
                        <Link href={step.href} className="text-sm font-medium text-slate-800 hover:text-emerald-700">
                          {step.label}
                        </Link>
                        <p className="mt-0.5 text-xs leading-5 text-slate-500">{step.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="divide-y divide-slate-50 border-t border-slate-100">
            {status.steps.map((step) => {
              const isRecommended = status.next_recommended_step?.key === step.key;
              return (
                <Link
                  key={step.key}
                  href={step.href}
                  className={`flex items-start gap-3 px-5 py-3.5 transition-colors hover:bg-slate-50 ${step.completed ? "opacity-60" : ""}`}
                >
                  <StepIcon icon={step.icon} completed={step.completed} />
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <p className={`text-sm font-medium ${step.completed ? "text-slate-400 line-through" : "text-slate-800"}`}>
                        {step.label}
                      </p>
                      {isRecommended && !step.completed && (
                        <span className="rounded-full bg-violet-100 px-2 py-0.5 text-[11px] font-semibold text-violet-700">
                          Recommended now
                        </span>
                      )}
                    </div>
                    <p className="mt-0.5 text-xs leading-5 text-slate-400">{step.description}</p>
                  </div>
                  {!step.completed && (
                    <svg className="mt-0.5 h-4 w-4 shrink-0 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.25 4.5l7.5 7.5-7.5 7.5" />
                    </svg>
                  )}
                </Link>
              );
            })}

            <div className="flex justify-end px-5 py-3">
              <button
                onClick={(event) => {
                  event.preventDefault();
                  dismiss();
                }}
                className="text-xs text-slate-400 hover:text-slate-600"
              >
                Dismiss checklist
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
