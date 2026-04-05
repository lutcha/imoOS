"use client";

/**
 * Mobile Design System — ImoOS Field App
 * Princípios mobile-first para equipas de campo em Cabo Verde
 * 
 * Design Tokens:
 * - Touch targets: mínimo 48px (WCAG 2.1)
 * - Fontes: 16px+ base (acessibilidade)
 * - Contraste: alto (visibilidade ao sol)
 * - Espaçamento: generoso para touch
 * - Cores: semânticas para status de obra
 */

import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

// ============================================
// STATUS COLORS (Obra)
// ============================================

export const statusColors = {
  pending: {
    bg: "bg-red-500",
    bgLight: "bg-red-100",
    text: "text-red-700",
    border: "border-red-200",
    icon: "🔴",
    label: "Não Iniciado",
  },
  in_progress: {
    bg: "bg-amber-500",
    bgLight: "bg-amber-100",
    text: "text-amber-700",
    border: "border-amber-200",
    icon: "🟡",
    label: "Em Andamento",
  },
  completed: {
    bg: "bg-green-500",
    bgLight: "bg-green-100",
    text: "text-green-700",
    border: "border-green-200",
    icon: "🟢",
    label: "Concluído",
  },
  blocked: {
    bg: "bg-gray-500",
    bgLight: "bg-gray-100",
    text: "text-gray-700",
    border: "border-gray-200",
    icon: "⚫",
    label: "Bloqueado",
  },
} as const;

export type TaskStatusKey = keyof typeof statusColors;

// ============================================
// BUTTON VARIANTS (Touch-Optimized)
// ============================================

export const mobileButtonVariants = cva(
  // Base: min-height 48px para touch target
  "inline-flex items-center justify-center min-h-[48px] px-4 py-3 font-semibold text-base rounded-xl transition-all active:scale-95 disabled:opacity-50 disabled:pointer-events-none",
  {
    variants: {
      variant: {
        // Ações primárias (concluir, salvar)
        primary: "bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm",
        
        // Ações secundárias (editar, adicionar)
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/90",
        
        // Status específicos
        success: "bg-green-500 text-white hover:bg-green-600 shadow-sm",
        warning: "bg-amber-500 text-white hover:bg-amber-600",
        danger: "bg-red-500 text-white hover:bg-red-600",
        
        // Outline para ações menos importantes
        outline: "border-2 border-border bg-transparent hover:bg-muted",
        
        // Ghost para ações sutis
        ghost: "hover:bg-muted",
        
        // FAB (Floating Action Button)
        fab: "bg-primary text-primary-foreground rounded-full w-14 h-14 min-h-[56px] shadow-lg hover:shadow-xl hover:scale-105",
      },
      size: {
        default: "",
        sm: "min-h-[40px] px-3 py-2 text-sm rounded-lg",
        lg: "min-h-[56px] px-6 py-4 text-lg",
        xl: "min-h-[64px] px-8 py-5 text-xl rounded-2xl",
        icon: "min-h-[48px] w-12 px-0",
      },
      fullWidth: {
        true: "w-full",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "default",
      fullWidth: false,
    },
  }
);

// ============================================
// CARD VARIANTS
// ============================================

export const mobileCardVariants = cva(
  "bg-white rounded-2xl shadow-sm border border-border overflow-hidden",
  {
    variants: {
      padding: {
        none: "",
        sm: "p-3",
        default: "p-4",
        lg: "p-5",
      },
      interactive: {
        true: "active:scale-[0.98] transition-transform cursor-pointer",
        false: "",
      },
    },
    defaultVariants: {
      padding: "default",
      interactive: false,
    },
  }
);

// ============================================
// UTILITY CLASSES
// ============================================

export const mobileUtilities = {
  // Touch targets garantidos
  touchTarget: "min-h-[48px] min-w-[48px]",
  touchTargetSm: "min-h-[40px] min-w-[40px]",
  touchTargetLg: "min-h-[56px] min-w-[56px]",
  
  // Texto legível ao sol
  textHighContrast: "text-foreground font-medium",
  textLabel: "text-sm font-semibold text-muted-foreground uppercase tracking-wide",
  
  // Espaçamento mobile
  sectionGap: "space-y-4",
  elementGap: "gap-3",
  
  // Safe areas iOS
  safeTop: "pt-[env(safe-area-inset-top)]",
  safeBottom: "pb-[env(safe-area-inset-bottom)]",
  safeX: "px-[env(safe-area-inset-left)] pr-[env(safe-area-inset-right)]",
  
  // Animações
  pressFeedback: "active:scale-95 transition-transform duration-100",
  slideIn: "animate-in slide-in-from-bottom-4 duration-300",
};

// ============================================
// TYPE EXPORTS
// ============================================

export type MobileButtonVariantProps = VariantProps<typeof mobileButtonVariants>;
export type MobileCardVariantProps = VariantProps<typeof mobileCardVariants>;
