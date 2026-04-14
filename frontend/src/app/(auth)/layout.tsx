/**
 * Auth layout — no sidebar/topbar
 * Route group: (auth) — doesn't affect URL path
 */
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Entrar — ImoOS",
};

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const isDevMode = process.env.NODE_ENV === "development";

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center p-4">
      {/* ⚠️ DEV MODE BANNER */}
      {isDevMode && (
        <div className="fixed top-0 left-0 right-0 bg-yellow-400 text-yellow-900 text-center py-2 px-4 text-sm font-semibold z-50">
          ⚠️ MODO DESENVOLVIMENTO — Autenticação simplificada ativa ⚠️
        </div>
      )}
      
      <div className={isDevMode ? "mt-10" : ""}>
        {children}
      </div>
    </div>
  );
}
