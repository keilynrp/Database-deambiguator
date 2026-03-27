"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

const STORAGE_KEY = "ukip_welcomed_v1";

const SLIDES = [
  {
    emoji: "📚",
    title: "Start with a real research portfolio",
    body: "UKIP's initial commercial path is research intelligence. Begin with your own publications, authors, and affiliations from CSV, Excel, BibTeX, or RIS instead of staying in demo mode.",
    cta: { label: "Go to Import", href: "/import-export" },
    color: "from-blue-600 to-cyan-500",
  },
  {
    emoji: "✨",
    title: "Enrich and harmonize what matters",
    body: "Use academic enrichment plus normalization rules to clean author names, affiliations, and publication metadata before stakeholders see the dashboard.",
    cta: { label: "Review Authority Data", href: "/authority" },
    color: "from-violet-600 to-fuchsia-500",
  },
  {
    emoji: "📈",
    title: "Turn clean data into recurring value",
    body: "Once the portfolio is clean, review coverage and trend KPIs, then add workflows or reports so the next reporting cycle needs less manual follow-up.",
    cta: { label: "Open Analytics", href: "/analytics/dashboard" },
    color: "from-emerald-600 to-teal-500",
  },
];

export default function WelcomeModal() {
  const [visible, setVisible] = useState(false);
  const [slide, setSlide] = useState(0);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const seen = localStorage.getItem(STORAGE_KEY);
    if (seen) return;
    const frame = window.requestAnimationFrame(() => setVisible(true));
    return () => window.cancelAnimationFrame(frame);
  }, []);

  const dismiss = () => {
    localStorage.setItem(STORAGE_KEY, "1");
    setVisible(false);
  };

  if (!visible) return null;

  const current = SLIDES[slide];
  const isLast = slide === SLIDES.length - 1;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="relative mx-4 w-full max-w-md overflow-hidden rounded-2xl bg-white shadow-2xl">
        <div className={`bg-gradient-to-br ${current.color} px-8 py-10 text-center text-white`}>
          <div className="mb-3 text-5xl">{current.emoji}</div>
          <h2 className="text-xl font-bold leading-snug">{current.title}</h2>
        </div>

        <div className="px-8 py-6">
          <p className="text-center text-sm leading-relaxed text-slate-600">{current.body}</p>
        </div>

        <div className="flex justify-center gap-2 pb-2">
          {SLIDES.map((_, index) => (
            <button
              key={index}
              onClick={() => setSlide(index)}
              className={`h-2 rounded-full transition-all ${index === slide ? "w-6 bg-violet-600" : "w-2 bg-slate-200"}`}
            />
          ))}
        </div>

        <div className="flex items-center justify-between gap-3 border-t border-slate-100 px-8 py-5">
          <button onClick={dismiss} className="text-sm text-slate-400 hover:text-slate-600">
            Skip tour
          </button>
          <div className="flex gap-2">
            {slide > 0 && (
              <button
                onClick={() => setSlide((currentSlide) => currentSlide - 1)}
                className="rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-600 hover:bg-slate-50"
              >
                Back
              </button>
            )}
            {!isLast ? (
              <button
                onClick={() => setSlide((currentSlide) => currentSlide + 1)}
                className="rounded-lg bg-violet-600 px-5 py-2 text-sm font-medium text-white hover:bg-violet-700"
              >
                Next
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
        >
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  );
}
