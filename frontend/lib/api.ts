/**
 * Centralized API configuration for UKIP frontend.
 *
 * In the browser all requests go through the Next.js proxy at /api/backend/*
 * so they stay on the same origin (no CORS / Private-Network-Access issues).
 * Server-side (SSR / API routes) hits the backend directly via NEXT_PUBLIC_API_URL.
 */
const DIRECT_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export const API_BASE =
  typeof window === "undefined"
    ? DIRECT_URL          // server-side: call backend directly
    : "/api/backend";     // browser: route through Next.js proxy (same-origin)

import { isPublicRoute } from "./publicRoutes";

/**
 * Authenticated fetch wrapper.
 * - Reads the Bearer token from localStorage (key: "ukip_token") and attaches it.
 * - On HTTP 401, clears the stored token and redirects to /login — but only on a
 *   page that requires a session. See the note on the 401 branch below.
 */
export async function apiFetch(path: string, options: RequestInit = {}): Promise<Response> {
  const token = typeof window !== "undefined" ? localStorage.getItem("ukip_token") : null;
  const isFormData = typeof FormData !== "undefined" && options.body instanceof FormData;

  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  // Let the browser set multipart boundaries for FormData requests.
  if (!isFormData && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  } catch {
    throw new Error(`Cannot connect to backend at ${API_BASE}. Is the server running?`);
  }

  // A 401 means "this page needs a session it does not have" — on a page that
  // needs one. On a public page it means a background provider call (branding,
  // enrichment stats) was answered for an anonymous visitor, which is expected
  // and not a reason to navigate anywhere.
  //
  // Without this guard the assignment below is a hard navigation that no route
  // guard can veto: it is why /embed/{token} bounced to /login even after the
  // shell allowlisted it, and why a customer's iframe showed a broken document.
  // /catalogs/{slug} had the same hole.
  if (
    response.status === 401 &&
    typeof window !== "undefined" &&
    !isPublicRoute(window.location.pathname)
  ) {
    localStorage.removeItem("ukip_token");
    window.location.href = "/login";
  }

  return response;
}
