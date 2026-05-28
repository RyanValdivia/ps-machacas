import React, { useState, useEffect } from 'react';
import { X, Printer } from 'lucide-react';
import type { CartItem, Customer, FormaPago } from '../../../../../auth/types/sale/sale';
import type { OpticalCenter } from '../../../../../types/opticalCenter';
import { getOpticalCenter } from '../../../../../services/opticalConfigService';

interface TicketPreviewProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  cart: CartItem[];
  customer: Customer | null;
  paymentMethod: FormaPago;
  adelanto: number;
  totalVenta: number;
  vendorName: string;
  observaciones?: string;
}

const TicketPreview: React.FC<TicketPreviewProps> = ({
  isOpen,
  onClose,
  onConfirm,
  cart,
  customer,
  paymentMethod,
  adelanto,
  totalVenta,
  vendorName,
  observaciones
}) => {
  const [opticalCenter, setOpticalCenter] = useState<OpticalCenter | null>(null);
  const [loadingOptical, setLoadingOptical] = useState(true);

  useEffect(() => {
    const loadOpticalCenter = async () => {
      try {
        const data = await getOpticalCenter();
        setOpticalCenter(data);
      } catch (error) {
        console.error('❌ Error cargando datos de la óptica:', error);
      } finally {
        setLoadingOptical(false);
      }
    };

    if (isOpen) {
      loadOpticalCenter();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const saldoPendiente = totalVenta - adelanto;
  const fechaActual = new Date().toLocaleString('es-PE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });

  return (
    <div className="fixed inset-0 bg-blur-sm backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-2xl max-w-md w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center space-x-2">
            <Printer className="w-5 h-5 text-blue-600" />
            <h2 className="text-lg font-bold text-gray-800">Vista Previa del Ticket</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Ticket Preview */}
        <div className="flex-1 overflow-y-auto p-4" style={{ fontFamily: '"Arial", sans-serif' }}>
          <div className="bg-white border-2 border-gray-300 rounded-lg p-2 text-xs">
            {/* Header del Ticket */}
            <div className="text-center pb-1 mb-1">
              {opticalCenter?.optLogo && (
                <img
                  src={opticalCenter.optLogo}
                  alt="Logo"
                  className="h-20 w-auto object-contain mx-auto mb-1"
                  style={{ imageRendering: 'crisp-edges' }}
                />
              )}
              <p className="text-base font-bold tracking-wide">
                {opticalCenter?.optNom || 'OPTICA VISION IDEAL'}
              </p>
              {opticalCenter?.optDir && (
                <p className="text-[10px] font-medium text-gray-700">
                  {opticalCenter.optDir.toUpperCase()}
                </p>
              )}
              {opticalCenter?.optTel && (
                <p className="text-[10px] font-medium text-gray-700">
                  TEL: {opticalCenter.optTel}
                </p>
              )}
              <p className="text-xs text-gray-600">{"=".repeat(44)}</p>
            </div>

            {/* Título NOTA DE VENTA */}
            <div className="text-center mb-1">
              <h4 className="text-lg font-extrabold">NOTA DE VENTA</h4>
              <p className="text-xs">RUC: 10296530722</p>
            </div>
            <p className="text-xs text-gray-600">{"-".repeat(44)}</p>

            {/* Información de la Venta */}
            <div className="space-y-0.5 mb-2 text-[10px]">
              <p>Nro: {fechaActual.split(',')[0]}</p>
              <p>Fecha: {fechaActual}</p>
              {vendorName && <p>Atendió: {vendorName}</p>}
              {customer?.cliNombreCom && <p>Cliente: {customer.cliNombreCom}</p>}
            </div>
            <p className="text-xs text-gray-600">{"-".repeat(44)}</p>

            {/* Productos */}
            <div className="py-1 mb-2">
              <p className="text-[10px] font-bold">CANT DESCRIPCION                IMPORTE</p>
              <p className="text-xs text-gray-600">{"-".repeat(44)}</p>
              {cart.map((item, index) => (
                <div key={index} className="mb-1 text-[10px]">
                  <p>
                    {item.quantity} {item.product.prodDescr.padEnd(26, " ")} S/{item.total.toFixed(2)}
                  </p>
                  {item.discountAmount > 0 && (
                    <p className="text-[9px] text-red-600">Desc: -S/{item.discountAmount.toFixed(2)}</p>
                  )}
                  <p className="text-xs text-gray-600">{"-".repeat(44)}</p>
                </div>
              ))}
            </div>

            {/* Totales */}
            <div className="space-y-0.5 text-[10px]">
              <p>Subtotal: S/{totalVenta.toFixed(2)}</p>
              <div className="text-center font-bold text-lg mt-2">
                TOTAL: S/{totalVenta.toFixed(2)}
              </div>
              {adelanto > 0 && (
                <>
                  <p>Adelanto: S/{adelanto.toFixed(2)}</p>
                  {saldoPendiente > 0 ? (
                    <>
                      <p>Saldo: S/{saldoPendiente.toFixed(2)}</p>
                      <div className="text-center text-blue-600 font-bold text-[11px] mt-1">
                        A CUENTA
                      </div>
                    </>
                  ) : (
                    <div className="text-center text-green-600 font-bold text-[11px] mt-1">
                      CANCELADO
                    </div>
                  )}
                  <div className="text-center text-[9px] text-gray-600 mt-0.5">
                    {paymentMethod}
                  </div>
                </>
              )}
            </div>

            {/* Observaciones */}
            {observaciones && (
              <div className="mt-2 pt-1">
                <p className="text-[9px] font-bold">OBS:</p>
                <p className="text-[9px] leading-tight text-gray-700">{observaciones}</p>
              </div>
            )}

            {/* Footer del Ticket */}
            <div className="text-center mt-2 pt-1">
              <p className="text-[9px] text-gray-700">
                Representación impresa de Nota de Venta
              </p>
              <p className="text-[9px] text-gray-700 leading-tight">
                Es normal notar cierto mareo y hasta dolor de cabeza durante primeros días,
                si persiste por favor acuda a una revisión con nosotros.
              </p>
              <p className="text-[10px] font-bold text-gray-800 mt-1">
                ¡Gracias por su compra!
              </p>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3 p-4 border-t border-gray-200 bg-gray-50">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2.5 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors font-medium"
          >
            Cancelar
          </button>
          <button
            onClick={onConfirm}
            className="flex-1 px-4 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium flex items-center justify-center gap-2"
          >
            <Printer className="w-4 h-4" />
            Confirmar e Imprimir
          </button>
        </div>
      </div>
    </div>
  );
};

export default TicketPreview;