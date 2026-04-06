/**
 * Types for BIM (Building Information Modeling) Module
 */

// ============================================================================
// Element Types
// ============================================================================

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

// ============================================================================
// Model Types
// ============================================================================

export interface BIMModel {
  id: string;
  name: string;
  url: string;
  fileSize: number;
  uploadedAt: string;
  projectId?: string;
  metadata?: {
    schema?: string;
    description?: string;
    author?: string;
    organization?: string;
    timestamp?: string;
    numElements?: number;
    numProperties?: number;
  };
}

export interface BIMModelUpload {
  file: File;
  name?: string;
  description?: string;
}

// ============================================================================
// Mapping Types
// ============================================================================

export interface TaskMapping {
  taskId: string;
  taskName: string;
  taskStatus: string;
  progress: number;
  startDate?: string;
  endDate?: string;
  responsible?: string;
}

export interface UnitMapping {
  unitId: string;
  unitNumber: string;
  unitType: string;
  status: string;
  area?: number;
  price?: number;
}

export interface MappedElement extends BIMElement {
  taskMapping?: TaskMapping;
  unitMapping?: UnitMapping;
  autoMapped: boolean;
  mappingConfidence: number;
}

export interface MappingRule {
  id: string;
  name: string;
  elementTypes: IFCType[];
  propertyFilter?: {
    property: string;
    operator: 'equals' | 'contains' | 'startsWith' | 'regex';
    value: string;
  };
  taskId?: string;
  unitId?: string;
  autoApply: boolean;
}

// ============================================================================
// Viewer Types
// ============================================================================

export type ColorByOption = 'status' | 'phase' | 'responsible' | 'type' | 'none';

export interface SectionPlaneConfig {
  enabled: boolean;
  axis: 'x' | 'y' | 'z';
  position: number;
  inverted: boolean;
}

export interface ViewerCamera {
  position: { x: number; y: number; z: number };
  target: { x: number; y: number; z: number };
  zoom: number;
}

export interface ViewerState {
  camera: ViewerCamera;
  colorBy: ColorByOption;
  sectionPlane?: SectionPlaneConfig;
  selectedElements: string[];
  visibleElements: string[];
}

// ============================================================================
// 4D / Timeline Types
// ============================================================================

export interface ConstructionPhase {
  id: string;
  name: string;
  startDate: string;
  endDate: string;
  color: string;
  elementGuids: string[];
}

export interface BIM4DTimeline {
  phases: ConstructionPhase[];
  currentPhase?: string;
  startDate: string;
  endDate: string;
}

// ============================================================================
// Floor Plan Types
// ============================================================================

export interface FloorPlan {
  id: string;
  name: string;
  fileUrl: string;
  fileType: 'pdf' | 'dwg' | 'dxf' | 'image';
  level?: string;
  scale?: number;
  uploadedAt: string;
  hotspots?: PlanHotspot[];
}

export interface PlanHotspot {
  id: string;
  x: number;
  y: number;
  label: string;
  targetType: 'unit' | 'bim_element';
  targetId: string;
  metadata?: Record<string, any>;
}

// ============================================================================
// API Response Types
// ============================================================================

export interface BIMElementsResponse {
  results: BIMElement[];
  count: number;
  next?: string;
  previous?: string;
}

export interface BIMModelsResponse {
  results: BIMModel[];
  count: number;
  next?: string;
  previous?: string;
}

// ============================================================================
// Constants
// ============================================================================

export const IFC_TYPE_NAMES: Record<string, string> = {
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

export const STATUS_COLORS: Record<string, string> = {
  not_started: '#9ca3af',
  in_progress: '#3b82f6',
  completed: '#22c55e',
  delayed: '#ef4444',
  pending: '#f59e0b',
};

export const PHASE_COLORS = [
  '#3b82f6', // blue
  '#22c55e', // green
  '#f59e0b', // amber
  '#ef4444', // red
  '#8b5cf6', // violet
  '#ec4899', // pink
  '#14b8a6', // teal
  '#f97316', // orange
];
