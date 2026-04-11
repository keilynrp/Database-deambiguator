"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useLanguage } from "../contexts/LanguageContext";

const STORAGE_KEY = "ukip_welcomed_v1";
const PERSONA_KEY = "ukip_persona_v1";

type PersonaId = "research" | "library" | "leadership";

type Slide = {
  emoji: string;
  title: string;
  body: string;
  cta: { label: string; href: string };
  color: string;
};

type PersonaOption = {
  id: PersonaId;
  label: string;
  summary: string;
};

function withFallback(
  t: (key: string, params?: Record<string, string | number>) => string,
  key: string,
  fallback: string,
  params?: Record<string, string | number>,
) {
  const value = t(key, params);
  return value === key ? fallback : value;
}

export default function WelcomeModal() {
  const { t } = useLanguage();
  const [visible, setVisible] = useState(false);
  const [slide, setSlide] = useState(0);
  const [persona, setPersona] = useState<PersonaId>(() => {
    if (typeof window === "undefined") return "research";
    const storedPersona = localStorage.getItem(PERSONA_KEY) as PersonaId | null;
    return storedPersona ?? "research";
  });

  useEffect(() => {
    if (typeof window === "undefined") return;
    const seen = localStorage.getItem(STORAGE_KEY);
    if (seen) return;
    const frame = window.requestAnimationFrame(() => setVisible(true));
    return () => window.cancelAnimationFrame(frame);
  }, []);

  const personaOptions = useMemo<PersonaOption[]>(() => [
    {
      id: "research",
      label: withFallback(t, "welcome.persona.research.label", "Research office"),
      summary: withFallback(t, "welcome.persona.research.summary", "Track portfolio quality, coverage, and institutional readiness."),
    },
    {
      id: "library",
      label: withFallback(t, "welcome.persona.library.label", "Library or metadata team"),
      summary: withFallback(t, "welcome.persona.library.summary", "Improve authority control, metadata consistency, and curation workflows."),
    },
    {
      id: "leadership",
      label: withFallback(t, "welcome.persona.leadership.label", "Leadership or strategy"),
      summary: withFallback(t, "welcome.persona.leadership.summary", "Move faster from imported records to a decision-ready executive readout."),
    },
  ], [t]);

  const slides = useMemo<Record<PersonaId, Slide[]>>(() => ({
    research: [
      {
        emoji: "📚",
        title: withFallback(t, "welcome.research.slide1.title", "Start with a real research portfolio"),
        body: withFallback(t, "welcome.research.slide1.body", "Bring in publications, authors, and affiliations from CSV, Excel, BibTeX, RIS, or Scientific Import so UKIP can work with something real right away."),
        cta: {
          label: withFallback(t, "welcome.research.slide1.cta", "Go to Import"),
          href: "/import-export",
        },
        color: "from-blue-600 to-cyan-500",
      },
      {
        emoji: "✨",
        title: withFallback(t, "welcome.research.slide2.title", "Enrich before sharing the first readout"),
        body: withFallback(t, "welcome.research.slide2.body", "Use enrichment and authority review to strengthen identifiers, citations, and concepts before leadership sees the first dashboard."),
        cta: {
          label: withFallback(t, "welcome.research.slide2.cta", "Open Executive Dashboard"),
          href: "/analytics/dashboard",
        },
        color: "from-violet-600 to-fuchsia-500",
      },
      {
        emoji: "📈",
        title: withFallback(t, "welcome.research.slide3.title", "Turn the portfolio into a repeatable briefing flow"),
        body: withFallback(t, "welcome.research.slide3.body", "Once coverage and quality improve, use benchmark signals and reports to support recurring institutional review."),
        cta: {
          label: withFallback(t, "welcome.research.slide3.cta", "Open Reports"),
          href: "/reports",
        },
        color: "from-emerald-600 to-teal-500",
      },
    ],
    library: [
      {
        emoji: "🧭",
        title: withFallback(t, "welcome.library.slide1.title", "Import records with a curation goal"),
        body: withFallback(t, "welcome.library.slide1.body", "Start with a manageable dataset so the team can inspect titles, authors, affiliations, and identifiers without noise."),
        cta: {
          label: withFallback(t, "welcome.library.slide1.cta", "Go to Import"),
          href: "/import-export",
        },
        color: "from-blue-600 to-cyan-500",
      },
      {
        emoji: "🧩",
        title: withFallback(t, "welcome.library.slide2.title", "Use authority review to clean ambiguous metadata"),
        body: withFallback(t, "welcome.library.slide2.body", "Resolve people, institutions, and inconsistent variants before they become reporting problems downstream."),
        cta: {
          label: withFallback(t, "welcome.library.slide2.cta", "Open Authority Review"),
          href: "/authority",
        },
        color: "from-violet-600 to-fuchsia-500",
      },
      {
        emoji: "✅",
        title: withFallback(t, "welcome.library.slide3.title", "Use quality and system status as curation cues"),
        body: withFallback(t, "welcome.library.slide3.body", "The knowledge table helps you distinguish pipeline progress from human review, so the team knows what still needs attention."),
        cta: {
          label: withFallback(t, "welcome.library.slide3.cta", "Open Knowledge Table"),
          href: "/",
        },
        color: "from-emerald-600 to-teal-500",
      },
    ],
    leadership: [
      {
        emoji: "🚀",
        title: withFallback(t, "welcome.leadership.slide1.title", "Start with a pilot-sized dataset"),
        body: withFallback(t, "welcome.leadership.slide1.body", "A focused import is enough to see whether the portfolio can support a credible executive narrative."),
        cta: {
          label: withFallback(t, "welcome.leadership.slide1.cta", "Launch Demo or Import"),
          href: "/import-export",
        },
        color: "from-blue-600 to-cyan-500",
      },
      {
        emoji: "📊",
        title: withFallback(t, "welcome.leadership.slide2.title", "Read coverage, quality, and benchmark together"),
        body: withFallback(t, "welcome.leadership.slide2.body", "The Executive Dashboard is strongest when enrichment and quality are high enough to trust the first interpretation."),
        cta: {
          label: withFallback(t, "welcome.leadership.slide2.cta", "Open Executive Dashboard"),
          href: "/analytics/dashboard",
        },
        color: "from-violet-600 to-fuchsia-500",
      },
      {
        emoji: "📝",
        title: withFallback(t, "welcome.leadership.slide3.title", "Move from exploration to a brief"),
        body: withFallback(t, "welcome.leadership.slide3.body", "Once the signals are stable, UKIP can turn the workspace into a concise brief for leadership or external review."),
        cta: {
          label: withFallback(t, "welcome.leadership.slide3.cta", "Open Reports"),
          href: "/reports",
        },
        color: "from-emerald-600 to-teal-500",
      },
    ],
  }), [t]);

  const dismiss = () => {
    localStorage.setItem(STORAGE_KEY, "1");
    localStorage.setItem(PERSONA_KEY, persona);
    setVisible(false);
  };

  const selectPersona = (nextPersona: PersonaId) => {
    setPersona(nextPersona);
    setSlide(0);
    localStorage.setItem(PERSONA_KEY, nextPersona);
  };

  if (!visible) return null;

  const currentSlides = slides[persona];
  const current = currentSlides[slide];
  const isLast = slide === currentSlides.length - 1;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="relative mx-4 w-full max-w-2xl overflow-hidden rounded-2xl bg-white shadow-2xl dark:bg-slate-900">
        <div className={`bg-gradient-to-br ${current.color} px-8 py-10 text-white`}>
          <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
            <div className="max-w-xl">
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-white/80">
                {withFallback(t, "welcome.eyebrow", "Welcome to UKIP")}
              </p>
              <div className="mt-3 flex items-center gap-3">
                <div className="text-5xl">{current.emoji}</div>
                <div>
                  <h2 className="text-xl font-bold leading-snug">{current.title}</h2>
                  <p className="mt-1 text-sm text-white/80">
                    {withFallback(t, "welcome.persona_prompt", "Choose the path that best matches your role.")}
                  </p>
                </div>
              </div>
            </div>
            <span className="rounded-full bg-white/15 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-white/90">
              {personaOptions.find((option) => option.id === persona)?.label}
            </span>
          </div>
        </div>

        <div className="border-b border-slate-100 px-8 py-5 dark:border-slate-800">
          <div className="grid gap-3 md:grid-cols-3">
            {personaOptions.map((option) => {
              const active = option.id === persona;
              return (
                <button
                  key={option.id}
                  onClick={() => selectPersona(option.id)}
                  className={`rounded-xl border px-4 py-3 text-left transition-colors ${
                    active
                      ? "border-violet-300 bg-violet-50 dark:border-violet-700 dark:bg-violet-950/30"
                      : "border-slate-200 bg-white hover:border-violet-200 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:hover:border-violet-800 dark:hover:bg-slate-800"
                  }`}
                >
                  <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">{option.label}</p>
                  <p className="mt-1 text-xs leading-5 text-slate-500 dark:text-slate-400">{option.summary}</p>
                </button>
              );
            })}
          </div>
        </div>

        <div className="px-8 py-6">
          <p className="text-sm leading-relaxed text-slate-600 dark:text-slate-300">{current.body}</p>
        </div>

        <div className="flex justify-center gap-2 pb-2">
          {currentSlides.map((_, index) => (
            <button
              key={index}
              onClick={() => setSlide(index)}
              className={`h-2 rounded-full transition-all ${index === slide ? "w-6 bg-violet-600" : "w-2 bg-slate-200 dark:bg-slate-700"}`}
              aria-label={`${withFallback(t, "welcome.step", "Step")} ${index + 1}`}
            />
          ))}
        </div>

        <div className="flex items-center justify-between gap-3 border-t border-slate-100 px-8 py-5 dark:border-slate-800">
          <button onClick={dismiss} className="text-sm text-slate-400 hover:text-slate-600 dark:text-slate-500 dark:hover:text-slate-300">
            {withFallback(t, "welcome.skip", "Skip for now")}
          </button>
          <div className="flex gap-2">
            {slide > 0 && (
              <button
                onClick={() => setSlide((currentSlide) => currentSlide - 1)}
                className="rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-600 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
              >
                {withFallback(t, "welcome.back", "Back")}
              </button>
            )}
            {!isLast ? (
              <button
                onClick={() => setSlide((currentSlide) => currentSlide + 1)}
                className="rounded-lg bg-violet-600 px-5 py-2 text-sm font-medium text-white hover:bg-violet-700"
              >
                {withFallback(t, "welcome.next", "Next")}
              </button>
            ) : (
              <Link
                href={current.cta.href}
                onClick={dismiss}
                className="rounded-lg bg-violet-600 px-5 py-2 text-sm font-medium text-white hover:bg-violet-700"
              >
                {current.cta.label}
              </Link>
            )}
          </div>
        </div>

        <button
          onClick={dismiss}
          className="absolute right-3 top-3 rounded-full p-1 text-white/70 hover:text-white"
          aria-label={withFallback(t, "welcome.close", "Close welcome dialog")}
        >
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  );
}
