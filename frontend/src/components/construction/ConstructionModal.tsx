import { useState } from "react";
import { X, Loader2 } from "lucide-react";
import { useTenant } from "@/contexts/TenantContext";
import { useCreateConstructionProject, ConstructionProject } from "@/hooks/useConstructionStats";

interface ConstructionModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ConstructionModal({ isOpen, onClose }: ConstructionModalProps) {
  const { schema } = useTenant();
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const [formData, setFormData] = useState({
    name: "",
    description: "",
    status: "PLANNING" as ConstructionProject["status"],
    start_date: "",
    expected_end_date: "",
    budget_cve: "",
    manager_name: "",
  });

  const createMutation = useCreateConstructionProject();

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg("");
    setLoading(true);

    try {
      await createMutation.mutateAsync({
        name: formData.name,
        description: formData.description,
        status: formData.status,
        start_date: formData.start_date || null,
        expected_end_date: formData.expected_end_date || null,
        budget_cve: formData.budget_cve || null,
        manager_name: formData.manager_name || null,
      });
      
      onClose();
      // Reset form
      setFormData({
        name: "",
        description: "",
        status: "PLANNING",
        start_date: "",
        expected_end_date: "",
        budget_cve: "",
        manager_name: "",
      });
    } catch (err: any) {
      console.error("Failed to create construction project", err);
      setErrorMsg(
        err.response?.data?.detail || 
        "Erro ao criar projecto de construção. Tente novamente."
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
      <div className="relative bg-white w-full max-w-2xl rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        <div className="border-b border-slate-100 px-6 py-4 flex items-center justify-between bg-slate-50/50">
          <div className="flex flex-col">
            <h2 className="text-xl font-bold text-slate-800">Nova Obra</h2>
            <p className="text-xs text-slate-500 font-medium">Inicie o acompanhamento de uma nova fase de construção</p>
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
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Nome da Obra *</label>
            <input 
              required
              type="text" 
              value={formData.name}
              onChange={e => setFormData({...formData, name: e.target.value})}
              className="w-full bg-slate-50 border border-slate-200 px-4 py-2.5 rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none"
              placeholder="Ex: Fundações Bloco A - Ocean View"
            />
          </div>

          <div className="grid grid-cols-2 gap-5">
            <div className="space-y-1.5 text-left">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Estado Inicial</label>
              <select 
                value={formData.status}
                onChange={e => setFormData({...formData, status: e.target.value as any})}
                className="w-full bg-slate-50 border border-slate-200 px-4 py-2.5 rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none appearance-none font-medium"
              >
                <option value="PLANNING">Planeamento</option>
                <option value="ACTIVE">Activo / Em Curso</option>
                <option value="ON_HOLD">Em Pausa</option>
              </select>
            </div>
            <div className="space-y-1.5 text-left">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Responsável / Gestor</label>
              <input 
                type="text" 
                value={formData.manager_name}
                onChange={e => setFormData({...formData, manager_name: e.target.value})}
                className="w-full bg-slate-50 border border-slate-200 px-4 py-2.5 rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none"
                placeholder="Nome do engenheiro/mestre"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-5">
            <div className="space-y-1.5 text-left">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Data de Início</label>
              <input 
                type="date" 
                value={formData.start_date}
                onChange={e => setFormData({...formData, start_date: e.target.value})}
                className="w-full bg-slate-50 border border-slate-200 px-4 py-2.5 rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none"
              />
            </div>
            <div className="space-y-1.5 text-left">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Previsão de Conclusão</label>
              <input 
                type="date" 
                value={formData.expected_end_date}
                onChange={e => setFormData({...formData, expected_end_date: e.target.value})}
                className="w-full bg-slate-50 border border-slate-200 px-4 py-2.5 rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none"
              />
            </div>
          </div>

          <div className="space-y-1.5 text-left">
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Orçamento Estimado (CVE)</label>
            <input 
              type="number" 
              value={formData.budget_cve}
              onChange={e => setFormData({...formData, budget_cve: e.target.value})}
              className="w-full bg-slate-50 border border-slate-200 px-4 py-2.5 rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none"
              placeholder="0.00"
            />
          </div>

          <div className="space-y-1.5 text-left">
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Objectivos / Notas</label>
            <textarea 
              rows={3}
              value={formData.description}
              onChange={e => setFormData({...formData, description: e.target.value})}
              className="w-full bg-slate-50 border border-slate-200 px-4 py-3 rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none resize-none"
              placeholder="Detalhes sobre esta obra..."
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
                <span>Criar Obra</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
