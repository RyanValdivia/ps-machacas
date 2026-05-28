import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { CreditCard } from 'lucide-react';

interface CajaChartProps {
  ventas: any[];
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4', '#ec4899'];

const CajaChart = ({ ventas }: CajaChartProps) => {
  if (!ventas || ventas.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Distribución por Caja</h3>
        <p className="text-sm text-gray-500">No hay datos de ventas por caja disponibles</p>
      </div>
    );
  }

  const chartData = ventas.map(v => ({
    name: v.caja_nombre,
    value: v.total_ventas,
    cantidad: v.cantidad_ventas,
    porcentaje: v.porcentaje_participacion
  }));

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
          <p className="font-semibold text-gray-900">{payload[0].name}</p>
          <p className="text-sm text-gray-600">Ventas: S/ {payload[0].value.toFixed(2)}</p>
          <p className="text-sm text-gray-600">Cantidad: {payload[0].payload.cantidad}</p>
          <p className="text-sm font-medium text-blue-600">
            {payload[0].payload.porcentaje.toFixed(1)}%
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Distribución por Caja</h3>
          <p className="text-sm text-gray-500 mt-1">Participación de cada punto de venta</p>
        </div>
        <CreditCard className="w-6 h-6 text-blue-600" />
      </div>

      <div className="flex flex-col md:flex-row items-center gap-6">
        {/* Gráfico de pastel */}
        <div className="flex-shrink-0">
          <ResponsiveContainer width={280} height={280}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ porcentaje }) => `${porcentaje.toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Lista de cajas */}
        <div className="flex-1 space-y-3">
          {ventas.map((caja, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <div 
                  className="w-4 h-4 rounded-full flex-shrink-0" 
                  style={{ backgroundColor: COLORS[index % COLORS.length] }}
                />
                <div>
                  <p className="text-sm font-medium text-gray-900">{caja.caja_nombre}</p>
                  <p className="text-xs text-gray-500">{caja.cantidad_ventas} ventas</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm font-semibold text-gray-900">
                  S/ {caja.total_ventas.toFixed(2)}
                </p>
                <p className="text-xs text-blue-600 font-medium">
                  {caja.porcentaje_participacion.toFixed(1)}%
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CajaChart;
