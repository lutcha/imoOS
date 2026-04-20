import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import apiClient from "@/lib/api-client";
import { useTenant } from "@/contexts/TenantContext";
import { toast } from "sonner";

export interface SignatureRequest {
  id: string;
  contract: string;
  token: string;
  status: "PENDING" | "SIGNED" | "EXPIRED";
  expires_at: string;
  signed_at: string | null;
  signature_image_s3_key: string | null;
  created_at: string;
}

export function useRequestSignature() {
  const qc = useQueryClient();
  const { schema } = useTenant();

  return useMutation({
    mutationFn: (contractId: string) =>
      apiClient
        .post<SignatureRequest>(`/contracts/contracts/${contractId}/request_signature/`)
        .then((r) => r.data),
    onSuccess: (_, contractId) => {
      toast.success("Pedido de assinatura enviado via WhatsApp!");
      qc.invalidateQueries({ queryKey: ["contracts", schema, "detail", contractId] });
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Erro ao solicitar assinatura.");
    }
  });
}

/**
 * Public hook to fetch signature detail by token
 */
export function useSignatureDetail(token: string) {
  return useQuery({
    queryKey: ["public-signature", token],
    queryFn: () =>
      apiClient
        .get(`/contracts/signatures/public_detail/?token=${token}`)
        .then((r) => r.data),
    enabled: !!token,
    retry: false,
  });
}

/**
 * Public hook to submit signature
 */
export function useSubmitSignature() {
  return useMutation({
    mutationFn: ({ token, fullName, signatureBase64 }: { token: string; fullName: string; signatureBase64: string }) =>
      apiClient
        .post(`/contracts/signatures/public_sign/`, {
          token,
          full_name: fullName,
          signature_base64: signatureBase64,
        })
        .then((r) => r.data),
    onSuccess: () => {
      toast.success("Documento assinado com sucesso!");
    },
    onError: (err: any) => {
        toast.error(err.response?.data?.detail || "Erro ao submeter assinatura.");
    }
  });
}
