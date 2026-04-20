import { useState } from "react";
import { X, Loader2 } from "lucide-react";
import { useTenant } from "@/contexts/TenantContext";
import { useCreateProject, ProjectStatus } from "@/hooks/useProjects";

interface ProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ProjectModal({ isOpen, onClose }: ProjectModalProps) {
  const { schema } = useTenant();
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const [formData, setFormData] = useState({
    name: "",
    code: "", // internal code/slug hint
    status: "PLANNING" as ProjectStatus,
    description: "",
    address: "",
    city: "",
    island: "Santiago",
    total_area: "",
    expected_delivery_date: "",
  });

  const createMutation = useCreateProject();

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg("");
    setLoading(true);

    try {
      await createMutation.mutateAsync({
        name: formData.name,
        status: formData.status,
        description: formData.description,
        address: formData.address,
        city: formData.city,
        island: formData.island,
        total_area: formData.total_area ? parseFloat(formData.total_area) : null,
        expected_delivery_date: formData.expected_delivery_date || null,
      } as any);
      
      onClose();
      // Reset form
      setFormData({
        name: "",
        code: "",
        status: "PLANNING",
        description: "",
        address: "",
        city: "",
        island: "Santiago",
        total_area: "",
        expected_delivery_date: "",
      });
    } catch (err: any) {
      console.error("Failed to create project", err);
      setErrorMsg(
        err.response?.data?.detail || 
        err.response?.data?.name?.[0] ||
        "Erro ao criar projecto. Verifique os dados e tente novamente."
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
            <h2 className="text-xl font-bold text-slate-800">Novo Projecto</h2>
            <p className="text-xs text-slate-500 font-medium">Registe um novo empreendimento imobiliário</p>
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

          <div className="grid grid-cols-2 gap-5">
            <div className="col-span-2 space-y-1.5 text-left">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Nome do Projecto *</label>
              <input 
                required
                type="text" 
                value={formData.name}
                onChange={e => setFormData({...formData, name: e.target.value})}
                className="w-full bg-slate-50 border border-slate-200 px-4 py-2.5 rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none"
                placeholder="Ex: Edifício Ocean View"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-5">
            <div className="space-y-1.5 text-left">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Fase Atual</label>
              <select 
                value={formData.status}
                onChange={e => setFormData({...formData, status: e.target.value as ProjectStatus})}
                className="w-full bg-slate-50 border border-slate-200 px-4 py-2.5 rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none appearance-none font-medium"
              >
                <option value="PLANNING">Planeamento</option>
                <option value="LICENSING">Licenciamento</option>
                <option value="CONSTRUCTION">Em Construção</option>
                <option value="COMPLETED">Concluído</option>
              </select>
            </div>
            <div className="space-y-1.5 text-left">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Entrega Prevista</label>
              <input 
                type="date" 
                value={formData.expected_delivery_date}
                onChange={e => setFormData({...formData, expected_delivery_date: e.target.value})}
                className="w-full bg-slate-50 border border-slate-200 px-4 py-2.5 rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none"
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-5">
            <div className="space-y-1.5 text-left">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Ilha</label>
              <select 
                value={formData.island}
                onChange={e => setFormData({...formData, island: e.target.value})}
                className="w-full bg-slate-50 border border-slate-200 px-4 py-2.5 rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none appearance-none font-medium"
              >
                <option value="Santiago">Santiago</option>
                <option value="São Vicente">São Vicente</option>
                <option value="Sal">Sal</option>
                <option value="Boa Vista">Boa Vista</option>
                <option value="Fogo">Fogo</option>
                <option value="Maio">Maio</option>
                <option value="Santo Antão">Santo Antão</option>
                <option value="São Nicolau">São Nicolau</option>
                <option value="Brava">Brava</option>
              </select>
            </div>
            <div className="space-y-1.5 text-left">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Cidade</label>
              <input 
                type="text" 
                value={formData.city}
                onChange={e => setFormData({...formData, city: e.target.value})}
                className="w-full bg-slate-50 border border-slate-200 px-4 py-2.5 rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none"
                placeholder="Ex: Praia"
              />
            </div>
            <div className="space-y-1.5 text-left">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Área Total (m²)</label>
              <input 
                type="number" 
                value={formData.total_area}
                onChange={e => setFormData({...formData, total_area: e.target.value})}
                className="w-full bg-slate-50 border border-slate-200 px-4 py-2.5 rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none"
                placeholder="0.00"
              />
            </div>
          </div>

          <div className="space-y-1.5 text-left">
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Endereço / Localização</label>
            <input 
              type="text" 
              value={formData.address}
              onChange={e => setFormData({...formData, address: e.target.value})}
              className="w-full bg-slate-50 border border-slate-200 px-4 py-2.5 rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none"
              placeholder="Ex: Palmarejo Baixo, Rua X"
            />
          </div>

          <div className="space-y-1.5 text-left">
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Descrição</label>
            <textarea 
              rows={3}
              value={formData.description}
              onChange={e => setFormData({...formData, description: e.target.value})}
              className="w-full bg-slate-50 border border-slate-200 px-4 py-3 rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none resize-none"
              placeholder="Breve descrição do empreendimento..."
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
                <span>Criar Projecto</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
