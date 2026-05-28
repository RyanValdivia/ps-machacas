import { Package, TrendingUp } from 'lucide-react';

interface TopProductosProps {
  productos: any[];
}

const TopProductos = ({ productos }: TopProductosProps) => {
  if (!productos || productos.length === 0) {
    return null;
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('es-PE', {
      style: 'currency',
      currency: 'PEN'
    }).format(value);
  };

  return (
    <div className="bg-white rounded-lg shadow-md border-2 border-gray-200">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-purple-700 text-white px-6 py-4 rounded-t-lg">
        <div className="flex items-center space-x-2">
          <TrendingUp className="w-6 h-6" />
          <h2 className="text-xl font-bold">Top Productos Más Vendidos</h2>
        </div>
        <p className="text-sm text-purple-100 mt-1">Últimos 30 días</p>
      </div>

      {/* Lista de Productos */}
      <div className="p-6">
        <div className="space-y-3">
          {productos.map((producto, index) => {
            const maxCantidad = productos[0]?.cantidad_vendida || 1;
            const porcentaje = (producto.cantidad_vendida / maxCantidad) * 100;
            
            return (
              <div key={index} className="relative">
                {/* Ranking badge */}
                <div className="flex items-start space-x-3">
                  <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                    index === 0 ? 'bg-yellow-400 text-yellow-900' :
                    index === 1 ? 'bg-gray-300 text-gray-700' :
                    index === 2 ? 'bg-orange-400 text-orange-900' :
                    'bg-blue-100 text-blue-900'
                  }`}>
                    {index + 1}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    {/* Nombre y Marca */}
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1 min-w-0 mr-4">
                        <p className="text-sm font-semibold text-gray-900 truncate">
                          {producto.prodCod__prodDescr || 'Producto sin nombre'}
                        </p>
                        {producto.prodCod__prodMarca && (
                          <p className="text-xs text-gray-600 mt-0.5">
                            {producto.prodCod__prodMarca}
                          </p>
                        )}
                      </div>
                      <div className="text-right flex-shrink-0">
                        <p className="text-sm font-bold text-gray-900">
                          {producto.cantidad_vendida} un.
                        </p>
                        <p className="text-xs text-green-600 font-semibold">
                          {formatCurrency(producto.total_ingresos)}
                        </p>
                      </div>
                    </div>
                    
                    {/* Barra de progreso */}
                    <div className="relative w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div 
                        className={`absolute inset-y-0 left-0 rounded-full transition-all duration-500 ${
                          index === 0 ? 'bg-gradient-to-r from-yellow-400 to-yellow-500' :
                          index === 1 ? 'bg-gradient-to-r from-gray-400 to-gray-500' :
                          index === 2 ? 'bg-gradient-to-r from-orange-400 to-orange-500' :
                          'bg-gradient-to-r from-blue-400 to-blue-500'
                        }`}
                        style={{ width: `${porcentaje}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {productos.length > 5 && (
          <div className="mt-4 pt-4 border-t-2 border-gray-200">
            <p className="text-xs text-gray-600 text-center">
              Mostrando top {productos.length} productos
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default TopProductos;
