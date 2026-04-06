/**
 * Element Mapper - Mapeia elementos BIM para Tasks e Units
 * 
 * Permite associar elementos IFC (paredes, portas, etc.) a:
 * - Tarefas de construção (ConstructionTask)
 * - Unidades habitacionais (Unit)
 */

import type { BIMElement, IFCType } from '@/hooks/useBIMElements';

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
  mappingConfidence: number; // 0-1, para mapeamentos automáticos
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

/**
 * Mapeia elementos BIM automaticamente baseado em regras
 */
export function autoMapElements(
  elements: BIMElement[],
  rules: MappingRule[],
  tasks: Array<{ id: string; name: string; status: string; progress: number }>,
  units: Array<{ id: string; number: string; type: string; status: string }>
): MappedElement[] {
  return elements.map(element => {
    const mapped: MappedElement = {
      ...element,
      autoMapped: false,
      mappingConfidence: 0,
    };

    // Aplicar regras
    for (const rule of rules) {
      if (!rule.autoApply) continue;

      // Verificar tipo de elemento
      if (!rule.elementTypes.includes(element.type)) {
        continue;
      }

      // Verificar filtro de propriedade se existir
      if (rule.propertyFilter && element.properties) {
        const propValue = element.properties[rule.propertyFilter.property];
        if (!propValue) continue;

        const matches = matchFilter(
          String(propValue),
          rule.propertyFilter.operator,
          rule.propertyFilter.value
        );
        if (!matches) continue;
      }

      // Aplicar mapeamento
      if (rule.taskId) {
        const task = tasks.find(t => t.id === rule.taskId);
        if (task) {
          mapped.taskMapping = {
            taskId: task.id,
            taskName: task.name,
            taskStatus: task.status,
            progress: task.progress,
          };
          mapped.autoMapped = true;
          mapped.mappingConfidence = 0.8;
        }
      }

      if (rule.unitId) {
        const unit = units.find(u => u.id === rule.unitId);
        if (unit) {
          mapped.unitMapping = {
            unitId: unit.id,
            unitNumber: unit.number,
            unitType: unit.type,
            status: unit.status,
          };
          mapped.autoMapped = true;
          mapped.mappingConfidence = 0.8;
        }
      }
    }

    // Tentar mapeamento por nome se não encontrou regra
    if (!mapped.taskMapping && !mapped.unitMapping) {
      // Procurar por padrões no nome
      const taskMatch = findTaskByNamePattern(element.name, tasks);
      if (taskMatch) {
        mapped.taskMapping = taskMatch;
        mapped.autoMapped = true;
        mapped.mappingConfidence = 0.6;
      }

      const unitMatch = findUnitByNamePattern(element.name, units);
      if (unitMatch) {
        mapped.unitMapping = unitMatch;
        mapped.autoMapped = true;
        mapped.mappingConfidence = 0.6;
      }
    }

    return mapped;
  });
}

/**
 * Cria mapeamento manual entre elemento e task
 */
export function createTaskMapping(
  elementGuid: string,
  taskId: string,
  taskData: TaskMapping
): MappedElement['taskMapping'] {
  return {
    ...taskData,
    taskId,
  };
}

/**
 * Cria mapeamento manual entre elemento e unit
 */
export function createUnitMapping(
  elementGuid: string,
  unitId: string,
  unitData: UnitMapping
): MappedElement['unitMapping'] {
  return {
    ...unitData,
    unitId,
  };
}

/**
 * Remove mapeamento de um elemento
 */
export function removeMapping(
  element: MappedElement,
  type: 'task' | 'unit' | 'both'
): MappedElement {
  const updated = { ...element };
  
  if (type === 'task' || type === 'both') {
    delete updated.taskMapping;
  }
  
  if (type === 'unit' || type === 'both') {
    delete updated.unitMapping;
  }
  
  // Resetar flags de mapeamento automático se não tiver mais mappings
  if (!updated.taskMapping && !updated.unitMapping) {
    updated.autoMapped = false;
    updated.mappingConfidence = 0;
  }
  
  return updated;
}

/**
 * Sugere mapeamentos baseado em similaridade
 */
export function suggestMappings(
  elements: BIMElement[],
  tasks: Array<{ id: string; name: string }>,
  units: Array<{ id: string; number: string; name?: string }>
): Array<{
  elementGuid: string;
  suggestedTaskId?: string;
  suggestedUnitId?: string;
  confidence: number;
  reason: string;
}> {
  const suggestions: ReturnType<typeof suggestMappings> = [];

  for (const element of elements) {
    // Pular elementos já mapeados
    if ('taskMapping' in element && element.taskMapping) continue;
    if ('unitMapping' in element && element.unitMapping) continue;

    // Procurar melhor match de task
    let bestTaskMatch: { id: string; score: number } | null = null;
    for (const task of tasks) {
      const score = calculateSimilarity(element.name, task.name);
      if (score > 0.5 && (!bestTaskMatch || score > bestTaskMatch.score)) {
        bestTaskMatch = { id: task.id, score };
      }
    }

    // Procurar melhor match de unit
    let bestUnitMatch: { id: string; score: number } | null = null;
    for (const unit of units) {
      const unitName = unit.name || unit.number;
      const score = calculateSimilarity(element.name, unitName);
      if (score > 0.5 && (!bestUnitMatch || score > bestUnitMatch.score)) {
        bestUnitMatch = { id: unit.id, score };
      }
    }

    // Adicionar sugestão se houver match bom
    if (bestTaskMatch || bestUnitMatch) {
      const confidence = Math.max(
        bestTaskMatch?.score || 0,
        bestUnitMatch?.score || 0
      );

      suggestions.push({
        elementGuid: element.guid,
        suggestedTaskId: bestTaskMatch?.id,
        suggestedUnitId: bestUnitMatch?.id,
        confidence,
        reason: generateSuggestionReason(element, bestTaskMatch, bestUnitMatch),
      });
    }
  }

  // Ordenar por confiança
  return suggestions.sort((a, b) => b.confidence - a.confidence);
}

/**
 * Agrupa elementos por task
 */
export function groupElementsByTask(
  elements: MappedElement[]
): Record<string, MappedElement[]> {
  const groups: Record<string, MappedElement[]> = {};

  for (const element of elements) {
    if (element.taskMapping) {
      const taskId = element.taskMapping.taskId;
      if (!groups[taskId]) {
        groups[taskId] = [];
      }
      groups[taskId].push(element);
    }
  }

  return groups;
}

/**
 * Agrupa elementos por unit
 */
export function groupElementsByUnit(
  elements: MappedElement[]
): Record<string, MappedElement[]> {
  const groups: Record<string, MappedElement[]> = {};

  for (const element of elements) {
    if (element.unitMapping) {
      const unitId = element.unitMapping.unitId;
      if (!groups[unitId]) {
        groups[unitId] = [];
      }
      groups[unitId].push(element);
    }
  }

  return groups;
}

// Helper functions

function matchFilter(
  value: string,
  operator: MappingRule['propertyFilter']['operator'],
  filterValue: string
): boolean {
  switch (operator) {
    case 'equals':
      return value.toLowerCase() === filterValue.toLowerCase();
    case 'contains':
      return value.toLowerCase().includes(filterValue.toLowerCase());
    case 'startsWith':
      return value.toLowerCase().startsWith(filterValue.toLowerCase());
    case 'regex':
      try {
        const regex = new RegExp(filterValue, 'i');
        return regex.test(value);
      } catch {
        return false;
      }
    default:
      return false;
  }
}

function findTaskByNamePattern(
  elementName: string,
  tasks: Array<{ id: string; name: string; status: string; progress: number }>
): TaskMapping | undefined {
  // Procurar por nomes similares
  for (const task of tasks) {
    const similarity = calculateSimilarity(elementName, task.name);
    if (similarity > 0.7) {
      return {
        taskId: task.id,
        taskName: task.name,
        taskStatus: task.status,
        progress: task.progress,
      };
    }
  }
  return undefined;
}

function findUnitByNamePattern(
  elementName: string,
  units: Array<{ id: string; number: string; type: string; status: string }>
): UnitMapping | undefined {
  // Procurar por número de unidade no nome do elemento
  for (const unit of units) {
    // Padrões comuns: "T1", "Apto 101", "Unit 1", etc.
    const patterns = [
      new RegExp(`\\b${unit.number}\\b`, 'i'),
      new RegExp(`\\b0*${unit.number}\\b`, 'i'),
    ];
    
    for (const pattern of patterns) {
      if (pattern.test(elementName)) {
        return {
          unitId: unit.id,
          unitNumber: unit.number,
          unitType: unit.type,
          status: unit.status,
        };
      }
    }
  }
  return undefined;
}

function calculateSimilarity(str1: string, str2: string): number {
  // Implementação simples de similaridade de strings
  // Usa distância de Levenshtein normalizada
  const s1 = str1.toLowerCase().trim();
  const s2 = str2.toLowerCase().trim();
  
  if (s1 === s2) return 1;
  if (s1.includes(s2) || s2.includes(s1)) return 0.8;
  
  const distance = levenshteinDistance(s1, s2);
  const maxLength = Math.max(s1.length, s2.length);
  return 1 - distance / maxLength;
}

function levenshteinDistance(str1: string, str2: string): number {
  const matrix: number[][] = [];

  for (let i = 0; i <= str2.length; i++) {
    matrix[i] = [i];
  }

  for (let j = 0; j <= str1.length; j++) {
    matrix[0][j] = j;
  }

  for (let i = 1; i <= str2.length; i++) {
    for (let j = 1; j <= str1.length; j++) {
      if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1];
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1,
          matrix[i][j - 1] + 1,
          matrix[i - 1][j] + 1
        );
      }
    }
  }

  return matrix[str2.length][str1.length];
}

function generateSuggestionReason(
  element: BIMElement,
  taskMatch: { id: string; score: number } | null,
  unitMatch: { id: string; score: number } | null
): string {
  const reasons: string[] = [];
  
  if (taskMatch && taskMatch.score > 0.7) {
    reasons.push(`Nome similar a tarefa (${Math.round(taskMatch.score * 100)}% match)`);
  }
  
  if (unitMatch && unitMatch.score > 0.7) {
    reasons.push(`Nome contém número de unidade (${Math.round(unitMatch.score * 100)}% match)`);
  }
  
  if (reasons.length === 0) {
    reasons.push('Padrão encontrado no nome');
  }
  
  return reasons.join('; ');
}

export default {
  autoMapElements,
  createTaskMapping,
  createUnitMapping,
  removeMapping,
  suggestMappings,
  groupElementsByTask,
  groupElementsByUnit,
};
