import { useEffect, useState } from 'react';
import { X, User, CreditCard, FileText, DollarSign, Package, Loader2, AlertCircle, FlaskConical } from 'lucide-react';
import saleService from '../../../auth/services/sale/saleService';
import type { VentaResponse } from '../../../auth/types/sale/sale';
import ModalEditarLaboratorio from './ModalEditarLaboratorio';

interface ModalDetallesVentaProps {
  venta: VentaResponse;
  isOpen: boolean;
  onClose: () => void;
}

const ModalDetallesVenta = ({ venta, isOpen, onClose }: ModalDetallesVentaProps) => {
  const [detalleCompleto, setDetalleCompleto] = useState<any>(null);
  const [detallesProductos, setDetallesProductos] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modalLaboratorioOpen, setModalLaboratorioOpen] = useState(false);
  const [detalleSeleccionado, setDetalleSeleccionado] = useState<any>(null);

  useEffect(() => {
    if (isOpen && venta.ventCod) {
      fetchDetalleCompleto();
    }
  }, [isOpen, venta.ventCod]);

  // ==================== DETECTAR TECLA ESC ====================
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen && !modalLaboratorioOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, onClose, modalLaboratorioOpen]);

  const fetchDetalleCompleto = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [ventaData, detallesData] = await Promise.all([
        saleService.getVentaById(venta.ventCod),
        saleService.getVentaDetalles(venta.ventCod)
      ]);
      
      setDetalleCompleto(ventaData);
      setDetallesProductos(detallesData);
    } catch (err: any) {
      console.error('Error al cargar detalle:', err);
      setError('Error al cargar los detalles de la venta');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-PE', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatCurrency = (value: string | number | undefined | null) => {
    if (value === undefined || value === null || value === '') return '0.00';
    const num = typeof value === 'string' ? parseFloat(value) : value;
    return isNaN(num) ? '0.00' : num.toFixed(2);
  };

  const handleEditarLaboratorio = (detalle: any) => {
    setDetalleSeleccionado(detalle);
    setModalLaboratorioOpen(true);
  };

  const handleLaboratorioActualizado = () => {
    fetchDetalleCompleto();
  };

  const getEstadoPagoConfig = (estado: string) => {
    const configs: Record<string, { text: string; bg: string }> = {
      'PENDIENTE': { text: 'text-amber-700', bg: 'bg-amber-100 border-amber-300' },
      'PARCIAL': { text: 'text-orange-700', bg: 'bg-orange-100 border-orange-300' },
      'PAGADO': { text: 'text-emerald-700', bg: 'bg-emerald-100 border-emerald-300' },
      'ANULADO': { text: 'text-red-700', bg: 'bg-red-100 border-red-300' },
    };
    return configs[estado] || { text: 'text-gray-700', bg: 'bg-gray-100 border-gray-300' };
  };

  const getEstadoRecojoConfig = (estado: string) => {
    const configs: Record<string, { text: string; bg: string }> = {
      'PENDIENTE': { text: 'text-amber-700', bg: 'bg-amber-100 border-amber-300' },
      'LABORATORIO': { text: 'text-cyan-700', bg: 'bg-cyan-100 border-cyan-300' },
      'LISTO': { text: 'text-violet-700', bg: 'bg-violet-100 border-violet-300' },
      'ENTREGADO': { text: 'text-emerald-700', bg: 'bg-emerald-100 border-emerald-300' },
      'ANULADO': { text: 'text-red-700', bg: 'bg-red-100 border-red-300' },
    };
    return configs[estado] || { text: 'text-gray-700', bg: 'bg-gray-100 border-gray-300' };
  };

  if (!isOpen) return null;

  const detalle = detalleCompleto || venta;
  const estadoPagoConfig = getEstadoPagoConfig(detalle.ventEstado);
  const estadoRecojoConfig = getEstadoRecojoConfig(detalle.ventEstadoRecoj);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-white border-b px-6 py-5 flex justify-between items-center">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Venta #{String(venta.ventCod).padStart(6, "0")}</h2>
            <p className="text-sm text-gray-500 mt-1">{formatDate(detalle.ventFecha)}</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg p-2 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4 overflow-y-auto max-h-[calc(90vh-100px)]">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-16">
              <Loader2 className="w-10 h-10 text-blue-500 animate-spin mb-3" />
              <p className="text-sm text-gray-500">Cargando detalles...</p>
            </div>
          ) : error ? (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h3 className="text-sm font-semibold text-red-900 mb-1">Error</h3>
                <p className="text-sm text-red-700">{error}</p>
                <button 
                  onClick={fetchDetalleCompleto} 
                  className="mt-2 text-sm text-red-600 hover:text-red-700 font-medium"
                >
                  Reintentar
                </button>
              </div>
            </div>
          ) : (
            <>
              {/* Estados */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {/* Estado Pago */}
                <div className={`${estadoPagoConfig.bg} border rounded-xl p-4`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <DollarSign className="w-5 h-5 text-gray-500" />
                      <p className="text-xs font-medium text-gray-600">Estado de Pago</p>
                    </div>
                    <p className={`text-lg font-semibold ${estadoPagoConfig.text}`}>
                      {detalle.estado_pago_display}
                    </p>
                  </div>
                </div>

                {/* Estado Recojo */}
                <div className={`${estadoRecojoConfig.bg} border rounded-xl p-4`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Package className="w-5 h-5 text-gray-500" />
                      <p className="text-xs font-medium text-gray-600">Estado de Pedido</p>
                    </div>
                    <p className={`text-lg font-semibold ${estadoRecojoConfig.text}`}>
                      {detalle.estado_pedido_display}
                    </p>
                  </div>
                </div>
              </div>

              {/* Cliente y Método de Pago */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {/* Cliente */}
                <div className="bg-gray-50 border border-gray-200 rounded-xl p-4">
                  <div className="flex items-center space-x-2 mb-3">
                    <User className="w-4 h-4 text-gray-500" />
                    <h3 className="text-xs font-semibold text-gray-700">Cliente</h3>
                  </div>
                  <div className="space-y-2">
                    <div>
                      <p className="text-xs text-gray-500">Nombre</p>
                      <p className="text-sm text-gray-900 font-medium mt-0.5">
                        {detalle.cliente?.cliNomCompleto || detalle.nombre_cliente || 'Cliente Genérico'}
                      </p>
                    </div>
                    {detalle.cliente && (
                      <div>
                        <p className="text-xs text-gray-500">Documento</p>
                        <p className="text-sm text-gray-900 mt-0.5">
                          {detalle.cliente.cliTipoDoc}: {detalle.cliente.cliNumDoc}
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Método de Pago */}
                <div className="bg-gray-50 border border-gray-200 rounded-xl p-4">
                  <div className="flex items-center space-x-2 mb-3">
                    <CreditCard className="w-4 h-4 text-gray-500" />
                    <h3 className="text-xs font-semibold text-gray-700">Pago</h3>
                  </div>
                  <div className="space-y-2">
                    <div>
                      <p className="text-xs text-gray-500">Forma de Pago</p>
                      <p className="text-sm text-gray-900 font-medium mt-0.5">
                        {(detalle as any).forma_pago_display || (detalle as any).ventFormaPago || 'No especificado'}
                      </p>
                    </div>
                    {(detalle as any).ventReferenciaPago && (
                      <div>
                        <p className="text-xs text-gray-500">Referencia</p>
                        <p className="text-sm text-gray-900 mt-0.5">{(detalle as any).ventReferenciaPago}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Productos */}
              {detallesProductos.length > 0 && (
                <div className="border border-gray-200 rounded-xl overflow-hidden">
                  <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
                    <div className="flex items-center space-x-2">
                      <Package className="w-4 h-4 text-gray-500" />
                      <h3 className="text-xs font-semibold text-gray-700">
                        Productos ({detallesProductos.filter(d => !d.ventDetAnulado).length})
                      </h3>
                    </div>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-gray-50">
                        <tr className="border-b border-gray-200">
                          <th className="text-left px-4 py-3 text-xs font-semibold text-gray-600">Descripción</th>
                          <th className="text-center px-4 py-3 text-xs font-semibold text-gray-600">Cant.</th>
                          <th className="text-right px-4 py-3 text-xs font-semibold text-gray-600">P. Unit.</th>
                          <th className="text-right px-4 py-3 text-xs font-semibold text-gray-600">Subtotal</th>
                          <th className="text-center px-4 py-3 text-xs font-semibold text-gray-600">Laboratorio</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-100">
                        {detallesProductos.filter(d => !d.ventDetAnulado).map((item, index) => {
                          return (
                          <tr key={item.ventDetCod} className="hover:bg-gray-50 transition-colors">
                            <td className="px-4 py-3">
                              <div>
                                <p className="text-sm font-medium text-gray-900">
                                  {item.esLunaPersonalizada 
                                    ? (() => {
                                        // Construir descripción completa desde los campos
                                        if (item.lunaMaterial || item.lunaTipo) {
                                          const partes = ['LUNA'];
                                          if (item.lunaMaterial) partes.push(item.lunaMaterial.toUpperCase());
                                          if (item.lunaTipo) partes.push(item.lunaTipo.toUpperCase());
                                          let desc = partes.join(' - ');
                                          if (item.lunaCaracteristicas) desc += ` (${item.lunaCaracteristicas})`;
                                          return desc;
                                        }
                                        // Fallback: usar ventDetDescripcion o producto
                                        return item.ventDetDescripcion || item.producto?.prodDescr || 'Luna Personalizada';
                                      })()
                                    : (item.producto?.prodDescr || item.ventDetDescripcion || `Producto #${item.prodCod}`)
                                  }
                                </p>
                                {!item.esLunaPersonalizada && (item.producto?.prodMarca || item.ventDetMarca) && (
                                  <p className="text-xs text-gray-500 mt-0.5">
                                    {item.producto?.prodMarca || item.ventDetMarca}
                                  </p>
                                )}
                              </div>
                            </td>
                            <td className="px-4 py-3 text-center text-sm text-gray-900 font-medium">
                              {item.ventDetCantidad}
                            </td>
                            <td className="px-4 py-3 text-right text-sm text-gray-700">
                              S/ {formatCurrency(item.ventDetPrecioUni)}
                            </td>
                            <td className="px-4 py-3 text-right text-sm text-gray-900 font-semibold">
                              S/ {formatCurrency(item.ventDetSubtotal)}
                            </td>
                            <td className="px-4 py-3 text-center">
                              {item.esLunaPersonalizada ? (
                                <div className="flex flex-col items-center space-y-1.5">
                                  {item.lunaLaboratorio_nombre ? (
                                    <>
                                      <div className="text-xs text-center">
                                        <p className="font-medium text-gray-900">{item.lunaLaboratorio_nombre}</p>
                                        <p className="text-gray-600 mt-0.5">S/ {formatCurrency(item.lunaCostoLaboratorio)}</p>
                                      </div>
                                      <button
                                        onClick={() => handleEditarLaboratorio(item)}
                                        className="text-blue-600 hover:text-blue-700 text-xs font-medium"
                                      >
                                        Editar
                                      </button>
                                    </>
                                  ) : (
                                    <button
                                      onClick={() => handleEditarLaboratorio(item)}
                                      className="flex items-center space-x-1 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-medium transition-colors"
                                    >
                                      <FlaskConical className="w-3.5 h-3.5" />
                                      <span>Agregar</span>
                                    </button>
                                  )}
                                </div>
                              ) : (
                                <span className="text-gray-400 text-xs">—</span>
                              )}
                            </td>
                          </tr>
                        );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Resumen de Montos */}
              <div className="bg-gray-50 border border-gray-200 rounded-xl p-4">
                <div className="flex items-center space-x-2 mb-4">
                  <DollarSign className="w-4 h-4 text-gray-500" />
                  <h3 className="text-xs font-semibold text-gray-700">Resumen de Pago</h3>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between py-2 text-sm">
                    <span className="text-gray-600">Subtotal</span>
                    <span className="text-gray-900 font-medium">
                      S/ {formatCurrency((detalle as any).ventSubTotal || detalle.ventTotal)}
                    </span>
                  </div>
                  {parseFloat(String((detalle as any).ventDescuento || 0)) > 0 && (
                    <div className="flex justify-between py-2 text-sm border-t border-gray-200">
                      <span className="text-gray-600">Descuento</span>
                      <span className="text-red-600 font-medium">
                        -S/ {formatCurrency((detalle as any).ventDescuento)}
                      </span>
                    </div>
                  )}
                  <div className="flex justify-between pt-3 mt-2 border-t-2 border-gray-300">
                    <span className="font-semibold text-gray-900">TOTAL</span>
                    <span className="font-bold text-lg text-gray-900">S/ {formatCurrency(detalle.ventTotal)}</span>
                  </div>
                  {parseFloat(String(detalle.ventAdelanto || 0)) > 0 && (
                    <>
                      <div className="flex justify-between py-2 text-sm border-t border-gray-200">
                        <span className="text-gray-600">Adelanto</span>
                        <span className="text-green-600 font-medium">
                          -S/ {formatCurrency(detalle.ventAdelanto)}
                        </span>
                      </div>
                      <div className="flex justify-between pt-3 mt-2 border-t-2 border-amber-300 bg-amber-50 -mx-4 px-4 py-3 rounded-lg">
                        <span className="text-gray-900 font-semibold">Saldo Pendiente</span>
                        <span className="text-gray-900 font-bold text-lg">
                          S/ {formatCurrency(detalle.ventSaldo)}
                        </span>
                      </div>
                    </>
                  )}
                </div>
              </div>

              {/* Observaciones */}
              {(detalle as any).ventObservaciones && (
                <div className="bg-gray-50 border border-gray-200 rounded-xl p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <FileText className="w-4 h-4 text-gray-500" />
                    <h3 className="text-xs font-semibold text-gray-700">Observaciones</h3>
                  </div>
                  <p className="text-sm text-gray-700 whitespace-pre-wrap">
                    {(detalle as any).ventObservaciones}
                  </p>
                </div>
              )}

              {/* Venta Anulada */}
              {detalle.ventAnulada && (
                <div className="bg-red-50 border-2 border-red-300 rounded-xl p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <AlertCircle className="w-5 h-5 text-red-600" />
                    <h3 className="text-sm font-semibold text-red-900">VENTA ANULADA</h3>
                  </div>
                  {(detalle as any).ventMotivoAnulacion && (
                    <p className="text-sm text-red-800">
                      <span className="font-medium">Motivo:</span> {(detalle as any).ventMotivoAnulacion}
                    </p>
                  )}
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="bg-white px-6 py-4 flex justify-end border-t border-gray-200">
          <button
            onClick={onClose}
            className="px-5 py-2 bg-gray-900 hover:bg-gray-800 text-white rounded-lg text-sm font-medium transition-colors"
          >
            Cerrar
          </button>
        </div>
      </div>

      {/* Modal de Edición de Laboratorio */}
      {modalLaboratorioOpen && detalleSeleccionado && (
        <ModalEditarLaboratorio
          detalle={detalleSeleccionado}
          isOpen={modalLaboratorioOpen}
          onClose={() => setModalLaboratorioOpen(false)}
          onActualizado={handleLaboratorioActualizado}
        />
      )}
    </div>
  );
};

export default ModalDetallesVenta;