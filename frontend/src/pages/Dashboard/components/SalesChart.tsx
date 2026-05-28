import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { TrendingUp } from 'lucide-react';

interface SalesChartProps {
  data: Array<{
    fecha: string;
    total: number;
    cantidad: number;
  }>;
}

const SalesChart = ({ data }: SalesChartProps) => {
  // Transformar datos para el gráfico
  const chartData = data.map(item => ({
    date: new Date(item.fecha).toLocaleDateString('es-PE', { day: '2-digit', month: 'short' }),
    revenue: item.total,
    total: item.cantidad
  }));

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center space-x-2 mb-6">
        <TrendingUp className="w-5 h-5 text-blue-500" />
        <h3 className="text-lg font-semibold text-gray-900">Ventas en el Tiempo</h3>
      </div>

      <div className="h-64">
        {chartData && chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis 
                dataKey="date" 
                stroke="#6b7280"
                fontSize={12}
              />
              <YAxis 
                stroke="#6b7280"
                fontSize={12}
                tickFormatter={(value) => `S/ ${value}`}
              />
              <Tooltip 
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
                formatter={(value: any) => {
                  const num = typeof value === 'string' ? parseFloat(value) : value;
                  return [`S/ ${isNaN(num) ? '0.00' : num.toFixed(2)}`, 'Ingresos'];
                }}
              />
              <Area 
                type="monotone" 
                dataKey="revenue" 
                stroke="#3b82f6" 
                strokeWidth={2}
                fill="url(#colorRevenue)" 
              />
            </AreaChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-full text-gray-400">
            <p>No hay datos disponibles</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SalesChart;
