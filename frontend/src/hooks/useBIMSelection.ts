/**
 * Hook para gerenciar seleção de elementos BIM
 * 
 * @example
 * const { selected, addToSelection, removeFromSelection, clearSelection, isSelected } = useBIMSelection();
 */

import { useState, useCallback, useRef } from 'react';
import type { BIMElement } from './useBIMElements';

export interface BIMSelectionState {
  selected: Set<string>; // Set de GUIDs
  selectedElements: BIMElement[];
  lastSelected: string | null;
}

export interface BIMSelectionActions {
  // Operações básicas
  addToSelection: (guid: string, element?: BIMElement) => void;
  removeFromSelection: (guid: string) => void;
  toggleSelection: (guid: string, element?: BIMElement) => void;
  clearSelection: () => void;
  
  // Seleção múltipla
  selectMultiple: (guids: string[], elements?: BIMElement[]) => void;
  replaceSelection: (guid: string, element?: BIMElement) => void;
  
  // Range selection (Shift+click)
  selectRange: (fromGuid: string, toGuid: string, allElements: BIMElement[]) => void;
  
  // Queries
  isSelected: (guid: string) => boolean;
  hasSelection: boolean;
  selectionCount: number;
  
  // Elementos selecionados
  getSelectedElements: () => string[];
  getSelectedElementData: () => BIMElement[];
}

export function useBIMSelection(): BIMSelectionState & BIMSelectionActions {
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [selectedElements, setSelectedElements] = useState<BIMElement[]>([]);
  const [lastSelected, setLastSelected] = useState<string | null>(null);
  
  // Ref para acesso síncrono aos elementos selecionados
  const elementsMapRef = useRef<Map<string, BIMElement>>(new Map());

  /**
   * Adiciona um elemento à seleção
   */
  const addToSelection = useCallback((guid: string, element?: BIMElement) => {
    setSelected(prev => {
      const newSet = new Set(prev);
      newSet.add(guid);
      return newSet;
    });
    
    if (element) {
      elementsMapRef.current.set(guid, element);
      setSelectedElements(prev => {
        if (prev.some(e => e.guid === guid)) return prev;
        return [...prev, element];
      });
    }
    
    setLastSelected(guid);
  }, []);

  /**
   * Remove um elemento da seleção
   */
  const removeFromSelection = useCallback((guid: string) => {
    setSelected(prev => {
      const newSet = new Set(prev);
      newSet.delete(guid);
      return newSet;
    });
    
    elementsMapRef.current.delete(guid);
    setSelectedElements(prev => prev.filter(e => e.guid !== guid));
    
    if (lastSelected === guid) {
      setLastSelected(null);
    }
  }, [lastSelected]);

  /**
   * Toggle seleção de um elemento
   */
  const toggleSelection = useCallback((guid: string, element?: BIMElement) => {
    setSelected(prev => {
      const newSet = new Set(prev);
      if (newSet.has(guid)) {
        newSet.delete(guid);
        elementsMapRef.current.delete(guid);
        setSelectedElements(els => els.filter(e => e.guid !== guid));
      } else {
        newSet.add(guid);
        if (element) {
          elementsMapRef.current.set(guid, element);
          setSelectedElements(els => {
            if (els.some(e => e.guid === guid)) return els;
            return [...els, element];
          });
        }
      }
      return newSet;
    });
    
    setLastSelected(guid);
  }, []);

  /**
   * Limpa toda a seleção
   */
  const clearSelection = useCallback(() => {
    setSelected(new Set());
    setSelectedElements([]);
    elementsMapRef.current.clear();
    setLastSelected(null);
  }, []);

  /**
   * Seleciona múltiplos elementos
   */
  const selectMultiple = useCallback((guids: string[], elements?: BIMElement[]) => {
    setSelected(prev => {
      const newSet = new Set(prev);
      guids.forEach(guid => newSet.add(guid));
      return newSet;
    });
    
    if (elements) {
      elements.forEach(el => {
        elementsMapRef.current.set(el.guid, el);
      });
      setSelectedElements(prev => {
        const existingGuids = new Set(prev.map(e => e.guid));
        const newElements = elements.filter(e => !existingGuids.has(e.guid));
        return [...prev, ...newElements];
      });
    }
    
    if (guids.length > 0) {
      setLastSelected(guids[guids.length - 1]);
    }
  }, []);

  /**
   * Substitui a seleção por um único elemento
   */
  const replaceSelection = useCallback((guid: string, element?: BIMElement) => {
    setSelected(new Set([guid]));
    elementsMapRef.current.clear();
    
    if (element) {
      elementsMapRef.current.set(guid, element);
      setSelectedElements([element]);
    } else {
      setSelectedElements([]);
    }
    
    setLastSelected(guid);
  }, []);

  /**
   * Seleciona um range de elementos (para Shift+click)
   */
  const selectRange = useCallback((
    fromGuid: string, 
    toGuid: string, 
    allElements: BIMElement[]
  ) => {
    // Criar lista plana de todos os elementos
    const flattenElements = (elements: BIMElement[]): BIMElement[] => {
      const result: BIMElement[] = [];
      elements.forEach(el => {
        result.push(el);
        if (el.children) {
          result.push(...flattenElements(el.children));
        }
      });
      return result;
    };

    const flatList = flattenElements(allElements);
    const fromIndex = flatList.findIndex(e => e.guid === fromGuid);
    const toIndex = flatList.findIndex(e => e.guid === toGuid);

    if (fromIndex === -1 || toIndex === -1) return;

    const start = Math.min(fromIndex, toIndex);
    const end = Math.max(fromIndex, toIndex);
    const rangeElements = flatList.slice(start, end + 1);
    const rangeGuids = rangeElements.map(e => e.guid);

    setSelected(prev => {
      const newSet = new Set(prev);
      rangeGuids.forEach(guid => newSet.add(guid));
      return newSet;
    });

    rangeElements.forEach(el => {
      elementsMapRef.current.set(el.guid, el);
    });
    
    setSelectedElements(prev => {
      const existingGuids = new Set(prev.map(e => e.guid));
      const newElements = rangeElements.filter(e => !existingGuids.has(e.guid));
      return [...prev, ...newElements];
    });

    setLastSelected(toGuid);
  }, []);

  /**
   * Verifica se um elemento está selecionado
   */
  const isSelected = useCallback((guid: string): boolean => {
    return selected.has(guid);
  }, [selected]);

  /**
   * Retorna array de GUIDs selecionados
   */
  const getSelectedElements = useCallback((): string[] => {
    return Array.from(selected);
  }, [selected]);

  /**
   * Retorna dados dos elementos selecionados
   */
  const getSelectedElementData = useCallback((): BIMElement[] => {
    return selectedElements;
  }, [selectedElements]);

  // Computed values
  const hasSelection = selected.size > 0;
  const selectionCount = selected.size;

  return {
    // State
    selected,
    selectedElements,
    lastSelected,
    
    // Actions
    addToSelection,
    removeFromSelection,
    toggleSelection,
    clearSelection,
    selectMultiple,
    replaceSelection,
    selectRange,
    
    // Queries
    isSelected,
    hasSelection,
    selectionCount,
    getSelectedElements,
    getSelectedElementData,
  };
}

export default useBIMSelection;
