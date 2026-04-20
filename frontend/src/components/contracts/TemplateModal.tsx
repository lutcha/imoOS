import { useState, useEffect } from "react";
import { X, Loader2, Info, Copy, Check } from "lucide-react";
import { useCreateContractTemplate } from "@/hooks/useContractSettings";
import { toast } from "sonner";

interface TemplateModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialData?: any;
}

const TEMPLATE_VARIABLES = [
  { name: "lead_name", desc: "Nome completo do cliente" },
  { name: "contract_number", desc: "Número do contrato (ex: CNT-2024-001)" },
  { name: "total_price_cve", desc: "Valor total da venda em CVE" },
  { name: "unit_code", desc: "Código da unidade (ex: B-101)" },
  { name: "payment_schedule_table", desc: "Tabela completa de tranches e pagamentos" },
];

export function TemplateModal({ isOpen, onClose, initialData }: TemplateModalProps) {
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [copiedVar, setCopiedVar] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    name: "",
    description: "",
    content: "",
    is_active: true,
  });

  const createMutation = useCreateContractTemplate();

  useEffect(() => {
    if (initialData) {
      setFormData({
        name: initialData.name || "",
        description: initialData.description || "",
        content: initialData.content || "",
        is_active: initialData.is_active ?? true,
      });
    } else {
      setFormData({
        name: "",
        description: "",
        content: "",
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
        // Update logic would go here if hook supported it
        // For now focusing on creation as requested
      } else {
        await createMutation.mutateAsync(formData);
        toast.success("Template criado com sucesso!");
      }
      onClose();
    } catch (err: any) {
      console.error("Failed to save template", err);
      setErrorMsg(err.response?.data?.detail || "Erro ao guardar template.");
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    const formatted = `{{ ${text} }}`;
    navigator.clipboard.writeText(formatted);
    setCopiedVar(text);
    setTimeout(() => setCopiedVar(null), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-slate-900/60 backdrop-blur-md" onClick={onClose} />
      <div className="relative bg-white w-full max-w-5xl h-[85vh] rounded-3xl shadow-2xl flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="border-b border-slate-100 px-8 py-5 flex items-center justify-between bg-white shrink-0">
          <div>
            <h2 className="text-xl font-bold text-slate-900">
              {initialData ? "Editar Template" : "Novo Template de Contracto"}
            </h2>
            <p className="text-xs text-muted-foreground font-medium mt-0.5">
              Defina a estrutura HTML e use variáveis dinâmicas para automação.
            </p>
          </div>
          <button 
            onClick={onClose}
            className="p-2 -mr-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-full transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="flex flex-1 min-h-0 overflow-hidden">
          {/* Main Form */}
          <form className="flex-1 overflow-y-auto p-8 flex flex-col gap-6" onSubmit={handleSubmit}>
            {errorMsg && (
              <div className="bg-red-50 text-red-600 px-4 py-3 rounded-xl text-sm font-bold border border-red-100 flex items-center gap-2">
                <Info className="h-4 w-4" />
                {errorMsg}
              </div>
            )}

            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-1.5">
                <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Nome do Template *</label>
                <input 
                  required
                  type="text" 
                  value={formData.name}
                  onChange={e => setFormData({...formData, name: e.target.value})}
                  className="w-full bg-slate-50 border border-slate-200 px-4 py-2.5 rounded-xl text-sm focus:bg-white focus:ring-4 focus:ring-primary/5 focus:border-primary transition-all outline-none font-bold"
                  placeholder="ex: Contrato de Promessa de Compra e Venda"
                />
              </div>
              <div className="space-y-1.5 flex flex-col justify-center">
                 <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2 flex items-center gap-2">
                    Estado
                 </label>
                 <div className="flex items-center gap-3">
                    <button
                        type="button"
                        onClick={() => setFormData({...formData, is_active: !formData.is_active})}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${formData.is_active ? 'bg-primary' : 'bg-slate-300'}`}
                    >
                        <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${formData.is_active ? 'translate-x-6' : 'translate-x-1'}`} />
                    </button>
                    <span className="text-sm font-bold text-slate-700">
                        {formData.is_active ? 'Activo' : 'Inactivo'}
                    </span>
                 </div>
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Descrição curta</label>
              <input 
                type="text" 
                value={formData.description}
                onChange={e => setFormData({...formData, description: e.target.value})}
                className="w-full bg-slate-50 border border-slate-200 px-4 py-2.5 rounded-xl text-sm focus:bg-white focus:ring-4 focus:ring-primary/5 focus:border-primary transition-all outline-none"
                placeholder="Indique para que situações este template é usado..."
              />
            </div>

            <div className="flex-1 flex flex-col min-h-0 space-y-1.5">
              <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest flex items-center justify-between">
                Conteúdo HTML
                <span className="bg-slate-100 px-2 py-0.5 rounded text-[9px]">Suporta Markdown e HTML</span>
              </label>
              <textarea 
                required
                value={formData.content}
                onChange={e => setFormData({...formData, content: e.target.value})}
                className="flex-1 w-full bg-slate-50 border border-slate-200 px-5 py-4 rounded-2xl text-sm font-mono focus:bg-white focus:ring-4 focus:ring-primary/5 focus:border-primary transition-all outline-none resize-none leading-relaxed"
                placeholder="<h1>Contrato de Compra e Venda</h1><p>Entre o proprietário e {{ lead_name }}...</p>"
              />
            </div>

            <div className="flex justify-end gap-3 pt-2">
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
                {initialData ? "Guardar Alterações" : "Criar Template"}
              </button>
            </div>
          </form>

          {/* Variables Sidebar */}
          <div className="w-80 border-l border-slate-100 bg-slate-50/50 p-8 overflow-y-auto">
            <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest mb-6">Variáveis Disponíveis</h3>
            <div className="space-y-4">
              {TEMPLATE_VARIABLES.map(v => (
                <div 
                  key={v.name} 
                  className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm group hover:border-primary/50 transition-all cursor-pointer"
                  onClick={() => copyToClipboard(v.name)}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <code className="text-xs font-black text-primary bg-primary/5 px-2 py-0.5 rounded-lg flex items-center gap-1.5">
                      {v.name}
                    </code>
                    {copiedVar === v.name ? (
                      <Check className="h-3 w-3 text-emerald-500" />
                    ) : (
                      <Copy className="h-3 w-3 text-slate-300 group-hover:text-primary transition-colors" />
                    )}
                  </div>
                  <p className="text-[11px] text-slate-500 font-medium leading-relaxed">
                    {v.desc}
                  </p>
                </div>
              ))}
            </div>

            <div className="mt-8 p-4 bg-orange-50 rounded-2xl border border-orange-100">
               <div className="flex items-center gap-2 text-orange-600 mb-2">
                 <Info className="h-4 w-4" />
                 <span className="text-[10px] font-black uppercase">Dica</span>
               </div>
               <p className="text-[10px] text-orange-700 leading-relaxed font-medium">
                 Use as variáveis entre chavetas duplas. Exemplo: <br/> 
                 <code className="bg-orange-100 px-1 rounded">{"{{ lead_name }}"}</code>
               </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
