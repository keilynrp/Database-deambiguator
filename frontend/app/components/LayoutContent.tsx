"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useSidebar } from "./SidebarProvider";
import Sidebar from "./Sidebar";
import Header from "./Header";
import { useAuth } from "../contexts/AuthContext";
import { useAssistant } from "../contexts/AssistantContext";
import { AppShell, PageShell } from "./layout";
import { UKIPAssistantPanel } from "./ukip";
import { isPublicRoute, isStandaloneRoute } from "../../lib/publicRoutes";

export default function LayoutContent({ children }: { children: React.ReactNode }) {
  const { collapsed } = useSidebar();
  const { isAuthenticated, hydrated } = useAuth();
  const { context: assistantContext } = useAssistant();
  const pathname = usePathname();
  const router = useRouter();

  // Both allowlists live in lib/publicRoutes so they are named, tested things.
  // /embed/{token} was missing from the inline version, which is why an
  // anonymous visitor to a customer's iframe landed on /login.
  const isPublic = isPublicRoute(pathname);
  const isStandalone = isStandaloneRoute(pathname);

  useEffect(() => {
    if (!hydrated) return;
    if (!isAuthenticated && !isPublic) {
      router.replace("/login");
    }
  }, [hydrated, isAuthenticated, isPublic, router]);

  // Block ALL rendering until auth state is resolved from localStorage.
  // Server renders null, client hydration also renders null (hydrated starts false),
  // so the DOM matches — zero hydration mismatch possible.
  if (!hydrated) {
    return null;
  }

  // Login and embed pages render without the shell (no sidebar / header). For an
  // embed this holds even with a session: the document gets framed at 480x320 by
  // a third party, and the operator previewing it must see what the customer sees.
  if (isStandalone) {
    return <>{children}</>;
  }

  if (isPublic && !isAuthenticated) {
    return <>{children}</>;
  }

  // Brief blank while the redirect above takes effect
  if (!isAuthenticated) {
    return null;
  }

  return (
    <AppShell sidebar={<Sidebar />} header={<Header />} collapsed={collapsed}>
      <PageShell constrained={!collapsed}>{children}</PageShell>
      <UKIPAssistantPanel context={assistantContext} />
    </AppShell>
  );
}
