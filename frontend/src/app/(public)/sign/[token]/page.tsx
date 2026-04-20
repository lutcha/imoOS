"use client";

import { use, useState, useRef, useEffect } from "react";
import dynamic from "next/dynamic";
import { 
  FileText, 
  CheckCircle2, 
  AlertCircle, 
  ChevronRight, 
  Eraser, 
  Lock, 
  Info,
  Calendar,
  Wallet,
  Building2,
  ChevronDown,
  Loader2
} from "lucide-react";
import { useSignatureDetail, useSubmitSignature } from "@/hooks/useSignatures";
import { formatCve, formatDate } from "@/lib/format";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";

// Dynamic import for SignatureCanvas to avoid SSR issues
const SignatureCanvas = dynamic(() => import("react-signature-canvas"), {
  ssr: false,
});

export default function PublicSignaturePage({
  params,
}: {
  params: Promise<{ token: string }>;
}) {
  const { token } = use(params);
  const { data: request, isLoading, isError, error } = useSignatureDetail(token);
  const submitSignature = useSubmitSignature();

  const [step, setStep] = useState(1);
  const [fullName, setFullName] = useState("");
  const sigPad = useRef<any>(null);
  const [hasSignature, setHasSignature] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  // Set lead name as default fullName when data loads
  useEffect(() => {
    if (request?.lead_name) {
      setFullName(request.lead_name);
    }
  }, [request]);

  const handleClear = () => {
    sigPad.current?.clear();
    setHasSignature(false);
  };

  const handleBeginSignature = () => {
     setHasSignature(true);
  };

  const handleSubmit = async () => {
    if (!fullName || !hasSignature) return;

    const signatureBase64 = sigPad.current?.getTrimmedCanvas().toDataURL("image/png");
    
    submitSignature.mutate(
      { token, fullName, signatureBase64 },
      {
        onSuccess: () => {
          setIsSuccess(true);
        },
      }
    );
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="h-8 w-8 text-primary animate-spin" />
          <p className="text-sm font-bold text-slate-500">A carregar contrato...</p>
        </div>
      </div>
    );
  }

  if (isError || isSuccess) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-md w-full bg-white rounded-3xl p-10 border border-slate-200 shadow-xl shadow-slate-200/50 text-center"
        >
          {isSuccess ? (
            <>
              <div className="h-20 w-20 rounded-full bg-emerald-100 flex items-center justify-center mx-auto mb-6">
                <CheckCircle2 className="h-10 w-10 text-emerald-600" />
              </div>
              <h1 className="text-2xl font-black text-slate-900 mb-2">Documento Assinado!</h1>
              <p className="text-slate-500 mb-8 leading-relaxed">
                O seu contrato foi processado e validado com sucesso. O vendedor será notificado e receberá uma cópia do documento nos próximos minutos.
              </p>
              <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100 flex flex-col gap-2">
                 <p className="text-[10px] uppercase font-bold text-slate-400 tracking-widest">Contrato n.º</p>
                 <p className="text-sm font-mono font-bold text-slate-700">{request?.contract_number}</p>
              </div>
            </>
          ) : (
            <>
              <div className="h-20 w-20 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-6">
                <AlertCircle className="h-10 w-10 text-red-600" />
              </div>
              <h1 className="text-2xl font-black text-slate-900 mb-2">Link Inválido</h1>
              <p className="text-slate-500 mb-8 leading-relaxed">
                {(error as any)?.response?.data?.detail || "Este link de assinatura expirou ou já foi validado anteriormente."}
              </p>
              <button 
                onClick={() => window.location.reload()}
                className="w-full py-4 bg-slate-900 text-white rounded-2xl font-bold hover:bg-slate-800 transition-all"
              >
                Tentar Novamente
              </button>
            </>
          )}
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans selection:bg-primary/10">
      {/* Premium Header */}
      <nav className="h-20 bg-white/80 backdrop-blur-md sticky top-0 z-50 border-b border-slate-200 flex items-center px-6 md:px-12 justify-between">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 bg-primary rounded-xl flex items-center justify-center shadow-lg shadow-primary/20">
            <Building2 className="h-5 w-5 text-white" />
          </div>
          <span className="text-xl font-black tracking-tighter">ImoOS <span className="text-primary">Sign</span></span>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 bg-slate-100 rounded-full border border-slate-200">
          <Lock className="h-3 w-3 text-slate-400" />
          <span className="text-[11px] font-bold text-slate-500 uppercase tracking-widest">Documento Seguro</span>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto py-12 px-6 grid grid-cols-1 lg:grid-cols-12 gap-10">
        
        {/* Left Column: Contract Info */}
        <div className="lg:col-span-4 space-y-6">
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm"
          >
            <div className="flex items-center gap-3 mb-6">
               <FileText className="h-6 w-6 text-primary" />
               <h2 className="text-lg font-black tracking-tight">Detalhes do Contrato</h2>
            </div>

            <div className="space-y-6">
              <div>
                <p className="text-[10px] uppercase font-bold text-slate-400 tracking-widest mb-1.5">Número do Contrato</p>
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-100 font-mono font-bold text-sm">
                  {request?.contract_number}
                </div>
              </div>

              <div className="grid grid-cols-1 gap-4">
                 {[
                   { label: "Unidade", value: request?.unit_code, icon: Building2 },
                   { label: "Comprador", value: request?.lead_name, icon: Info },
                   { label: "Valor Total", value: formatCve(request?.total_price_cve), icon: Wallet },
                   { label: "Expira em", value: formatDate(request?.expires_at), icon: Calendar },
                 ].map((item) => (
                   <div key={item.label} className="flex items-center gap-3 p-3 hover:bg-slate-50 rounded-xl transition-colors group">
                      <div className="h-10 w-10 bg-white rounded-2xl shadow-sm border border-slate-100 flex items-center justify-center group-hover:border-primary/20 transition-all">
                        <item.icon className="h-5 w-5 text-slate-400 group-hover:text-primary transition-colors" />
                      </div>
                      <div>
                        <p className="text-[10px] uppercase font-black text-slate-400 tracking-tight">{item.label}</p>
                        <p className="text-sm font-bold text-slate-700">{item.value}</p>
                      </div>
                   </div>
                 ))}
              </div>
            </div>

            <div className="mt-10 p-4 bg-amber-50 rounded-2xl border border-amber-100 flex gap-3 italic">
              <AlertCircle className="h-5 w-5 text-amber-600 shrink-0" />
              <p className="text-[11px] font-bold text-amber-800 leading-relaxed">
                Ao assinar este documento, o senhor(a) concorda com os termos comerciais descritos acima e com a activação imediata do contrato.
              </p>
            </div>
          </motion.div>
        </div>

        {/* Right Column: Signature Pad */}
        <div className="lg:col-span-8 flex flex-col gap-6">
          <AnimatePresence mode="wait">
            {step === 1 ? (
              <motion.div 
                key="step1"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 1.05 }}
                className="flex-1 bg-white rounded-3xl p-10 border border-slate-200 shadow-xl shadow-slate-200/50 flex flex-col items-center justify-center text-center"
              >
                <div className="h-20 w-20 rounded-full bg-primary/5 flex items-center justify-center mb-6">
                    <FileText className="h-10 w-10 text-primary" />
                </div>
                <h2 className="text-3xl font-black text-slate-900 mb-2">Preparado para Assinar?</h2>
                <p className="text-slate-500 max-w-sm mb-10 leading-relaxed">
                   Antes de prosseguir, por favor confirme se leu e concorda com todos os termos do contrato enviado.
                </p>
                <button 
                  onClick={() => setStep(2)}
                  className="px-12 py-5 bg-primary text-white rounded-2xl font-black text-lg shadow-xl shadow-primary/20 hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center gap-3"
                >
                  Confirmar e Assinar <ChevronRight className="h-6 w-6" />
                </button>
              </motion.div>
            ) : (
              <motion.div 
                key="step2"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex-1 bg-white rounded-3xl overflow-hidden border border-slate-200 shadow-xl shadow-slate-200/50 flex flex-col"
              >
                <div className="p-8 border-b border-slate-100 flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-black text-slate-900">Assinatura Digital</h2>
                    <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mt-0.5">Introduza o seu nome e desenhe a assinatura</p>
                  </div>
                  <button onClick={() => setStep(1)} className="text-xs font-bold text-slate-400 hover:text-slate-900 transition-colors underline underline-offset-4">
                    Voltar
                  </button>
                </div>

                <div className="p-8 flex-1 flex flex-col gap-8">
                  <div className="space-y-2">
                    <label className="text-xs font-black text-slate-500 uppercase ml-1">Nome Completo</label>
                    <input 
                      type="text" 
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      placeholder="Introduza o seu nome conforme o documento"
                      className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-6 py-4 text-sm font-bold focus:ring-4 focus:ring-primary/10 focus:border-primary outline-none transition-all placeholder:text-slate-300"
                    />
                  </div>

                  <div className="flex-1 flex flex-col gap-4">
                    <div className="flex items-center justify-between ml-1">
                      <label className="text-xs font-black text-slate-500 uppercase">Espaço para Assinatura</label>
                      <button 
                        onClick={handleClear}
                        className="flex items-center gap-1.5 text-[10px] font-black text-red-500 uppercase tracking-tight hover:underline"
                      >
                        <Eraser className="h-3.5 w-3.5" /> Limpar
                      </button>
                    </div>
                    <div className="flex-1 min-h-[300px] relative rounded-3xl border-2 border-dashed border-slate-200 bg-slate-50 group hover:bg-slate-100/50 transition-colors overflow-hidden">
                      <SignatureCanvas
                        ref={sigPad}
                        canvasProps={{ className: "w-full h-full cursor-crosshair absolute inset-0" }}
                        onBegin={handleBeginSignature}
                      />
                      {!hasSignature && (
                        <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
                          <p className="text-xs font-bold text-slate-300 uppercase tracking-widest flex items-center gap-2">
                            Desenhe aqui o seu visto <ChevronDown className="h-4 w-4 animate-bounce" />
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                <div className="p-8 bg-slate-50 border-t border-slate-100 flex items-center justify-between gap-6">
                   <div className="flex-1 flex items-center gap-3 text-slate-400">
                      <Lock className="h-5 w-5 opacity-50" />
                      <p className="text-[10px] font-medium max-w-[240px]">
                        Esta assinatura será encriptada e anexada ao contrato com validade jurídica digital.
                      </p>
                   </div>
                   <button 
                    disabled={!fullName || !hasSignature || submitSignature.isPending}
                    onClick={handleSubmit}
                    className="px-10 py-5 bg-slate-900 text-white rounded-2xl font-black text-sm shadow-xl shadow-slate-200 hover:bg-slate-800 disabled:opacity-30 disabled:hover:bg-slate-900 transition-all flex items-center justify-center gap-2 group min-w-[240px]"
                   >
                    {submitSignature.isPending ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <CheckCircle2 className="h-4 w-4 text-emerald-400 group-hover:scale-110 transition-transform" />
                    )}
                    Confirmar Assinatura Final
                   </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>

      {/* Subtle background deco */}
      <div className="fixed top-0 left-0 w-full h-full pointer-events-none opacity-[0.03] z-[-1]">
        <div className="absolute top-[-10%] right-[-10%] w-[50%] h-[50%] bg-primary rounded-full blur-[200px]" />
        <div className="absolute bottom-[-10%] left-[-10%] w-[50%] h-[50%] bg-primary/40 rounded-full blur-[200px]" />
      </div>
    </div>
  );
}
