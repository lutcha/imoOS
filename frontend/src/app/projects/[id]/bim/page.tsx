'use client';

/**
 * Página BIM Viewer
 * 
 * Visualizador 3D de modelos IFC com:
 * - TreeView de elementos (esquerda)
 * - Viewer 3D (centro)
 * - Propriedades do elemento (direita)
 * - Timeline 4D (fundo - opcional)
 */

import React, { useState, useCallback, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { 
  Upload, 
  FileUp, 
  AlertCircle,
  Layers,
  Maximize2,
  Minimize2,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';

// Components
import { IFCViewer } from '@/components/bim/IFCViewer';
import { ElementProperties } from '@/components/bim/ElementProperties';
import { BIMTreeView } from '@/components/bim/BIMTreeView';
import { ColorBySelector, ColorByOption } from '@/components/bim/ColorBySelector';
import { SectionPlane, SectionPlaneConfig } from '@/components/bim/SectionPlane';

// Hooks
import { useBIMModel, BIMModel } from '@/hooks/useBIMModel';
import { useBIMElements, BIMElement } from '@/hooks/useBIMElements';
import { useBIMSelection } from '@/hooks/useBIMSelection';

// Lib
import type { TaskMapping, UnitMapping } from '@/lib/bim/element-mapper';

export default function BIMPage() {
  const params = useParams();
  const projectId = params.id as string;

  // State
  const [selectedModel, setSelectedModel] = useState<BIMModel | null>(null);
  const [colorBy, setColorBy] = useState<ColorByOption>('none');
  const [sectionConfig, setSectionConfig] = useState<SectionPlaneConfig>({
    enabled: false,
    axis: 'z',
    position: 0,
    inverted: false,
  });
  const [selectedElementData, setSelectedElementData] = useState<BIMElement | null>(null);
  const [taskMapping, setTaskMapping] = useState<TaskMapping | undefined>();
  const [unitMapping, setUnitMapping] = useState<UnitMapping | undefined>();
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  // Hooks
  const { 
    model, 
    loading: modelLoading, 
    error: modelError,
    fetchModels,
    uploadModel,
  } = useBIMModel(projectId);

  const {
    elements,
    loading: elementsLoading,
    error: elementsError,
    fetchElements,
    getElementProperties,
    linkToTask,
    linkToUnit,
  } = useBIMElements(selectedModel?.id || null);

  const {
    selected: selectedGuids,
    selectedElements,
    lastSelected,
    addToSelection,
    removeFromSelection,
    toggleSelection,
    clearSelection,
    replaceSelection,
    isSelected,
  } = useBIMSelection();

  // Carregar modelos na inicialização
  useEffect(() => {
    fetchModels().then(models => {
      if (models.length > 0) {
        setSelectedModel(models[0]);
      }
    });
  }, [fetchModels]);

  // Carregar elementos quando modelo mudar
  useEffect(() => {
    if (selectedModel) {
      fetchElements();
    }
  }, [selectedModel, fetchElements]);

  // Atualizar dados do elemento selecionado
  useEffect(() => {
    if (lastSelected) {
      getElementProperties(lastSelected).then(element => {
        if (element) {
          setSelectedElementData(element);
          // Carregar mappings se existirem
          if (element.linkedTaskId) {
            // Buscar dados da task
            setTaskMapping({
              taskId: element.linkedTaskId,
              taskName: 'Tarefa vinculada',
              taskStatus: 'in_progress',
              progress: 50,
            });
          } else {
            setTaskMapping(undefined);
          }
          
          if (element.linkedUnitId) {
            setUnitMapping({
              unitId: element.linkedUnitId,
              unitNumber: '101',
              unitType: 'T2',
              status: 'available',
            });
          } else {
            setUnitMapping(undefined);
          }
        }
      });
    } else {
      setSelectedElementData(null);
      setTaskMapping(undefined);
      setUnitMapping(undefined);
    }
  }, [lastSelected, getElementProperties]);

  // Handlers
  const handleElementSelect = useCallback((guid: string, properties?: any) => {
    replaceSelection(guid);
  }, [replaceSelection]);

  const handleTreeSelect = useCallback((guid: string, multiSelect?: boolean) => {
    if (multiSelect) {
      toggleSelection(guid);
    } else {
      replaceSelection(guid);
    }
  }, [toggleSelection, replaceSelection]);

  const handleFileDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    const ifcFile = files.find(f => f.name.endsWith('.ifc'));
    
    if (ifcFile) {
      try {
        const newModel = await uploadModel(ifcFile);
        setSelectedModel(newModel);
        setUploadDialogOpen(false);
      } catch (err) {
        console.error('Upload failed:', err);
      }
    }
  }, [uploadModel]);

  const handleFileInput = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.name.endsWith('.ifc')) {
      try {
        const newModel = await uploadModel(file);
        setSelectedModel(newModel);
        setUploadDialogOpen(false);
      } catch (err) {
        console.error('Upload failed:', err);
      }
    }
  }, [uploadModel]);

  const handleLinkToTask = useCallback(async () => {
    if (!lastSelected) return;
    // Abrir modal de seleção de tarefa
    console.log('Link to task:', lastSelected);
  }, [lastSelected]);

  const handleLinkToUnit = useCallback(async () => {
    if (!lastSelected) return;
    // Abrir modal de seleção de unidade
    console.log('Link to unit:', lastSelected);
  }, [lastSelected]);

  const handleUnlinkTask = useCallback(async () => {
    if (!lastSelected) return;
    await linkToTask(lastSelected, null);
    setTaskMapping(undefined);
  }, [lastSelected, linkToTask]);

  const handleUnlinkUnit = useCallback(async () => {
    if (!lastSelected) return;
    await linkToUnit(lastSelected, null);
    setUnitMapping(undefined);
  }, [lastSelected, linkToUnit]);

  // Loading state
  if (modelLoading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-8rem)]">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">A carregar modelo BIM...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-4">
          <h1 className="text-2xl font-bold">Modelo BIM</h1>
          {selectedModel && (
            <Badge variant="secondary" className="flex items-center gap-1">
              <Layers className="w-3 h-3" />
              {selectedModel.name}
            </Badge>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Model Selector */}
          {model && (
            <select
              className="px-3 py-1.5 border rounded-md text-sm bg-white"
              value={selectedModel?.id || ''}
              onChange={(e) => {
                const modelId = e.target.value;
                // Buscar modelo na lista
              }}
            >
              <option value="">Selecionar modelo...</option>
              <option value={model.id}>{model.name}</option>
            </select>
          )}

          {/* Upload Button */}
          <Dialog open={uploadDialogOpen} onOpenChange={setUploadDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" size="sm">
                <Upload className="w-4 h-4 mr-1" />
                Upload IFC
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Upload de Modelo IFC</DialogTitle>
              </DialogHeader>
              <div
                className={`
                  border-2 border-dashed rounded-lg p-8 text-center
                  transition-colors
                  ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300'}
                `}
                onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={handleFileDrop}
              >
                <FileUp className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                <p className="text-gray-600 mb-2">
                  Arraste um ficheiro .ifc ou clique para selecionar
                </p>
                <input
                  type="file"
                  accept=".ifc"
                  className="hidden"
                  id="ifc-upload"
                  onChange={handleFileInput}
                />
                <label htmlFor="ifc-upload">
                  <Button variant="outline" size="sm" className="cursor-pointer" asChild>
                    <span>Selecionar Ficheiro</span>
                  </Button>
                </label>
              </div>
            </DialogContent>
          </Dialog>

          {/* Fullscreen Toggle */}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsFullscreen(!isFullscreen)}
          >
            {isFullscreen ? (
              <Minimize2 className="w-4 h-4" />
            ) : (
              <Maximize2 className="w-4 h-4" />
            )}
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {(modelError || elementsError) && (
        <Alert variant="destructive" className="mb-4">
          <AlertCircle className="w-4 h-4" />
          <AlertDescription>
            {modelError || elementsError}
          </AlertDescription>
        </Alert>
      )}

      {/* Main Content - 3 Columns */}
      <div className="flex-1 grid grid-cols-12 gap-4 min-h-0">
        {/* Left Column - Tree View (20%) */}
        <Card className="col-span-3 flex flex-col overflow-hidden">
          <BIMTreeView
            elements={elements}
            selectedGuids={Array.from(selectedGuids)}
            onSelectElement={handleTreeSelect}
          />
        </Card>

        {/* Center Column - 3D Viewer (60%) */}
        <Card className="col-span-6 relative overflow-hidden">
          {selectedModel ? (
            <IFCViewer
              projectId={projectId}
              modelUrl={selectedModel.url}
              selectedElements={Array.from(selectedGuids)}
              onElementSelect={handleElementSelect}
              colorBy={colorBy}
              elements={elements}
              className="w-full h-full"
            />
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-gray-400">
              <Layers className="w-16 h-16 mb-4" />
              <p className="text-lg">Nenhum modelo carregado</p>
              <p className="text-sm">Faça upload de um ficheiro IFC</p>
            </div>
          )}

          {/* Section Plane Controls */}
          <div className="absolute bottom-4 left-4 w-64">
            <SectionPlane
              config={sectionConfig}
              onChange={setSectionConfig}
            />
          </div>
        </Card>

        {/* Right Column - Properties (20%) */}
        <Card className="col-span-3 flex flex-col overflow-hidden">
          <div className="p-3 border-b">
            <h3 className="font-medium text-sm">Propriedades</h3>
          </div>
          <div className="flex-1 overflow-hidden">
            <ElementProperties
              element={selectedElementData}
              taskMapping={taskMapping}
              unitMapping={unitMapping}
              onLinkToTask={handleLinkToTask}
              onLinkToUnit={handleLinkToUnit}
              onUnlinkTask={handleUnlinkTask}
              onUnlinkUnit={handleUnlinkUnit}
            />
          </div>

          {/* Color By Selector */}
          <div className="border-t p-3">
            <ColorBySelector
              value={colorBy}
              onChange={setColorBy}
            />
          </div>
        </Card>
      </div>

      {/* Footer - Timeline 4D (opcional) */}
      {false && (
        <Card className="mt-4 h-24">
          <div className="p-3">
            <h4 className="text-sm font-medium mb-2">Timeline 4D</h4>
            <div className="flex items-center gap-4">
              <Button variant="outline" size="sm">
                Play
              </Button>
              <div className="flex-1 h-2 bg-gray-200 rounded-full">
                <div className="w-1/3 h-full bg-blue-500 rounded-full" />
              </div>
              <span className="text-sm text-gray-500">Fase 1 de 5</span>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
