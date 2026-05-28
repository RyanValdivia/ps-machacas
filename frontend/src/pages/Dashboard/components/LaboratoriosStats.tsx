import { FlaskConical, TrendingUp, DollarSign, AlertCircle } from 'lucide-react';

interface LaboratoriosStatsProps {
  data: any[];
  resumen: any;
  financiero: any;
}

const LaboratoriosStats = ({ data, resumen, financiero }: LaboratoriosStatsProps) => {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 border-2 border-gray-200">
        <div className="flex items-center space-x-2 mb-4">
          <FlaskConical className="w-6 h-6 text-blue-600" />
          <h2 className="text-xl font-bold text-gray-900">Estadísticas de Laboratorios</h2>
        </div>
        <div className="text-center py-8 text-gray-500">
          <AlertCircle className="w-12 h-12 mx-auto mb-2 text-gray-400" />
          <p>No hay datos de laboratorios disponibles</p>
        </div>
      </div>
    );
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
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-4 rounded-t-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <FlaskConical className="w-6 h-6" />
            <h2 className="text-xl font-bold">Estadísticas de Laboratorios</h2>
          </div>
          <div className="text-right">
            <p className="text-sm text-blue-100">Últimos 30 días</p>
          </div>
        </div>
      </div>

      {/* Resumen General */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-6 bg-gray-50 border-b-2 border-gray-200">
        <div className="bg-white rounded-lg p-4 border-2 border-blue-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-600 font-semibold uppercase">Total Ingresos Lunas</p>
              <p className="text-2xl font-bold text-blue-600">
                {formatCurrency(financiero.ingreso_total_lunas)}
              </p>
            </div>
            <DollarSign className="w-10 h-10 text-blue-500 opacity-20" />
          </div>
        </div>

        <div className="bg-white rounded-lg p-4 border-2 border-green-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-600 font-semibold uppercase">Ganancia Total</p>
              <p className="text-2xl font-bold text-green-600">
                {formatCurrency(financiero.ganancia_total)}
              </p>
              <p className="text-xs text-green-700 font-semibold mt-1">
                Margen: {financiero.margen_promedio}%
              </p>
            </div>
            <TrendingUp className="w-10 h-10 text-green-500 opacity-20" />
          </div>
        </div>

        <div className="bg-white rounded-lg p-4 border-2 border-orange-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-600 font-semibold uppercase">Costo Laboratorios</p>
              <p className="text-2xl font-bold text-orange-600">
                {formatCurrency(financiero.costo_total_laboratorios)}
              </p>
            </div>
            <FlaskConical className="w-10 h-10 text-orange-500 opacity-20" />
          </div>
        </div>
      </div>

      {/* Resumen de Lunas */}
      <div className="px-6 py-4 bg-gray-50 border-b-2 border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex space-x-6">
            <div>
              <p className="text-xs text-gray-600 font-semibold">Total Lunas</p>
              <p className="text-xl font-bold text-gray-900">{resumen.total_lunas}</p>
            </div>
            <div>
              <p className="text-xs text-gray-600 font-semibold">Con Laboratorio</p>
              <p className="text-xl font-bold text-green-600">{resumen.lunas_con_laboratorio}</p>
            </div>
            <div>
              <p className="text-xs text-gray-600 font-semibold">Pendientes</p>
              <p className="text-xl font-bold text-amber-600">{resumen.lunas_pendientes}</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-xs text-gray-600 font-semibold">Completado</p>
            <p className="text-2xl font-bold text-blue-600">{resumen.porcentaje_completado}%</p>
          </div>
        </div>
      </div>

      {/* Tabla de Laboratorios */}
      <div className="p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Detalle por Laboratorio</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-200 border-b-2 border-gray-400">
              <tr>
                <th className="text-left p-3 font-semibold text-gray-700">Laboratorio</th>
                <th className="text-center p-3 font-semibold text-gray-700">Lunas</th>
                <th className="text-right p-3 font-semibold text-gray-700">Costo Total</th>
                <th className="text-right p-3 font-semibold text-gray-700">Total Vendido</th>
                <th className="text-right p-3 font-semibold text-gray-700">Ganancia</th>
                <th className="text-right p-3 font-semibold text-gray-700">Margen</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data.map((lab, index) => (
                <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                  <td className="p-3 text-gray-900 font-medium">
                    <div className="flex items-center space-x-2">
                      <FlaskConical className="w-4 h-4 text-blue-600" />
                      <span>{lab.laboratorio}</span>
                    </div>
                  </td>
                  <td className="p-3 text-center text-gray-900 font-semibold">
                    {lab.cantidad_lunas}
                  </td>
                  <td className="p-3 text-right text-gray-900">
                    {formatCurrency(lab.total_costo)}
                  </td>
                  <td className="p-3 text-right text-gray-900 font-semibold">
                    {formatCurrency(lab.total_vendido)}
                  </td>
                  <td className={`p-3 text-right font-bold ${
                    lab.ganancia >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {formatCurrency(lab.ganancia)}
                  </td>
                  <td className="p-3 text-right">
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                      lab.margen_porcentaje >= 50 ? 'bg-green-100 text-green-800' :
                      lab.margen_porcentaje >= 30 ? 'bg-blue-100 text-blue-800' :
                      lab.margen_porcentaje >= 10 ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {lab.margen_porcentaje.toFixed(1)}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default LaboratoriosStats;
