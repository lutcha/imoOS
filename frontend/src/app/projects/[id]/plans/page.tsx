'use client';

/**
 * Página de Plantas 2D
 * 
 * Visualizador de plantas PDF/DWG com:
 * - Lista de plantas disponíveis
 * - Visualizador PDF.js
 * - Hotspots clicáveis para navegação ao BIM 3D
 */

import React, { useState, useCallback, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { 
  Upload, 
  FileText, 
  MapPin,
  Eye,
  ChevronLeft,
  ChevronRight,
  ZoomIn,
  ZoomOut,
  RotateCw,
  Layers,
  Box,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import apiClient from '@/lib/api-client';

// Tipos
interface FloorPlan {
  id: string;
  name: string;
  fileUrl: string;
  fileType: 'pdf' | 'dwg' | 'dxf' | 'image';
  level?: string;
  uploadedAt: string;
  hotspots?: PlanHotspot[];
}

interface PlanHotspot {
  id: string;
  x: number; // Porcentagem 0-100
  y: number; // Porcentagem 0-100
  label: string;
  targetType: 'unit' | 'bim_element';
  targetId: string;
}

export default function PlansPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;

  // State
  const [plans, setPlans] = useState<FloorPlan[]>([]);
  const [selectedPlan, setSelectedPlan] = useState<FloorPlan | null>(null);
  const [loading, setLoading] = useState(true);
  const [zoom, setZoom] = useState(1);
  const [rotation, setRotation] = useState(0);
  const [showHotspots, setShowHotspots] = useState(true);
  const [selectedHotspot, setSelectedHotspot] = useState<PlanHotspot | null>(null);

  // Carregar plantas
  useEffect(() => {
    const fetchPlans = async () => {
      try {
        // Simular chamada API - substituir pelo endpoint real
        // const response = await apiClient.get(`/api/v1/projects/${projectId}/plans/`);
        // setPlans(response.data.results);
        
        // Dados mock para demonstração
        setPlans([
          {
            id: '1',
            name: 'Planta Piso 0 - Térreo',
            fileUrl: '/sample/planta-t0.pdf',
            fileType: 'pdf',
            level: 'Piso 0',
            uploadedAt: '2024-01-15',
            hotspots: [
              { id: 'h1', x: 30, y: 40, label: 'T1-101', targetType: 'unit', targetId: 'unit-1' },
              { id: 'h2', x: 60, y: 40, label: 'T2-102', targetType: 'unit', targetId: 'unit-2' },
            ],
          },
          {
            id: '2',
            name: 'Planta Piso 1',
            fileUrl: '/sample/planta-p1.pdf',
            fileType: 'pdf',
            level: 'Piso 1',
            uploadedAt: '2024-01-15',
          },
          {
            id: '3',
            name: 'Corte A-A',
            fileUrl: '/sample/corte-aa.pdf',
            fileType: 'pdf',
            uploadedAt: '2024-01-16',
          },
        ]);
      } catch (error) {
        console.error('Error fetching plans:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPlans();
  }, [projectId]);

  // Handlers
  const handleZoomIn = useCallback(() => {
    setZoom(prev => Math.min(prev + 0.25, 3));
  }, []);

  const handleZoomOut = useCallback(() => {
    setZoom(prev => Math.max(prev - 0.25, 0.5));
  }, []);

  const handleRotate = useCallback(() => {
    setRotation(prev => (prev + 90) % 360);
  }, []);

  const handleHotspotClick = useCallback((hotspot: PlanHotspot) => {
    setSelectedHotspot(hotspot);
    
    if (hotspot.targetType === 'unit') {
      // Navegar para página da unidade
      // router.push(`/projects/${projectId}/units/${hotspot.targetId}`);
    } else if (hotspot.targetType === 'bim_element') {
      // Navegar para BIM 3D com elemento selecionado
      router.push(`/projects/${projectId}/bim?element=${hotspot.targetId}`);
    }
  }, [projectId, router]);

  const handleUpload = useCallback(async (file: File) => {
    try {
      // Upload da planta
      console.log('Uploading plan:', file.name);
      // await apiClient.post(`/api/v1/projects/${projectId}/plans/`, formData);
    } catch (error) {
      console.error('Error uploading plan:', error);
    }
  }, [projectId]);

  // Loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-8rem)]">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-4">
          <h1 className="text-2xl font-bold">Plantas 2D</h1>
          {selectedPlan && (
            <Badge variant="secondary">{selectedPlan.name}</Badge>
          )}
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" asChild>
            <label className="cursor-pointer">
              <Upload className="w-4 h-4 mr-1" />
              Upload Planta
              <input
                type="file"
                accept=".pdf,.dwg,.dxf,.png,.jpg,.jpeg"
                className="hidden"
                onChange={(e) => e.target.files?.[0] && handleUpload(e.target.files[0])}
              />
            </label>
          </Button>
          
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => router.push(`/projects/${projectId}/bim`)}
          >
            <Box className="w-4 h-4 mr-1" />
            Ver BIM 3D
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 grid grid-cols-12 gap-4 min-h-0">
        {/* Sidebar - Lista de Plantas */}
        <Card className="col-span-3 flex flex-col overflow-hidden">
          <div className="p-3 border-b">
            <h3 className="font-medium text-sm">Plantas Disponíveis</h3>
          </div>
          <div className="flex-1 overflow-y-auto p-2 space-y-2">
            {plans.map((plan) => (
              <button
                key={plan.id}
                onClick={() => {
                  setSelectedPlan(plan);
                  setZoom(1);
                  setRotation(0);
                }}
                className={`
                  w-full p-3 rounded-lg text-left transition-colors
                  ${selectedPlan?.id === plan.id 
                    ? 'bg-blue-50 border border-blue-200' 
                    : 'hover:bg-gray-50 border border-transparent'
                  }
                `}
              >
                <div className="flex items-start gap-3">
                  <FileText className={`
                    w-5 h-5 mt-0.5
                    ${selectedPlan?.id === plan.id ? 'text-blue-600' : 'text-gray-400'}
                  `} />
                  <div className="flex-1 min-w-0">
                    <p className={`text-sm font-medium truncate ${
                      selectedPlan?.id === plan.id ? 'text-blue-700' : 'text-gray-700'
                    }`}>
                      {plan.name}
                    </p>
                    {plan.level && (
                      <p className="text-xs text-gray-500">{plan.level}</p>
                    )}
                    <p className="text-xs text-gray-400">
                      {new Date(plan.uploadedAt).toLocaleDateString('pt-PT')}
                    </p>
                  </div>
                </div>
              </button>
            ))}

            {plans.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <FileText className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">Nenhuma planta carregada</p>
                <p className="text-xs">Faça upload de PDFs ou DWG</p>
              </div>
            )}
          </div>
        </Card>

        {/* Viewer */}
        <Card className="col-span-9 relative overflow-hidden bg-gray-100">
          {selectedPlan ? (
            <>
              {/* Toolbar */}
              <div className="absolute top-4 left-1/2 -translate-x-1/2 flex items-center gap-1 bg-white rounded-lg shadow-lg p-1 z-10">
                <Button variant="ghost" size="sm" onClick={handleZoomOut}>
                  <ZoomOut className="w-4 h-4" />
                </Button>
                <span className="text-sm text-gray-600 min-w-[60px] text-center">
                  {Math.round(zoom * 100)}%
                </span>
                <Button variant="ghost" size="sm" onClick={handleZoomIn}>
                  <ZoomIn className="w-4 h-4" />
                </Button>
                <div className="w-px h-4 bg-gray-200 mx-1" />
                <Button variant="ghost" size="sm" onClick={handleRotate}>
                  <RotateCw className="w-4 h-4" />
                </Button>
                <div className="w-px h-4 bg-gray-200 mx-1" />
                <Button 
                  variant={showHotspots ? 'secondary' : 'ghost'} 
                  size="sm"
                  onClick={() => setShowHotspots(!showHotspots)}
                >
                  <MapPin className="w-4 h-4" />
                </Button>
              </div>

              {/* Document Viewer */}
              <div 
                className="w-full h-full overflow-auto flex items-center justify-center p-8"
                style={{
                  cursor: zoom > 1 ? 'grab' : 'default',
                }}
              >
                <div 
                  className="relative transition-transform duration-200"
                  style={{
                    transform: `scale(${zoom}) rotate(${rotation}deg)`,
                    transformOrigin: 'center center',
                  }}
                >
                  {/* PDF/Document placeholder */}
                  <div 
                    className="bg-white shadow-lg"
                    style={{
                      width: '595px', // A4 width at 72 DPI
                      height: '842px', // A4 height at 72 DPI
                      minWidth: '595px',
                      minHeight: '842px',
                    }}
                  >
                    {/* Placeholder content */}
                    <div className="w-full h-full flex flex-col items-center justify-center text-gray-300 border-2 border-dashed border-gray-200">
                      <FileText className="w-16 h-16 mb-4" />
                      <p className="text-lg font-medium">{selectedPlan.name}</p>
                      <p className="text-sm">Visualizador PDF não disponível na demonstração</p>
                    </div>

                    {/* Hotspots */}
                    {showHotspots && selectedPlan.hotspots?.map((hotspot) => (
                      <button
                        key={hotspot.id}
                        onClick={() => handleHotspotClick(hotspot)}
                        className="absolute transform -translate-x-1/2 -translate-y-1/2 group"
                        style={{
                          left: `${hotspot.x}%`,
                          top: `${hotspot.y}%`,
                        }}
                        title={hotspot.label}
                      >
                        <div className="relative">
                          <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                            <MapPin className="w-4 h-4 text-white" />
                          </div>
                          <div className="absolute top-full left-1/2 -translate-x-1/2 mt-1 bg-gray-900 text-white text-xs px-2 py-1 rounded whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity">
                            {hotspot.label}
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Navigation arrows */}
              <button 
                className="absolute left-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-white rounded-full shadow-lg flex items-center justify-center hover:bg-gray-50"
                onClick={() => {
                  const currentIndex = plans.findIndex(p => p.id === selectedPlan.id);
                  if (currentIndex > 0) {
                    setSelectedPlan(plans[currentIndex - 1]);
                  }
                }}
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <button 
                className="absolute right-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-white rounded-full shadow-lg flex items-center justify-center hover:bg-gray-50"
                onClick={() => {
                  const currentIndex = plans.findIndex(p => p.id === selectedPlan.id);
                  if (currentIndex < plans.length - 1) {
                    setSelectedPlan(plans[currentIndex + 1]);
                  }
                }}
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-gray-400">
              <Layers className="w-16 h-16 mb-4" />
              <p className="text-lg">Selecione uma planta</p>
              <p className="text-sm">Escolha um documento da lista</p>
            </div>
          )}
        </Card>
      </div>

      {/* Hotspot Info Panel */}
      {selectedHotspot && (
        <Card className="mt-4 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <MapPin className="w-5 h-5 text-blue-500" />
              <div>
                <p className="font-medium">{selectedHotspot.label}</p>
                <p className="text-sm text-gray-500">
                  Tipo: {selectedHotspot.targetType === 'unit' ? 'Unidade' : 'Elemento BIM'}
                </p>
              </div>
            </div>
            <div className="flex gap-2">
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => {
                  if (selectedHotspot.targetType === 'bim_element') {
                    router.push(`/projects/${projectId}/bim?element=${selectedHotspot.targetId}`);
                  }
                }}
              >
                <Eye className="w-4 h-4 mr-1" />
                Ver no BIM
              </Button>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => setSelectedHotspot(null)}
              >
                Fechar
              </Button>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
