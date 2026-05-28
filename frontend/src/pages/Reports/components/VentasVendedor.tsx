import { UserCircle, TrendingUp, Award } from 'lucide-react';

interface VentasVendedorProps {
  ventas: any[];
}

const VentasVendedor = ({ ventas }: VentasVendedorProps) => {
  const formatCurrency = (value: number) => value.toFixed(2);

  if (!ventas || ventas.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center space-x-2 mb-4">
          <UserCircle className="w-5 h-5 text-gray-400" />
          <h3 className="text-lg font-semibold text-gray-900">Ventas por Vendedor</h3>
        </div>
        <p className="text-sm text-gray-500">No hay datos de ventas disponibles</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-white">
        <div className="flex items-center space-x-2">
          <UserCircle className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">Desempeño de Vendedores</h3>
        </div>
      </div>
      
      <div className="p-6">
        <div className="space-y-3">
          {ventas.map((vendedor, index) => (
            <div 
              key={vendedor.vendedor_id || index} 
              className="flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <div className="flex items-center space-x-4 flex-1">
                {index < 3 && (
                  <Award className={`w-5 h-5 ${
                    index === 0 ? 'text-yellow-500' :
                    index === 1 ? 'text-gray-400' :
                    'text-orange-600'
                  }`} />
                )}
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-gray-900 truncate">
                    {vendedor.vendedor_nombre}
                  </p>
                  <p className="text-sm text-gray-500">
                    {vendedor.cantidad_ventas} ventas
                  </p>
                </div>
              </div>
              
              <div className="flex items-center space-x-6">
                <div className="text-right">
                  <p className="text-lg font-bold text-green-600">
                    S/ {formatCurrency(vendedor.total_vendido)}
                  </p>
                  <p className="text-xs text-gray-500">
                    Promedio: S/ {formatCurrency(vendedor.promedio_venta)}
                  </p>
                </div>
                
                <div className="w-16 h-16 flex items-center justify-center bg-blue-50 rounded-lg">
                  <div className="text-center">
                    <p className="text-xl font-bold text-blue-600">
                      {vendedor.cantidad_ventas}
                    </p>
                    <p className="text-xs text-blue-600">ventas</p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default VentasVendedor;
