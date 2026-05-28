import { Package, FlaskConical, TrendingUp } from 'lucide-react';

interface CostosProveedoresProps {
  proveedores: any[];
}

const CostosProveedores = ({ proveedores }: CostosProveedoresProps) => {
  const formatCurrency = (value: number) => value.toFixed(2);

  if (!proveedores || proveedores.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Costos por Proveedor</h3>
        <p className="text-sm text-gray-500">No hay datos de proveedores disponibles</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Costos y Ganancias por Proveedor</h3>
        <p className="text-sm text-gray-500 mt-1">Análisis de rentabilidad por proveedor</p>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Proveedor
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                <div className="flex items-center justify-end space-x-1">
                  <Package className="w-3.5 h-3.5" />
                  <span>Productos</span>
                </div>
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                <div className="flex items-center justify-end space-x-1">
                  <FlaskConical className="w-3.5 h-3.5" />
                  <span>Lunas</span>
                </div>
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                Costo Total
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                Venta Total
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                <div className="flex items-center justify-end space-x-1">
                  <TrendingUp className="w-3.5 h-3.5" />
                  <span>Ganancia</span>
                </div>
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                Margen
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {proveedores.map((prov, index) => (
              <tr key={prov.proveedor_id} className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm">
                  <div className="font-medium text-gray-900">{prov.proveedor_nombre}</div>
                  <div className="text-xs text-gray-500">
                    {prov.cantidad_productos} prod. • {prov.cantidad_lunas} lunas
                  </div>
                </td>
                <td className="px-6 py-4 text-sm text-right">
                  <div className="text-gray-900">S/ {formatCurrency(prov.costo_productos)}</div>
                  <div className="text-xs text-gray-500">S/ {formatCurrency(prov.venta_productos)}</div>
                </td>
                <td className="px-6 py-4 text-sm text-right">
                  <div className="text-gray-900">S/ {formatCurrency(prov.costo_lunas)}</div>
                  <div className="text-xs text-gray-500">S/ {formatCurrency(prov.venta_lunas)}</div>
                </td>
                <td className="px-6 py-4 text-sm text-right font-medium text-red-600">
                  S/ {formatCurrency(prov.costo_total)}
                </td>
                <td className="px-6 py-4 text-sm text-right font-medium text-gray-900">
                  S/ {formatCurrency(prov.venta_total)}
                </td>
                <td className="px-6 py-4 text-sm text-right font-semibold text-green-600">
                  S/ {formatCurrency(prov.ganancia)}
                </td>
                <td className="px-6 py-4 text-sm text-right">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    prov.margen_porcentaje >= 50 ? 'bg-green-100 text-green-800' :
                    prov.margen_porcentaje >= 30 ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {formatCurrency(prov.margen_porcentaje)}%
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default CostosProveedores;
