"use client";

import dynamic from "next/dynamic";

// Dynamic import to avoid prerendering issues
const MobileObraContent = dynamic(
  () => import("./ObraContent"),
  { 
    ssr: false,
    loading: () => (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }
);

export default function MobileObraPage() {
  return <MobileObraContent />;
}
