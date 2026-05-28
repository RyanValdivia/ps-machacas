import api from "./api";

export interface Laboratorio {
  id: number;
  labNombre: string;
  labActivo: boolean;
  labFechaCreacion: string;
  total_lunas?: number;
  total_gastado?: string;
}

export interface EstadisticasLaboratorio {
  laboratorios: Laboratorio[];
  total_laboratorios: number;
  total_lunas_procesadas: number;
  total_invertido: number;
}

const laboratorioService = {
  /**
   * Obtener todos los laboratorios activos
   */
  async getAll(incluirInactivos: boolean = false): Promise<Laboratorio[]> {
    try {
      const params = incluirInactivos ? '?incluir_inactivos=true' : '';
      const response = await api.get(`/sales/laboratorios/${params}`);
      return response.data;
    } catch (error) {
      console.error("Error al obtener laboratorios:", error);
      throw error;
    }
  },

  /**
   * Obtener laboratorios con estadísticas
   */
  async getAllConEstadisticas(): Promise<Laboratorio[]> {
    try {
      const response = await api.get('/sales/laboratorios/?con_estadisticas=true');
      return response.data;
    } catch (error) {
      console.error("Error al obtener laboratorios con estadísticas:", error);
      throw error;
    }
  },

  /**
   * Obtener un laboratorio específico
   */
  async getById(id: number): Promise<Laboratorio> {
    try {
      const response = await api.get(`/sales/laboratorios/${id}/`);
      return response.data;
    } catch (error) {
      console.error(`Error al obtener laboratorio ${id}:`, error);
      throw error;
    }
  },

  /**
   * Crear nuevo laboratorio
   */
  async create(data: { labNombre: string }): Promise<Laboratorio> {
    try {
      const response = await api.post('/sales/laboratorios/', data);
      return response.data;
    } catch (error) {
      console.error("Error al crear laboratorio:", error);
      throw error;
    }
  },

  /**
   * Actualizar laboratorio
   */
  async update(id: number, data: Partial<Laboratorio>): Promise<Laboratorio> {
    try {
      const response = await api.patch(`/sales/laboratorios/${id}/`, data);
      return response.data;
    } catch (error) {
      console.error(`Error al actualizar laboratorio ${id}:`, error);
      throw error;
    }
  },

  /**
   * Desactivar laboratorio (soft delete)
   */
  async delete(id: number): Promise<void> {
    try {
      await api.delete(`/sales/laboratorios/${id}/`);
    } catch (error) {
      console.error(`Error al desactivar laboratorio ${id}:`, error);
      throw error;
    }
  },

  /**
   * Reactivar laboratorio
   */
  async activar(id: number): Promise<void> {
    try {
      await api.post(`/sales/laboratorios/${id}/activar/`);
    } catch (error) {
      console.error(`Error al activar laboratorio ${id}:`, error);
      throw error;
    }
  },

  /**
   * Obtener estadísticas generales de laboratorios
   */
  async getEstadisticas(): Promise<EstadisticasLaboratorio> {
    try {
      const response = await api.get('/sales/laboratorios/estadisticas/');
      return response.data;
    } catch (error) {
      console.error("Error al obtener estadísticas:", error);
      throw error;
    }
  },
};

export default laboratorioService;
