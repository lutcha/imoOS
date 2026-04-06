/**
 * Hook para listar e gerenciar elementos BIM
 * 
 * @example
 * const { elements, loading, error, fetchElements, getElementProperties } = useBIMElements(modelId);
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import apiClient from '@/lib/api-client';

export type IFCType = 
  | 'IfcProject'
  | 'IfcSite'
  | 'IfcBuilding'
  | 'IfcBuildingStorey'
  | 'IfcSpace'
  | 'IfcWall'
  | 'IfcWallStandardCase'
  | 'IfcCurtainWall'
  | 'IfcDoor'
  | 'IfcWindow'
  | 'IfcSlab'
  | 'IfcRoof'
  | 'IfcColumn'
  | 'IfcBeam'
  | 'IfcStair'
  | 'IfcRailing'
  | 'IfcFurnishingElement'
  | 'IfcFlowTerminal'
  | 'IfcDistributionElement'
  | 'IfcElementAssembly'
  | 'IfcSystem'
  | 'IfcZone'
  | string;

export interface BIMElement {
  expressId: number;
  guid: string;
  name: string;
  type: IFCType;
  description?: string;
  parentGuid?: string;
  level?: string;
  children?: BIMElement[];
  // Propriedades extras
  properties?: Record<string, any>;
  // Links
  linkedTaskId?: string;
  linkedUnitId?: string;
  // Status visual
  status?: 'not_started' | 'in_progress' | 'completed' | 'delayed' | 'pending';
  color?: string;
  visible?: boolean;
  selected?: boolean;
}

export interface BIMElementFilter {
  types?: IFCType[];
  level?: string;
  status?: string;
  search?: string;
  hasTask?: boolean;
  hasUnit?: boolean;
}

export function useBIMElements(modelId: string | null) {
  const [elements, setElements] = useState<BIMElement[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState(0);
  
  const abortControllerRef = useRef<AbortController | null>(null);
  const elementsMapRef = useRef<Map<string, BIMElement>>(new Map());

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  /**
   * Busca elementos do modelo BIM
   */
  const fetchElements = useCallback(async (
    filter?: BIMElementFilter,
    page: number = 1,
    pageSize: number = 100
  ): Promise<BIMElement[]> => {
    if (!modelId) {
      setElements([]);
      return [];
    }

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      params.append('model', modelId);
      params.append('page', page.toString());
      params.append('page_size', pageSize.toString());

      if (filter?.types?.length) {
        filter.types.forEach(type => params.append('type', type));
      }
      if (filter?.level) {
        params.append('level', filter.level);
      }
      if (filter?.status) {
        params.append('status', filter.status);
      }
      if (filter?.search) {
        params.append('search', filter.search);
      }
      if (filter?.hasTask !== undefined) {
        params.append('has_task', filter.hasTask.toString());
      }
      if (filter?.hasUnit !== undefined) {
        params.append('has_unit', filter.hasUnit.toString());
      }

      const response = await apiClient.get(`/api/v1/bim/elements/?${params.toString()}`, {
        signal: abortControllerRef.current.signal,
      });

      const results: BIMElement[] = response.data.results || [];
      const count: number = response.data.count || 0;

      // Criar mapa para acesso rápido
      elementsMapRef.current.clear();
      results.forEach(el => {
        elementsMapRef.current.set(el.guid, el);
      });

      setElements(results);
      setTotalCount(count);
      setLoading(false);

      return results;
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        return [];
      }
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar elementos';
      setError(errorMessage);
      setLoading(false);
      throw err;
    }
  }, [modelId]);

  /**
   * Busca propriedades detalhadas de um elemento
   */
  const getElementProperties = useCallback(async (guid: string): Promise<BIMElement | null> => {
    if (!modelId) return null;

    try {
      const response = await apiClient.get(`/api/v1/bim/elements/${guid}/?model=${modelId}`);
      const element: BIMElement = response.data;

      // Atualizar no mapa e na lista
      elementsMapRef.current.set(guid, element);
      setElements(prev => 
        prev.map(el => el.guid === guid ? { ...el, ...element } : el)
      );

      return element;
    } catch (err) {
      console.error('Error fetching element properties:', err);
      return null;
    }
  }, [modelId]);

  /**
   * Busca elementos hierarquicamente (tree view)
   */
  const fetchElementTree = useCallback(async (): Promise<BIMElement[]> => {
    if (!modelId) return [];

    try {
      const response = await apiClient.get(`/api/v1/bim/elements/tree/?model=${modelId}`);
      const tree: BIMElement[] = response.data || [];
      
      // Popular mapa recursivamente
      const populateMap = (nodes: BIMElement[]) => {
        nodes.forEach(node => {
          elementsMapRef.current.set(node.guid, node);
          if (node.children) {
            populateMap(node.children);
          }
        });
      };
      populateMap(tree);

      return tree;
    } catch (err) {
      console.error('Error fetching element tree:', err);
      return [];
    }
  }, [modelId]);

  /**
   * Atualiza o link de um elemento com uma tarefa
   */
  const linkToTask = useCallback(async (guid: string, taskId: string | null) => {
    if (!modelId) return;

    try {
      const response = await apiClient.patch(`/api/v1/bim/elements/${guid}/`, {
        linked_task_id: taskId,
      });

      // Atualizar estado local
      setElements(prev =>
        prev.map(el =>
          el.guid === guid
            ? { ...el, linkedTaskId: taskId || undefined }
            : el
        )
      );

      return response.data;
    } catch (err) {
      console.error('Error linking element to task:', err);
      throw err;
    }
  }, [modelId]);

  /**
   * Atualiza o link de um elemento com uma unidade
   */
  const linkToUnit = useCallback(async (guid: string, unitId: string | null) => {
    if (!modelId) return;

    try {
      const response = await apiClient.patch(`/api/v1/bim/elements/${guid}/`, {
        linked_unit_id: unitId,
      });

      // Atualizar estado local
      setElements(prev =>
        prev.map(el =>
          el.guid === guid
            ? { ...el, linkedUnitId: unitId || undefined }
            : el
        )
      );

      return response.data;
    } catch (err) {
      console.error('Error linking element to unit:', err);
      throw err;
    }
  }, [modelId]);

  /**
   * Atualiza status visual de elementos
   */
  const updateElementsStatus = useCallback(async (guids: string[], status: string) => {
    if (!modelId) return;

    try {
      await apiClient.post('/api/v1/bim/elements/bulk-update/', {
        guids,
        status,
      });

      // Atualizar estado local
      setElements(prev =>
        prev.map(el =>
          guids.includes(el.guid)
            ? { ...el, status: status as any }
            : el
        )
      );
    } catch (err) {
      console.error('Error updating elements status:', err);
      throw err;
    }
  }, [modelId]);

  /**
   * Busca elemento por GUID (do cache)
   */
  const getElementByGuid = useCallback((guid: string): BIMElement | undefined => {
    return elementsMapRef.current.get(guid);
  }, []);

  /**
   * Busca elementos por tipo
   */
  const getElementsByType = useCallback((type: IFCType): BIMElement[] => {
    return elements.filter(el => el.type === type);
  }, [elements]);

  /**
   * Busca elementos por nível/piso
   */
  const getElementsByLevel = useCallback((level: string): BIMElement[] => {
    return elements.filter(el => el.level === level);
  }, [elements]);

  return {
    elements,
    loading,
    error,
    totalCount,
    fetchElements,
    fetchElementTree,
    getElementProperties,
    getElementByGuid,
    getElementsByType,
    getElementsByLevel,
    linkToTask,
    linkToUnit,
    updateElementsStatus,
  };
}

export default useBIMElements;
