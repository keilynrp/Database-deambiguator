"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useSidebar } from "./SidebarProvider";
import Sidebar from "./Sidebar";
import Header from "./Header";
import { useAuth } from "../contexts/AuthContext";

export default function LayoutContent({ children }: { children: React.ReactNode }) {
  const { collapsed } = useSidebar();
  const { isAuthenticated, hydrated } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  const isLoginPage = pathname === "/login";

  useEffect(() => {
    if (!hydrated) return;
    if (!isAuthenticated && !isLoginPage) {
      router.replace("/login");
    }
  }, [hydrated, isAuthenticated, isLoginPage, router]);

  // Block ALL rendering until auth state is resolved from localStorage.
  // Server renders null, client hydration also renders null (hydrated starts false),
  // so the DOM matches — zero hydration mismatch possible.
  if (!hydrated) {
    return null;
  }

  // Login page renders without the shell (no sidebar / header)
  if (isLoginPage) {
    return <>{children}</>;
  }

  // Brief blank while the redirect above takes effect
  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div
        className={`flex min-w-0 flex-1 flex-col transition-[margin,width] duration-300 ease-out ${
          collapsed
            ? "lg:ml-16 lg:w-[calc(100%-4rem)]"
            : "lg:ml-64 lg:w-[calc(100%-16rem)]"
        }`}
      >
        <Header />
        <main className="flex-1 bg-gray-50 p-4 dark:bg-gray-950 lg:p-6">
          <div
            className={`mx-auto transition-[max-width] duration-300 ease-out ${
              collapsed ? "max-w-none" : "max-w-7xl"
            }`}
          >
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
