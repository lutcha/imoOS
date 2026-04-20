import { ReactNode } from "react";
import { FileText } from "lucide-react";
import { ContractsNav } from "./_components/ContractsNav";

export default function ContractsLayout({ children }: { children: ReactNode }) {
  return (
    <div className="space-y-6">
      {/* Page header (Shared across all contract subpages) */}
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div className="flex items-center space-x-4">
          <div className="h-14 w-14 rounded-2xl bg-primary/10 flex items-center justify-center border border-primary/10">
            <FileText className="h-8 w-8 text-primary" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-foreground">Gestão de Contratos</h1>
            <p className="text-sm text-muted-foreground mt-0.5">
              Automatização e controlo financeiro
            </p>
          </div>
        </div>
      </div>

      <ContractsNav />

      {children}
    </div>
  );
}
