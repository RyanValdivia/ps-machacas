/**
 * Servicio de impresión de tickets
 * Compatible con Tauri y desarrollo local
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface DatosImpresion {
  venta_id?: number;  // Si se envía, busca la venta en BD
  folio?: string;
  fecha?: string;
  vendedor?: string;
  cliente?: string;
  productos?: Array<{
    cantidad: number;
    nombre: string;
    precio_unitario: number;
    subtotal: number;
    descuento?: number;
  }>;
  subtotal?: number;
  descuento?: number;
  total: number;
  adelanto?: number;
  saldo?: number;
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

class PrinterService {
  /**
   * Imprime un ticket de venta
   * @param datos Datos de la venta a imprimir
   * @returns Resultado de la impresión
   */
  async imprimirTicket(datos: DatosImpresion): Promise<ResultadoImpresion> {
    try {
      const response = await fetch(`${API_URL}/api/sales/imprimir/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(datos),
      });

      const resultado = await response.json();
      return resultado;
    } catch (error) {
      console.error('Error al imprimir ticket:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Error desconocido al imprimir',
      };
    }
  }

  /**
   * Imprime un ticket usando el ID de la venta
   * (busca automáticamente los datos en la BD)
   * @param ventaId ID de la venta
   * @returns Resultado de la impresión
   */
  async imprimirTicketPorId(ventaId: number): Promise<ResultadoImpresion> {
    return this.imprimirTicket({ venta_id: ventaId, total: 0 });
  }

  /**
   * Prueba la conexión con la impresora
   * @returns Resultado de la prueba
   */
  async probarImpresora(): Promise<ResultadoImpresion> {
    try {
      const response = await fetch(`${API_URL}/api/sales/imprimir/test/`, {
        method: 'GET',
      });

      const resultado = await response.json();
      return resultado;
    } catch (error) {
      console.error('Error al probar impresora:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Error al conectar con la impresora',
      };
    }
  }
}

export const printerService = new PrinterService();
export default printerService;
