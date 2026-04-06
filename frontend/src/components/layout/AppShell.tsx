"use client";

/**
 * AppShell — renders Sidebar+Topbar only for authenticated app routes.
 * Auth routes (/login) and superadmin routes (/superadmin) render children directly.
 */
import { usePathname } from "next/navigation";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

const SHELL_EXCLUDED = ["/login", "/superadmin"];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  const isExcluded = SHELL_EXCLUDED.some((p) => pathname?.startsWith(p));

  if (isExcluded) {
    return <>{children}</>;
  }

  return (
    <>
      <Sidebar />
      <div className="flex flex-col min-h-screen bg-muted/30 ml-64">
        <Topbar />
        <main className="flex-1 mt-16 p-8">
          {children}
        </main>
      </div>
    </>
  );
}
