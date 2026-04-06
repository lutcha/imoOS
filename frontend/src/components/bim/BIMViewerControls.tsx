'use client';

/**
 * BIMViewerControls - Controlos do visualizador BIM
 * 
 * Botões flutuantes para: reset view, zoom to fit, toggle grid, etc.
 */

import React from 'react';
import {
  RotateCcw,
  Maximize,
  Grid3X3,
  Eye,
  EyeOff,
  Layers,
  Camera,
} from 'lucide-react';

export interface BIMViewerControlsProps {
  onResetView?: () => void;
  onZoomToFit?: () => void;
  onToggleGrid?: () => void;
  onToggleAxes?: () => void;
  onToggleWireframe?: () => void;
  onScreenshot?: () => void;
  className?: string;
}

export function BIMViewerControls({
  onResetView,
  onZoomToFit,
  onToggleGrid,
  onToggleAxes,
  onToggleWireframe,
  onScreenshot,
  className = '',
}: BIMViewerControlsProps) {
  return (
    <div className={`absolute top-4 right-4 flex flex-col gap-2 ${className}`}>
      {/* View Controls */}
      <div className="bg-white rounded-lg shadow-lg p-1.5 flex flex-col gap-1">
        <ControlButton
          onClick={onResetView}
          title="Reset View (R)"
          icon={<RotateCcw className="w-4 h-4" />}
        />
        <ControlButton
          onClick={onZoomToFit}
          title="Zoom to Fit (F)"
          icon={<Maximize className="w-4 h-4" />}
        />
        <ControlButton
          onClick={onScreenshot}
          title="Screenshot (S)"
          icon={<Camera className="w-4 h-4" />}
        />
      </div>

      {/* Display Controls */}
      <div className="bg-white rounded-lg shadow-lg p-1.5 flex flex-col gap-1">
        <ControlButton
          onClick={onToggleGrid}
          title="Toggle Grid (G)"
          icon={<Grid3X3 className="w-4 h-4" />}
        />
        <ControlButton
          onClick={onToggleAxes}
          title="Toggle Axes (A)"
          icon={<Layers className="w-4 h-4" />}
        />
        <ControlButton
          onClick={onToggleWireframe}
          title="Toggle Wireframe (W)"
          icon={<WireframeIcon />}
        />
      </div>
    </div>
  );
}

interface ControlButtonProps {
  onClick?: () => void;
  title: string;
  icon: React.ReactNode;
  active?: boolean;
}

function ControlButton({ onClick, title, icon, active }: ControlButtonProps) {
  return (
    <button
      onClick={onClick}
      title={title}
      className={`
        p-2 rounded-md transition-colors
        ${active 
          ? 'bg-blue-100 text-blue-600' 
          : 'hover:bg-gray-100 text-gray-600'
        }
      `}
    >
      {icon}
    </button>
  );
}

function WireframeIcon() {
  return (
    <svg
      className="w-4 h-4"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <rect x="3" y="3" width="18" height="18" rx="2" />
      <path d="M3 9h18" />
      <path d="M9 21V9" />
    </svg>
  );
}

export default BIMViewerControls;
