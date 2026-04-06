'use client';

/**
 * ElementProperties - Painel de propriedades do elemento selecionado
 * 
 * Mostra dados técnicos do IFC e links para tarefas/unidades
 */

import React, { useState } from 'react';
import { 
  Link2, 
  Unlink, 
  Building2, 
  Hammer, 
  CheckCircle2, 
  AlertCircle,
  Info,
  ChevronDown,
  ChevronRight,
  ExternalLink,
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import type { BIMElement, IFCType } from '@/hooks/useBIMElements';
import type { TaskMapping, UnitMapping } from '@/lib/bim/element-mapper';

export interface ElementPropertiesProps {
  element: BIMElement | null;
  taskMapping?: TaskMapping;
  unitMapping?: UnitMapping;
  onLinkToTask?: () => void;
  onLinkToUnit?: () => void;
  onUnlinkTask?: () => void;
  onUnlinkUnit?: () => void;
  onNavigateToTask?: (taskId: string) => void;
  onNavigateToUnit?: (unitId: string) => void;
  className?: string;
}

// Mapeamento de tipos IFC para nomes amigáveis
const IFC_TYPE_NAMES: Record<string, string> = {
  IfcProject: 'Projeto',
  IfcSite: 'Terreno',
  IfcBuilding: 'Edifício',
  IfcBuildingStorey: 'Piso',
  IfcSpace: 'Espaço',
  IfcWall: 'Parede',
  IfcWallStandardCase: 'Parede (Padrão)',
  IfcCurtainWall: 'Parede Cortina',
  IfcDoor: 'Porta',
  IfcWindow: 'Janela',
  IfcSlab: 'Laje',
  IfcRoof: 'Cobertura',
  IfcColumn: 'Coluna',
  IfcBeam: 'Viga',
  IfcStair: 'Escada',
  IfcRailing: 'Guarda-corpo',
  IfcFurnishingElement: 'Mobiliário',
  IfcFlowTerminal: 'Terminal Hidráulico',
  IfcDistributionElement: 'Elemento de Distribuição',
  IfcElementAssembly: 'Conjunto',
  IfcSystem: 'Sistema',
  IfcZone: 'Zona',
};

// Cores por tipo de elemento
const TYPE_COLORS: Record<string, string> = {
  IfcWall: 'bg-gray-100 text-gray-700',
  IfcDoor: 'bg-amber-100 text-amber-700',
  IfcWindow: 'bg-blue-100 text-blue-700',
  IfcSlab: 'bg-stone-100 text-stone-700',
  IfcRoof: 'bg-red-100 text-red-700',
  IfcColumn: 'bg-gray-100 text-gray-700',
  IfcBeam: 'bg-gray-100 text-gray-700',
  IfcStair: 'bg-orange-100 text-orange-700',
};

export function ElementProperties({
  element,
  taskMapping,
  unitMapping,
  onLinkToTask,
  onLinkToUnit,
  onUnlinkTask,
  onUnlinkUnit,
  onNavigateToTask,
  onNavigateToUnit,
  className = '',
}: ElementPropertiesProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(['general', 'links'])
  );

  if (!element) {
    return (
      <div className={`p-4 text-center text-gray-500 ${className}`}>
        <Info className="w-8 h-8 mx-auto mb-2 opacity-50" />
        <p className="text-sm">Selecione um elemento no modelo 3D<br />para ver suas propriedades</p>
      </div>
    );
  }

  const toggleSection = (section: string) => {
    setExpandedSections(prev => {
      const next = new Set(prev);
      if (next.has(section)) {
        next.delete(section);
      } else {
        next.add(section);
      }
      return next;
    });
  };

  const typeName = IFC_TYPE_NAMES[element.type] || element.type;
  const typeColor = TYPE_COLORS[element.type] || 'bg-gray-100 text-gray-700';

  return (
    <div className={`h-full overflow-y-auto ${className}`}>
      {/* Header */}
      <div className="p-4 border-b">
        <Badge className={`${typeColor} mb-2`}>
          {typeName}
        </Badge>
        <h3 className="font-semibold text-gray-900 break-words">
          {element.name}
        </h3>
        <p className="text-xs text-gray-500 mt-1 font-mono">
          {element.guid}
        </p>
      </div>

      {/* Informações Gerais */}
      <Section
        title="Informações Gerais"
        icon={<Info className="w-4 h-4" />}
        expanded={expandedSections.has('general')}
        onToggle={() => toggleSection('general')}
      >
        <PropertyGrid>
          <Property label="Express ID" value={element.expressId.toString()} />
          {element.level && (
            <Property label="Nível" value={element.level} />
          )}
          {element.description && (
            <Property label="Descrição" value={element.description} span={2} />
          )}
          {element.properties?.['OverallHeight'] && (
            <Property 
              label="Altura" 
              value={`${element.properties['OverallHeight'].value} ${element.properties['OverallHeight'].unit || 'm'}`} 
            />
          )}
          {element.properties?.['OverallWidth'] && (
            <Property 
              label="Largura" 
              value={`${element.properties['OverallWidth'].value} ${element.properties['OverallWidth'].unit || 'm'}`} 
            />
          )}
        </PropertyGrid>
      </Section>

      {/* Links */}
      <Section
        title="Associações"
        icon={<Link2 className="w-4 h-4" />}
        expanded={expandedSections.has('links')}
        onToggle={() => toggleSection('links')}
      >
        <div className="space-y-3">
          {/* Task Link */}
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-2">
              <Hammer className="w-4 h-4 text-gray-500" />
              <span className="text-sm font-medium">Tarefa de Construção</span>
            </div>
            
            {taskMapping ? (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-900">{taskMapping.taskName}</span>
                  <TaskStatusBadge status={taskMapping.taskStatus} progress={taskMapping.progress} />
                </div>
                {taskMapping.progress !== undefined && (
                  <div className="w-full h-1.5 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-blue-500 rounded-full"
                      style={{ width: `${taskMapping.progress}%` }}
                    />
                  </div>
                )}
                <div className="flex gap-2 pt-1">
                  {onNavigateToTask && (
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="flex-1"
                      onClick={() => onNavigateToTask(taskMapping.taskId)}
                    >
                      <ExternalLink className="w-3 h-3 mr-1" />
                      Ver Tarefa
                    </Button>
                  )}
                  {onUnlinkTask && (
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={onUnlinkTask}
                    >
                      <Unlink className="w-3 h-3" />
                    </Button>
                  )}
                </div>
              </div>
            ) : (
              <Button 
                variant="outline" 
                size="sm" 
                className="w-full"
                onClick={onLinkToTask}
              >
                <Link2 className="w-3 h-3 mr-1" />
                Associar a Tarefa
              </Button>
            )}
          </div>

          {/* Unit Link */}
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-2">
              <Building2 className="w-4 h-4 text-gray-500" />
              <span className="text-sm font-medium">Unidade Habitacional</span>
            </div>
            
            {unitMapping ? (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-900">
                    Unidade {unitMapping.unitNumber}
                  </span>
                  <UnitStatusBadge status={unitMapping.status} />
                </div>
                <div className="text-xs text-gray-500">
                  Tipo: {unitMapping.unitType}
                </div>
                <div className="flex gap-2 pt-1">
                  {onNavigateToUnit && (
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="flex-1"
                      onClick={() => onNavigateToUnit(unitMapping.unitId)}
                    >
                      <ExternalLink className="w-3 h-3 mr-1" />
                      Ver Unidade
                    </Button>
                  )}
                  {onUnlinkUnit && (
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={onUnlinkUnit}
                    >
                      <Unlink className="w-3 h-3" />
                    </Button>
                  )}
                </div>
              </div>
            ) : (
              <Button 
                variant="outline" 
                size="sm" 
                className="w-full"
                onClick={onLinkToUnit}
              >
                <Link2 className="w-3 h-3 mr-1" />
                Associar a Unidade
              </Button>
            )}
          </div>
        </div>
      </Section>

      {/* Propriedades IFC */}
      {element.properties && Object.keys(element.properties).length > 0 && (
        <Section
          title="Propriedades IFC"
          icon={<Info className="w-4 h-4" />}
          expanded={expandedSections.has('properties')}
          onToggle={() => toggleSection('properties')}
        >
          <PropertyGrid>
            {Object.entries(element.properties)
              .filter(([key]) => !['OverallHeight', 'OverallWidth'].includes(key))
              .slice(0, 10)
              .map(([key, value]: [string, any]) => (
                <Property 
                  key={key}
                  label={formatPropertyName(key)}
                  value={formatPropertyValue(value)}
                  span={2}
                />
              ))}
          </PropertyGrid>
          {Object.keys(element.properties).length > 10 && (
            <p className="text-xs text-gray-500 text-center mt-2">
              +{Object.keys(element.properties).length - 10} propriedades
            </p>
          )}
        </Section>
      )}
    </div>
  );
}

// Sub-components

interface SectionProps {
  title: string;
  icon: React.ReactNode;
  expanded: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}

function Section({ title, icon, expanded, onToggle, children }: SectionProps) {
  return (
    <div className="border-b last:border-b-0">
      <button
        onClick={onToggle}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-2">
          <span className="text-gray-500">{icon}</span>
          <span className="font-medium text-sm">{title}</span>
        </div>
        {expanded ? (
          <ChevronDown className="w-4 h-4 text-gray-400" />
        ) : (
          <ChevronRight className="w-4 h-4 text-gray-400" />
        )}
      </button>
      {expanded && (
        <div className="px-4 pb-4">
          {children}
        </div>
      )}
    </div>
  );
}

function PropertyGrid({ children }: { children: React.ReactNode }) {
  return (
    <div className="grid grid-cols-2 gap-2 text-sm">
      {children}
    </div>
  );
}

interface PropertyProps {
  label: string;
  value: string;
  span?: 1 | 2;
}

function Property({ label, value, span = 1 }: PropertyProps) {
  return (
    <div className={span === 2 ? 'col-span-2' : ''}>
      <div className="text-xs text-gray-500">{label}</div>
      <div className="text-gray-900 break-words">{value}</div>
    </div>
  );
}

function TaskStatusBadge({ status, progress }: { status: string; progress?: number }) {
  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'completed':
        return { color: 'bg-green-100 text-green-700', icon: CheckCircle2 };
      case 'in_progress':
        return { color: 'bg-blue-100 text-blue-700', icon: Hammer };
      case 'delayed':
        return { color: 'bg-red-100 text-red-700', icon: AlertCircle };
      default:
        return { color: 'bg-gray-100 text-gray-700', icon: Info };
    }
  };

  const config = getStatusConfig(status);
  const Icon = config.icon;

  return (
    <Badge className={config.color}>
      <Icon className="w-3 h-3 mr-1" />
      {progress !== undefined ? `${progress}%` : status}
    </Badge>
  );
}

function UnitStatusBadge({ status }: { status: string }) {
  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'sold':
        return { color: 'bg-red-100 text-red-700', label: 'Vendida' };
      case 'reserved':
        return { color: 'bg-amber-100 text-amber-700', label: 'Reservada' };
      case 'available':
        return { color: 'bg-green-100 text-green-700', label: 'Disponível' };
      default:
        return { color: 'bg-gray-100 text-gray-700', label: status };
    }
  };

  const config = getStatusConfig(status);

  return (
    <Badge className={config.color}>
      {config.label}
    </Badge>
  );
}

// Helpers

function formatPropertyName(name: string): string {
  // Converter camelCase para palavras separadas
  return name
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, str => str.toUpperCase())
    .trim();
}

function formatPropertyValue(value: any): string {
  if (value === null || value === undefined) return '-';
  if (typeof value === 'boolean') return value ? 'Sim' : 'Não';
  if (typeof value === 'object') {
    if (value.value !== undefined) return String(value.value);
    return JSON.stringify(value);
  }
  return String(value);
}

export default ElementProperties;
