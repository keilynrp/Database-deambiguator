/* eslint-disable @next/next/no-img-element */
"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { useSidebar } from "./SidebarProvider";
import { useLanguage } from "../contexts/LanguageContext";
import { useBranding, type BrandingSettings } from "../contexts/BrandingContext";
import { navSections } from "./sidebarNav";

// ── Logo icon — shows uploaded image or default DB icon ───────────────────────

function LogoIcon({ branding, size = 8 }: { branding: BrandingSettings; size?: number }) {
  const apiBase = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");
  const logoSrc = branding.logo_url?.startsWith("/static/")
    ? `${apiBase}${branding.logo_url}`
    : branding.logo_url || "";
  const px = `h-${size} w-${size}`;

  return (
    <div
      className={`flex ${px} items-center justify-center overflow-hidden rounded-lg`}
      style={{ backgroundColor: branding.accent_color || "#6366f1" }}
    >
      {logoSrc ? (
        <img
          src={logoSrc}
          alt={branding.platform_name}
          className="h-full w-full object-contain p-1"
          onError={(e) => { (e.currentTarget as HTMLImageElement).style.display = "none"; }}
        />
      ) : (
        <svg className="h-5 w-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
        </svg>
      )}
    </div>
  );
}

export default function Sidebar() {
  const pathname = usePathname();
  const { collapsed, toggle, mobileOpen, closeMobile } = useSidebar();
  const { t } = useLanguage();
  const { branding } = useBranding();

  // On desktop: fixed sidebar, collapsed or expanded
  // On mobile: full-width drawer, hidden until mobileOpen
  const desktopWidth = collapsed ? "lg:w-20" : "lg:w-64";
  const mobileTranslate = mobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0";

  return (
    <>
      {/* Mobile backdrop */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={closeMobile}
          aria-hidden="true"
        />
      )}

      <aside
        className={`fixed left-0 top-0 z-50 flex h-screen w-72 flex-col border-r border-gray-200 bg-white transition-transform duration-300 dark:border-gray-800 dark:bg-gray-900 lg:w-auto ${desktopWidth} ${mobileTranslate}`}
      >
        {/* Logo */}
        <div className="flex h-16 items-center justify-between border-b border-gray-200 px-6 dark:border-gray-800">
          {(!collapsed || mobileOpen) && (
            <Link href="/" className="flex items-center gap-2" onClick={closeMobile}>
              <LogoIcon branding={branding} size={8} />
              <span className="text-base font-semibold text-gray-900 dark:text-white">{branding.platform_name}</span>
            </Link>
          )}
          {/* Desktop collapse toggle — hidden on mobile */}
          <button
            onClick={toggle}
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
            className="hidden rounded-lg p-1.5 text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800 lg:block"
          >
            <svg className="h-5 w-5" aria-hidden="true" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {collapsed ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
              )}
            </svg>
          </button>
          {/* Mobile close button */}
          <button
            onClick={closeMobile}
            aria-label="Close navigation"
            className="rounded-lg p-1.5 text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800 lg:hidden"
          >
            <svg className="h-5 w-5" aria-hidden="true" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto px-4 py-4">
          {navSections.map((section, sectionIdx) => (
            <div key={section.header} className={sectionIdx > 0 ? "mt-6" : ""}>
              {collapsed && !mobileOpen ? (
                sectionIdx > 0 && <div className="mx-3 mb-3 h-px bg-gray-200 dark:bg-gray-800" />
              ) : (
                <div className="mb-2 px-3">
                  <span className="text-xs font-semibold uppercase tracking-wider text-gray-400 dark:text-gray-500">
                    {t(section.translationKey)}
                  </span>
                </div>
              )}
              <ul className="space-y-1">
                {section.items.map((item) => {
                  const isActive =
                    item.href === "/"
                      ? pathname === "/"
                      : pathname === item.href || pathname.startsWith(item.href + "/");
                  return (
                    <li key={item.href}>
                      <Link
                        href={item.href}
                        onClick={closeMobile}
                        className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                          isActive
                            ? "bg-blue-50 text-blue-600 dark:bg-blue-600/10 dark:text-blue-400"
                            : "text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
                        }`}
                        title={collapsed && !mobileOpen ? t(item.translationKey) : undefined}
                      >
                        <span className={isActive ? "text-blue-600 dark:text-blue-400" : "text-gray-400 dark:text-gray-500"}>
                          {item.icon}
                        </span>
                        {(!collapsed || mobileOpen) && t(item.translationKey)}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </nav>

        {/* Footer */}
        <div className="border-t border-gray-200 px-4 py-4 dark:border-gray-800">
          {(!collapsed || mobileOpen) ? (
            <div className="rounded-lg bg-gray-50 px-3 py-3 dark:bg-gray-800">
              <p className="text-xs font-semibold text-gray-900 dark:text-white">UKIP</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">v1.0 — Sprint 35</p>
            </div>
          ) : (
            <div className="flex justify-center">
              <span className="text-xs font-bold text-gray-400">U</span>
            </div>
          )}
        </div>
      </aside>
    </>
  );
}

