import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import { TrendingUp } from 'lucide-react';

interface VendedorChartProps {
  ventas: any[];
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4'];

const VendedorChart = ({ ventas }: VendedorChartProps) => {
  if (!ventas || ventas.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Desempeño por Vendedor</h3>
        <p className="text-sm text-gray-500">No hay datos de ventas por vendedor disponibles</p>
      </div>
    );
  }

  const chartData = ventas.map(v => ({
    nombre: v.vendedor_nombre.split(' ')[0], // Solo primer nombre
    ventas: v.total_vendido,
    cantidad: v.cantidad_ventas
  }));

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Desempeño por Vendedor</h3>
          <p className="text-sm text-gray-500 mt-1">Total vendido por cada vendedor</p>
        </div>
        <TrendingUp className="w-6 h-6 text-blue-600" />
      </div>
      
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis 
            dataKey="nombre" 
            tick={{ fill: '#6b7280', fontSize: 12 }}
            axisLine={{ stroke: '#e5e7eb' }}
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
            formatter={(value: any) => [`S/ ${value.toFixed(2)}`, 'Total Vendido']}
          />
          <Bar dataKey="ventas" radius={[8, 8, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Leyenda personalizada */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-6 pt-6 border-t border-gray-200">
        {ventas.slice(0, 6).map((vendedor, index) => (
          <div key={index} className="flex items-center space-x-2">
            <div 
              className="w-3 h-3 rounded-full" 
              style={{ backgroundColor: COLORS[index % COLORS.length] }}
            />
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-gray-900 truncate">
                {vendedor.vendedor_nombre}
              </p>
              <p className="text-xs text-gray-500">
                {vendedor.cantidad_ventas} ventas
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default VendedorChart;
