import { useState, useEffect } from "react";
import { X, Loader2, CreditCard, Percent, CalendarDays } from "lucide-react";
import { useCreatePaymentPattern } from "@/hooks/useContractSettings";
import { toast } from "sonner";

interface PatternModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialData?: any;
}

export function PatternModal({ isOpen, onClose, initialData }: PatternModalProps) {
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const [formData, setFormData] = useState({
    name: "",
    description: "",
    down_payment_percentage: "20",
    down_payment_due_days: 7,
    installments_count: 12,
    installments_interval_days: 30,
    is_active: true,
  });

  const createMutation = useCreatePaymentPattern();

  useEffect(() => {
    if (initialData) {
      setFormData({
        name: initialData.name || "",
        description: initialData.description || "",
        down_payment_percentage: String(initialData.down_payment_percentage || "20"),
        down_payment_due_days: initialData.down_payment_due_days || 7,
        installments_count: initialData.installments_count || 12,
        installments_interval_days: initialData.installments_interval_days || 30,
        is_active: initialData.is_active ?? true,
      });
    } else {
      setFormData({
        name: "",
        description: "",
        down_payment_percentage: "20",
        down_payment_due_days: 7,
        installments_count: 12,
        installments_interval_days: 30,
        is_active: true,
      });
    }
  }, [initialData, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg("");
    setLoading(true);

    try {
      if (initialData?.id) {
        // Update logic
      } else {
        await createMutation.mutateAsync(formData as any);
        toast.success("Padrão de pagamento criado!");
      }
      onClose();
    } catch (err: any) {
      console.error("Failed to save pattern", err);
      setErrorMsg(err.response?.data?.detail || "Erro ao guardar padrão.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-slate-900/60 backdrop-blur-md" onClick={onClose} />
      <div className="relative bg-white w-full max-w-lg rounded-3xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="border-b border-slate-100 px-8 py-5 flex items-center justify-between bg-slate-50/50">
          <div>
            <h2 className="text-xl font-bold text-slate-900">
              {initialData ? "Configurar Padrão" : "Novo Padrão de Pagamento"}
            </h2>
            <p className="text-xs text-muted-foreground font-medium mt-0.5">
              Defina a estrutura padrão para as tranches dos seus contratos.
            </p>
          </div>
          <button 
            onClick={onClose}
            className="p-2 -mr-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-full transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <form className="p-8 space-y-6" onSubmit={handleSubmit}>
          {errorMsg && (
            <div className="bg-red-50 text-red-600 px-4 py-3 rounded-xl text-sm font-bold border border-red-100">
              {errorMsg}
            </div>
          )}

          <div className="space-y-1.5">
            <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Nome do Padrão *</label>
            <input 
              required
              type="text" 
              value={formData.name}
              onChange={e => setFormData({...formData, name: e.target.value})}
              className="w-full bg-slate-50 border border-slate-200 px-4 py-3 rounded-xl text-sm focus:bg-white focus:ring-4 focus:ring-primary/5 focus:border-primary transition-all outline-none font-bold"
              placeholder="ex: Plano Standard (20% + 24x)"
            />
          </div>

          <div className="grid grid-cols-2 gap-5">
            <div className="space-y-1.5">
              <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest flex items-center gap-1.5">
                <Percent className="h-3 w-3" /> Entrada (%) *
              </label>
              <input 
                required
                type="number" 
                value={formData.down_payment_percentage}
                onChange={e => setFormData({...formData, down_payment_percentage: e.target.value})}
                className="w-full bg-slate-50 border border-slate-200 px-4 py-3 rounded-xl text-sm focus:bg-white outline-none font-bold"
                placeholder="20"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest flex items-center gap-1.5">
                <CalendarDays className="h-3 w-3" /> Dias p/ Sinal *
              </label>
              <input 
                required
                type="number" 
                value={formData.down_payment_due_days}
                onChange={e => setFormData({...formData, down_payment_due_days: Number(e.target.value)})}
                className="w-full bg-slate-50 border border-slate-200 px-4 py-3 rounded-xl text-sm focus:bg-white outline-none font-bold"
                placeholder="7"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-5">
            <div className="space-y-1.5">
              <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest flex items-center gap-1.5">
                <CreditCard className="h-3 w-3" /> Nº Prestações *
              </label>
              <input 
                required
                type="number" 
                value={formData.installments_count}
                onChange={e => setFormData({...formData, installments_count: Number(e.target.value)})}
                className="w-full bg-slate-50 border border-slate-200 px-4 py-3 rounded-xl text-sm focus:bg-white outline-none font-bold"
                placeholder="24"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Intervalo (Dias) *</label>
              <input 
                required
                type="number" 
                value={formData.installments_interval_days}
                onChange={e => setFormData({...formData, installments_interval_days: Number(e.target.value)})}
                className="w-full bg-slate-50 border border-slate-200 px-4 py-3 rounded-xl text-sm focus:bg-white outline-none font-bold"
                placeholder="30"
              />
            </div>
          </div>

          <div className="space-y-1.5">
             <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Descrição</label>
             <textarea 
               value={formData.description}
               onChange={e => setFormData({...formData, description: e.target.value})}
               className="w-full bg-slate-50 border border-slate-200 px-4 py-2.5 rounded-xl text-sm focus:bg-white outline-none resize-none"
               rows={2}
               placeholder="Ex: Padrão recomendado para as moradias tipo A..."
             />
          </div>

          <div className="pt-4 flex justify-end gap-3">
            <button 
              type="button" 
              onClick={onClose}
              className="px-6 py-2.5 rounded-xl text-sm font-bold text-slate-500 hover:bg-slate-100 transition-colors"
            >
              Cancelar
            </button>
            <button 
              type="submit" 
              disabled={loading}
              className="flex items-center gap-2 px-8 py-2.5 rounded-xl text-sm font-black text-white bg-primary hover:bg-primary/90 transition-all shadow-xl shadow-primary/25 active:scale-95 disabled:opacity-70"
            >
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
              {initialData ? "Guardar Alterações" : "Criar Padrão"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
