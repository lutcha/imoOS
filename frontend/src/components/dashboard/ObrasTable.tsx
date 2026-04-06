"use client";

import { useState } from "react";
import Link from "next/link";
import { 
  Search, 
  Filter, 
  MoreHorizontal, 
  ArrowUpDown,
  Eye,
  Edit,
  HardHat
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Skeleton } from "@/components/ui/Skeleton";
import { Badge } from "@/components/ui/badge";
import { formatDate, formatCveCompact } from "@/lib/format";
import { ConstructionProject, getStatusLabel, getStatusColor } from "@/hooks/useConstructionStats";

type SortField = "name" | "status" | "progress" | "expected_end_date" | "budget";
type SortOrder = "asc" | "desc";

interface ObrasTableProps {
  projects: ConstructionProject[];
  isLoading?: boolean;
  error?: Error | null;
}

export function ObrasTable({ projects, isLoading, error }: ObrasTableProps) {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [sortField, setSortField] = useState<SortField>("progress");
  const [sortOrder, setSortOrder] = useState<SortOrder>("desc");

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortOrder("desc");
    }
  };

  const filteredProjects = projects
    .filter((p) => {
      const matchesSearch = p.name.toLowerCase().includes(search.toLowerCase()) ||
        p.description?.toLowerCase().includes(search.toLowerCase());
      const matchesStatus = statusFilter === "ALL" || p.status === statusFilter;
      return matchesSearch && matchesStatus;
    })
    .sort((a, b) => {
      let comparison = 0;
      switch (sortField) {
        case "name":
          comparison = a.name.localeCompare(b.name);
          break;
        case "status":
          comparison = a.status.localeCompare(b.status);
          break;
        case "progress":
          comparison = a.overall_progress_pct - b.overall_progress_pct;
          break;
        case "expected_end_date":
          comparison = (a.expected_end_date || "").localeCompare(b.expected_end_date || "");
          break;
        case "budget":
          comparison = parseFloat(a.budget_cve || "0") - parseFloat(b.budget_cve || "0");
          break;
      }
      return sortOrder === "asc" ? comparison : -comparison;
    });

  const statusOptions = [
    { value: "ALL", label: "Todos" },
    { value: "PLANNING", label: "Planeamento" },
    { value: "ACTIVE", label: "Em Construção" },
    { value: "ON_HOLD", label: "Em Pausa" },
    { value: "COMPLETED", label: "Concluído" },
  ];

  if (error) {
    return (
      <div className="rounded-2xl border border-border bg-white p-8 text-center">
        <div className="mx-auto h-12 w-12 rounded-full bg-red-50 flex items-center justify-center mb-4">
          <HardHat className="h-6 w-6 text-red-500" />
        </div>
        <h3 className="text-sm font-medium text-foreground">Erro ao carregar obras</h3>
        <p className="text-xs text-muted-foreground mt-1">Tente recarregar a página</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Pesquisar obras..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-xl border border-border bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 rounded-xl border border-border bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
          >
            {statusOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="rounded-2xl border border-border bg-white shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border bg-slate-50/50">
                <th 
                  className="px-4 py-3 text-left font-medium text-muted-foreground cursor-pointer hover:text-foreground"
                  onClick={() => handleSort("name")}
                >
                  <div className="flex items-center gap-1">
                    Obra
                    <ArrowUpDown className="h-3 w-3" />
                  </div>
                </th>
                <th 
                  className="px-4 py-3 text-left font-medium text-muted-foreground cursor-pointer hover:text-foreground"
                  onClick={() => handleSort("status")}
                >
                  <div className="flex items-center gap-1">
                    Estado
                    <ArrowUpDown className="h-3 w-3" />
                  </div>
                </th>
                <th 
                  className="px-4 py-3 text-left font-medium text-muted-foreground cursor-pointer hover:text-foreground"
                  onClick={() => handleSort("progress")}
                >
                  <div className="flex items-center gap-1">
                    Progresso
                    <ArrowUpDown className="h-3 w-3" />
                  </div>
                </th>
                <th 
                  className="px-4 py-3 text-left font-medium text-muted-foreground cursor-pointer hover:text-foreground"
                  onClick={() => handleSort("expected_end_date")}
                >
                  <div className="flex items-center gap-1">
                    Previsão
                    <ArrowUpDown className="h-3 w-3" />
                  </div>
                </th>
                <th 
                  className="px-4 py-3 text-left font-medium text-muted-foreground cursor-pointer hover:text-foreground"
                  onClick={() => handleSort("budget")}
                >
                  <div className="flex items-center gap-1">
                    Orçamento
                    <ArrowUpDown className="h-3 w-3" />
                  </div>
                </th>
                <th className="px-4 py-3 text-right font-medium text-muted-foreground">
                  Ações
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {isLoading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <tr key={i}>
                    <td className="px-4 py-3"><Skeleton className="h-4 w-32" /></td>
                    <td className="px-4 py-3"><Skeleton className="h-5 w-20 rounded-full" /></td>
                    <td className="px-4 py-3"><Skeleton className="h-4 w-24" /></td>
                    <td className="px-4 py-3"><Skeleton className="h-4 w-20" /></td>
                    <td className="px-4 py-3"><Skeleton className="h-4 w-24" /></td>
                    <td className="px-4 py-3"><Skeleton className="h-8 w-8 rounded-full ml-auto" /></td>
                  </tr>
                ))
              ) : filteredProjects.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-12 text-center">
                    <div className="mx-auto h-12 w-12 rounded-full bg-slate-50 flex items-center justify-center mb-4">
                      <HardHat className="h-6 w-6 text-slate-400" />
                    </div>
                    <h3 className="text-sm font-medium text-foreground">Nenhuma obra encontrada</h3>
                    <p className="text-xs text-muted-foreground mt-1">
                      {search || statusFilter !== "ALL" 
                        ? "Tente ajustar os filtros" 
                        : "As obras aparecerão aqui quando forem criadas"}
                    </p>
                  </td>
                </tr>
              ) : (
                filteredProjects.map((project) => {
                  const statusColors = getStatusColor(project.status);
                  const budgeted = parseFloat(project.budget_cve || "0");
                  const actual = parseFloat(project.actual_cost_cve || "0");
                  const variance = budgeted > 0 ? ((actual - budgeted) / budgeted) * 100 : 0;
                  const isOverBudget = variance > 10;

                  return (
                    <tr key={project.id} className="hover:bg-slate-50/70 transition-colors">
                      <td className="px-4 py-3">
                        <div>
                          <p className="font-medium text-foreground">{project.name}</p>
                          <p className="text-xs text-muted-foreground line-clamp-1">{project.description}</p>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <span className={cn(
                          "inline-flex items-center rounded-md border px-2 py-0.5 text-[11px] font-medium",
                          statusColors.bg,
                          statusColors.text,
                          statusColors.border
                        )}>
                          {getStatusLabel(project.status)}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <div className="w-20 bg-slate-100 rounded-full h-2 overflow-hidden">
                            <div
                              style={{ width: `${project.overall_progress_pct}%` }}
                              className={cn(
                                "h-2 rounded-full transition-all",
                                project.overall_progress_pct >= 100 
                                  ? "bg-emerald-500" 
                                  : project.overall_progress_pct >= 50 
                                    ? "bg-blue-500" 
                                    : "bg-amber-500"
                              )}
                            />
                          </div>
                          <span className="text-xs font-medium text-muted-foreground">
                            {Math.round(project.overall_progress_pct)}%
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {formatDate(project.expected_end_date)}
                      </td>
                      <td className="px-4 py-3">
                        <div>
                          <p className="text-sm font-medium">
                            {formatCveCompact(budgeted)}
                          </p>
                          {actual > 0 && (
                            <p className={cn(
                              "text-xs",
                              isOverBudget ? "text-red-600" : "text-muted-foreground"
                            )}>
                              Real: {formatCveCompact(actual)}
                              {isOverBudget && " ⚠"}
                            </p>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex items-center justify-end gap-1">
                          <Link
                            href={`/construction/${project.id}`}
                            className="p-1.5 rounded-lg hover:bg-slate-100 text-muted-foreground hover:text-foreground transition-colors"
                            title="Ver detalhes"
                          >
                            <Eye className="h-4 w-4" />
                          </Link>
                          <button
                            className="p-1.5 rounded-lg hover:bg-slate-100 text-muted-foreground hover:text-foreground transition-colors"
                            title="Editar"
                          >
                            <Edit className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
