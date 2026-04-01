"use client";

import { useQuery } from "@tanstack/react-query";
import apiClient from "@/lib/api-client";
import { useAuth } from "@/contexts/AuthContext";
import { Skeleton } from "@/components/ui/Skeleton";
import { Download, FileText } from "lucide-react";

interface Document {
  contract_number: string;
  unit_code: string;
  status: string;
  pdf_s3_key: string;
  signed_at: string | null;
}

export default function InvestorDocuments() {
  const { isAuthenticated } = useAuth();

  const { data: docs, isLoading } = useQuery<Document[]>({
    queryKey: ["investor-documents"],
    queryFn: () =>
      apiClient.get<Document[]>("/investors/portal/my_documents/").then((r) => r.data),
    enabled: isAuthenticated,
  });

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-48" />
        {[0, 1, 2].map((i) => <Skeleton key={i} className="h-16 rounded-xl" />)}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-foreground">Documentos</h1>

      {!docs || docs.length === 0 ? (
        <div className="bg-white rounded-xl border border-border px-6 py-12 text-center">
          <FileText className="h-10 w-10 text-muted-foreground mx-auto mb-3" />
          <p className="text-muted-foreground text-sm">Nenhum documento disponível.</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-border divide-y divide-border">
          {docs.map((doc) => (
            <div
              key={doc.pdf_s3_key}
              className="flex items-center justify-between px-6 py-4"
            >
              <div className="flex items-center gap-4">
                <FileText className="h-5 w-5 text-primary shrink-0" />
                <div>
                  <p className="font-medium text-sm">{doc.contract_number}</p>
                  <p className="text-xs text-muted-foreground">
                    Unidade: {doc.unit_code}
                    {doc.signed_at
                      ? ` · Assinado em ${new Date(doc.signed_at).toLocaleDateString("pt-CV")}`
                      : ""}
                  </p>
                </div>
              </div>
              {/* In production, generate a pre-signed URL via a dedicated endpoint. */}
              <button
                className="flex items-center gap-2 text-sm text-primary hover:underline"
                onClick={() => alert(`S3 key: ${doc.pdf_s3_key}`)}
              >
                <Download className="h-4 w-4" />
                Descarregar
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
