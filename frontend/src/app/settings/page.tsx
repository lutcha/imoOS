"use client";

import { useState } from "react";
import {
    Palette,
    Settings2,
    Lock,
    Share2,
    Save,
    Upload,
    Check,
    AlertCircle
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useTenantSettings, useUpdateTenantSettings } from "@/hooks/useTenantSettings";
import { Skeleton } from "@/components/ui/Skeleton";

const TABS = [
    { id: "branding", label: "Branding", icon: Palette },
    { id: "crm", label: "CRM", icon: Settings2 },
    { id: "reservations", label: "Reservas", icon: Lock },
    { id: "integrations", label: "Integrações", icon: Share2 },
] as const;

type TabId = (typeof TABS)[number]["id"];

export default function SettingsPage() {
    const [activeTab, setActiveTab] = useState<TabId>("branding");
    const { data: settings, isLoading } = useTenantSettings();
    const updateSettings = useUpdateTenantSettings();

    const [isSuccess, setIsSuccess] = useState(false);

    const handleSave = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        const formData = new FormData(e.currentTarget);
        const data = Object.fromEntries(formData.entries());

        try {
            await updateSettings.mutateAsync(data);
            setIsSuccess(true);
            setTimeout(() => setIsSuccess(false), 3000);
        } catch (error) {
            console.error("Error updating settings:", error);
        }
    };

    if (isLoading) {
        return (
            <div className="space-y-6">
                <Skeleton className="h-10 w-48" />
                <div className="grid grid-cols-4 gap-4 h-12">
                    {Array.from({ length: 4 }).map((_, i) => (
                        <Skeleton key={i} className="h-full rounded-xl" />
                    ))}
                </div>
                <Skeleton className="h-[400px] w-full rounded-2xl" />
            </div>
        );
    }

    return (
        <div className="space-y-6 max-w-4xl">
            <div>
                <h1 className="text-3xl font-bold tracking-tight text-foreground">Definições</h1>
                <p className="text-muted-foreground mt-1 text-sm">Configure as preferências da sua instância ImoOS</p>
            </div>

            <div className="flex p-1 bg-muted rounded-xl border border-border w-fit">
                {TABS.map((tab) => {
                    const Icon = tab.icon;
                    return (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={cn(
                                "flex items-center px-4 py-2 rounded-lg text-xs font-bold transition-all whitespace-nowrap",
                                activeTab === tab.id
                                    ? "bg-white shadow-sm text-primary"
                                    : "text-muted-foreground hover:text-foreground"
                            )}
                        >
                            <Icon className="h-3.5 w-3.5 mr-2" />
                            {tab.label}
                        </button>
                    );
                })}
            </div>

            <form onSubmit={handleSave} className="rounded-2xl border border-border bg-white shadow-sm overflow-hidden">
                <div className="p-8 space-y-8">
                    {activeTab === "branding" && (
                        <div className="space-y-6 animate-in fade-in duration-300">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                <div className="space-y-4 text-sm">
                                    <label className="font-bold text-foreground">Nome da Empresa</label>
                                    <input
                                        name="name"
                                        defaultValue={settings?.name}
                                        className="w-full h-11 px-4 rounded-xl border border-border bg-slate-50 focus:bg-white focus:ring-2 focus:ring-primary/20 outline-none transition-all font-medium"
                                        placeholder="Ex: Imobiliária Mar Azul"
                                    />
                                </div>
                                <div className="space-y-4 text-sm">
                                    <label className="font-bold text-foreground">Subdomínio</label>
                                    <div className="relative">
                                        <input
                                            name="subdomain"
                                            defaultValue={settings?.subdomain}
                                            disabled
                                            className="w-full h-11 px-4 rounded-xl border border-border bg-slate-100 text-muted-foreground outline-none font-mono cursor-not-allowed"
                                        />
                                        <span className="absolute right-4 top-1/2 -translate-y-1/2 text-[10px] font-bold uppercase text-muted-foreground/50">Bloqueado</span>
                                    </div>
                                </div>
                            </div>

                            <div className="pt-6 border-t border-border grid grid-cols-1 md:grid-cols-2 gap-8">
                                <div className="space-y-4 text-sm">
                                    <label className="font-bold text-foreground">Cores da Interface</label>
                                    <div className="flex gap-4">
                                        <div className="flex-1 space-y-2">
                                            <span className="text-[10px] uppercase tracking-wider font-bold text-muted-foreground">Primária</span>
                                            <div className="flex items-center space-x-3 h-11 px-3 rounded-xl border border-border bg-slate-50">
                                                <input name="primary_color" type="color" defaultValue={settings?.primary_color || "#3b82f6"} className="h-6 w-6 rounded-md border-none bg-transparent cursor-pointer" />
                                                <span className="font-mono text-xs uppercase">{settings?.primary_color}</span>
                                            </div>
                                        </div>
                                        <div className="flex-1 space-y-2">
                                            <span className="text-[10px] uppercase tracking-wider font-bold text-muted-foreground">Secundária</span>
                                            <div className="flex items-center space-x-3 h-11 px-3 rounded-xl border border-border bg-slate-50">
                                                <input name="secondary_color" type="color" defaultValue={settings?.secondary_color || "#1e293b"} className="h-6 w-6 rounded-md border-none bg-transparent cursor-pointer" />
                                                <span className="font-mono text-xs uppercase">{settings?.secondary_color}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div className="space-y-4 text-sm">
                                    <label className="font-bold text-foreground">Logo da Empresa</label>
                                    <div className="flex items-center space-x-5">
                                        <div className="h-16 w-16 rounded-2xl border-2 border-dashed border-border flex items-center justify-center bg-slate-50/50 hover:bg-slate-100/50 transition-colors cursor-pointer group">
                                            <Upload className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
                                        </div>
                                        <div className="text-[11px] text-muted-foreground space-y-1">
                                            <p className="font-bold text-foreground/70">SVG, PNG ou JPG</p>
                                            <p>Recomendado: 512x512px</p>
                                            <p>Tamanho máx: 2MB</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === "crm" && (
                        <div className="space-y-6 animate-in fade-in duration-300">
                            <div className="bg-slate-50 rounded-2xl p-6 border border-border flex items-start space-x-4">
                                <AlertCircle className="h-5 w-5 text-primary mt-0.5 shrink-0" />
                                <div className="space-y-1">
                                    <p className="text-sm font-bold text-foreground">Configuração de Etapas do Pipeline</p>
                                    <p className="text-xs text-muted-foreground">As 7 etapas configuradas (Novo → Contactado → ... → Ganho/Perdido) são as recomendadas para o padrão Cape Verde Real Estate.</p>
                                </div>
                            </div>
                            <p className="text-sm text-muted-foreground italic">Opções avançadas de automação de CRM disponíveis em breve.</p>
                        </div>
                    )}

                    {activeTab === "reservations" && (
                        <div className="space-y-6 animate-in fade-in duration-300">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                <div className="space-y-4 text-sm">
                                    <label className="font-bold text-foreground">Tempo de Bloqueio (Auto-Release)</label>
                                    <div className="relative">
                                        <input
                                            type="number"
                                            defaultValue={48}
                                            className="w-full h-11 px-4 rounded-xl border border-border bg-slate-50 outline-none font-medium"
                                        />
                                        <span className="absolute right-4 top-1/2 -translate-y-1/2 text-xs font-bold text-muted-foreground">Horas</span>
                                    </div>
                                    <p className="text-[11px] text-muted-foreground">Tempo até que uma reserva expire se o pagamento não for confirmado.</p>
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === "integrations" && (
                        <div className="space-y-6 animate-in fade-in duration-300">
                            <div className="rounded-2xl border border-border p-6 flex items-center justify-between">
                                <div className="flex items-center space-x-4">
                                    <div className="h-10 w-10 rounded-xl bg-slate-900 flex items-center justify-center">
                                        <Share2 className="h-5 w-5 text-white" />
                                    </div>
                                    <div>
                                        <p className="text-sm font-bold text-foreground">Facebook Lead Ads</p>
                                        <p className="text-xs text-muted-foreground">Sincronize leads diretamente das campanhas Meta.</p>
                                    </div>
                                </div>
                                <button type="button" className="px-4 py-2 rounded-lg border border-border text-xs font-bold hover:bg-slate-50 transition-colors">Conectar</button>
                            </div>
                        </div>
                    )}
                </div>

                <div className="px-8 py-5 border-t border-border bg-slate-50/50 flex items-center justify-between">
                    <p className="text-xs text-muted-foreground font-medium">As alterações são aplicadas globalmente na instância.</p>
                    <button
                        type="submit"
                        disabled={updateSettings.isPending}
                        className={cn(
                            "flex items-center space-x-2 rounded-xl bg-primary px-6 py-2.5 text-sm font-bold text-white transition-all shadow-lg shadow-primary/20",
                            isSuccess ? "bg-emerald-500 shadow-emerald-500/20" : "hover:bg-primary/90",
                            updateSettings.isPending && "opacity-50 cursor-not-allowed"
                        )}
                    >
                        {isSuccess ? (
                            <>
                                <Check className="h-4 w-4" />
                                <span>Guardado</span>
                            </>
                        ) : updateSettings.isPending ? (
                            <span>A guardar...</span>
                        ) : (
                            <>
                                <Save className="h-4 w-4" />
                                <span>Guardar Alterações</span>
                            </>
                        )}
                    </button>
                </div>
            </form>
        </div>
    );
}
