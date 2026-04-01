"use client";

import { useQuery } from "@tanstack/react-query";
import apiClient from "@/lib/api-client";
import { useAuth } from "@/contexts/AuthContext";
import { Skeleton } from "@/components/ui/Skeleton";
import { AlertTriangle, TrendingUp } from "lucide-react";

interface ResourceUsage {
  current: number;
  limit: number;
  pct_used: number;
}

interface UsageData {
  plan: "starter" | "pro" | "enterprise";
  projects: ResourceUsage;
  units: ResourceUsage;
  users: ResourceUsage;
}

interface PlanEvent {
  id: string;
  event_type: string;
  from_plan: string;
  to_plan: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

const PLAN_COLORS: Record<string, string> = {
  starter: "bg-slate-100 text-slate-800",
  pro: "bg-blue-100 text-blue-800",
  enterprise: "bg-purple-100 text-purple-800",
};

const PLAN_LABELS: Record<string, string> = {
  starter: "Starter",
  pro: "Pro",
  enterprise: "Enterprise",
};

const EVENT_LABELS: Record<string, string> = {
  PLAN_UPGRADED: "Upgrade",
  PLAN_DOWNGRADED: "Downgrade",
  LIMIT_HIT: "Limite Atingido",
  TRIAL_STARTED: "Trial Iniciado",
  TRIAL_ENDED: "Trial Terminado",
};

function progressColor(pct: number): string {
  if (pct >= 80) return "bg-red-500";
  if (pct >= 60) return "bg-amber-400";
  return "bg-emerald-500";
}

function UsageBar({ label, usage }: { label: string; usage: ResourceUsage }) {
  const color = progressColor(usage.pct_used);
  return (
    <div className="space-y-1.5">
      <div className="flex justify-between text-sm">
        <span className="font-medium text-foreground">{label}</span>
        <span className="text-muted-foreground">
          {usage.current} / {usage.limit}
          {usage.pct_used >= 80 && (
            <AlertTriangle className="inline ml-1.5 h-3.5 w-3.5 text-red-500" />
          )}
        </span>
      </div>
      <div className="h-2 rounded-full bg-muted overflow-hidden">
        <div
          className={`h-full rounded-full transition-all ${color}`}
          style={{ width: `${Math.min(usage.pct_used, 100)}%` }}
        />
      </div>
      <p className="text-xs text-muted-foreground">{usage.pct_used}% utilizado</p>
    </div>
  );
}

export default function BillingPage() {
  const { isAuthenticated } = useAuth();

  const { data: usage, isLoading: loadingUsage } = useQuery<UsageData>({
    queryKey: ["tenant-usage"],
    queryFn: () =>
      apiClient.get<UsageData>("/tenant/usage/").then((r) => r.data),
    enabled: isAuthenticated,
  });

  const { data: events, isLoading: loadingEvents } = useQuery<PlanEvent[]>({
    queryKey: ["plan-events"],
    queryFn: () =>
      apiClient.get<PlanEvent[]>("/tenant/plan-events/").then((r) => r.data),
    enabled: isAuthenticated,
  });

  if (loadingUsage) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-40 rounded-xl" />
        <Skeleton className="h-48 rounded-xl" />
      </div>
    );
  }

  return (
    <div className="max-w-2xl space-y-8">
      <h1 className="text-2xl font-bold text-foreground">Plano & Consumo</h1>

      {/* Current Plan */}
      <div className="bg-white rounded-xl border border-border p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground mb-1">Plano actual</p>
            <span
              className={`inline-block rounded-full px-3 py-1 text-sm font-semibold ${
                PLAN_COLORS[usage?.plan ?? "starter"]
              }`}
            >
              {PLAN_LABELS[usage?.plan ?? "starter"]}
            </span>
          </div>
          <button
            className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary/90 transition-colors"
            onClick={() => window.open("mailto:sales@imos.cv?subject=Upgrade ImoOS", "_blank")}
          >
            <TrendingUp className="h-4 w-4" />
            Upgrade
          </button>
        </div>
        <p className="text-xs text-muted-foreground">
          Para upgrade ou downgrade contacte a nossa equipa comercial.
        </p>
      </div>

      {/* Usage */}
      {usage && (
        <div className="bg-white rounded-xl border border-border p-6 space-y-6">
          <h2 className="font-semibold text-foreground">Consumo actual</h2>
          <UsageBar label="Projectos" usage={usage.projects} />
          <UsageBar label="Unidades" usage={usage.units} />
          <UsageBar label="Utilizadores" usage={usage.users} />
        </div>
      )}

      {/* Event History */}
      <div className="bg-white rounded-xl border border-border overflow-hidden">
        <div className="px-6 py-4 border-b border-border">
          <h2 className="font-semibold text-foreground">Histórico de eventos</h2>
        </div>
        {loadingEvents ? (
          <div className="p-6 space-y-3">
            {[0, 1, 2].map((i) => <Skeleton key={i} className="h-10" />)}
          </div>
        ) : !events || events.length === 0 ? (
          <p className="px-6 py-8 text-muted-foreground text-sm text-center">
            Nenhum evento registado.
          </p>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr>
                <th className="text-left px-6 py-3 text-muted-foreground font-medium">Data</th>
                <th className="text-left px-6 py-3 text-muted-foreground font-medium">Evento</th>
                <th className="text-left px-6 py-3 text-muted-foreground font-medium">De</th>
                <th className="text-left px-6 py-3 text-muted-foreground font-medium">Para</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {events.map((e) => (
                <tr key={e.id} className="hover:bg-muted/30">
                  <td className="px-6 py-3 text-muted-foreground">
                    {new Date(e.created_at).toLocaleDateString("pt-CV")}
                  </td>
                  <td className="px-6 py-3 font-medium">
                    {EVENT_LABELS[e.event_type] ?? e.event_type}
                  </td>
                  <td className="px-6 py-3">{e.from_plan || "—"}</td>
                  <td className="px-6 py-3">{e.to_plan || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
