import { useState, useEffect } from 'react';
import { X, DollarSign, Package, CheckCircle, Trash2, Zap } from 'lucide-react';
import type { VentaResponse } from '../../../auth/types/sale/sale';
import saleService from '../../../auth/services/sale/saleService';
import { 
  showSuccessToast, 
  showErrorToast, 
  showConfirmation,
  showErrorAlert 
} from '../../../utils/sweetAlertConfig';

interface ModalGestionarVentaProps {
  venta: VentaResponse;
  isOpen: boolean;
  onClose: () => void;
  onVentaActualizada: () => void;
}

const ModalGestionarVenta = ({ venta, isOpen, onClose, onVentaActualizada }: ModalGestionarVentaProps) => {
  const [loading, setLoading] = useState(false);
  const [showPagoForm, setShowPagoForm] = useState(false);
  const [showAnularForm, setShowAnularForm] = useState(false);
  const [showCompletarPagoForm, setShowCompletarPagoForm] = useState(false);
  const [ventaCompleta, setVentaCompleta] = useState<any>(null);
  
  // Estados del formulario de pago
  const [montoPago, setMontoPago] = useState('');
  const [formaPago, setFormaPago] = useState<'EFECTIVO' | 'YAPE' | 'VISA'>('EFECTIVO');
  const [formaPagoCompleto, setFormaPagoCompleto] = useState<'EFECTIVO' | 'YAPE' | 'VISA'>('EFECTIVO');
  const [referenciaPago, setReferenciaPago] = useState('');
  const [tarjetaTipo, setTarjetaTipo] = useState<'VISA' | ''>('');
  
  // Estado del formulario de anulación
  const [motivoAnulacion, setMotivoAnulacion] = useState('');

  useEffect(() => {
    if (isOpen && venta.ventCod) {
      fetchVentaCompleta();
    }
  }, [isOpen, venta.ventCod]);

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

  const fetchVentaCompleta = async () => {
    try {
      const ventaData = await saleService.getVentaById(venta.ventCod);
      setVentaCompleta(ventaData);
    } catch (error) {
      console.error('Error al cargar datos completos de venta:', error);
      setVentaCompleta(venta);
    }
  };
  
  if (!isOpen) return null;

  const ventaActual = ventaCompleta || venta;

  const formatCurrency = (value: string | number | undefined | null) => {
    if (value === undefined || value === null || value === '') return '0.00';
    const num = typeof value === 'string' ? parseFloat(value) : value;
    return isNaN(num) ? '0.00' : num.toFixed(2);
  };

  const saldo = ventaActual.ventSaldo || 0;

  const handleRegistrarPago = async () => {
    if (!montoPago || parseFloat(montoPago) <= 0) {
      showErrorToast('Ingrese un monto válido');
      return;
    }

    if (parseFloat(montoPago) > parseFloat(String(saldo))) {
      showErrorAlert('Monto inválido', `El monto no puede exceder el saldo pendiente (S/ ${formatCurrency(saldo)})`);
      return;
    }
  
    setLoading(true);
    try {
      const data = await saleService.registrarPago(ventaActual.ventCod, {
        monto: parseFloat(montoPago),
        forma_pago: formaPago,
        referencia_pago: referenciaPago || undefined,
        tarjeta_tipo: tarjetaTipo || undefined,
      });
      
      showSuccessToast(`${data.mensaje}. Saldo actual: S/ ${formatCurrency(data.saldo_actual || 0)}`);
      setMontoPago('');
      setReferenciaPago('');
      setTarjetaTipo('');
      setShowPagoForm(false);
      await fetchVentaCompleta();
      onVentaActualizada();
    } catch (error: any) {
      console.error('Error:', error);
      showErrorAlert('Error al registrar pago', error.response?.data?.error || error.message || 'Error al registrar el pago');
    } finally {
      setLoading(false);
    }
  };

  const enviarMensajeWhatsApp = (telefono: string, nombre: string) => {
    if (!telefono) return;

    const mensaje = `Buenas ${nombre}, le hablamos de parte de Vision Ideal. 
                      Queremos avisarle que su pedido ya está listo para recoger. 
                      ¡Lo esperamos!`;

    const mensajeCodificado = encodeURIComponent(mensaje);

    // limpiar teléfono (solo números)
    const telefonoLimpio = telefono.replace(/\D/g, '');

    const url = `https://wa.me/51${telefonoLimpio}?text=${mensajeCodificado}`;
    window.open(url, '_blank');
  };


  const handleMarcarListo = async () => {
    const result = await showConfirmation(
      '¿Marcar como lista?',
      '¿Esta venta está lista para recoger?',
      'Sí, marcar como lista',
      'Cancelar'
    );
    
    if (!result.isConfirmed) return;
  
    setLoading(true);
    try {
      await saleService.marcarListo(ventaActual.ventCod);
      showSuccessToast('Venta marcada como lista para recoger');

      enviarMensajeWhatsApp(
        ventaActual.cliente?.cliTelefono || ventaActual.telefono_cliente,
        ventaActual.cliente?.cliNomCompleto || ventaActual.nombre_cliente || 'cliente'
      );

      await fetchVentaCompleta();
      onVentaActualizada();
      
    } catch (error: any) {
      console.error('Error:', error);
      showErrorAlert('Error', error.response?.data?.error || error.message || 'Error al marcar como listo');
    } finally {
      setLoading(false);
    }
  };

  const handleMarcarEntregado = async () => {
    const result = await showConfirmation(
      '¿Marcar como entregada?',
      'Confirmar que esta venta ha sido entregada al cliente',
      'Sí, marcar como entregada',
      'Cancelar'
    );
    
    if (!result.isConfirmed) return;
  
    setLoading(true);
    try {
      await saleService.marcarEntregado(ventaActual.ventCod);
      showSuccessToast('Venta marcada como entregada');
      await fetchVentaCompleta();
      onVentaActualizada();
    } catch (error: any) {
      console.error('Error:', error);
      showErrorAlert('Error', error.response?.data?.error || error.message || 'Error al marcar como entregado');
    } finally {
      setLoading(false);
    }
  };

  const handleAnularVenta = async () => {
    if (!motivoAnulacion.trim()) {
      showErrorToast('Ingrese el motivo de anulación');
      return;
    }
  
    const result = await showConfirmation(
      '⚠️ ¿Anular venta?',
      'Esta acción es irreversible. La venta será anulada permanentemente.',
      'Sí, anular venta',
      'Cancelar'
    );
    
    if (!result.isConfirmed) return;
  
    setLoading(true);
    try {
      await saleService.anularVenta(ventaActual.ventCod, {
        motivo: motivoAnulacion,
      });
      showSuccessToast('Venta anulada exitosamente');
      onVentaActualizada();
      onClose();
    } catch (error: any) {
      console.error('Error:', error);
      showErrorAlert('Error al anular', error.response?.data?.error || error.message || 'Error al anular la venta');
    } finally {
      setLoading(false);
    }
  };

  const handleCompletarPago = async () => {
    const result = await showConfirmation(
      'Completar pago',
      `¿Completar el pago de S/ ${formatCurrency(saldo)} con ${formaPagoCompleto}?`,
      'Sí, completar pago',
      'Cancelar'
    );
    
    if (!result.isConfirmed) return;
  
    setLoading(true);
    try {
      const data = await saleService.registrarPago(ventaActual.ventCod, {
        monto: parseFloat(saldo.toString()),
        forma_pago: formaPagoCompleto,
        referencia_pago: undefined,
        tarjeta_tipo: undefined,
      });
      
      showSuccessToast(`${data.mensaje}. Venta completamente pagada.`);
      setShowCompletarPagoForm(false);
      setFormaPagoCompleto('EFECTIVO'); // Reset a efectivo
      await fetchVentaCompleta();
      onVentaActualizada();
    } catch (error: any) {
      console.error('Error:', error);
      showErrorAlert('Error al completar pago', error.response?.data?.error || error.message || 'Error al completar el pago');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center z-50 p-4 bg-black/20 backdrop-blur-sm">
      <div className="bg-white rounded-xl shadow-lg w-full max-w-lg max-h-[90vh] overflow-hidden border border-gray-200">
        {/* Header */}
        <div className="bg-white px-6 py-4 flex justify-between items-center border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Gestionar Venta</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg p-1.5 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-5 overflow-y-auto max-h-[calc(90vh-120px)]">
          {/* Información de la venta */}
          <div className="bg-gray-50 border border-gray-200 px-4 py-3 rounded-xl">
            <div className="flex justify-between items-start mb-2">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  Venta #{String(ventaActual.ventCod).padStart(6, "0")}
                </h3>
                <p className="text-sm text-gray-600">
                  {ventaActual.cliente?.cliNomCompleto || ventaActual.nombre_cliente || 'Cliente Genérico'}
                </p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-gray-900">S/ {formatCurrency(ventaActual.ventTotal)}</p>
                <p className="text-sm text-red-600">Saldo: S/ {formatCurrency(saldo)}</p>
              </div>
            </div>
            <div className="flex space-x-2 mt-2">
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                ventaActual.ventEstado === 'PAGADO' ? 'bg-green-100 text-green-800' :
                ventaActual.ventEstado === 'PARCIAL' ? 'bg-orange-100 text-orange-800' :
                ventaActual.ventEstado === 'ANULADO' ? 'bg-red-100 text-red-800' :
                'bg-yellow-100 text-yellow-800'
              }`}>
                {ventaActual.estado_pago_display}
              </span>
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                ventaActual.ventEstadoRecoj === 'ENTREGADO' ? 'bg-green-100 text-green-800' :
                ventaActual.ventEstadoRecoj === 'LISTO' ? 'bg-violet-100 text-violet-800' :
                ventaActual.ventEstadoRecoj === 'LABORATORIO' ? 'bg-cyan-100 text-cyan-800' :
                ventaActual.ventEstadoRecoj === 'ANULADO' ? 'bg-red-100 text-red-800' :
                'bg-yellow-100 text-yellow-800'
              }`}>
                {ventaActual.estado_pedido_display}
              </span>
            </div>
          </div>

          {/* SECCIÓN PAGOS */}
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-gray-700 uppercase tracking-wide border-b border-gray-200 pb-2">
              Pagos
            </h3>
            
            {/* Botones de acción de pago */}
            {!showPagoForm && !showCompletarPagoForm ? (
              <div className="space-y-2">
                {/* Botón Completar Pago */}
                <button
                  onClick={() => setShowCompletarPagoForm(true)}
                  disabled={loading || ventaActual.ventEstado === 'PAGADO' || ventaActual.ventAnulada || saldo <= 0}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white px-4 py-3 rounded-lg font-medium transition-colors flex items-center justify-between"
                >
                  <div className="flex items-center space-x-3">
                    <Zap className="w-5 h-5" />
                    <div className="text-left">
                      <div className="font-medium">Completar Pago</div>
                      <div className="text-xs opacity-90">Cancelar S/ {formatCurrency(saldo)}</div>
                    </div>
                  </div>
                </button>

                {/* Botón Registrar Pago */}
                <button
                  onClick={() => setShowPagoForm(true)}
                  disabled={loading || ventaActual.ventEstado === 'PAGADO' || ventaActual.ventAnulada}
                  className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white px-4 py-3 rounded-lg font-medium transition-colors flex items-center justify-between"
                >
                  <div className="flex items-center space-x-3">
                    <DollarSign className="w-5 h-5" />
                    <div className="text-left">
                      <div className="font-medium">Registrar Pago Parcial</div>
                      <div className="text-xs opacity-90">Pendiente: S/ {formatCurrency(saldo)}</div>
                    </div>
                  </div>
                </button>
              </div>
            ) : showCompletarPagoForm ? (
              /* Formulario Completar Pago */
              <div className="bg-blue-50 border border-blue-200 p-4 rounded-xl space-y-3">
                <div className="flex justify-between items-center mb-2">
                  <h4 className="font-semibold text-blue-900">Completar Pago</h4>
                  <button
                    onClick={() => {
                      setShowCompletarPagoForm(false);
                      setFormaPagoCompleto('EFECTIVO');
                    }}
                    className="text-blue-600 hover:text-blue-800"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                <div className="bg-white border border-blue-200 rounded-lg p-3 mb-3">
                  <p className="text-sm text-gray-600 mb-1">Monto a pagar:</p>
                  <p className="text-3xl font-bold text-blue-600">S/ {formatCurrency(saldo)}</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Forma de Pago
                  </label>
                  <select
                    value={formaPagoCompleto}
                    onChange={(e) => setFormaPagoCompleto(e.target.value as any)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
                  >
                    <option value="EFECTIVO">Efectivo</option>
                    <option value="YAPE">Yape</option>
                    <option value="VISA">Visa</option>
                  </select>
                </div>

                <button
                  onClick={handleCompletarPago}
                  disabled={loading}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center justify-center space-x-2"
                >
                  <Zap className="w-5 h-5" />
                  <span>{loading ? 'Procesando...' : 'Confirmar Pago Completo'}</span>
                </button>
              </div>
            ) : (
              /* Formulario Registrar Pago Parcial */
              <div className="bg-green-50 border border-green-200 p-4 rounded-xl space-y-3">
                <div className="flex justify-between items-center mb-2">
                  <h4 className="font-semibold text-green-900">Registrar Pago</h4>
                  <button
                    onClick={() => setShowPagoForm(false)}
                    className="text-green-600 hover:text-green-800"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Monto (Saldo: S/ {formatCurrency(saldo)})
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={montoPago}
                    onChange={(e) => setMontoPago(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-green-500"
                    placeholder="0.00"
                    max={parseFloat(saldo.toString())}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Forma de Pago
                  </label>
                  <select
                    value={formaPago}
                    onChange={(e) => setFormaPago(e.target.value as any)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-green-500"
                  >
                    <option value="EFECTIVO">Efectivo</option>
                    <option value="YAPE">Yape</option>
                    <option value="VISA">Visa</option>
                  </select>
                </div>

                {/* Sin campos adicionales para métodos de pago */}

                <button
                  onClick={handleRegistrarPago}
                  disabled={loading}
                  className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                >
                  {loading ? 'Procesando...' : 'Confirmar Pago'}
                </button>
              </div>
            )}
          </div>

          {/* SECCIÓN GESTIÓN */}
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-gray-700 uppercase tracking-wide border-b border-gray-200 pb-2">
              Gestión de Pedido
            </h3>
            
            <button
              onClick={handleMarcarListo}
              disabled={loading || ventaActual.ventEstadoRecoj !== 'PENDIENTE' || ventaActual.ventAnulada}
              className="w-full bg-indigo-500 hover:bg-indigo-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white px-4 py-3 rounded-lg font-medium transition-colors flex items-center justify-between shadow-md"
            >
              <div className="flex items-center space-x-3">
                <Package className="w-5 h-5" />
                <div className="text-left">
                  <div className="font-semibold">Marcar Listo</div>
                  <div className="text-xs opacity-90">
                    Estado: {ventaActual.estado_pedido_display}
                  </div>
                </div>
              </div>
            </button>

            <button
              onClick={handleMarcarEntregado}
              disabled={loading || ventaActual.ventEstadoRecoj !== 'LISTO' || ventaActual.ventAnulada}
              className="w-full bg-teal-500 hover:bg-teal-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white px-4 py-3 rounded-lg font-medium transition-colors flex items-center justify-between shadow-md"
            >
              <div className="flex items-center space-x-3">
                <CheckCircle className="w-5 h-5" />
                <div className="text-left">
                  <div className="font-semibold">Marcar Entregado</div>
                  <div className="text-xs opacity-90">Completar entrega</div>
                </div>
              </div>
            </button>
          </div>

          {/* SECCIÓN ANULAR */}
          <div className="space-y-3">
            <h3 className="text-sm font-bold text-gray-700 uppercase tracking-wide border-b-2 border-gray-300 pb-2">
              Zona de Peligro
            </h3>

            {!showAnularForm ? (
              <button
                onClick={() => setShowAnularForm(true)}
                disabled={loading || ventaActual.ventAnulada}
                className="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white px-4 py-3 rounded-lg font-medium transition-colors flex items-center justify-between shadow-md"
              >
                <div className="flex items-center space-x-3">
                  <Trash2 className="w-5 h-5" />
                  <div className="text-left">
                    <div className="font-semibold">Anular Venta</div>
                    <div className="text-xs opacity-90">Acción irreversible</div>
                  </div>
                </div>
              </button>
            ) : (
              <div className="bg-red-50 border-2 border-red-200 p-4 rounded-lg space-y-3">
                <div className="flex justify-between items-center mb-2">
                  <h4 className="font-bold text-red-900">Anular Venta</h4>
                  <button
                    onClick={() => setShowAnularForm(false)}
                    className="text-red-700 hover:text-red-900"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">
                    Motivo de Anulación *
                  </label>
                  <textarea
                    value={motivoAnulacion}
                    onChange={(e) => setMotivoAnulacion(e.target.value)}
                    className="w-full px-3 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
                    placeholder="Escriba el motivo..."
                    rows={3}
                  />
                </div>

                <button
                  onClick={handleAnularVenta}
                  disabled={loading || !motivoAnulacion.trim()}
                  className="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-semibold transition-colors"
                >
                  {loading ? 'Procesando...' : 'Confirmar Anulación'}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="bg-gray-100 px-5 py-3 flex justify-end border-t-2 border-gray-200">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-medium transition-colors"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
};

export default ModalGestionarVenta;