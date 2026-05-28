import { useState, useEffect } from 'react';
import { 
  Package,
  TrendingUp,
  TrendingDown,
  DollarSign,
  AlertCircle
} from 'lucide-react';
import SalesChart from './components/SalesChart';
import VentasPendientesEntrega from './components/VentasPendientesEntrega';
import dashboardService from '../../services/dashboardService';
import { useAuth } from '../../auth/hooks/useAuth';

const Dashboard = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [periodo, setPeriodo] = useState<'dia' | 'semana' | 'mes'>('dia');
  const [estadisticas, setEstadisticas] = useState<any>(null);


  useEffect(() => {
    loadDashboardData();
  }, [periodo]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      console.log('📊 Cargando dashboard con período:', periodo);
      const data = await dashboardService.getEstadisticasDashboard(periodo);
      console.log('✅ Datos recibidos:', data);
      setEstadisticas(data);
    } catch (error) {
      console.error('❌ Error cargando dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando dashboard...</p>
        </div>
      </div>
    );
  }

  if (!estadisticas) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-gray-600">Error al cargar estadísticas</p>
          <button 
            onClick={loadDashboardData}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  const { resumen_general, proveedores, top_productos, estadisticas_lunas, ventas_pendientes, ventas_por_dia } = estadisticas;
  
  // Validar que existan los datos necesarios
  if (!resumen_general) {
    console.error('❌ No hay resumen_general en las estadísticas');
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-orange-500 mx-auto mb-4" />
          <p className="text-gray-600">Datos incompletos</p>
          <p className="text-sm text-gray-500 mt-2">Período: {periodo}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-sm text-gray-500 mt-1">
            Bienvenido, {user?.usuNombreCom}
          </p>
        </div>

        {/* Selector de período */}
        <div className="flex space-x-2">
          <button
            onClick={() => setPeriodo('dia')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              periodo === 'dia'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            Hoy
          </button>
          <button
            onClick={() => setPeriodo('semana')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              periodo === 'semana'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            Semana
          </button>
          <button
            onClick={() => setPeriodo('mes')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              periodo === 'mes'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            Mes
          </button>
        </div>
      </div>

      {/* Cards de resumen */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Ingresos Totales */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Ingresos</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                S/ {resumen_general.ingresos_totales.toFixed(2)}
              </p>
              <div className="flex items-center mt-2">
                {resumen_general.variacion_ingresos >= 0 ? (
                  <TrendingUp className="w-4 h-4 text-green-600 mr-1" />
                ) : (
                  <TrendingDown className="w-4 h-4 text-red-600 mr-1" />
                )}
                <span className={`text-xs font-medium ${
                  resumen_general.variacion_ingresos >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {Math.abs(resumen_general.variacion_ingresos).toFixed(1)}%
                </span>
                <span className="text-xs text-gray-500 ml-1">vs anterior</span>
              </div>
            </div>
            <DollarSign className="w-12 h-12 text-blue-500" />
          </div>
        </div>

        {/* Ganancias */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Ganancias</p>
              <p className="text-2xl font-bold text-green-600 mt-1">
                S/ {resumen_general.ganancias_totales.toFixed(2)}
              </p>
              <p className="text-xs text-gray-500 mt-2">
                Margen: {resumen_general.margen_general.toFixed(1)}%
              </p>
            </div>
            <TrendingUp className="w-12 h-12 text-green-500" />
          </div>
        </div>

        {/* Costos */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Costos</p>
              <p className="text-2xl font-bold text-red-600 mt-1">
                S/ {resumen_general.costos_totales.toFixed(2)}
              </p>
              <p className="text-xs text-gray-500 mt-2">
                {resumen_general.cantidad_ventas} ventas
              </p>
            </div>
            <Package className="w-12 h-12 text-red-500" />
          </div>
        </div>

        {/* Lunas Pendientes */}
        {estadisticas_lunas && estadisticas_lunas.total_lunas > 0 && (
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Lunas Pendientes</p>
                <p className="text-2xl font-bold text-orange-600 mt-1">
                  {estadisticas_lunas.lunas_pendientes || 0}
                </p>
                <p className="text-xs text-gray-500 mt-2">
                  {estadisticas_lunas.total_lunas || 0} total de lunas
                </p>
              </div>
              <AlertCircle className="w-10 h-10 text-orange-500" />
            </div>
          </div>
        )}
      </div>

      {/* Ventas Pendientes de Entrega */}
      {estadisticas?.ventas_listas && estadisticas?.ventas_pendientes && (
        <VentasPendientesEntrega 
          ventasListas={estadisticas.ventas_listas}
          ventasPendientes={estadisticas.ventas_pendientes}
        />
      )}

      {/* Gráfico de ventas */}
      <SalesChart data={ventas_por_dia || []} />
    </div>
  );
};

export default Dashboard;
