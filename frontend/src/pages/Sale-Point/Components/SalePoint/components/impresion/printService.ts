/**
 * Servicio de impresión de tickets térmicos
 * Compatible con desarrollo actual y futuro con Tauri
 */

import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export interface ProductoImpresion {
  cantidad: number;
  nombre: string;
  precio_unitario: number;
  subtotal: number;
  descuento?: number;
}

export interface DatosImpresion {
  folio: string;
  fecha: string;
  vendedor: string;
  cliente?: string;
  productos: ProductoImpresion[];
  subtotal: number;
  descuento_total: number;
  total: number;
  adelanto: number;
  saldo: number;
  metodo_pago?: string;
  referencia_pago?: string;
  observaciones?: string;
}

export interface ResultadoImpresion {
  success: boolean;
  mensaje?: string;
  error?: string;
  sugerencia?: string;
}

/**
 * Imprime un ticket de venta
 */
export const imprimirTicket = async (datos: DatosImpresion): Promise<ResultadoImpresion> => {
  try {
    const token = localStorage.getItem('accessToken');
    
    const response = await axios.post<ResultadoImpresion>(
      `${API_BASE_URL}/ventas/imprimir/`,
      datos,
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      }
    );
    
    return response.data;
  } catch (error: any) {
    if (error.response?.data) {
      return error.response.data;
    }
    
    return {
      success: false,
      error: error.message || 'Error al conectar con el servidor',
      sugerencia: 'Verifica que el backend esté ejecutándose'
    };
  }
};

/**
 * Prueba la conexión con la impresora térmica
 */
export const probarImpresora = async (): Promise<ResultadoImpresion> => {
  try {
    const token = localStorage.getItem('accessToken');
    
    const response = await axios.get<ResultadoImpresion>(
      `${API_BASE_URL}/ventas/imprimir/test/`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );
    
    return response.data;
  } catch (error: any) {
    if (error.response?.data) {
      return error.response.data;
    }
    
    return {
      success: false,
      error: error.message || 'Error al conectar con el servidor',
      sugerencia: 'Verifica que el backend esté ejecutándose'
    };
  }
};

/**
 * Reimprime el ticket de una venta existente
 */
export const reimprimirVenta = async (ventaId: number): Promise<ResultadoImpresion> => {
  try {
    const token = localStorage.getItem('accessToken');
    
    const response = await axios.post<ResultadoImpresion>(
      `${API_BASE_URL}/ventas/${ventaId}/imprimir/`,
      {},
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );
    
    return response.data;
  } catch (error: any) {
    if (error.response?.data) {
      return error.response.data;
    }
    
    return {
      success: false,
      error: error.message || 'Error al conectar con el servidor'
    };
  }
};
