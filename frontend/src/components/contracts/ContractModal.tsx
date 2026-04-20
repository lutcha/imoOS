import { useState } from "react";
import { X, Loader2 } from "lucide-react";
import { useTenant } from "@/contexts/TenantContext";
import { useCreateContract } from "@/hooks/useContracts";
import { useLeads } from "@/hooks/useLeads";
import { useUnits } from "@/hooks/useUnits";

interface ContractModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ContractModal({ isOpen, onClose }: ContractModalProps) {
  const { schema } = useTenant();
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const [formData, setFormData] = useState({
    unit: "",
    lead: "",
    total_price_cve: "",
    signed_at: "",
    notes: "",
  });

  const { data: leadsData } = useLeads({ page_size: 100 });
  const { data: unitsData } = useUnits({ status: "AVAILABLE", page_size: 100 });

  const createMutation = useCreateContract();

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg("");
    setLoading(true);

    try {
      await createMutation.mutateAsync({
        unit: formData.unit,
        lead: formData.lead,
        total_price_cve: formData.total_price_cve,
        signed_at: formData.signed_at || null,
        notes: formData.notes,
      } as any);
      
      onClose();
      // Reset form
      setFormData({
        unit: "",
        lead: "",
        total_price_cve: "",
        signed_at: "",
        notes: "",
      });
    } catch (err: any) {
      console.error("Failed to create contract", err);
      setErrorMsg(
        err.response?.data?.detail || 
        "Erro ao criar contrato. Verifique se a unidade ainda está disponível."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-0">
      <div 
        className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" 
        onClick={onClose} 
      />
      <div className="relative bg-white w-full max-w-lg rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        <div className="border-b border-slate-100 px-6 py-4 flex items-center justify-between bg-slate-50/50">
          <div className="flex flex-col">
            <h2 className="text-xl font-bold text-slate-800">Novo Contrato</h2>
            <p className="text-xs text-slate-500 font-medium">Formalize uma venda criando um novo contrato</p>
          </div>
          <button 
            onClick={onClose}
            className="p-2 -mr-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-full transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <form className="p-6 space-y-5" onSubmit={handleSubmit}>
          {errorMsg && (
            <div className="bg-red-50 text-red-600 px-4 py-3 rounded-lg text-sm font-medium border border-red-100">
              {errorMsg}
            </div>
          )}

          <div className="space-y-1.5 text-left">
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Cliente (Lead) *</label>
            <select 
              required
              value={formData.lead}
              onChange={e => setFormData({...formData, lead: e.target.value})}
              className="w-full bg-slate-50 border border-slate-200 px-4 py-2.5 rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none appearance-none font-medium"
            >
              <option value="">Seleccione um cliente...</option>
              {leadsData?.results.map(lead => (
                <option key={lead.id} value={lead.id}>
                  {lead.first_name} {lead.last_name} ({lead.email || lead.phone})
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-1.5 text-left">
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Unidade *</label>
            <select 
              required
              value={formData.unit}
              onChange={e => setFormData({...formData, unit: e.target.value})}
              className="w-full bg-slate-50 border border-slate-200 px-4 py-2.5 rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none appearance-none font-medium"
            >
              <option value="">Seleccione uma unidade disponível...</option>
              {unitsData?.results.map(unit => (
                <option key={unit.id} value={unit.id}>
                  {unit.code} - {unit.description || 'Sem descrição'} ({unit.area_bruta}m²)
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-5">
            <div className="space-y-1.5 text-left">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Preço de Venda (CVE) *</label>
              <input 
                required
                type="number" 
                value={formData.total_price_cve}
                onChange={e => setFormData({...formData, total_price_cve: e.target.value})}
                className="w-full bg-slate-50 border border-slate-200 px-4 py-2.5 rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none"
                placeholder="0.00"
              />
            </div>
            <div className="space-y-1.5 text-left">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Data de Assinatura</label>
              <input 
                type="date" 
                value={formData.signed_at}
                onChange={e => setFormData({...formData, signed_at: e.target.value})}
                className="w-full bg-slate-50 border border-slate-200 px-4 py-2.5 rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none"
              />
            </div>
          </div>

          <div className="space-y-1.5 text-left">
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Observações / Condições</label>
            <textarea 
              rows={3}
              value={formData.notes}
              onChange={e => setFormData({...formData, notes: e.target.value})}
              className="w-full bg-slate-50 border border-slate-200 px-4 py-3 rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none resize-none"
              placeholder="Detalhes adicionais, condições de pagamento..."
            />
          </div>

          <div className="pt-2 flex justify-end space-x-3">
            <button 
              type="button" 
              onClick={onClose}
              disabled={loading}
              className="px-5 py-2.5 rounded-xl text-sm font-bold text-slate-600 hover:bg-slate-100 transition-colors"
            >
              Cancelar
            </button>
            <button 
              type="submit" 
              disabled={loading}
              className="flex items-center space-x-2 px-6 py-2.5 rounded-xl text-sm font-bold text-white bg-primary hover:bg-primary/90 transition-colors shadow-lg shadow-primary/20 disabled:opacity-70"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>A Guardar...</span>
                </>
              ) : (
                <span>Criar Contrato</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
