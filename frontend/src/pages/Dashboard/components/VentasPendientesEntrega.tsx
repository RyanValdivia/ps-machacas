import { Truck, Clock, User, Package, AlertCircle } from 'lucide-react';
import { useState } from 'react';

interface Venta {
  ventCod: number;
  ventFecha: string;
  cliCod__cliNombreCom: string;
  ventTotal: number;
  ventSaldo: number;
  ventEstadoRecoj: string;
  productos?: string;
}

interface VentasListasProps {
  ventasListas: Venta[];
  ventasPendientes: Venta[];
}

const VentasPendientesEntrega = ({ ventasListas, ventasPendientes }: VentasListasProps) => {
  const [mostrar, setMostrar] = useState<'listas' | 'pendientes'>('listas');

  const formatoMoneda = (valor: number) => {
    if (valor === null || valor === undefined) return 'S/ 0.00';
    return `S/ ${Number(valor).toFixed(2)}`;
  };

  const formatoFecha = (fecha: string) => {
    if (!fecha) return '';
    try {
      const date = new Date(fecha);
      const dia = date.getDate().toString().padStart(2, '0');
      const mes = (date.getMonth() + 1).toString().padStart(2, '0');
      return `${dia}/${mes}`;
    } catch {
      return '';
    }
  };

  const datosActuales = mostrar === 'listas' ? (ventasListas || []) : (ventasPendientes || []);
  const total = datosActuales.length;
  const conSaldo = datosActuales.filter(v => v.ventSaldo > 0).length;

  return (
    <div className="bg-white rounded-lg sm:rounded-xl border border-gray-200">
      {/* Header */}
      <div className="px-3 sm:px-6 py-3 sm:py-4 border-b border-gray-200 bg-gray-50">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 sm:gap-4">
          <div>
            <h3 className="text-sm sm:text-lg font-semibold text-gray-900">Listo/Pendiente para entrega</h3>
          </div>
          
          {/* Toggle */}
          <div className="flex gap-2">
            <button
              onClick={() => setMostrar('listas')}
              className={`flex items-center gap-1.5 px-2.5 sm:px-4 py-1.5 sm:py-2 rounded-lg text-xs sm:text-sm font-medium transition-all ${
                mostrar === 'listas'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <Truck className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
              <span>Listos</span>
              <span className="px-1.5 py-0.5 rounded-full text-xs bg-white/20">
                {ventasListas?.length || 0}
              </span>
            </button>
            
            <button
              onClick={() => setMostrar('pendientes')}
              className={`flex items-center gap-1.5 px-2.5 sm:px-4 py-1.5 sm:py-2 rounded-lg text-xs sm:text-sm font-medium transition-all ${
                mostrar === 'pendientes'
                  ? 'bg-orange-600 text-white shadow-md'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <Clock className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
              <span>Pendientes</span>
              <span className="px-1.5 py-0.5 rounded-full text-xs bg-white/20">
                {ventasPendientes?.length || 0}
              </span>
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-2 sm:p-4">
        {datosActuales.length > 0 ? (
          <div className="space-y-2">
            {datosActuales.map((venta) => {
              const tieneSaldo = venta.ventSaldo > 0;
              const colorBorde = mostrar === 'listas' ? 'border-blue-200 bg-blue-50/50' : 'border-orange-200 bg-orange-50/50';
              
              return (
                <div
                  key={venta.ventCod}
                  className={`border-2 rounded-lg p-2 sm:p-3 transition-shadow hover:shadow-md ${colorBorde}`}
                >
                  {/* Mobile y Desktop Unificado */}
                  <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2">
                    {/* Izquierda */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1.5">
                        <span className={`px-2 py-0.5 sm:px-2.5 sm:py-1 rounded text-xs sm:text-sm font-bold ${
                          mostrar === 'listas' ? 'bg-blue-600 text-white' : 'bg-orange-600 text-white'
                        }`}>
                          #{venta.ventCod}
                        </span>
                        <span className="text-xs text-gray-500">{formatoFecha(venta.ventFecha)}</span>
                      </div>
                      
                      <div className="flex items-start gap-1.5 mb-1.5">
                        <User className="w-3.5 h-3.5 text-gray-400 flex-shrink-0 mt-0.5" />
                        <span className="text-xs sm:text-sm font-medium text-gray-900 line-clamp-1">
                          {venta.cliCod__cliNombreCom || 'Sin cliente'}
                        </span>
                      </div>

                      {venta.productos && (
                        <div className="flex items-start gap-1.5 mb-1.5">
                          <Package className="w-3.5 h-3.5 text-gray-400 flex-shrink-0 mt-0.5" />
                          <span className="text-xs text-gray-600 line-clamp-1">
                            {venta.productos}
                          </span>
                        </div>
                      )}
                    </div>

                    {/* Derecha */}
                    <div className="flex items-center sm:flex-col sm:items-end gap-2">
                      <div className="flex-1 sm:flex-none text-left sm:text-right">
                        <p className="text-xs text-gray-500">Total</p>
                        <p className="text-sm sm:text-base font-bold text-gray-900">
                          {formatoMoneda(venta.ventTotal)}
                        </p>
                      </div>
                      
                      {tieneSaldo && (
                        <div className="flex-1 sm:flex-none px-2 py-1 rounded bg-red-100 text-right sm:mt-1">
                          <p className="text-xs text-red-600">Saldo</p>
                          <p className="text-xs sm:text-sm font-bold text-red-700">
                            {formatoMoneda(venta.ventSaldo)}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-6 sm:py-12">
            <Package className="w-10 h-10 sm:w-16 sm:h-16 text-gray-300 mx-auto mb-2 sm:mb-4" />
            <p className="text-sm sm:text-base text-gray-500">
              No hay ventas {mostrar === 'listas' ? 'listas' : 'pendientes'}
            </p>
          </div>
        )}

        {/* Footer */}
        {datosActuales.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-200">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 text-xs sm:text-sm">
              <span className="text-gray-600 font-medium">
                {total} {mostrar === 'listas' ? 'lista(s)' : 'pendiente(s)'} para entregar
              </span>
              {conSaldo > 0 && (
                <div className="flex items-center gap-1.5 text-red-600">
                  <AlertCircle className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                  <span className="font-medium">{conSaldo} con saldo pendiente</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VentasPendientesEntrega;
