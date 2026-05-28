import api from "../api";

// services/lunaService.ts

// ==================== TIPOS ====================
export interface LunaMaterial {
  lunMatCod: number;
  lunMatNombre: string;
  lunMatDescripcion: string;
  lunMatActivo: boolean;
}

export interface LunaTipo {
  lunTipCod: number;
  lunTipNombre: string;
  lunTipDescripcion: string;
  lunTipActivo: boolean;
}

export interface LunaCaracteristica {
  lunCarCod: number;
  lunCarNombre: string;
  lunCarDescripcion: string;
  lunCarPrecioAdicional: number;
  lunCarActivo: boolean;
}

export interface LunaConfiguracion {
  lunConfCod: number;
  lunMatCod: {
    lunMatCod: number;
    lunMatNombre: string;
  };
  lunTipCod: {
    lunTipCod: number;
    lunTipNombre: string;
  };
  lunConfPrecioBase: number;
  lunConfActivo: boolean;
}

export interface CalculoPrecioRequest {
  lunConfCod: number;
  caracteristicas: number[];
}

export interface CalculoPrecioResponse {
  precio_base: number;
  precio_adicional: number;
  precio_total: number;
}

// ==================== SERVICIO ====================
class LunaService {
  private baseUrl = '/lunas';

  /**
   * Obtener todos los materiales activos
   */
  async getMateriales(): Promise<LunaMaterial[]> {
    const response = await api.get<LunaMaterial[]>(`${this.baseUrl}/materiales/`);
    return response.data;
  }

  /**
   * Obtener todos los tipos activos
   */
  async getTipos(): Promise<LunaTipo[]> {
    const response = await api.get<LunaTipo[]>(`${this.baseUrl}/tipos/`);
    return response.data;
  }

  /**
   * Obtener todas las características activas
   */
  async getCaracteristicas(): Promise<LunaCaracteristica[]> {
    const response = await api.get<LunaCaracteristica[]>(`${this.baseUrl}/caracteristicas/`);
    // Convertir precios a números (Django envía Decimal como string)
    return response.data.map(caract => ({
      ...caract,
      lunCarPrecioAdicional: Number(caract.lunCarPrecioAdicional)
    }));
  }

  /**
   * Obtener configuración por material y tipo
   */
  async getConfiguracion(materialId: number, tipoId: number): Promise<LunaConfiguracion> {
    const response = await api.get<LunaConfiguracion>(`${this.baseUrl}/configuracion/buscar/`, {
      params: {
        material: materialId,
        tipo: tipoId
      }
    });
    // Convertir precio base a número
    return {
      ...response.data,
      lunConfPrecioBase: Number(response.data.lunConfPrecioBase)
    };
  }

  /**
   * Calcular precio total (base + características)
   */
  async calcularPrecio(data: CalculoPrecioRequest): Promise<CalculoPrecioResponse> {
    const response = await api.post<CalculoPrecioResponse>(
      `${this.baseUrl}/configuracion/calcular_precio/`,
      {
        configuracion_id: data.lunConfCod,
        caracteristicas_ids: data.caracteristicas
      }
    );
    // Convertir precios a números
    return {
      ...response.data,
      precio_base: Number(response.data.precio_base),
      precio_adicional: Number(response.data.precio_adicional || 0),
      precio_total: Number(response.data.precio_total)
    };
  }

  /**
   * Obtener producto dummy LUNA-PERS
   */
  async getProductoDummy(): Promise<any> {
    const response = await api.get(`${this.baseUrl}/configuracion/producto_dummy/`);
    return response.data;
  }
}

export const lunaService = new LunaService();
