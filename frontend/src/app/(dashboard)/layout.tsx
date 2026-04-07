"use client";

import { ProtectedPage } from "@/components/layout/AppShell";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <ProtectedPage>{children}</ProtectedPage>;
}
