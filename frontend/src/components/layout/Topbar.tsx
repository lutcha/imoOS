"use client";

import { Bell, Search, User, LogOut, Settings, HelpCircle, ChevronDown } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useState } from "react";
import { cn } from "@/lib/utils";

export function Topbar() {
    const { user, tenant, logout } = useAuth();
    const [showUserMenu, setShowUserMenu] = useState(false);
    const [showNotifications, setShowNotifications] = useState(false);

    // Get initials from user context
    const initials = user?.initials || "??";

    return (
        <header className="h-20 border-b border-border bg-white/80 backdrop-blur-md sticky top-0 z-30 px-8 flex items-center justify-between transition-all">
            {/* Search Bar */}
            <div className="flex-1 max-w-xl">
                <div className="relative group">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
                    <input
                        type="text"
                        placeholder="Pesquisar..."
                        className="w-full bg-slate-50 border border-border h-11 pl-11 pr-4 rounded-xl text-sm font-medium outline-none focus:bg-white focus:ring-2 focus:ring-primary/10 transition-all placeholder:text-muted-foreground/60 focus:border-primary/30"
                    />
                </div>
            </div>

            {/* Right Actions */}
            <div className="flex items-center space-x-6">
                {/* Notifications */}
                <div className="relative">
                    <button
                        onClick={() => setShowNotifications(!showNotifications)}
                        className={cn(
                            "p-2.5 rounded-xl border border-border transition-all relative group",
                            showNotifications ? "bg-slate-50 text-primary border-primary/20" : "hover:bg-slate-50 text-muted-foreground hover:text-foreground"
                        )}
                    >
                        <Bell className="h-5 w-5" />
                        <span className="absolute top-2.5 right-2.5 h-2 w-2 bg-primary rounded-full border-2 border-white shadow-[0_0_8px_rgba(59,130,246,0.6)] animate-pulse"></span>
                    </button>

                    {showNotifications && (
                        <>
                            <div className="fixed inset-0 z-10" onClick={() => setShowNotifications(false)} />
                            <div className="absolute right-0 mt-3 w-80 bg-white rounded-2xl border border-border shadow-xl z-20 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
                                <div className="px-5 py-4 border-b border-border bg-slate-50/50 flex items-center justify-between">
                                    <span className="text-xs font-bold text-foreground">Notificações</span>
                                    <span className="text-[10px] text-primary font-bold hover:underline cursor-pointer">Lidas</span>
                                </div>
                                <div className="divide-y divide-border max-h-96 overflow-y-auto">
                                    <div className="px-5 py-4 hover:bg-slate-50 transition-colors cursor-pointer group">
                                        <p className="text-xs font-bold text-foreground group-hover:text-primary transition-colors">Nova visualização de imóvel</p>
                                        <p className="text-[11px] text-muted-foreground mt-1 line-clamp-2">O lead João Silva acabou de visualizar o Edifício Ocean View.</p>
                                        <p className="text-[9px] text-muted-foreground/60 mt-1.5 font-bold uppercase tracking-wider">há 2 minutos</p>
                                    </div>
                                    <div className="px-5 py-4 hover:bg-slate-50 transition-colors cursor-pointer group opacity-60">
                                        <p className="text-xs font-bold text-foreground group-hover:text-primary transition-colors">Reserva pendente</p>
                                        <p className="text-[11px] text-muted-foreground mt-1 line-clamp-2">A reserva da Unidade A10 excepira em 2 horas.</p>
                                        <p className="text-[9px] text-muted-foreground/60 mt-1.5 font-bold uppercase tracking-wider">há 1 hora</p>
                                    </div>
                                </div>
                            </div>
                        </>
                    )}
                </div>

                <div className="h-8 w-px bg-border"></div>

                {/* User Profile */}
                <div className="relative">
                    <button
                        data-testid="user-menu"
                        onClick={() => setShowUserMenu(!showUserMenu)}
                        className={cn(
                            "flex items-center space-x-3 p-1.5 pr-3 rounded-xl border border-transparent transition-all",
                            showUserMenu ? "bg-slate-50 border-border" : "hover:bg-slate-50"
                        )}
                    >
                        <div className="h-9 w-9 rounded-lg bg-primary/10 border border-primary/10 flex items-center justify-center text-primary font-black text-sm shadow-inner">
                            {initials}
                        </div>
                        <div className="text-left hidden md:block">
                            <p className="text-sm font-bold text-slate-900 leading-none">
                                {user?.fullName}
                            </p>
                            <p className="text-[11px] text-muted-foreground mt-1 font-medium italic">
                                {tenant?.name || "ImoOS"}
                            </p>
                        </div>
                        <ChevronDown className={cn("h-3.5 w-3.5 text-muted-foreground transition-transform", showUserMenu && "rotate-180")} />
                    </button>

                    {showUserMenu && (
                        <>
                            <div className="fixed inset-0 z-10" onClick={() => setShowUserMenu(false)} />
                            <div className="absolute right-0 mt-3 w-64 bg-white rounded-2xl border border-border shadow-xl z-20 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
                                <div className="px-5 py-4 border-b border-border bg-slate-50/50">
                                    <p className="text-xs font-bold text-foreground">{user?.email}</p>
                                    <p className="text-[10px] text-muted-foreground font-medium mt-0.5">Administrador</p>
                                </div>
                                <div className="p-2">
                                    <button className="w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl text-xs font-bold text-muted-foreground hover:bg-slate-50 hover:text-foreground transition-all">
                                        <User className="h-4 w-4" />
                                        <span>O meu perfil</span>
                                    </button>
                                    <button className="w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl text-xs font-bold text-muted-foreground hover:bg-slate-50 hover:text-foreground transition-all">
                                        <Settings className="h-4 w-4" />
                                        <span>Definições</span>
                                    </button>
                                    <button className="w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl text-xs font-bold text-muted-foreground hover:bg-slate-50 hover:text-foreground transition-all">
                                        <HelpCircle className="h-4 w-4" />
                                        <span>Suporte</span>
                                    </button>
                                </div>
                                <div className="p-2 border-t border-border bg-slate-50/30">
                                    <button
                                        data-testid="logout-btn"
                                        onClick={() => logout()}
                                        className="w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl text-xs font-bold text-red-500 hover:bg-red-50 transition-all"
                                    >
                                        <LogOut className="h-4 w-4" />
                                        <span>Sair da conta</span>
                                    </button>
                                </div>
                            </div>
                        </>
                    )}
                </div>
            </div>
        </header>
    );
}
