'use client';

/**
 * BIMTreeView - Árvore hierárquica de elementos BIM
 * 
 * Estrutura: IfcProject > IfcSite > IfcBuilding > IfcBuildingStorey > Elementos
 */

import React, { useState, useMemo, useCallback } from 'react';
import { 
  ChevronRight, 
  ChevronDown, 
  Search,
  Building2,
  MapPin,
  Home,
  Layers,
  Box,
  Square,
  Circle,
  Triangle,
  CheckCircle2,
  Clock,
  AlertCircle,
  CircleDashed,
} from 'lucide-react';
import { Input } from '@/components/ui/input';
import type { BIMElement, IFCType } from '@/hooks/useBIMElements';

export interface BIMTreeViewProps {
  elements: BIMElement[];
  selectedGuids: string[];
  onSelectElement: (guid: string, multiSelect?: boolean) => void;
  onExpandElement?: (guid: string) => void;
  className?: string;
}

// Ícones por tipo de elemento
const TYPE_ICONS: Record<string, React.ReactNode> = {
  IfcProject: <Building2 className="w-4 h-4" />,
  IfcSite: <MapPin className="w-4 h-4" />,
  IfcBuilding: <Home className="w-4 h-4" />,
  IfcBuildingStorey: <Layers className="w-4 h-4" />,
  IfcSpace: <Square className="w-4 h-4" />,
  IfcWall: <Box className="w-4 h-4" />,
  IfcWallStandardCase: <Box className="w-4 h-4" />,
  IfcDoor: <Box className="w-4 h-4 rotate-45" />,
  IfcWindow: <Square className="w-4 h-4" />,
  IfcSlab: <Layers className="w-4 h-4" />,
  IfcRoof: <Triangle className="w-4 h-4" />,
  IfcColumn: <Box className="w-4 h-4" />,
  IfcBeam: <Box className="w-4 h-4 rotate-90" />,
  IfcStair: <Layers className="w-4 h-4" />,
  IfcRailing: <Circle className="w-4 h-4" />,
};

// Cores por tipo
const TYPE_COLORS: Record<string, string> = {
  IfcProject: 'text-blue-600',
  IfcSite: 'text-green-600',
  IfcBuilding: 'text-indigo-600',
  IfcBuildingStorey: 'text-purple-600',
};

// Ícones de status
const STATUS_ICONS: Record<string, { icon: React.ReactNode; color: string }> = {
  completed: { icon: <CheckCircle2 className="w-3 h-3" />, color: 'text-green-500' },
  in_progress: { icon: <Clock className="w-3 h-3" />, color: 'text-blue-500' },
  delayed: { icon: <AlertCircle className="w-3 h-3" />, color: 'text-red-500' },
  pending: { icon: <CircleDashed className="w-3 h-3" />, color: 'text-amber-500' },
  not_started: { icon: <Circle className="w-3 h-3" />, color: 'text-gray-400' },
};

interface TreeNode {
  element: BIMElement;
  children: TreeNode[];
  level: number;
}

export function BIMTreeView({
  elements,
  selectedGuids,
  onSelectElement,
  onExpandElement,
  className = '',
}: BIMTreeViewProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedGuids, setExpandedGuids] = useState<Set<string>>(new Set());

  // Construir árvore hierárquica
  const treeData = useMemo(() => {
    const elementMap = new Map<string, BIMElement>();
    elements.forEach(el => elementMap.set(el.guid, el));

    // Encontrar raízes (elementos sem pai ou pai não na lista)
    const roots: TreeNode[] = [];
    const childrenMap = new Map<string, string[]>();

    elements.forEach(element => {
      if (element.parentGuid && elementMap.has(element.parentGuid)) {
        if (!childrenMap.has(element.parentGuid)) {
          childrenMap.set(element.parentGuid, []);
        }
        childrenMap.get(element.parentGuid)!.push(element.guid);
      } else {
        roots.push({ element, children: [], level: 0 });
      }
    });

    // Função recursiva para construir árvore
    const buildTree = (guid: string, level: number): TreeNode => {
      const element = elementMap.get(guid)!;
      const childGuids = childrenMap.get(guid) || [];
      const children = childGuids.map(childGuid => buildTree(childGuid, level + 1));
      return { element, children, level };
    };

    // Atualizar raízes com filhos
    roots.forEach(root => {
      const childGuids = childrenMap.get(root.element.guid) || [];
      root.children = childGuids.map(guid => buildTree(guid, 1));
    });

    // Se não houver raízes, usar todos os elementos como raiz (flat)
    if (roots.length === 0 && elements.length > 0) {
      return elements.map(el => ({
        element: el,
        children: [],
        level: 0,
      }));
    }

    return roots;
  }, [elements]);

  // Filtrar elementos por busca
  const filteredTreeData = useMemo(() => {
    if (!searchQuery.trim()) return treeData;

    const query = searchQuery.toLowerCase();
    
    const filterNode = (node: TreeNode): TreeNode | null => {
      const matches = 
        node.element.name.toLowerCase().includes(query) ||
        node.element.type.toLowerCase().includes(query) ||
        node.element.guid.toLowerCase().includes(query);

      const filteredChildren = node.children
        .map(filterNode)
        .filter((n): n is TreeNode => n !== null);

      if (matches || filteredChildren.length > 0) {
        return {
          ...node,
          children: filteredChildren,
        };
      }
      return null;
    };

    return treeData.map(filterNode).filter((n): n is TreeNode => n !== null);
  }, [treeData, searchQuery]);

  // Toggle expand/collapse
  const toggleExpanded = useCallback((guid: string) => {
    setExpandedGuids(prev => {
      const next = new Set(prev);
      if (next.has(guid)) {
        next.delete(guid);
      } else {
        next.add(guid);
      }
      return next;
    });
    onExpandElement?.(guid);
  }, [onExpandElement]);

  // Expandir todos
  const expandAll = useCallback(() => {
    const allGuids = new Set(elements.map(el => el.guid));
    setExpandedGuids(allGuids);
  }, [elements]);

  // Colapsar todos
  const collapseAll = useCallback(() => {
    setExpandedGuids(new Set());
  }, []);

  // Renderizar nó da árvore
  const renderNode = (node: TreeNode): React.ReactNode => {
    const { element, children, level } = node;
    const isSelected = selectedGuids.includes(element.guid);
    const isExpanded = expandedGuids.has(element.guid);
    const hasChildren = children.length > 0;
    const statusConfig = element.status ? STATUS_ICONS[element.status] : null;

    const paddingLeft = level * 16 + 8;

    return (
      <div key={element.guid}>
        <div
          className={`
            flex items-center gap-1 py-1.5 px-2 cursor-pointer
            hover:bg-gray-100 transition-colors
            ${isSelected ? 'bg-blue-50 border-l-2 border-blue-500' : 'border-l-2 border-transparent'}
          `}
          style={{ paddingLeft: `${paddingLeft}px` }}
          onClick={(e) => {
            e.stopPropagation();
            onSelectElement(element.guid, e.ctrlKey || e.metaKey);
          }}
          onDoubleClick={() => {
            if (hasChildren) {
              toggleExpanded(element.guid);
            }
          }}
        >
          {/* Expand/Collapse button */}
          <button
            className={`
              w-4 h-4 flex items-center justify-center rounded
              ${hasChildren ? 'hover:bg-gray-200' : 'invisible'}
            `}
            onClick={(e) => {
              e.stopPropagation();
              toggleExpanded(element.guid);
            }}
          >
            {isExpanded ? (
              <ChevronDown className="w-3 h-3 text-gray-500" />
            ) : (
              <ChevronRight className="w-3 h-3 text-gray-500" />
            )}
          </button>

          {/* Type Icon */}
          <span className={TYPE_COLORS[element.type] || 'text-gray-500'}>
            {TYPE_ICONS[element.type] || <Box className="w-4 h-4" />}
          </span>

          {/* Name */}
          <span className={`
            text-sm truncate flex-1
            ${isSelected ? 'font-medium text-blue-700' : 'text-gray-700'}
          `}>
            {element.name}
          </span>

          {/* Status Badge */}
          {statusConfig && (
            <span className={statusConfig.color} title={`Status: ${element.status}`}>
              {statusConfig.icon}
            </span>
          )}

          {/* Linked indicators */}
          {(element.linkedTaskId || element.linkedUnitId) && (
            <span className="w-2 h-2 rounded-full bg-blue-400" title="Associado" />
          )}
        </div>

        {/* Children */}
        {isExpanded && children.length > 0 && (
          <div>
            {children.map(child => renderNode(child))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Header */}
      <div className="p-3 border-b space-y-2">
        <div className="relative">
          <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input
            placeholder="Pesquisar elementos..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-8 h-8 text-sm"
          />
        </div>
        <div className="flex justify-between text-xs">
          <button
            onClick={expandAll}
            className="text-blue-600 hover:text-blue-700"
          >
            Expandir tudo
          </button>
          <button
            onClick={collapseAll}
            className="text-blue-600 hover:text-blue-700"
          >
            Colapsar tudo
          </button>
        </div>
      </div>

      {/* Tree Content */}
      <div className="flex-1 overflow-y-auto">
        {filteredTreeData.length === 0 ? (
          <div className="p-4 text-center text-gray-500 text-sm">
            {searchQuery ? 'Nenhum elemento encontrado' : 'Sem elementos'}
          </div>
        ) : (
          filteredTreeData.map(node => renderNode(node))
        )}
      </div>

      {/* Footer */}
      <div className="p-2 border-t text-xs text-gray-500 flex justify-between">
        <span>{elements.length} elementos</span>
        {selectedGuids.length > 0 && (
          <span>{selectedGuids.length} selecionados</span>
        )}
      </div>
    </div>
  );
}

export default BIMTreeView;
