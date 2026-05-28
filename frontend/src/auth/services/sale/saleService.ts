// services/saleService.ts
import api from "../api";
import type {
  Venta,
  CreateVentaDTO,
  RegistrarPagoDTO,
  PagoResponse,
  Comprobante,
  VentaFilters,
  PaginatedVentasResponse,
  CreateVentaConClienteResponse
} from "../../types/sale/sale";

export const saleService = {
  // ==================== CREAR VENTA ====================
  async createVenta(data: CreateVentaDTO): Promise<Venta> {
    const { data: response } = await api.post<Venta>('/sales/ventas/', data);
    return response;
  },

  // ==================== LISTAR VENTAS ====================
  async getAll(filters?: VentaFilters): Promise<PaginatedVentasResponse> {
    const { data } = await api.get<PaginatedVentasResponse>(
      '/sales/ventas/',
      { params: filters }
    );
    return data;
  },

  // ==================== OBTENER VENTA POR ID ====================
  async getById(id: number): Promise<Venta> {
    const { data } = await api.get<Venta>(`/sales/ventas/${id}/`);
    return data;
  },

  // Alias para compatibilidad con modales
  async getVentaById(id: number): Promise<Venta> {
    return this.getById(id);
  },

  // ==================== OBTENER DETALLES DE VENTA ====================
  async getVentaDetalles(ventaId: number) {
    const venta = await this.getById(ventaId);
    return venta.detalles || [];
  },

  // ==================== ACTUALIZAR VENTA ====================
  async update(id: number, data: Partial<CreateVentaDTO>): Promise<Venta> {
    const { data: response } = await api.put<Venta>(
      `/sales/ventas/${id}/`,
      data
    );
    return response;
  },

  async partialUpdate(id: number, data: Partial<CreateVentaDTO>): Promise<Venta> {
    const { data: response } = await api.patch<Venta>(
      `/sales/ventas/${id}/`,
      data
    );
    return response;
  },

  // ==================== REGISTRAR PAGO ====================
  async registrarPago(
    ventaId: number,
    data: RegistrarPagoDTO
  ): Promise<PagoResponse> {
    const { data: response } = await api.post<PagoResponse>(
      `/sales/ventas/${ventaId}/registrar_pago/`,
      data
    );
    return response;
  },

  // ==================== ANULAR VENTA ====================
  async anular(ventaId: number, motivo: string): Promise<Venta> {
    const { data } = await api.post<Venta>(
      `/sales/ventas/${ventaId}/anular/`,
      { motivo }
    );
    return data;
  },

  // Alias para compatibilidad con ModalGestionarVenta
  async anularVenta(ventaId: number, params: { motivo: string }): Promise<Venta> {
    return this.anular(ventaId, params.motivo);
  },

  // ==================== ESTADOS DE PEDIDO ====================
  async marcarListo(ventaId: number): Promise<Venta> {
    const { data } = await api.post<Venta>(
      `/sales/ventas/${ventaId}/marcar_listo/`
    );
    return data;
  },

  async marcarEntregado(ventaId: number): Promise<Venta> {
    const { data } = await api.post<Venta>(
      `/sales/ventas/${ventaId}/marcar_entregado/`
    );
    return data;
  },

  // ==================== CONSULTAS ESPECIALES ====================
  async getPendientes(): Promise<Venta[]> {
    const { data } = await api.get<Venta[]>(
      '/sales/ventas/pendientes/'
    );
    return data;
  },

  async getDelDia(): Promise<Venta[]> {
    const { data } = await api.get<Venta[]>(
      '/sales/ventas/del_dia/'
    );
    return data;
  },

  // ==================== COMPROBANTE ====================
  async getComprobante(ventaId: number): Promise<Comprobante> {
    const { data } = await api.get<Comprobante>(
      `/sales/ventas/${ventaId}/comprobante/`
    );
    return data;
  },

  // ==================== ELIMINAR VENTA ====================
  async delete(ventaId: number): Promise<void> {
    await api.delete(`/sales/ventas/${ventaId}/`);
  },

  async createVentaConCliente(data: any): Promise<CreateVentaConClienteResponse> {
    const { data: response } = await api.post<CreateVentaConClienteResponse>('/sales/ventas/', data);
    return response;
  },

  // ==================== ACTUALIZAR DATOS DE LABORATORIO ====================
  async actualizarLaboratorio(
    detalleId: number,
    data: {
      lunaLaboratorio?: string;
      lunaCostoLaboratorio?: number;
    }
  ): Promise<any> {
    const { data: response } = await api.patch(
      `/sales/ventas-detalle/${detalleId}/actualizar_laboratorio/`,
      data
    );
    return response;
  },
};



export default saleService;