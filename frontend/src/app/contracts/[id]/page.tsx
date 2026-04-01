"use client";

import Link from "next/link";
import {
  ArrowLeft,
  FileText,
  FileDown,
  Wallet,
  Clock,
  CheckCircle2,
  AlertCircle,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useContract, type ContractStatus } from "@/hooks/useContracts";
import {
  useGeneratePaymentPlan,
  useMarkPaymentPaid,
  type PaymentStatus,
  type PaymentType,
  type MarkPaidPayload,
} from "@/hooks/usePaymentPlans";
import { Skeleton } from "@/components/ui/Skeleton";
import { formatDate, formatCve } from "@/lib/format";

// ----- Contract status badge -----

const CONTRACT_STATUS_CONFIG: Record<
  ContractStatus,
  { label: string; className: string }
> = {
  DRAFT:     { label: "Rascunho",  className: "bg-slate-100 text-slate-600 border-slate-200" },
  ACTIVE:    { label: "Activo",    className: "bg-emerald-50 text-emerald-700 border-emerald-200" },
  COMPLETED: { label: "Concluído", className: "bg-blue-50 text-blue-700 border-blue-200" },
  CANCELLED: { label: "Cancelado", className: "bg-red-50 text-red-600 border-red-200" },
};

function ContractStatusBadge({ status }: { status: ContractStatus }) {
  const cfg = CONTRACT_STATUS_CONFIG[status] ?? CONTRACT_STATUS_CONFIG.DRAFT;
  return (
    <span className={cn("inline-flex items-center rounded-full border px-2.5 py-0.5 text-[11px] font-bold", cfg.className)}>
      {cfg.label}
    </span>
  );
}

// ----- Payment status badge -----

type EffectivePaymentStatus = PaymentStatus | "OVERDUE";

const PAYMENT_STATUS_CONFIG: Record<
  EffectivePaymentStatus,
  { label: string; className: string; icon: React.ElementType }
> = {
  PENDING: { label: "Pendente",   className: "bg-amber-50 text-amber-700 border-amber-200",      icon: Clock },
  PAID:    { label: "Pago",       className: "bg-emerald-50 text-emerald-700 border-emerald-200", icon: CheckCircle2 },
  OVERDUE: { label: "Em Atraso",  className: "bg-red-50 text-red-600 border-red-200",             icon: AlertCircle },
};

function PaymentStatusBadge({ status, dueDate }: { status: PaymentStatus; dueDate: string }) {
  const effective: EffectivePaymentStatus =
    status === "PENDING" && new Date(dueDate) < new Date() ? "OVERDUE" : status;
  const cfg = PAYMENT_STATUS_CONFIG[effective];
  const Icon = cfg.icon;
  return (
    <span className={cn("inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-[11px] font-bold", cfg.className)}>
      <Icon className="h-3 w-3" />
      {cfg.label}
    </span>
  );
}

// ----- Payment type label -----

const PAYMENT_TYPE_LABELS: Record<PaymentType, string> = {
  DEPOSIT:     "Sinal",
  INSTALLMENT: "Prestação",
  FINAL:       "Escritura",
};

// ----- Page -----

export default function ContractDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const { data: contract, isLoading, isError } = useContract(params.id);

  const generatePlan = useGeneratePaymentPlan();
  const markPaid = useMarkPaymentPaid();

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-32 rounded-xl" />
        <Skeleton className="h-32 w-full rounded-2xl" />
        <Skeleton className="h-64 w-full rounded-2xl" />
      </div>
    );
  }

  if (isError || !contract) {
    return (
      <div className="space-y-4">
        <Link
          href="/contracts"
          className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Contratos
        </Link>
        <div className="rounded-2xl border border-red-200 bg-red-50 p-8 text-center">
          <p className="text-sm font-bold text-red-600">Erro ao carregar contrato.</p>
        </div>
      </div>
    );
  }

  const payments = contract.payments ?? [];
  const hasPlan = payments.length > 0;

  return (
    <div className="space-y-6">
      {/* Back link */}
      <Link
        href="/contracts"
        className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        Contratos
      </Link>

      {/* Header card */}
      <div className="rounded-2xl border border-border bg-white shadow-sm p-6">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div className="flex items-center gap-4">
            <div className="h-14 w-14 rounded-2xl bg-primary/10 flex items-center justify-center border border-primary/10">
              <FileText className="h-8 w-8 text-primary" />
            </div>
            <div>
              <div className="flex items-center gap-3 flex-wrap">
                <h1 className="font-mono text-2xl font-bold tracking-tight text-foreground">
                  {contract.contract_number}
                </h1>
                <ContractStatusBadge status={contract.status} />
              </div>
              <p className="text-sm text-muted-foreground mt-0.5">
                Criado em {formatDate(contract.created_at)}
              </p>
            </div>
          </div>

          {contract.pdf_s3_key && (
            <button
              disabled
              className="inline-flex items-center gap-2 rounded-xl border border-border px-4 py-2.5 text-sm font-bold text-muted-foreground cursor-not-allowed opacity-60"
              title="PDF disponível em breve"
            >
              <FileDown className="h-4 w-4" />
              PDF
            </button>
          )}
        </div>

        {/* Info grid */}
        <div className="mt-6 grid grid-cols-2 md:grid-cols-3 gap-6 pt-6 border-t border-border">
          {[
            { label: "Lead",         value: contract.lead_name },
            { label: "Unidade",      value: contract.unit_code },
            { label: "Vendedor",     value: contract.vendor_email ?? "—" },
            { label: "Valor Total",  value: formatCve(contract.total_price_cve) },
            { label: "Assinado em",  value: formatDate(contract.signed_at) },
          ].map(({ label, value }) => (
            <div key={label}>
              <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider mb-1">
                {label}
              </p>
              <p className="text-sm font-semibold text-foreground">{value}</p>
            </div>
          ))}
        </div>

        {/* Notes */}
        {contract.notes && (
          <div className="mt-6 pt-6 border-t border-border">
            <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider mb-2">
              Notas
            </p>
            <p className="text-sm text-foreground whitespace-pre-wrap">{contract.notes}</p>
          </div>
        )}
      </div>

      {/* Payment plan card */}
      <div className="rounded-2xl border border-border bg-white shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-border flex items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Wallet className="h-5 w-5 text-primary" />
            <h2 className="text-base font-bold text-foreground">Plano de Pagamentos</h2>
          </div>

          {!hasPlan && contract.status !== "CANCELLED" && (
            <button
              onClick={() => generatePlan.mutate(contract.id)}
              disabled={generatePlan.isPending}
              className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2 text-xs font-bold text-white shadow-md shadow-primary/20 hover:opacity-90 transition-opacity disabled:opacity-60"
            >
              {generatePlan.isPending ? "A gerar…" : "Gerar Plano"}
            </button>
          )}
        </div>

        {generatePlan.isError && (
          <div className="px-6 py-3 border-b border-red-200 bg-red-50">
            <p className="text-xs font-bold text-red-600">
              Erro ao gerar plano de pagamentos. Tente novamente.
            </p>
          </div>
        )}

        {!hasPlan ? (
          <div className="p-16 flex flex-col items-center text-center">
            <div className="h-14 w-14 rounded-2xl bg-muted flex items-center justify-center mb-4">
              <Wallet className="h-7 w-7 text-muted-foreground/40" />
            </div>
            <p className="text-sm font-bold text-foreground">Sem plano de pagamentos</p>
            <p className="text-xs text-muted-foreground mt-1">
              {contract.status === "CANCELLED"
                ? "Contrato cancelado."
                : "Clique em «Gerar Plano» para criar as prestações."}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-slate-50/50">
                  {["Tipo", "Valor CVE", "Data Prevista", "Referência MBE", "Estado", ""].map((h) => (
                    <th
                      key={h}
                      className="px-6 py-4 text-left text-[10px] font-bold text-muted-foreground uppercase tracking-widest whitespace-nowrap"
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {payments.map((p) => {
                  const isActionable = p.status === "PENDING";
                  const isMarking = markPaid.isPending && (markPaid.variables as MarkPaidPayload)?.payment_id === p.id;

                  return (
                    <tr key={p.id} className="hover:bg-slate-50/70 transition-colors">
                      <td className="px-6 py-4 font-medium text-foreground whitespace-nowrap">
                        {PAYMENT_TYPE_LABELS[p.payment_type as PaymentType] ?? p.payment_type}
                      </td>
                      <td className="px-6 py-4 font-black text-foreground whitespace-nowrap">
                        {formatCve(p.amount_cve)}
                      </td>
                      <td className="px-6 py-4 text-muted-foreground text-xs whitespace-nowrap">
                        {formatDate(p.due_date)}
                      </td>
                      <td className="px-6 py-4 font-mono text-xs text-muted-foreground">
                        {p.reference || <span className="opacity-40">—</span>}
                      </td>
                      <td className="px-6 py-4">
                        <PaymentStatusBadge status={p.status} dueDate={p.due_date} />
                      </td>
                      <td className="px-6 py-4">
                        {p.status !== "PAID" && (
                          <button
                            onClick={() => markPaid.mutate({ payment_id: p.id })}
                            disabled={isMarking}
                            className="text-xs border border-primary/30 text-primary rounded-lg px-3 py-1.5 hover:bg-primary/10 transition-colors disabled:opacity-60 whitespace-nowrap"
                          >
                            {isMarking ? "A processar…" : "Marcar como Pago"}
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
