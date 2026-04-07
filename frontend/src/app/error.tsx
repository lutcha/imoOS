"use client";

import { useEffect } from "react";

export default function ErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log error to console
    console.error("App error:", error);
  }, [error]);

  // Check if it's an auth error
  const isAuthError = error.message?.includes("401") || 
                      error.message?.includes("unauthorized") ||
                      error.digest?.includes("401");

  if (isAuthError) {
    // Redirect to login
    if (typeof window !== "undefined") {
      window.location.replace("/login");
      return null;
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900">Algo correu mal</h2>
        <p className="mt-2 text-gray-600">{error.message || "Erro inesperado"}</p>
        <button
          onClick={() => reset()}
          className="mt-4 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90"
        >
          Tentar novamente
        </button>
      </div>
    </div>
  );
}
