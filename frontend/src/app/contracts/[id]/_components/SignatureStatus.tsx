"use client";

import { useMemo } from "react";
import { CheckCircle2, Clock, XCircle, AlertCircle, History, ExternalLink } from "lucide-react";
import { cn } from "@/lib/utils";
import { formatDate } from "@/lib/format";

interface SignatureRequest {
  id: string;
  token: string;
  expires_at: string;
  signed_at: string | null;
  signed_by_name: string;
  status: 'PENDING' | 'SIGNED' | 'EXPIRED' | 'CANCELLED';
  created_at: string;
}

interface SignatureStatusProps {
  requests: SignatureRequest[];
}

const STATUS_CONFIG = {
  PENDING: { label: "Pendente", icon: Clock, className: "text-amber-600 bg-amber-50 border-amber-100" },
  SIGNED: { label: "Assinado", icon: CheckCircle2, className: "text-emerald-600 bg-emerald-50 border-emerald-100" },
  EXPIRED: { label: "Expirado", icon: AlertCircle, className: "text-slate-500 bg-slate-50 border-slate-100" },
  CANCELLED: { label: "Cancelado", icon: XCircle, className: "text-red-600 bg-red-50 border-red-100" },
};

export function SignatureStatus({ requests }: SignatureStatusProps) {
  const latestRequest = requests[0];

  if (!requests.length) return null;

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
      <h3 className="text-sm font-bold text-foreground mb-4 flex items-center gap-2">
        <History className="h-4 w-4 text-slate-400" />
        Estado das Assinaturas
      </h3>

      <div className="space-y-4">
        {/* Latest Request Card */}
        {latestRequest && (
          <div className={cn(
            "p-4 rounded-xl border flex flex-col gap-3",
            STATUS_CONFIG[latestRequest.status].className
          )}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {(() => {
                  const Icon = STATUS_CONFIG[latestRequest.status].icon;
                  return <Icon className="h-4 w-4" />;
                })()}
                <span className="text-xs font-black uppercase tracking-tight">
                  {STATUS_CONFIG[latestRequest.status].label}
                </span>
              </div>
              <span className="text-[10px] font-medium opacity-70">
                {formatDate(latestRequest.created_at)}
              </span>
            </div>

            {latestRequest.status === 'SIGNED' ? (
              <div className="space-y-1">
                <p className="text-[11px] font-bold">Assinado por: {latestRequest.signed_by_name}</p>
                <p className="text-[10px] opacity-80">Em {formatDate(latestRequest.signed_at!)}</p>
              </div>
            ) : latestRequest.status === 'PENDING' ? (
              <div className="flex flex-col gap-1">
                 <p className="text-[11px] font-bold">Link enviado via WhatsApp</p>
                 <p className="text-[10px] opacity-80 flex items-center gap-1">
                    Expira em {formatDate(latestRequest.expires_at)}
                 </p>
                 <a 
                    href={`/sign/${latestRequest.token}`} 
                    target="_blank" 
                    className="mt-2 flex items-center justify-center gap-1.5 py-1.5 bg-white/50 border border-current/20 rounded-lg text-[10px] font-black hover:bg-white/80 transition-all"
                 >
                    Ver Portal <ExternalLink className="h-3 w-3" />
                 </a>
              </div>
            ) : null}
          </div>
        )}

        {/* History List (if more than 1) */}
        {requests.length > 1 && (
          <div className="space-y-2">
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest pl-1">Histórico</p>
            {requests.slice(1, 3).map((req) => (
              <div key={req.id} className="flex items-center justify-between p-2 rounded-lg bg-slate-50 border border-slate-100 italic">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-bold text-slate-600">{STATUS_CONFIG[req.status].label}</span>
                </div>
                <span className="text-[10px] text-slate-400">{formatDate(req.created_at)}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
