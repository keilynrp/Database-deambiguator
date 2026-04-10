"use client";

function localeForLanguage(language?: string): string {
  if (language === "es") return "es-MX";
  if (language === "en") return "en-US";
  if (typeof navigator !== "undefined" && navigator.language) return navigator.language;
  return "en-US";
}

function parseAppDate(iso: string | null | undefined): Date | null {
  if (!iso) return null;
  const normalized = /([zZ]|[+-]\d{2}:\d{2})$/.test(iso) ? iso : `${iso}Z`;
  const date = new Date(normalized);
  return Number.isNaN(date.getTime()) ? null : date;
}

export function formatDate(
  iso: string | null | undefined,
  language?: string,
  options: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "short",
    day: "2-digit",
  },
  fallback = "—",
): string {
  const date = parseAppDate(iso);
  if (!date) return fallback;
  return new Intl.DateTimeFormat(localeForLanguage(language), options).format(date);
}

export function formatDateTime(
  iso: string | null | undefined,
  language?: string,
  options: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  },
  fallback = "—",
): string {
  const date = parseAppDate(iso);
  if (!date) return fallback;
  return new Intl.DateTimeFormat(localeForLanguage(language), options).format(date);
}

export function formatRelativeTime(
  iso: string | null | undefined,
  language?: string,
  fallback = "—",
): string {
  const date = parseAppDate(iso);
  if (!date) return fallback;
  const diff = Math.max(0, Date.now() - date.getTime());
  const seconds = Math.floor(diff / 1000);
  if (seconds <= 0) {
    return language === "es" ? "justo ahora" : "just now";
  }
  const rtf = new Intl.RelativeTimeFormat(localeForLanguage(language), { numeric: "auto" });
  if (seconds < 60) return rtf.format(-seconds, "second");
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return rtf.format(-minutes, "minute");
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return rtf.format(-hours, "hour");
  const days = Math.floor(hours / 24);
  if (days < 30) return rtf.format(-days, "day");
  return formatDateTime(iso, language, {
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: language !== "es",
  }, fallback);
}
