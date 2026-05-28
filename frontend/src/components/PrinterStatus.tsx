import React, { useState, useEffect } from 'react';
import { printerService } from '../auth/services/printer/printerService';

interface PrinterStatusProps {
  className?: string;
  onStatusChange?: (isConnected: boolean) => void;
}

export const PrinterStatus: React.FC<PrinterStatusProps> = ({ 
  className = '', 
  onStatusChange 
}) => {
  const [isChecking, setIsChecking] = useState(false);
  const [isConnected, setIsConnected] = useState<boolean | null>(null);
  const [lastError, setLastError] = useState<string>('');
  const [lastCheck, setLastCheck] = useState<Date | null>(null);

  const checkPrinterStatus = async () => {
    setIsChecking(true);
    setLastError('');

    try {
      const result = await printerService.probarImpresora();
      const connected = result.success;
      
      setIsConnected(connected);
      setLastCheck(new Date());
      
      if (!connected && result.error) {
        setLastError(result.error);
      }
      
      if (onStatusChange) {
        onStatusChange(connected);
      }
    } catch (error: any) {
      setIsConnected(false);
      setLastError(error.message || 'Error al verificar impresora');
      
      if (onStatusChange) {
        onStatusChange(false);
      }
    } finally {
      setIsChecking(false);
    }
  };

  useEffect(() => {
    // Verificar al montar
    checkPrinterStatus();
    
    // Verificar cada 5 minutos
    const interval = setInterval(checkPrinterStatus, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = () => {
    if (isChecking) {
      return (
        <div className="flex items-center gap-2 text-blue-600">
          <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-600 border-t-transparent"></div>
          <span className="text-xs">Verificando...</span>
        </div>
      );
    }

    if (isConnected === null) {
      return (
        <div className="flex items-center gap-2 text-gray-500">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="text-xs">Sin verificar</span>
        </div>
      );
    }

    if (isConnected) {
      return (
        <div className="flex items-center gap-2 text-green-600">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="text-xs font-medium">Impresora lista</span>
        </div>
      );
    }

    return (
      <div className="flex items-center gap-2 text-red-600">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span className="text-xs font-medium">Impresora desconectada</span>
      </div>
    );
  };

  return (
    <div className={`bg-white rounded-lg shadow-sm border p-3 ${className}`}>
      <div className="flex items-center justify-between">
        {getStatusIcon()}
        
        <button
          onClick={checkPrinterStatus}
          disabled={isChecking}
          className="text-xs px-3 py-1 rounded-md bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          title="Verificar conexión"
        >
          🔄 Verificar
        </button>
      </div>

      {lastError && (
        <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700">
          <p className="font-medium">⚠️ {lastError}</p>
        </div>
      )}

      {lastCheck && (
        <div className="mt-2 text-xs text-gray-500">
          Última verificación: {lastCheck.toLocaleTimeString('es-PE', { 
            hour: '2-digit', 
            minute: '2-digit' 
          })}
        </div>
      )}
    </div>
  );
};

export default PrinterStatus;
