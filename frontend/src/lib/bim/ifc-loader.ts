/**
 * IFC Loader - Utilitários para carregar e processar arquivos IFC
 * 
 * Usa @thatopen/components e web-ifc para parsing de IFC
 */

import * as THREE from 'three';
import * as OBC from '@thatopen/components';
import * as FRAGS from '@thatopen/fragments';
import type { BIMElement, IFCType } from '@/hooks/useBIMElements';

// Configuração do Web-IFC
const WEB_IFC_SETTINGS = {
  COORDINATE_TO_ORIGIN: true,
  USE_FAST_BOOLS: true,
  CIRCLE_SEGMENTS_LOW: 6,
  CIRCLE_SEGMENTS_MEDIUM: 12,
  CIRCLE_SEGMENTS_HIGH: 24,
};

export interface IFCLoadResult {
  scene: THREE.Scene;
  fragments: FRAGS.FragmentsGroup;
  elements: BIMElement[];
  properties: Map<number, any>;
  levels: string[];
  types: IFCType[];
}

export interface IFCLoadProgress {
  stage: 'downloading' | 'parsing' | 'geometry' | 'properties' | 'complete';
  progress: number; // 0-100
  message: string;
}

export type ProgressCallback = (progress: IFCLoadProgress) => void;

/**
 * Classe responsável por carregar e gerenciar modelos IFC
 */
export class IFCLoader {
  private components: OBC.Components;
  private fragments: OBC.FragmentsManager;
  private fragmentIfcLoader: OBC.IfcLoader;
  private isInitialized: boolean = false;
  
  constructor() {
    this.components = new OBC.Components();
    this.fragments = this.components.get(OBC.FragmentsManager);
    this.fragmentIfcLoader = this.components.get(OBC.IfcLoader);
  }

  /**
   * Inicializa o loader com configurações
   */
  async initialize(): Promise<void> {
    if (this.isInitialized) return;

    try {
      // Configurar o loader IFC
      this.fragmentIfcLoader.settings.wasm = {
        path: 'https://unpkg.com/web-ifc@0.0.59/',
        absolute: true,
      };
      
      this.fragmentIfcLoader.settings.webIfc.COORDINATE_TO_ORIGIN = WEB_IFC_SETTINGS.COORDINATE_TO_ORIGIN;
      this.fragmentIfcLoader.settings.webIfc.USE_FAST_BOOLS = WEB_IFC_SETTINGS.USE_FAST_BOOLS;

      this.isInitialized = true;
    } catch (error) {
      console.error('Error initializing IFC Loader:', error);
      throw new Error('Falha ao inicializar carregador IFC');
    }
  }

  /**
   * Carrega um arquivo IFC a partir de URL
   */
  async loadFromURL(
    url: string, 
    onProgress?: ProgressCallback
  ): Promise<IFCLoadResult> {
    if (!this.isInitialized) {
      await this.initialize();
    }

    try {
      // Download
      onProgress?.({
        stage: 'downloading',
        progress: 0,
        message: 'A descarregar modelo...',
      });

      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Failed to download: ${response.statusText}`);
      }

      const contentLength = parseInt(response.headers.get('content-length') || '0');
      const reader = response.body?.getReader();
      
      let receivedLength = 0;
      const chunks: Uint8Array[] = [];

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          
          chunks.push(value);
          receivedLength += value.length;
          
          if (contentLength > 0) {
            const progress = Math.round((receivedLength / contentLength) * 100);
            onProgress?.({
              stage: 'downloading',
              progress: progress * 0.3, // Download = 30% do total
              message: `A descarregar... ${progress}%`,
            });
          }
        }
      }

      // Concatenar chunks
      const allChunks = new Uint8Array(receivedLength);
      let position = 0;
      for (const chunk of chunks) {
        allChunks.set(chunk, position);
        position += chunk.length;
      }

      return this.loadFromBuffer(allChunks, onProgress);
    } catch (error) {
      console.error('Error loading IFC from URL:', error);
      throw error;
    }
  }

  /**
   * Carrega um arquivo IFC a partir de File/Blob
   */
  async loadFromFile(
    file: File, 
    onProgress?: ProgressCallback
  ): Promise<IFCLoadResult> {
    if (!this.isInitialized) {
      await this.initialize();
    }

    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      
      reader.onprogress = (event) => {
        if (event.lengthComputable) {
          const progress = Math.round((event.loaded / event.total) * 100);
          onProgress?.({
            stage: 'downloading',
            progress: progress * 0.3,
            message: `A ler ficheiro... ${progress}%`,
          });
        }
      };

      reader.onload = async (event) => {
        try {
          const buffer = event.target?.result as ArrayBuffer;
          if (!buffer) {
            reject(new Error('Failed to read file'));
            return;
          }
          
          const result = await this.loadFromBuffer(
            new Uint8Array(buffer), 
            onProgress
          );
          resolve(result);
        } catch (error) {
          reject(error);
        }
      };

      reader.onerror = () => {
        reject(new Error('Error reading file'));
      };

      reader.readAsArrayBuffer(file);
    });
  }

  /**
   * Carrega IFC a partir de buffer
   */
  private async loadFromBuffer(
    data: Uint8Array, 
    onProgress?: ProgressCallback
  ): Promise<IFCLoadResult> {
    // Parsing
    onProgress?.({
      stage: 'parsing',
      progress: 30,
      message: 'A analisar estrutura IFC...',
    });

    try {
      // Carregar modelo
      const buffer = data.buffer as ArrayBuffer;
      const fragmentsGroup = await this.fragmentIfcLoader.load(buffer);

      onProgress?.({
        stage: 'geometry',
        progress: 60,
        message: 'A processar geometria...',
      });

      // Criar cena
      const scene = new THREE.Scene();
      scene.add(fragmentsGroup);

      // Extrair elementos e propriedades
      onProgress?.({
        stage: 'properties',
        progress: 80,
        message: 'A extrair propriedades...',
      });

      const { elements, properties, levels, types } = await this.extractData(
        fragmentsGroup
      );

      onProgress?.({
        stage: 'complete',
        progress: 100,
        message: 'Modelo carregado com sucesso!',
      });

      return {
        scene,
        fragments: fragmentsGroup,
        elements,
        properties,
        levels,
        types,
      };
    } catch (error) {
      console.error('Error parsing IFC:', error);
      throw new Error('Erro ao analisar ficheiro IFC');
    }
  }

  /**
   * Extrai dados dos elementos do modelo
   */
  private async extractData(
    fragmentsGroup: FRAGS.FragmentsGroup
  ): Promise<{
    elements: BIMElement[];
    properties: Map<number, any>;
    levels: string[];
    types: IFCType[];
  }> {
    const elements: BIMElement[] = [];
    const properties = new Map<number, any>();
    const levelsSet = new Set<string>();
    const typesSet = new Set<IFCType>();

    try {
      // Obter dados do fragment
      const fragmentKeys = Object.keys(fragmentsGroup.keyFragments);
      
      for (const expressID of fragmentKeys) {
        const id = parseInt(expressID);
        
        try {
          // Tentar obter propriedades do elemento
          const props = await fragmentsGroup.getProperties(id);
          
          if (props) {
            properties.set(id, props);
            
            const element: BIMElement = {
              expressId: id,
              guid: props.GlobalId?.value || `ID_${id}`,
              name: props.Name?.value || props.LongName?.value || `Elemento ${id}`,
              type: props.type || props.constructor?.name || 'IfcElement',
              description: props.Description?.value,
            };

            // Extrair nível/andar
            if (props.ContainedInStructure && props.ContainedInStructure[0]) {
              const structureId = props.ContainedInStructure[0].value;
              // Tentar obter nome do nível
              const levelProps = await fragmentsGroup.getProperties(structureId);
              if (levelProps?.Name?.value) {
                element.level = levelProps.Name.value;
                levelsSet.add(levelProps.Name.value);
              }
            }

            elements.push(element);
            typesSet.add(element.type);
          }
        } catch (e) {
          // Elemento sem propriedades, criar entrada básica
          elements.push({
            expressId: id,
            guid: `ID_${id}`,
            name: `Elemento ${id}`,
            type: 'IfcElement',
          });
        }
      }
    } catch (error) {
      console.warn('Error extracting data:', error);
    }

    return {
      elements,
      properties,
      levels: Array.from(levelsSet).sort(),
      types: Array.from(typesSet),
    };
  }

  /**
   * Libera recursos
   */
  dispose(): void {
    this.fragments.dispose();
    this.components.dispose();
    this.isInitialized = false;
  }
}

// Singleton instance
let globalLoader: IFCLoader | null = null;

export function getIFCLoader(): IFCLoader {
  if (!globalLoader) {
    globalLoader = new IFCLoader();
  }
  return globalLoader;
}

export function disposeIFCLoader(): void {
  if (globalLoader) {
    globalLoader.dispose();
    globalLoader = null;
  }
}

/**
 * Helpers para cores por status
 */
export const STATUS_COLORS: Record<string, THREE.Color> = {
  not_started: new THREE.Color(0x9ca3af), // gray-400
  in_progress: new THREE.Color(0x3b82f6), // blue-500
  completed: new THREE.Color(0x22c55e),   // green-500
  delayed: new THREE.Color(0xef4444),     // red-500
  pending: new THREE.Color(0xf59e0b),     // amber-500
};

/**
 * Helpers para cores por fase
 */
export const PHASE_COLORS = [
  new THREE.Color(0x3b82f6), // blue
  new THREE.Color(0x22c55e), // green
  new THREE.Color(0xf59e0b), // amber
  new THREE.Color(0xef4444), // red
  new THREE.Color(0x8b5cf6), // violet
  new THREE.Color(0xec4899), // pink
  new THREE.Color(0x14b8a6), // teal
  new THREE.Color(0xf97316), // orange
];

/**
 * Retorna cor para um elemento baseado no status
 */
export function getColorByStatus(status: string): THREE.Color {
  return STATUS_COLORS[status] || STATUS_COLORS.not_started;
}

/**
 * Retorna cor para um elemento baseado na fase (index)
 */
export function getColorByPhase(phaseIndex: number): THREE.Color {
  return PHASE_COLORS[phaseIndex % PHASE_COLORS.length];
}

export default IFCLoader;
