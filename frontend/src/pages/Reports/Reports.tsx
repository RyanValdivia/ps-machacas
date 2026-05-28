import { useState, useEffect } from 'react';
import { DollarSign, TrendingUp, Package, ShoppingCart } from 'lucide-react';
import StatCard from './components/StatCard';
import CostosProveedores from './components/CostosProveedores';
import VentasVendedor from './components/VentasVendedor';
import VentasCaja from './components/VentasCaja';
import VendedorChart from './components/VendedorChart';
import CajaChart from './components/CajaChart';
import ProveedorChart from './components/ProveedorChart';
import dashboardService from '../../services/dashboardService';

export default function Reports() {
    const [loading, setLoading] = useState(true);
    const [periodo, setPeriodo] = useState<'dia' | 'mes' | 'año'>('mes');
    const [estadisticas, setEstadisticas] = useState<any>(null);

    useEffect(() => {
        loadReportData();
    }, [periodo]);

    const loadReportData = async () => {
        try {
            setLoading(true);
            const data = await dashboardService.getEstadisticasDashboard(periodo === 'año' ? 'mes' : periodo);
            setEstadisticas(data);
        } catch (error) {
            console.error('Error cargando reportes:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">Cargando reportes...</p>
                </div>
            </div>
        );
    }

    const resumen = estadisticas?.resumen_general;

    return (
        <div className="min-h-screen bg-gray-50 p-6 space-y-6">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Reportes Analíticos</h1>
                    <p className="text-sm text-gray-500 mt-1">
                        Análisis detallado de ventas, rentabilidad y desempeño
                    </p>
                </div>

                {/* Selector de período */}
                <div className="flex space-x-2">
                    <button
                        onClick={() => setPeriodo('dia')}
                        className={`px-6 py-2.5 rounded-lg text-sm font-medium transition-all ${
                            periodo === 'dia'
                                ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30'
                                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                        }`}
                    >
                        Día
                    </button>
                    <button
                        onClick={() => setPeriodo('mes')}
                        className={`px-6 py-2.5 rounded-lg text-sm font-medium transition-all ${
                            periodo === 'mes'
                                ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30'
                                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                        }`}
                    >
                        Mes
                    </button>
                    <button
                        onClick={() => setPeriodo('año')}
                        className={`px-6 py-2.5 rounded-lg text-sm font-medium transition-all ${
                            periodo === 'año'
                                ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30'
                                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                        }`}
                    >
                        Año
                    </button>
                </div>
            </div>

            {/* Cards de Resumen */}
            {resumen && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <StatCard
                        title="Ingresos Totales"
                        value={`S/ ${resumen.ingresos_totales.toFixed(2)}`}
                        subtitle={`${resumen.cantidad_ventas} ventas realizadas`}
                        icon={<DollarSign className="w-6 h-6" />}
                        trend={{
                            value: resumen.variacion_ingresos,
                            isPositive: resumen.variacion_ingresos >= 0
                        }}
                        color="blue"
                    />
                    <StatCard
                        title="Ganancias"
                        value={`S/ ${resumen.ganancias_totales.toFixed(2)}`}
                        subtitle={`Margen: ${resumen.margen_general.toFixed(1)}%`}
                        icon={<TrendingUp className="w-6 h-6" />}
                        color="green"
                    />
                    <StatCard
                        title="Costos"
                        value={`S/ ${resumen.costos_totales.toFixed(2)}`}
                        subtitle="Total invertido"
                        icon={<Package className="w-6 h-6" />}
                        color="red"
                    />
                    <StatCard
                        title="Ticket Promedio"
                        value={`S/ ${resumen.ticket_promedio.toFixed(2)}`}
                        subtitle="Por venta"
                        icon={<ShoppingCart className="w-6 h-6" />}
                        color="purple"
                    />
                </div>
            )}

            {/* Gráficos */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Gráfico de vendedores */}
                <VendedorChart ventas={estadisticas?.ventas_vendedor || []} />
                
                {/* Gráfico de cajas */}
                <CajaChart ventas={estadisticas?.ventas_caja || []} />
            </div>

            {/* Gráfico de Proveedores */}
            {estadisticas?.proveedores && estadisticas.proveedores.length > 0 && (
                <ProveedorChart proveedores={estadisticas.proveedores} />
            )}

            {/* Tablas Detalladas */}
            <div className="space-y-6">
                {/* Costos y Ganancias por Proveedor */}
                {estadisticas?.proveedores && estadisticas.proveedores.length > 0 && (
                    <CostosProveedores proveedores={estadisticas.proveedores} />
                )}

                {/* Tablas de Vendedores y Cajas */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <VentasVendedor ventas={estadisticas?.ventas_vendedor || []} />
                    <VentasCaja ventas={estadisticas?.ventas_caja || []} />
                </div>
            </div>
        </div>
    );
}
