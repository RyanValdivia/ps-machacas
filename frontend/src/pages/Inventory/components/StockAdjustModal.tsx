// Inventory/components/StockAdjustModal.tsx

import React, { useState } from 'react';
import Modal from '../../../components/Modal/modal';
import type { Product } from '../../../auth/types/product/product';
import { showErrorToast, showWarningToast } from '../../../utils/sweetAlertConfig';

interface StockAdjustModalProps {
  isOpen: boolean;
  onClose: () => void;
  product: Product | null;
  onAdjust: (productId: number, cantidad: number, tipo: 'entrada' | 'salida') => Promise<void>;
}

const StockAdjustModal: React.FC<StockAdjustModalProps> = ({
  isOpen,
  onClose,
  product,
  onAdjust,
}) => {
  const [tipo, setTipo] = useState<'entrada' | 'salida'>('entrada');
  const [cantidad, setCantidad] = useState<number>(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!product) return;

    if (cantidad <= 0) {
      showWarningToast('La cantidad debe ser mayor a 0');
      setError('La cantidad debe ser mayor a 0');
      return;
    }

    if (tipo === 'salida' && cantidad > product.prodStock) {
      showWarningToast(`Stock insuficiente. Disponible: ${product.prodStock}`);
      setError(`Stock insuficiente. Disponible: ${product.prodStock}`);
      return;
    }

    setLoading(true);
    setError('');

    try {
      await onAdjust(product.prodCod, cantidad, tipo);
      onClose();
      // Resetear
      setCantidad(1);
      setTipo('entrada');
    } catch (err: any) {
      const errorMsg = err.response?.data?.error || 'Error al ajustar stock';
      setError(errorMsg);
      showErrorToast(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const nuevoStock = product
    ? tipo === 'entrada'
      ? product.prodStock + cantidad
      : product.prodStock - cantidad
    : 0;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Ajustar Stock" size="sm">
      {product && (
        <div className="space-y-4">
          {/* Info del producto */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-gray-900">{product.prodDescr}</h4>
            <p className="text-sm text-gray-600">Código: {product.prodCode}</p>
            <p className="text-lg font-bold text-blue-600 mt-2">
              Stock actual: {product.prodStock}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Tipo de movimiento */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tipo de Movimiento
              </label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setTipo('entrada')}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    tipo === 'entrada'
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Entrada
                </button>
                <button
                  type="button"
                  onClick={() => setTipo('salida')}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    tipo === 'salida'
                      ? 'bg-red-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Salida
                </button>
              </div>
            </div>

            {/* Cantidad */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Cantidad
              </label>
              <input
                type="number"
                min="1"
                value={cantidad}
                onChange={(e) => {
                  setCantidad(parseInt(e.target.value) || 1);
                  setError('');
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
              />
            </div>

            {/* Previsualización */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <p className="text-sm text-blue-800">
                <span className="font-semibold">Stock después del ajuste:</span>{' '}
                <span className={nuevoStock < 0 ? 'text-red-600 font-bold' : 'font-bold'}>
                  {nuevoStock}
                </span>
              </p>
            </div>

            {/* Error */}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}

            {/* Botones */}
            <div className="flex justify-end gap-3 pt-4 border-t">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                disabled={loading}
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                disabled={loading || nuevoStock < 0}
              >
                {loading ? 'Guardando...' : 'Confirmar Ajuste'}
              </button>
            </div>
          </form>
        </div>
      )}
    </Modal>
  );
};

export default StockAdjustModal;