"use client";

/**
 * Mobile Header — ImoOS Field App
 * Header compacto otimizado para mobile
 */
import { useState } from "react";
import { Menu, X, HardHat } from "lucide-react";
import { cn } from "@/lib/utils";

interface MobileHeaderProps {
  title?: string;
  showMenu?: boolean;
}

export function MobileHeader({ title = "ImoOS Obra", showMenu = true }: MobileHeaderProps) {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 bg-primary text-primary-foreground shadow-md">
      <div className="flex items-center justify-between h-14 px-4">
        {/* Logo/Title */}
        <div className="flex items-center gap-2">
          <HardHat className="w-6 h-6" />
          <h1 className="text-lg font-bold truncate">{title}</h1>
        </div>

        {/* Menu Button */}
        {showMenu && (
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className={cn(
              "p-2 rounded-lg transition-colors",
              "hover:bg-white/10 active:bg-white/20",
              "min-h-[44px] min-w-[44px] flex items-center justify-center"
            )}
            aria-label={menuOpen ? "Fechar menu" : "Abrir menu"}
          >
            {menuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        )}
      </div>

      {/* Dropdown Menu */}
      {menuOpen && showMenu && (
        <nav className="absolute top-full left-0 right-0 bg-primary border-t border-white/10 shadow-lg">
          <div className="py-2">
            <MenuItem href="/mobile/obra" onClick={() => setMenuOpen(false)}>
              📋 Minhas Tarefas
            </MenuItem>
            <MenuItem href="/mobile/obra?tab=completed" onClick={() => setMenuOpen(false)}>
              ✅ Concluídas
            </MenuItem>
            <MenuItem href="/mobile/sync" onClick={() => setMenuOpen(false)}>
              🔄 Sincronização
            </MenuItem>
            <MenuItem href="/mobile/settings" onClick={() => setMenuOpen(false)}>
              ⚙️ Configurações
            </MenuItem>
            <div className="border-t border-white/10 mt-2 pt-2">
              <MenuItem href="/" onClick={() => setMenuOpen(false)}>
                🖥️ Versão Desktop
              </MenuItem>
            </div>
          </div>
        </nav>
      )}
    </header>
  );
}

function MenuItem({ 
  href, 
  children, 
  onClick 
}: { 
  href: string; 
  children: React.ReactNode; 
  onClick?: () => void;
}) {
  return (
    <a
      href={href}
      onClick={onClick}
      className={cn(
        "block px-4 py-3 text-base font-medium",
        "hover:bg-white/10 active:bg-white/20",
        "transition-colors"
      )}
    >
      {children}
    </a>
  );
}
