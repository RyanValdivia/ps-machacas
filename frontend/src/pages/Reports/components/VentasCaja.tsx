import { CreditCard, DollarSign, TrendingUp } from 'lucide-react';

interface VentasCajaProps {
  ventas: any[];
}

const VentasCaja = ({ ventas }: VentasCajaProps) => {
  const formatCurrency = (value: number) => value.toFixed(2);

  if (!ventas || ventas.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center space-x-2 mb-4">
          <CreditCard className="w-5 h-5 text-gray-400" />
          <h3 className="text-lg font-semibold text-gray-900">Ventas por Caja</h3>
        </div>
        <p className="text-sm text-gray-500">No hay datos de ventas disponibles</p>
      </div>
    );
  }

  const maxVentas = Math.max(...ventas.map(c => c.total_ventas));

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-purple-50 to-white">
        <div className="flex items-center space-x-2">
          <CreditCard className="w-5 h-5 text-purple-600" />
          <h3 className="text-lg font-semibold text-gray-900">Actividad por Caja</h3>
        </div>
      </div>
      
      <div className="p-6">
        <div className="space-y-4">
          {ventas.map((caja, index) => {
            const percentage = (caja.total_ventas / maxVentas) * 100;
            
            return (
              <div key={caja.caja_id || index} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                    <span className="font-semibold text-gray-900">
                      {caja.caja_nombre}
                    </span>
                  </div>
                  <div className="flex items-center space-x-4">
                    <span className="text-sm text-gray-600">
                      {caja.cantidad_ventas} ventas
                    </span>
                    <span className="font-bold text-green-600">
                      S/ {formatCurrency(caja.total_ventas)}
                    </span>
                    <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                      {formatCurrency(caja.porcentaje_participacion)}%
                    </span>
                  </div>
                </div>
                
                {/* Barra de progreso */}
                <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                  <div 
                    className="bg-gradient-to-r from-purple-500 to-purple-600 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>

        {/* Total */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-600">Total General</span>
            <span className="text-xl font-bold text-gray-900">
              S/ {formatCurrency(ventas.reduce((sum, c) => sum + c.total_ventas, 0))}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VentasCaja;
