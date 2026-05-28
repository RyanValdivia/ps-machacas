import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Package, TrendingUp } from 'lucide-react';

interface ProveedorChartProps {
  proveedores: any[];
}

const ProveedorChart = ({ proveedores }: ProveedorChartProps) => {
  if (!proveedores || proveedores.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Rentabilidad por Proveedor</h3>
        <p className="text-sm text-gray-500">No hay datos de proveedores disponibles</p>
      </div>
    );
  }

  // Tomar los top 8 proveedores por ganancia
  const topProveedores = proveedores.slice(0, 8);

  const chartData = topProveedores.map(p => ({
    nombre: p.proveedor_nombre.length > 15 
      ? p.proveedor_nombre.substring(0, 15) + '...' 
      : p.proveedor_nombre,
    costos: p.costo_total,
    ventas: p.venta_total,
    ganancia: p.ganancia
  }));

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Rentabilidad por Proveedor</h3>
          <p className="text-sm text-gray-500 mt-1">Comparativa de costos, ventas y ganancias</p>
        </div>
        <Package className="w-6 h-6 text-blue-600" />
      </div>
      
      <ResponsiveContainer width="100%" height={350}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis 
            dataKey="nombre" 
            tick={{ fill: '#6b7280', fontSize: 11 }}
            axisLine={{ stroke: '#e5e7eb' }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis 
            tick={{ fill: '#6b7280', fontSize: 12 }}
            axisLine={{ stroke: '#e5e7eb' }}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#fff', 
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
            }}
            formatter={(value: any) => `S/ ${value.toFixed(2)}`}
          />
          <Legend 
            wrapperStyle={{ paddingTop: '20px' }}
            iconType="circle"
          />
          <Bar 
            dataKey="costos" 
            name="Costos" 
            fill="#ef4444" 
            radius={[4, 4, 0, 0]}
          />
          <Bar 
            dataKey="ventas" 
            name="Ventas" 
            fill="#3b82f6" 
            radius={[4, 4, 0, 0]}
          />
          <Bar 
            dataKey="ganancia" 
            name="Ganancia" 
            fill="#10b981" 
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>

      {/* Resumen de top 3 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6 pt-6 border-t border-gray-200">
        {topProveedores.slice(0, 3).map((proveedor, index) => (
          <div key={index} className="p-4 bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-gray-500">TOP {index + 1}</span>
              <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                proveedor.margen_porcentaje >= 50 ? 'bg-green-100 text-green-800' :
                proveedor.margen_porcentaje >= 30 ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {proveedor.margen_porcentaje.toFixed(1)}% margen
              </span>
            </div>
            <p className="text-sm font-semibold text-gray-900 truncate">
              {proveedor.proveedor_nombre}
            </p>
            <p className="text-lg font-bold text-green-600 mt-1">
              S/ {proveedor.ganancia.toFixed(2)}
            </p>
            <p className="text-xs text-gray-500">
              {proveedor.cantidad_productos + proveedor.cantidad_lunas} productos vendidos
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProveedorChart;
