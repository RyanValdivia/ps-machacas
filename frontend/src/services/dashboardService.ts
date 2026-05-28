// services/dashboardService.ts
import api from "../auth/services/api";

const dashboardService = {
  // Usar endpoints existentes de sales, products y clients
  
  async getVentasStats() {
    // Usar endpoint de ventas filtrado por fecha
    const hoy = new Date().toISOString().split('T')[0];
    const inicioMes = new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0];
    
    const [ventasHoy, ventasMes, ventasPendientes] = await Promise.all([
      api.get(`/sales/ventas/?fecha_inicio=${hoy}`),
      api.get(`/sales/ventas/?fecha_inicio=${inicioMes}`),
      api.get('/sales/ventas/pendientes/')
    ]);
    
    return {
      ventasHoy: ventasHoy.data,
      ventasMes: ventasMes.data,
      ventasPendientes: ventasPendientes.data
    };
  },

  async getProductosStats() {
    const { data } = await api.get('/products/');
    const productos = data.results || data;
    
    return {
      total: productos.length,
      bajoStock: productos.filter((p: any) => p.prodStock < 10).length,
      sinStock: productos.filter((p: any) => p.prodStock === 0).length
    };
  },

  async getClientesStats() {
    const { data } = await api.get('/clients/client/');
    return {
      total: data.count || (data.results?.length || 0)
    };
  },

  async getProductosBajoStock() {
    const { data } = await api.get('/products/');
    const productos = data.results || data;
    return productos.filter((p: any) => p.prodStock < 10 && p.prodStock > 0);
  },

  async getProductosSinStock() {
    const { data } = await api.get('/products/');
    const productos = data.results || data;
    return productos.filter((p: any) => p.prodStock === 0);
  },

  async getEstadisticasDashboard(periodo?: 'dia' | 'semana' | 'mes' | 'personalizado', fechaDesde?: string, fechaHasta?: string) {
    const params: any = {};
    if (periodo) params.periodo = periodo;
    if (fechaDesde) params.fecha_desde = fechaDesde;
    if (fechaHasta) params.fecha_hasta = fechaHasta;
    
    const { data } = await api.get('/sales/ventas/estadisticas_dashboard/', { params });
    return data;
  },
};

export default dashboardService;
