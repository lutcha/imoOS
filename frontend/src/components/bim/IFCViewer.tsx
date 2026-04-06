'use client';

/**
 * IFCViewer - Componente principal do visualizador BIM 3D
 * 
 * Usa Three.js + @thatopen/components para renderizar modelos IFC
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { IFCLoader, getColorByStatus, getColorByPhase, IFCLoadProgress } from '@/lib/bim/ifc-loader';
import type { BIMElement } from '@/hooks/useBIMElements';
import { BIMViewerControls } from './BIMViewerControls';

export interface IFCViewerProps {
  projectId: string;
  modelUrl: string | null;
  selectedElements?: string[];
  onElementSelect?: (guid: string, properties: any) => void;
  onElementHover?: (guid: string | null) => void;
  colorBy?: 'status' | 'phase' | 'responsible' | 'type' | 'none';
  elements?: BIMElement[];
  className?: string;
}

interface ViewerState {
  loading: boolean;
  progress: number;
  message: string;
  error: string | null;
}

export function IFCViewer({
  projectId,
  modelUrl,
  selectedElements = [],
  onElementSelect,
  onElementHover,
  colorBy = 'none',
  elements = [],
  className = '',
}: IFCViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const controlsRef = useRef<OrbitControls | null>(null);
  const loaderRef = useRef<IFCLoader | null>(null);
  const fragmentsRef = useRef<any>(null);
  const raycasterRef = useRef<THREE.Raycaster | null>(null);
  const mouseRef = useRef<THREE.Vector2>(new THREE.Vector2());
  const highlightMeshRef = useRef<THREE.Mesh | null>(null);
  const animationFrameRef = useRef<number | null>(null);

  const [state, setState] = useState<ViewerState>({
    loading: false,
    progress: 0,
    message: '',
    error: null,
  });

  const [isInitialized, setIsInitialized] = useState(false);

  // Inicializa o viewer Three.js
  const initializeViewer = useCallback(() => {
    if (!containerRef.current || isInitialized) return;

    // Scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf5f5f5);
    
    // Grid
    const grid = new THREE.GridHelper(50, 50, 0x888888, 0xcccccc);
    scene.add(grid);
    
    // Axes
    const axes = new THREE.AxesHelper(5);
    scene.add(axes);

    // Camera
    const camera = new THREE.PerspectiveCamera(
      45,
      containerRef.current.clientWidth / containerRef.current.clientHeight,
      0.1,
      1000
    );
    camera.position.set(20, 20, 20);

    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    containerRef.current.appendChild(renderer.domElement);

    // Controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.target.set(0, 0, 0);

    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 20, 10);
    directionalLight.castShadow = true;
    scene.add(directionalLight);

    // Raycaster
    const raycaster = new THREE.Raycaster();

    // Highlight box (invisible initially)
    const highlightGeometry = new THREE.BoxGeometry(1, 1, 1);
    const highlightMaterial = new THREE.MeshBasicMaterial({
      color: 0x3b82f6,
      transparent: true,
      opacity: 0.3,
      depthTest: false,
    });
    const highlightMesh = new THREE.Mesh(highlightGeometry, highlightMaterial);
    highlightMesh.visible = false;
    scene.add(highlightMesh);

    // Store refs
    sceneRef.current = scene;
    cameraRef.current = camera;
    rendererRef.current = renderer;
    controlsRef.current = controls;
    raycasterRef.current = raycaster;
    highlightMeshRef.current = highlightMesh;

    // Animation loop
    const animate = () => {
      animationFrameRef.current = requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    setIsInitialized(true);
  }, [isInitialized]);

  // Carrega o modelo IFC
  const loadModel = useCallback(async (url: string) => {
    if (!isInitialized || !sceneRef.current) return;

    setState({ loading: true, progress: 0, message: 'A iniciar...', error: null });

    try {
      if (!loaderRef.current) {
        loaderRef.current = new IFCLoader();
        await loaderRef.current.initialize();
      }

      const onProgress = (progress: IFCLoadProgress) => {
        setState(prev => ({
          ...prev,
          progress: progress.progress,
          message: progress.message,
        }));
      };

      const result = await loaderRef.current.loadFromURL(url, onProgress);

      // Adicionar modelo à cena
      if (fragmentsRef.current) {
        sceneRef.current.remove(fragmentsRef.current);
      }
      fragmentsRef.current = result.fragments;
      sceneRef.current.add(result.fragments);

      // Ajustar câmera para fit no modelo
      const box = new THREE.Box3().setFromObject(result.fragments);
      const center = box.getCenter(new THREE.Vector3());
      const size = box.getSize(new THREE.Vector3());
      const maxDim = Math.max(size.x, size.y, size.z);
      
      if (cameraRef.current && controlsRef.current) {
        const distance = maxDim * 1.5;
        cameraRef.current.position.set(
          center.x + distance,
          center.y + distance,
          center.z + distance
        );
        controlsRef.current.target.copy(center);
        controlsRef.current.update();
      }

      setState({ loading: false, progress: 100, message: 'Concluído', error: null });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Erro ao carregar modelo';
      setState({ loading: false, progress: 0, message: '', error: message });
    }
  }, [isInitialized]);

  // Handle mouse move para hover
  const handleMouseMove = useCallback((event: React.MouseEvent) => {
    if (!containerRef.current || !raycasterRef.current || !cameraRef.current || !sceneRef.current) return;

    const rect = containerRef.current.getBoundingClientRect();
    mouseRef.current.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouseRef.current.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    raycasterRef.current.setFromCamera(mouseRef.current, cameraRef.current);

    // Verificar interseções com o modelo
    if (fragmentsRef.current) {
      const intersects = raycasterRef.current.intersectObjects(
        fragmentsRef.current.children,
        true
      );

      if (intersects.length > 0) {
        const intersect = intersects[0];
        
        // Atualizar highlight
        if (highlightMeshRef.current) {
          highlightMeshRef.current.position.copy(intersect.point);
          highlightMeshRef.current.visible = true;
        }

        // Encontrar GUID do elemento
        const object = intersect.object;
        if (object.userData?.guid) {
          onElementHover?.(object.userData.guid);
        }
      } else {
        if (highlightMeshRef.current) {
          highlightMeshRef.current.visible = false;
        }
        onElementHover?.(null);
      }
    }
  }, [onElementHover]);

  // Handle click para seleção
  const handleClick = useCallback((event: React.MouseEvent) => {
    if (!containerRef.current || !raycasterRef.current || !cameraRef.current || !sceneRef.current) return;

    const rect = containerRef.current.getBoundingClientRect();
    mouseRef.current.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouseRef.current.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    raycasterRef.current.setFromCamera(mouseRef.current, cameraRef.current);

    if (fragmentsRef.current) {
      const intersects = raycasterRef.current.intersectObjects(
        fragmentsRef.current.children,
        true
      );

      if (intersects.length > 0) {
        const object = intersects[0].object;
        const guid = object.userData?.guid || object.userData?.expressID?.toString();
        
        if (guid) {
          onElementSelect?.(guid, object.userData);
        }
      }
    }
  }, [onElementSelect]);

  // Handle resize
  const handleResize = useCallback(() => {
    if (!containerRef.current || !cameraRef.current || !rendererRef.current) return;

    const width = containerRef.current.clientWidth;
    const height = containerRef.current.clientHeight;

    cameraRef.current.aspect = width / height;
    cameraRef.current.updateProjectionMatrix();
    rendererRef.current.setSize(width, height);
  }, []);

  // Aplicar color coding
  useEffect(() => {
    if (!fragmentsRef.current || !elements.length) return;

    fragmentsRef.current.traverse((object: THREE.Object3D) => {
      if (object instanceof THREE.Mesh) {
        const guid = object.userData?.guid;
        if (!guid) return;

        const element = elements.find(e => e.guid === guid);
        if (!element) return;

        let color: THREE.Color | null = null;

        switch (colorBy) {
          case 'status':
            if (element.status) {
              color = getColorByStatus(element.status);
            }
            break;
          case 'phase':
            // Usar expressId como índice de fase (simplificado)
            color = getColorByPhase(element.expressId % 8);
            break;
          case 'responsible':
            // Hash do nome para cor
            const hash = element.name.split('').reduce((a, b) => {
              a = ((a << 5) - a) + b.charCodeAt(0);
              return a & a;
            }, 0);
            color = getColorByPhase(Math.abs(hash) % 8);
            break;
        }

        if (color && object.material) {
          if (Array.isArray(object.material)) {
            object.material.forEach(m => {
              if (m instanceof THREE.MeshStandardMaterial) {
                m.color.copy(color!);
              }
            });
          } else if (object.material instanceof THREE.MeshStandardMaterial) {
            object.material.color.copy(color);
          }
        }
      }
    });
  }, [colorBy, elements]);

  // Highlight elementos selecionados
  useEffect(() => {
    if (!fragmentsRef.current) return;

    fragmentsRef.current.traverse((object: THREE.Object3D) => {
      if (object instanceof THREE.Mesh) {
        const guid = object.userData?.guid;
        const isSelected = guid && selectedElements.includes(guid);
        
        if (isSelected) {
          object.userData.originalEmissive = (object.material as THREE.MeshStandardMaterial)?.emissive?.clone();
          if (object.material instanceof THREE.MeshStandardMaterial) {
            object.material.emissive.setHex(0x3b82f6);
            object.material.emissiveIntensity = 0.3;
          }
        } else {
          if (object.userData.originalEmissive && object.material instanceof THREE.MeshStandardMaterial) {
            object.material.emissive.copy(object.userData.originalEmissive);
            object.material.emissiveIntensity = 0;
          }
        }
      }
    });
  }, [selectedElements]);

  // Initialize
  useEffect(() => {
    initializeViewer();
    
    window.addEventListener('resize', handleResize);
    
    return () => {
      window.removeEventListener('resize', handleResize);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (rendererRef.current && containerRef.current) {
        containerRef.current.removeChild(rendererRef.current.domElement);
        rendererRef.current.dispose();
      }
      loaderRef.current?.dispose();
    };
  }, [initializeViewer, handleResize]);

  // Load model when URL changes
  useEffect(() => {
    if (modelUrl && isInitialized) {
      loadModel(modelUrl);
    }
  }, [modelUrl, isInitialized, loadModel]);

  return (
    <div className={`relative w-full h-full ${className}`}>
      {/* Viewer Container */}
      <div
        ref={containerRef}
        className="w-full h-full cursor-crosshair"
        onMouseMove={handleMouseMove}
        onClick={handleClick}
      />

      {/* Loading Overlay */}
      {state.loading && (
        <div className="absolute inset-0 bg-black/50 flex flex-col items-center justify-center text-white">
          <div className="w-64">
            <div className="text-sm mb-2">{state.message}</div>
            <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-500 transition-all duration-300"
                style={{ width: `${state.progress}%` }}
              />
            </div>
            <div className="text-xs text-gray-400 mt-1 text-right">
              {Math.round(state.progress)}%
            </div>
          </div>
        </div>
      )}

      {/* Error Overlay */}
      {state.error && (
        <div className="absolute inset-0 bg-black/70 flex items-center justify-center">
          <div className="bg-white rounded-lg p-6 max-w-md">
            <h3 className="text-lg font-semibold text-red-600 mb-2">Erro</h3>
            <p className="text-gray-700 mb-4">{state.error}</p>
            <button
              onClick={() => setState(prev => ({ ...prev, error: null }))}
              className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-md text-sm"
            >
              Fechar
            </button>
          </div>
        </div>
      )}

      {/* Controls */}
      {isInitialized && (
        <BIMViewerControls
          onResetView={() => {
            if (cameraRef.current && controlsRef.current) {
              cameraRef.current.position.set(20, 20, 20);
              controlsRef.current.target.set(0, 0, 0);
              controlsRef.current.update();
            }
          }}
          onZoomToFit={() => {
            if (fragmentsRef.current && cameraRef.current && controlsRef.current) {
              const box = new THREE.Box3().setFromObject(fragmentsRef.current);
              const center = box.getCenter(new THREE.Vector3());
              const size = box.getSize(new THREE.Vector3());
              const maxDim = Math.max(size.x, size.y, size.z);
              const distance = maxDim * 1.5;
              
              cameraRef.current.position.set(
                center.x + distance,
                center.y + distance,
                center.z + distance
              );
              controlsRef.current.target.copy(center);
              controlsRef.current.update();
            }
          }}
          onToggleGrid={() => {
            sceneRef.current?.children.forEach(child => {
              if (child instanceof THREE.GridHelper) {
                child.visible = !child.visible;
              }
            });
          }}
        />
      )}
    </div>
  );
}

export default IFCViewer;
