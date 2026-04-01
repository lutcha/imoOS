'use client';

import React, { useEffect, useState, useRef } from 'react';
import { useParams } from 'next/navigation';

interface ContractDetails {
  contract_number: string;
  lead_name: string;
  unit_code: string;
  total_price_cve: number;
  expires_at: string;
}

export default function SignContractPage() {
  const { token } = useParams();
  
  const [details, setDetails] = useState<ContractDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [signedByName, setSignedByName] = useState('');
  
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);

  useEffect(() => {
    fetch(`/api/v1/sign/${token}/`)
      .then(res => {
        if (!res.ok) {
          throw new Error('Link de assinatura expirado ou inválido.');
        }
        return res.json();
      })
      .then(data => {
        setDetails(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [token]);

  // Prevent scrolling when drawing on touch devices
  useEffect(() => {
    const preventScroll = (e: TouchEvent) => {
      if (e.target === canvasRef.current) {
        e.preventDefault();
      }
    };
    document.addEventListener('touchmove', preventScroll, { passive: false });
    return () => document.removeEventListener('touchmove', preventScroll);
  }, []);

  const getCoordinates = (e: React.MouseEvent | React.TouchEvent) => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };
    
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    let clientX, clientY;
    if ('touches' in e) {
        clientX = e.touches[0].clientX;
        clientY = e.touches[0].clientY;
    } else {
        clientX = (e as React.MouseEvent).clientX;
        clientY = (e as React.MouseEvent).clientY;
    }

    return {
      x: (clientX - rect.left) * scaleX,
      y: (clientY - rect.top) * scaleY
    };
  };

  const startDrawing = (e: React.MouseEvent | React.TouchEvent) => {
    setIsDrawing(true);
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Smooth lines
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.lineWidth = 3;
    ctx.strokeStyle = '#000';

    const { x, y } = getCoordinates(e);
    ctx.beginPath();
    ctx.moveTo(x, y);
  };

  const draw = (e: React.MouseEvent | React.TouchEvent) => {
    if (!isDrawing) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const { x, y } = getCoordinates(e);
    ctx.lineTo(x, y);
    ctx.stroke();
  };

  const stopDrawing = () => {
    setIsDrawing(false);
  };

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  };

  const submitSignature = async () => {
    if (!signedByName.trim()) {
      alert('Por favor, introduza o seu nome completo.');
      return;
    }
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    // Extrait data URL without the prefix
    const signaturePngBase64 = canvas.toDataURL('image/png').split(',')[1];
    
    setLoading(true);
    try {
      const res = await fetch(`/api/v1/sign/${token}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          signature_png_base64: signaturePngBase64,
          signed_by_name: signedByName,
        })
      });
      
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Falha ao submeter a assinatura.');
      }
      setSuccess(true);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !details && !error) {
    return <div className="p-8 text-center text-gray-500">A carregar detalhes do contrato...</div>;
  }

  if (error) {
    return (
      <div className="max-w-md mx-auto mt-12 p-6 bg-red-50 text-red-600 rounded-lg text-center shadow">
        <h2 className="text-xl font-bold mb-2">Erro na Assinatura</h2>
        <p>{error}</p>
        <p className="mt-4 text-sm text-red-500">Este link expirou ou já foi utilizado. Contacte a promotora para novo link.</p>
      </div>
    );
  }

  if (success) {
    return (
      <div className="max-w-md mx-auto mt-12 p-6 bg-green-50 text-green-700 rounded-lg text-center shadow">
        <svg className="w-16 h-16 mx-auto mb-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
        <h2 className="text-xl font-bold mb-2">Contrato assinado com sucesso!</h2>
        <p>Receberá o PDF completo assinado no seu WhatsApp dentro de breves momentos.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="max-w-xl flex-1 bg-white rounded-xl shadow-md p-6">
        <h1 className="text-2xl font-bold mb-6 text-gray-800 border-b pb-4">Assinatura de Contrato</h1>
        
        {details && (
          <div className="mb-8 p-5 bg-gray-50 border border-gray-100 rounded-lg space-y-3 text-sm text-gray-700">
            <div className="flex justify-between border-b pb-2">
              <span className="font-semibold text-gray-500">Contrato Nº</span>
              <span>{details.contract_number}</span>
            </div>
            <div className="flex justify-between border-b pb-2">
              <span className="font-semibold text-gray-500">Comprador</span>
              <span>{details.lead_name}</span>
            </div>
            <div className="flex justify-between border-b pb-2">
              <span className="font-semibold text-gray-500">Unidade</span>
              <span>{details.unit_code}</span>
            </div>
            <div className="flex justify-between items-center bg-gray-100 p-2 rounded">
              <span className="font-semibold text-gray-500">Valor Total</span>
              <span className="font-bold text-lg">{Number(details.total_price_cve).toLocaleString()} CVE</span>
            </div>
          </div>
        )}

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Nome Completo</label>
            <input 
              type="text"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-shadow"
              placeholder="Digite o seu nome conforme consta no documento"
              value={signedByName}
              onChange={(e) => setSignedByName(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Assinatura Digital</label>
            <div className="border border-gray-300 rounded-lg bg-gray-50 overflow-hidden touch-none relative shadow-inner">
              <canvas
                ref={canvasRef}
                width={800} /* increased internal resolution for better lines */
                height={300}
                className="w-full cursor-crosshair h-48 bg-white"
                onMouseDown={startDrawing}
                onMouseMove={draw}
                onMouseUp={stopDrawing}
                onMouseLeave={stopDrawing}
                onTouchStart={startDrawing}
                onTouchMove={draw}
                onTouchEnd={stopDrawing}
              />
            </div>
            <div className="flex justify-end mt-2">
              <button 
                type="button" 
                onClick={clearCanvas}
                className="text-sm text-gray-500 hover:text-red-500 font-medium transition-colors"
                title="Apagar assinatura atual"
              >
                Limpar assinatura
              </button>
            </div>
          </div>

          <button
            onClick={submitSignature}
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-4 px-4 rounded-lg focus:outline-none focus:ring-4 focus:ring-blue-500 focus:ring-opacity-50 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-md text-lg"
          >
            {loading ? 'A processar...' : 'Confirmar Assinatura'}
          </button>
        </div>
      </div>
    </div>
  );
}
