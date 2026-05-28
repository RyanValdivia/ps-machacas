import { useState, useEffect } from 'react';
import { X, FlaskConical, Save } from 'lucide-react';
import saleService from '../../../auth/services/sale/saleService';
import supplierService from '../../../services/supplierService';
import type { Supplier } from '../../../types/supplier';
import { showSuccessToast, showErrorToast, showErrorAlert } from '../../../utils/sweetAlertConfig';

interface ModalEditarLaboratorioProps {
  detalle: any;
  isOpen: boolean;
  onClose: () => void;
  onActualizado: () => void;
}

const ModalEditarLaboratorio = ({ detalle, isOpen, onClose, onActualizado }: ModalEditarLaboratorioProps) => {
  const [loading, setLoading] = useState(false);
  const [loadingProveedores, setLoadingProveedores] = useState(false);
  const [proveedores, setProveedores] = useState<Supplier[]>([]);
  const [laboratorioId, setLaboratorioId] = useState<number | ''>('');
  const [costo, setCosto] = useState('');

  // Cargar proveedores activos
  useEffect(() => {
    if (isOpen) {
      cargarProveedores();
    }
  }, [isOpen]);

  // Setear valores iniciales
  useEffect(() => {
    if (isOpen && detalle) {
      setLaboratorioId(detalle.lunaLaboratorio_id || '');
      setCosto(detalle.lunaCostoLaboratorio || '');
    }
  }, [isOpen, detalle]);

  const cargarProveedores = async () => {
    setLoadingProveedores(true);
    try {
      const data = await supplierService.getAll({ prov_estado: 'Active' });
      setProveedores(data);
    } catch (error) {
      console.error('Error cargando proveedores:', error);
      showErrorToast('Error al cargar la lista de proveedores');
    } finally {
      setLoadingProveedores(false);
    }
  };

  // ==================== DETECTAR TECLA ESC ====================
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleGuardar = async () => {
    if (!laboratorioId) {
      showErrorToast('Por favor seleccione un laboratorio');
      return;
    }

    if (!costo || parseFloat(costo) <= 0) {
      showErrorToast('Por favor ingrese un costo válido');
      return;
    }

    setLoading(true);
    try {
      await saleService.actualizarLaboratorio(detalle.ventDetCod, {
        lunaLaboratorio: laboratorioId,
        lunaCostoLaboratorio: parseFloat(costo),
      });

      showSuccessToast('Datos del laboratorio actualizados correctamente');
      onActualizado();
      onClose();
    } catch (error: any) {
      console.error('Error:', error);
      showErrorAlert('Error al actualizar', error.response?.data?.error || error.message || 'Error al actualizar');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/20 backdrop-blur-sm">
      <div className="bg-white rounded-xl shadow-lg w-full max-w-md overflow-hidden border border-gray-200">
        {/* Header */}
        <div className="bg-white px-6 py-4 flex justify-between items-center border-b border-gray-200">
          <div className="flex items-center space-x-2">
            <FlaskConical className="w-5 h-5 text-gray-500" />
            <h2 className="text-lg font-semibold text-gray-900">Datos del Laboratorio</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg p-1.5 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-5">
          {/* Información del producto */}
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-3">
            <p className="text-xs text-gray-500 mb-1">Producto</p>
            <p className="text-sm font-medium text-gray-900">
              {detalle?.ventDetDescripcion || 'Luna Personalizada'}
            </p>
            {detalle?.ventDetMarca && (
              <p className="text-xs text-gray-600 mt-1">{detalle.ventDetMarca}</p>
            )}
          </div>

          {/* Campo Laboratorio */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Laboratorio <span className="text-red-500">*</span>
            </label>
            {loadingProveedores ? (
              <div className="text-sm text-gray-500 py-2">Cargando proveedores...</div>
            ) : (
              <select
                value={laboratorioId}
                onChange={(e) => setLaboratorioId(e.target.value ? parseInt(e.target.value) : '')}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-gray-400 focus:border-gray-400 text-sm"
                disabled={loading}
              >
                <option value="">Seleccione un laboratorio</option>
                {proveedores.map((prov) => (
                  <option key={prov.provCod} value={prov.provCod}>
                    {prov.provRazSocial}
                  </option>
                ))}
              </select>
            )}
          </div>

          {/* Campo Costo */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Costo (S/) <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              step="0.01"
              min="0"
              value={costo}
              onChange={(e) => setCosto(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-gray-400 focus:border-gray-400 text-sm"
              placeholder="0.00"
              disabled={loading}
            />
          </div>
        </div>

        {/* Footer */}
        <div className="bg-white px-6 py-4 flex justify-end space-x-3 border-t border-gray-200">
          <button
            onClick={onClose}
            disabled={loading}
            className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 disabled:opacity-50 rounded-lg font-medium transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={handleGuardar}
            disabled={loading}
            className="px-4 py-2 text-sm bg-black hover:bg-gray-800 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors flex items-center space-x-2"
          >
            <Save className="w-4 h-4" />
            <span>{loading ? 'Guardando...' : 'Guardar'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default ModalEditarLaboratorio;
