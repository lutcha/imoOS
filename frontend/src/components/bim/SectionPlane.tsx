'use client';

/**
 * SectionPlane - Corte/planta do modelo BIM
 * 
 * Permite criar planos de corte para ver seções do modelo
 */

import React, { useState, useCallback } from 'react';
import { 
  Scissors, 
  FlipHorizontal, 
  FlipVertical,
  RotateCcw,
  Eye,
  EyeOff,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';

export interface SectionPlaneConfig {
  enabled: boolean;
  axis: 'x' | 'y' | 'z';
  position: number; // 0-100
  inverted: boolean;
}

export interface SectionPlaneProps {
  config: SectionPlaneConfig;
  onChange: (config: SectionPlaneConfig) => void;
  bounds?: { min: number; max: number };
  className?: string;
}

export function SectionPlane({
  config,
  onChange,
  bounds = { min: -10, max: 10 },
  className = '',
}: SectionPlaneProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const updateConfig = useCallback((updates: Partial<SectionPlaneConfig>) => {
    onChange({ ...config, ...updates });
  }, [config, onChange]);

  const axisLabels = {
    x: 'Corte X (Lateral)',
    y: 'Corte Y (Frontal)',
    z: 'Planta Z (Horizontal)',
  };

  const normalizedPosition = (config.position - bounds.min) / (bounds.max - bounds.min);

  return (
    <div className={`bg-white rounded-lg shadow-lg ${className}`}>
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Scissors className="w-4 h-4 text-gray-600" />
          <span className="font-medium text-sm">Plano de Corte</span>
          {config.enabled && (
            <span className="w-2 h-2 rounded-full bg-green-500" />
          )}
        </div>
        {isExpanded ? (
          <ChevronUp className="w-4 h-4 text-gray-400" />
        ) : (
          <ChevronDown className="w-4 h-4 text-gray-400" />
        )}
      </button>

      {/* Content */}
      {isExpanded && (
        <div className="px-4 pb-4 space-y-4">
          {/* Enable/Disable */}
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Ativar corte</span>
            <Button
              variant={config.enabled ? 'default' : 'outline'}
              size="sm"
              onClick={() => updateConfig({ enabled: !config.enabled })}
            >
              {config.enabled ? (
                <>
                  <Eye className="w-4 h-4 mr-1" />
                  Ativo
                </>
              ) : (
                <>
                  <EyeOff className="w-4 h-4 mr-1" />
                  Inativo
                </>
              )}
            </Button>
          </div>

          {config.enabled && (
            <>
              {/* Axis Selection */}
              <div className="space-y-2">
                <span className="text-sm text-gray-600">Eixo</span>
                <div className="flex gap-2">
                  {(['x', 'y', 'z'] as const).map((axis) => (
                    <button
                      key={axis}
                      onClick={() => updateConfig({ axis })}
                      className={`
                        flex-1 py-2 px-3 rounded-md text-sm font-medium
                        transition-colors
                        ${config.axis === axis
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }
                      `}
                    >
                      {axis.toUpperCase()}
                    </button>
                  ))}
                </div>
                <p className="text-xs text-gray-500">
                  {axisLabels[config.axis]}
                </p>
              </div>

              {/* Position Slider */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Posição</span>
                  <span className="text-sm font-mono">
                    {config.position.toFixed(2)}m
                  </span>
                </div>
                <Slider
                  value={[normalizedPosition * 100]}
                  onValueChange={([value]) => {
                    const position = bounds.min + (value / 100) * (bounds.max - bounds.min);
                    updateConfig({ position });
                  }}
                  min={0}
                  max={100}
                  step={1}
                />
                <div className="flex justify-between text-xs text-gray-400">
                  <span>{bounds.min}m</span>
                  <span>{bounds.max}m</span>
                </div>
              </div>

              {/* Invert */}
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Inverter direção</span>
                <Button
                  variant={config.inverted ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => updateConfig({ inverted: !config.inverted })}
                >
                  {config.inverted ? (
                    <FlipHorizontal className="w-4 h-4" />
                  ) : (
                    <FlipVertical className="w-4 h-4" />
                  )}
                </Button>
              </div>

              {/* Reset */}
              <Button
                variant="ghost"
                size="sm"
                className="w-full"
                onClick={() => updateConfig({
                  enabled: false,
                  position: (bounds.min + bounds.max) / 2,
                  inverted: false,
                })}
              >
                <RotateCcw className="w-4 h-4 mr-1" />
                Resetar
              </Button>
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default SectionPlane;
