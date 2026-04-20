"use client";

/**
 * CRM page — ImoOS
 * Pipeline Kanban board + List view toggle.
 */
import { Search, Users2, LayoutList, LayoutGrid } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { useLeads } from "@/hooks/useLeads";
import { LeadStatusBadge } from "@/components/ui/StatusBadge";
import { Skeleton } from "@/components/ui/Skeleton";
import { formatDate } from "@/lib/format";
import { KanbanBoard } from "@/components/crm/KanbanBoard";
import { LeadModal } from "@/components/crm/LeadModal";

export default function CrmPage() {
  const [viewType, setViewType] = useState<"kanban" | "list">("kanban");
  const [search, setSearch] = useState("");
  const [isLeadModalOpen, setIsLeadModalOpen] = useState(false);

  const { data: leadsPage, isLoading: leadsLoading } = useLeads({
    search: search || undefined,
    ordering: "-created_at",
    page_size: 50,
  });

  return (
    <div className="space-y-6 h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">CRM</h1>
          <p className="text-muted-foreground mt-1 text-sm">Gestão de pipeline e leads</p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex items-center p-1 bg-muted rounded-xl border border-border">
            <button
              onClick={() => setViewType("kanban")}
              className={cn(
                "flex items-center px-3 py-1.5 rounded-lg text-xs font-bold transition-all",
                viewType === "kanban" ? "bg-white shadow-sm text-primary" : "text-muted-foreground hover:text-foreground"
              )}
            >
              <LayoutGrid className="h-3.5 w-3.5 mr-1.5" />
              Kanban
            </button>
            <button
              onClick={() => setViewType("list")}
              className={cn(
                "flex items-center px-3 py-1.5 rounded-lg text-xs font-bold transition-all",
                viewType === "list" ? "bg-white shadow-sm text-primary" : "text-muted-foreground hover:text-foreground"
              )}
            >
              <LayoutList className="h-3.5 w-3.5 mr-1.5" />
              Lista
            </button>
          </div>

          <button 
            onClick={() => setIsLeadModalOpen(true)}
            className="flex items-center space-x-2 rounded-xl bg-primary px-5 py-2.5 text-sm font-bold text-white transition-all hover:bg-primary/90 shadow-lg shadow-primary/20 hover:scale-[1.02] active:scale-[0.98]"
          >
            <Users2 className="h-4 w-4" />
            <span>Novo Lead</span>
          </button>
        </div>
      </div>

      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center rounded-xl border border-border bg-white px-4 py-2.5 shadow-sm min-w-80 group focus-within:ring-2 focus-within:ring-primary/10 transition-all">
          <Search className="h-4 w-4 text-muted-foreground mr-2.5 shrink-0 group-focus-within:text-primary" />
          <input
            type="text"
            placeholder="Pesquisar leads por nome, email ou telefone…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="bg-transparent text-sm outline-none placeholder:text-muted-foreground w-full font-medium"
          />
        </div>
      </div>

      {/* Main View Area */}
      <div className="flex-1 min-h-0">
        {viewType === "kanban" ? (
          <KanbanBoard />
        ) : (
          <div className="rounded-2xl border border-border bg-white shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border bg-slate-50/50">
                    {["Nome", "Email", "Telefone", "Estado", "Origem", "Tipologia", "Data"].map((h) => (
                      <th key={h} className="px-6 py-4 text-left text-xs font-bold text-muted-foreground uppercase tracking-widest whitespace-nowrap">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {leadsLoading ? (
                    Array.from({ length: 6 }).map((_, i) => (
                      <tr key={i}>
                        {Array.from({ length: 7 }).map((_, j) => (
                          <td key={j} className="px-6 py-4">
                            <Skeleton className="h-4 w-24" />
                          </td>
                        ))}
                      </tr>
                    ))
                  ) : (leadsPage?.results ?? []).length === 0 ? (
                    <tr>
                      <td colSpan={7} className="px-6 py-20 text-center text-muted-foreground text-sm font-medium">
                        {search ? "Nenhum lead encontrado para a pesquisa." : "Ainda não há leads registados."}
                      </td>
                    </tr>
                  ) : (
                    (leadsPage?.results ?? []).map((lead) => (
                      <tr
                        key={lead.id}
                        className="hover:bg-slate-50/80 transition-colors cursor-pointer"
                      >
                        <td className="px-6 py-4 font-bold text-foreground whitespace-nowrap">
                          {lead.first_name} {lead.last_name}
                        </td>
                        <td className="px-6 py-4 text-muted-foreground font-medium">{lead.email}</td>
                        <td className="px-6 py-4 text-muted-foreground font-medium">{lead.phone || "—"}</td>
                        <td className="px-6 py-4 text-muted-foreground">
                          <LeadStatusBadge status={lead.status} />
                        </td>
                        <td className="px-6 py-4 text-muted-foreground font-medium capitalize">
                          {lead.source.toLowerCase()}
                        </td>
                        <td className="px-6 py-4 text-muted-foreground font-medium">
                          {lead.preferred_typology || "—"}
                        </td>
                        <td className="px-6 py-4 text-muted-foreground whitespace-nowrap font-medium">
                          {formatDate(lead.created_at)}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      <LeadModal 
        isOpen={isLeadModalOpen} 
        onClose={() => setIsLeadModalOpen(false)} 
      />
    </div>
  );
}

