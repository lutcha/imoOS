import { useState, useEffect } from "react";
import { X, Loader2 } from "lucide-react";
import { useTenant } from "@/contexts/TenantContext";
import { useCreateUnit, useUnitTypes } from "@/hooks/useUnits";
import { useProjects } from "@/hooks/useProjects";
import { useBuildings, useFloors } from "@/hooks/useBuildings";

interface UnitModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function UnitModal({ isOpen, onClose }: UnitModalProps) {
  const { schema } = useTenant();
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const [formData, setFormData] = useState({
    project: "",
    building: "",
    floor: "",
    unit_type: "",
    code: "",
    description: "",
    area_bruta: "",
    status: "AVAILABLE",
  });

  const { data: projectsData } = useProjects({ page_size: 100 });
  const { data: buildingsData } = useBuildings(formData.project);
  const { data: floorsData } = useFloors(formData.building);
  const { data: unitTypesData } = useUnitTypes();

  const createMutation = useCreateUnit();

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg("");
    setLoading(true);

    try {
      await createMutation.mutateAsync({
        floor: formData.floor,
        unit_type: formData.unit_type,
        code: formData.code,
        description: formData.description,
        area_bruta: formData.area_bruta || "0.00",
        status: formData.status as any,
      } as any);
      
      onClose();
      // Reset form
      setFormData({
        project: "",
        building: "",
        floor: "",
        unit_type: "",
        code: "",
        description: "",
        area_bruta: "",
        status: "AVAILABLE",
      });
    } catch (err: any) {
      console.error("Failed to create unit", err);
      setErrorMsg(
        err.response?.data?.detail || 
        "Erro ao criar unidade. Verifique se o código é único."
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
            <h2 className="text-xl font-bold text-slate-800">Nova Unidade</h2>
            <p className="text-xs text-slate-500 font-medium">Adicione uma nova fracção ou lote ao inventário</p>
          </div>
          <button 
            onClick={onClose}
            className="p-2 -mr-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-full transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <form className="p-6 space-y-4" onSubmit={handleSubmit}>
          {errorMsg && (
            <div className="bg-red-50 text-red-600 px-4 py-3 rounded-lg text-sm font-medium border border-red-100">
              {errorMsg}
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5 text-left">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Projecto *</label>
              <select 
                required
                value={formData.project}
                onChange={e => setFormData({...formData, project: e.target.value, building: "", floor: ""})}
                className="w-full bg-slate-50 border border-slate-200 px-4 py-2 rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none appearance-none font-medium"
              >
                <option value="">Seleccione o projecto...</option>
                {projectsData?.results.map(proj => (
                  <option key={proj.id} value={proj.id}>{proj.properties.name}</option>
                ))}
              </select>
            </div>
            <div className="space-y-1.5 text-left">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Edifício *</label>
              <select 
                required
                disabled={!formData.project}
                value={formData.building}
                onChange={e => setFormData({...formData, building: e.target.value, floor: ""})}
                className="w-full bg-slate-50 border border-slate-200 px-4 py-2 rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none appearance-none font-medium disabled:opacity-50"
              >
                <option value="">Seleccione o edifício...</option>
                {buildingsData?.map(b => (
                  <option key={b.id} value={b.id}>{b.name}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5 text-left">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Piso *</label>
              <select 
                required
                disabled={!formData.building}
                value={formData.floor}
                onChange={e => setFormData({...formData, floor: e.target.value})}
                className="w-full bg-slate-50 border border-slate-200 px-4 py-2 rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none appearance-none font-medium disabled:opacity-50"
              >
                <option value="">Seleccione o piso...</option>
                {floorsData?.map(f => (
                  <option key={f.id} value={f.id}>{f.description} (Nível {f.level})</option>
                ))}
              </select>
            </div>
            <div className="space-y-1.5 text-left">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Tipologia *</label>
              <select 
                required
                value={formData.unit_type}
                onChange={e => setFormData({...formData, unit_type: e.target.value})}
                className="w-full bg-slate-50 border border-slate-200 px-4 py-2 rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none appearance-none font-medium"
              >
                <option value="">Seleccione a tipologia...</option>
                {unitTypesData?.map(ut => (
                  <option key={ut.id} value={ut.id}>{ut.name} ({ut.code})</option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-1.5 text-left">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Código da Unidade *</label>
              <input 
                required
                type="text" 
                value={formData.code}
                onChange={e => setFormData({...formData, code: e.target.value})}
                className="w-full bg-slate-50 border border-slate-200 px-4 py-2 rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none"
                placeholder="Ex: A101"
              />
            </div>
            <div className="space-y-1.5 text-left">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Área Bruta (m²)</label>
              <input 
                type="number" 
                value={formData.area_bruta}
                onChange={e => setFormData({...formData, area_bruta: e.target.value})}
                className="w-full bg-slate-50 border border-slate-200 px-4 py-2 rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none"
                placeholder="0.00"
              />
            </div>
            <div className="space-y-1.5 text-left">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Estado</label>
              <select 
                value={formData.status}
                onChange={e => setFormData({...formData, status: e.target.value})}
                className="w-full bg-slate-50 border border-slate-200 px-4 py-2 rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none appearance-none font-medium"
              >
                <option value="AVAILABLE">Disponível</option>
                <option value="MAINTENANCE">Manutenção</option>
                <option value="RESERVED">Reservado</option>
              </select>
            </div>
          </div>

          <div className="space-y-1.5 text-left">
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Descrição Detalhada</label>
            <textarea 
              rows={2}
              value={formData.description}
              onChange={e => setFormData({...formData, description: e.target.value})}
              className="w-full bg-slate-50 border border-slate-200 px-4 py-2 rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none resize-none"
              placeholder="Ex: Apartamento com vista mar, varanda privativa..."
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
                <span>Criar Unidade</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
