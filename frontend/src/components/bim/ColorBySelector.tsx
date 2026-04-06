'use client';

/**
 * ColorBySelector - Seletor de coloração do modelo BIM
 * 
 * Opções: Status, Fase, Responsável, Tipo, Nenhum
 */

import React from 'react';
import { Palette, Check } from 'lucide-react';

export type ColorByOption = 'status' | 'phase' | 'responsible' | 'type' | 'none';

export interface ColorBySelectorProps {
  value: ColorByOption;
  onChange: (value: ColorByOption) => void;
  className?: string;
}

interface ColorByConfig {
  value: ColorByOption;
  label: string;
  description: string;
  colors: string[];
}

const COLOR_BY_OPTIONS: ColorByConfig[] = [
  {
    value: 'none',
    label: 'Original',
    description: 'Cores originais do modelo',
    colors: ['#e5e7eb'],
  },
  {
    value: 'status',
    label: 'Status',
    description: 'Colorir por estado da tarefa',
    colors: ['#22c55e', '#3b82f6', '#f59e0b', '#ef4444', '#9ca3af'],
  },
  {
    value: 'phase',
    label: 'Fase',
    description: 'Colorir por fase de construção',
    colors: ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'],
  },
  {
    value: 'responsible',
    label: 'Responsável',
    description: 'Colorir por responsável',
    colors: ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6'],
  },
  {
    value: 'type',
    label: 'Tipo',
    description: 'Colorir por tipo de elemento',
    colors: ['#6b7280', '#8b5cf6', '#f59e0b', '#3b82f6', '#22c55e', '#ef4444'],
  },
];

export function ColorBySelector({
  value,
  onChange,
  className = '',
}: ColorBySelectorProps) {
  const selectedOption = COLOR_BY_OPTIONS.find(opt => opt.value === value);

  return (
    <div className={`${className}`}>
      {/* Label */}
      <div className="flex items-center gap-2 mb-2">
        <Palette className="w-4 h-4 text-gray-500" />
        <span className="text-sm font-medium text-gray-700">Colorir por</span>
      </div>

      {/* Options */}
      <div className="space-y-1">
        {COLOR_BY_OPTIONS.map((option) => (
          <button
            key={option.value}
            onClick={() => onChange(option.value)}
            className={`
              w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left
              transition-colors
              ${value === option.value 
                ? 'bg-blue-50 border border-blue-200' 
                : 'hover:bg-gray-50 border border-transparent'
              }
            `}
          >
            {/* Color preview */}
            <div className="flex -space-x-1">
              {option.colors.slice(0, 4).map((color, i) => (
                <div
                  key={i}
                  className="w-4 h-4 rounded-full border-2 border-white"
                  style={{ backgroundColor: color }}
                />
              ))}
              {option.colors.length > 4 && (
                <div className="w-4 h-4 rounded-full border-2 border-white bg-gray-200 flex items-center justify-center text-[8px] text-gray-600">
                  +
                </div>
              )}
            </div>

            {/* Text */}
            <div className="flex-1 min-w-0">
              <div className={`text-sm font-medium ${
                value === option.value ? 'text-blue-700' : 'text-gray-700'
              }`}>
                {option.label}
              </div>
              <div className="text-xs text-gray-500 truncate">
                {option.description}
              </div>
            </div>

            {/* Checkmark */}
            {value === option.value && (
              <Check className="w-4 h-4 text-blue-600" />
            )}
          </button>
        ))}
      </div>

      {/* Legend (when colorBy is active) */}
      {value !== 'none' && selectedOption && (
        <div className="mt-4 pt-4 border-t">
          <div className="text-xs font-medium text-gray-500 mb-2">
            Legenda
          </div>
          <ColorLegend type={value} />
        </div>
      )}
    </div>
  );
}

function ColorLegend({ type }: { type: ColorByOption }) {
  const legends: Record<string, Array<{ color: string; label: string }>> = {
    status: [
      { color: '#22c55e', label: 'Concluído' },
      { color: '#3b82f6', label: 'Em Progresso' },
      { color: '#f59e0b', label: 'Pendente' },
      { color: '#ef4444', label: 'Atrasado' },
      { color: '#9ca3af', label: 'Não Iniciado' },
    ],
    phase: [
      { color: '#3b82f6', label: 'Fase 1' },
      { color: '#22c55e', label: 'Fase 2' },
      { color: '#f59e0b', label: 'Fase 3' },
      { color: '#ef4444', label: 'Fase 4' },
      { color: '#8b5cf6', label: 'Fase 5' },
    ],
    responsible: [
      { color: '#3b82f6', label: 'Equipe A' },
      { color: '#22c55e', label: 'Equipe B' },
      { color: '#f59e0b', label: 'Equipe C' },
      { color: '#ef4444', label: 'Subcontratado' },
    ],
    type: [
      { color: '#6b7280', label: 'Estrutural' },
      { color: '#8b5cf6', label: 'Arquitetura' },
      { color: '#f59e0b', label: 'MEP' },
      { color: '#3b82f6', label: 'Acabamento' },
    ],
  };

  const items = legends[type] || [];

  return (
    <div className="space-y-1.5">
      {items.map((item, i) => (
        <div key={i} className="flex items-center gap-2">
          <div
            className="w-3 h-3 rounded"
            style={{ backgroundColor: item.color }}
          />
          <span className="text-xs text-gray-600">{item.label}</span>
        </div>
      ))}
    </div>
  );
}

export default ColorBySelector;
