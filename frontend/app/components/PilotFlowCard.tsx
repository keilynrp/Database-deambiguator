"use client";

import Link from "next/link";
import { useMemo } from "react";
import { useLanguage } from "../contexts/LanguageContext";

export type PilotFlowStepId = "import" | "enrich" | "review" | "brief";

type Tone = "blue" | "sky" | "amber" | "emerald" | "violet";

interface PilotFlowCardProps {
  currentStep: PilotFlowStepId;
  title: string;
  body: string;
  primaryCta?: {
    href: string;
    label: string;
  };
  secondaryCta?: {
    href: string;
    label: string;
  };
  tone?: Tone;
}

const STEP_ORDER: PilotFlowStepId[] = ["import", "enrich", "review", "brief"];

const TONE_STYLES: Record<Tone, string> = {
  blue: "border-blue-200 bg-blue-50 dark:border-blue-500/20 dark:bg-blue-500/5",
  sky: "border-sky-200 bg-sky-50 dark:border-sky-500/20 dark:bg-sky-500/5",
  amber: "border-amber-200 bg-amber-50 dark:border-amber-500/20 dark:bg-amber-500/5",
  emerald: "border-emerald-200 bg-emerald-50 dark:border-emerald-500/20 dark:bg-emerald-500/5",
  violet: "border-violet-200 bg-violet-50 dark:border-violet-500/20 dark:bg-violet-500/5",
};

const TONE_TEXT: Record<Tone, { eyebrow: string; title: string; body: string; primary: string; secondary: string; chip: string }> = {
  blue: {
    eyebrow: "text-blue-700 dark:text-blue-300",
    title: "text-blue-950 dark:text-blue-100",
    body: "text-blue-800 dark:text-blue-200",
    primary: "bg-blue-600 hover:bg-blue-700 text-white",
    secondary: "border-blue-300 bg-white text-blue-700 hover:bg-blue-100 dark:border-blue-700 dark:bg-gray-900 dark:text-blue-300 dark:hover:bg-blue-950/30",
    chip: "border-blue-200 bg-white/80 text-blue-900 dark:border-blue-500/20 dark:bg-gray-900/70 dark:text-blue-100",
  },
  sky: {
    eyebrow: "text-sky-700 dark:text-sky-300",
    title: "text-sky-950 dark:text-sky-100",
    body: "text-sky-800 dark:text-sky-200",
    primary: "bg-sky-600 hover:bg-sky-700 text-white",
    secondary: "border-sky-300 bg-white text-sky-700 hover:bg-sky-100 dark:border-sky-700 dark:bg-gray-900 dark:text-sky-300 dark:hover:bg-sky-950/30",
    chip: "border-sky-200 bg-white/80 text-sky-900 dark:border-sky-500/20 dark:bg-gray-900/70 dark:text-sky-100",
  },
  amber: {
    eyebrow: "text-amber-700 dark:text-amber-300",
    title: "text-amber-950 dark:text-amber-100",
    body: "text-amber-800 dark:text-amber-200",
    primary: "bg-amber-600 hover:bg-amber-700 text-white",
    secondary: "border-amber-300 bg-white text-amber-700 hover:bg-amber-100 dark:border-amber-700 dark:bg-gray-900 dark:text-amber-300 dark:hover:bg-amber-950/30",
    chip: "border-amber-200 bg-white/80 text-amber-900 dark:border-amber-500/20 dark:bg-gray-900/70 dark:text-amber-100",
  },
  emerald: {
    eyebrow: "text-emerald-700 dark:text-emerald-300",
    title: "text-emerald-950 dark:text-emerald-100",
    body: "text-emerald-800 dark:text-emerald-200",
    primary: "bg-emerald-600 hover:bg-emerald-700 text-white",
    secondary: "border-emerald-300 bg-white text-emerald-700 hover:bg-emerald-100 dark:border-emerald-700 dark:bg-gray-900 dark:text-emerald-300 dark:hover:bg-emerald-950/30",
    chip: "border-emerald-200 bg-white/80 text-emerald-900 dark:border-emerald-500/20 dark:bg-gray-900/70 dark:text-emerald-100",
  },
  violet: {
    eyebrow: "text-violet-700 dark:text-violet-300",
    title: "text-violet-950 dark:text-violet-100",
    body: "text-violet-800 dark:text-violet-200",
    primary: "bg-violet-600 hover:bg-violet-700 text-white",
    secondary: "border-violet-300 bg-white text-violet-700 hover:bg-violet-100 dark:border-violet-700 dark:bg-gray-900 dark:text-violet-300 dark:hover:bg-violet-950/30",
    chip: "border-violet-200 bg-white/80 text-violet-900 dark:border-violet-500/20 dark:bg-gray-900/70 dark:text-violet-100",
  },
};

export default function PilotFlowCard({
  currentStep,
  title,
  body,
  primaryCta,
  secondaryCta,
  tone = "sky",
}: PilotFlowCardProps) {
  const { t } = useLanguage();
  const currentIndex = STEP_ORDER.indexOf(currentStep);
  const toneText = TONE_TEXT[tone];

  const steps = useMemo(() => (
    STEP_ORDER.map((stepId, index) => {
      const status =
        index < currentIndex ? "done" :
        index === currentIndex ? "current" :
        "upcoming";

      return {
        id: stepId,
        status,
        title: t(`page.home.guided.step.${stepId}.title`),
        statusLabel: t(`page.home.guided.status.${status}`),
        numberLabel: t("page.home.guided.step_number", { count: index + 1 }),
      };
    })
  ), [currentIndex, t]);

  return (
    <div className={`rounded-2xl border p-5 shadow-sm ${TONE_STYLES[tone]}`}>
      <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
        <div className="max-w-3xl">
          <p className={`text-xs font-semibold uppercase tracking-[0.18em] ${toneText.eyebrow}`}>
            {t("component.pilot_flow.eyebrow")}
          </p>
          <h2 className={`mt-2 text-lg font-semibold ${toneText.title}`}>
            {title}
          </h2>
          <p className={`mt-1 text-sm ${toneText.body}`}>
            {body}
          </p>
        </div>

        {(primaryCta || secondaryCta) && (
          <div className="flex flex-wrap gap-2 xl:justify-end">
            {primaryCta && (
              <Link
                href={primaryCta.href}
                className={`inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors ${toneText.primary}`}
              >
                {primaryCta.label}
              </Link>
            )}
            {secondaryCta && (
              <Link
                href={secondaryCta.href}
                className={`inline-flex items-center gap-2 rounded-lg border px-4 py-2 text-sm font-medium transition-colors ${toneText.secondary}`}
              >
                {secondaryCta.label}
              </Link>
            )}
          </div>
        )}
      </div>

      <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
        {steps.map((step) => (
          <div
            key={step.id}
            className={`rounded-xl border px-4 py-3 shadow-sm ${toneText.chip} ${step.status === "current" ? "ring-2 ring-current/10" : ""}`}
          >
            <div className="flex items-center justify-between gap-3">
              <span className="text-[11px] font-semibold uppercase tracking-[0.14em] opacity-70">
                {step.numberLabel}
              </span>
              <span className="text-[11px] font-semibold uppercase tracking-[0.14em] opacity-80">
                {step.statusLabel}
              </span>
            </div>
            <p className="mt-2 text-sm font-semibold">
              {step.title}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
