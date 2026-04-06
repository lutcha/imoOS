/**
 * Hook para carregar e gerenciar modelos BIM (IFC)
 * 
 * @example
 * const { model, loading, error, loadModel, unloadModel } = useBIMModel(projectId);
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import * as THREE from 'three';
import apiClient from '@/lib/api-client';

export interface BIMModel {
  id: string;
  name: string;
  url: string;
  fileSize: number;
  uploadedAt: string;
  metadata?: {
    schema?: string;
    description?: string;
    author?: string;
    organization?: string;
    timestamp?: string;
  };
}

export interface BIMModelState {
  model: BIMModel | null;
  scene: THREE.Scene | null;
  loading: boolean;
  error: string | null;
  progress: number;
}

export function useBIMModel(projectId: string) {
  const [state, setState] = useState<BIMModelState>({
    model: null,
    scene: null,
    loading: false,
    error: null,
    progress: 0,
  });

  const abortControllerRef = useRef<AbortController | null>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      if (sceneRef.current) {
        // Cleanup Three.js resources
        sceneRef.current.traverse((object) => {
          if (object instanceof THREE.Mesh) {
            object.geometry?.dispose();
            if (Array.isArray(object.material)) {
              object.material.forEach(m => m.dispose());
            } else {
              object.material?.dispose();
            }
          }
        });
      }
    };
  }, []);

  /**
   * Busca lista de modelos BIM do projeto
   */
  const fetchModels = useCallback(async (): Promise<BIMModel[]> => {
    try {
      const response = await apiClient.get(`/api/v1/bim/models/?project=${projectId}`);
      return response.data.results || [];
    } catch (err) {
      console.error('Error fetching BIM models:', err);
      return [];
    }
  }, [projectId]);

  /**
   * Carrega um modelo BIM específico
   */
  const loadModel = useCallback(async (modelId: string) => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    setState(prev => ({ ...prev, loading: true, error: null, progress: 0 }));

    try {
      // Buscar informações do modelo
      const modelResponse = await apiClient.get(`/api/v1/bim/models/${modelId}/`);
      const modelData: BIMModel = modelResponse.data;

      setState(prev => ({ ...prev, model: modelData, progress: 30 }));

      // Criar cena Three.js
      const scene = new THREE.Scene();
      scene.background = new THREE.Color(0xf5f5f5);
      sceneRef.current = scene;

      setState(prev => ({ ...prev, scene, progress: 50 }));

      // O carregamento real do IFC será feito pelo IFCViewer component
      // usando @thatopen/components
      setState(prev => ({ 
        ...prev, 
        loading: false, 
        progress: 100 
      }));

      return { model: modelData, scene };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar modelo';
      setState(prev => ({ 
        ...prev, 
        loading: false, 
        error: errorMessage,
        progress: 0 
      }));
      throw err;
    }
  }, [projectId]);

  /**
   * Descarrega o modelo atual
   */
  const unloadModel = useCallback(() => {
    if (sceneRef.current) {
      sceneRef.current.traverse((object) => {
        if (object instanceof THREE.Mesh) {
          object.geometry?.dispose();
          if (Array.isArray(object.material)) {
            object.material.forEach(m => m.dispose());
          } else {
            object.material?.dispose();
          }
        }
      });
    }
    sceneRef.current = null;
    setState({
      model: null,
      scene: null,
      loading: false,
      error: null,
      progress: 0,
    });
  }, []);

  /**
   * Faz upload de um novo modelo IFC
   */
  const uploadModel = useCallback(async (file: File, name?: string) => {
    setState(prev => ({ ...prev, loading: true, error: null, progress: 0 }));

    try {
      // 1. Obter URL pré-assinado para upload
      const presignResponse = await apiClient.post('/api/v1/bim/models/upload-url/', {
        filename: file.name,
        content_type: 'application/ifc',
        project: projectId,
      });

      const { upload_url, model_id } = presignResponse.data;

      setState(prev => ({ ...prev, progress: 30 }));

      // 2. Fazer upload para S3/Storage
      await fetch(upload_url, {
        method: 'PUT',
        body: file,
        headers: {
          'Content-Type': 'application/ifc',
        },
      });

      setState(prev => ({ ...prev, progress: 70 }));

      // 3. Confirmar upload e processar modelo
      const confirmResponse = await apiClient.post(`/api/v1/bim/models/${model_id}/process/`, {
        name: name || file.name,
        file_size: file.size,
      });

      setState(prev => ({ ...prev, progress: 100, loading: false }));

      return confirmResponse.data as BIMModel;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao fazer upload';
      setState(prev => ({ 
        ...prev, 
        loading: false, 
        error: errorMessage 
      }));
      throw err;
    }
  }, [projectId]);

  /**
   * Remove um modelo
   */
  const deleteModel = useCallback(async (modelId: string) => {
    try {
      await apiClient.delete(`/api/v1/bim/models/${modelId}/`);
      if (state.model?.id === modelId) {
        unloadModel();
      }
    } catch (err) {
      console.error('Error deleting model:', err);
      throw err;
    }
  }, [state.model?.id, unloadModel]);

  return {
    ...state,
    fetchModels,
    loadModel,
    unloadModel,
    uploadModel,
    deleteModel,
  };
}

export default useBIMModel;
