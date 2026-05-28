/**
 * Utilidades para formatear datos de venta para impresión
 */

import type { CartItem } from '../../../../../../auth/types/sale/sale';
import type { DatosImpresion, ProductoImpresion } from './printService';
import type { User } from '../../../../../../auth/types/user';

/**
 * Convierte los datos de una venta del punto de venta al formato de impresión
 */
export const formatearDatosParaImpresion = (
  ventaCreada: any,
  cart: CartItem[],
  currentUser: User | null,
  adelanto: number,
  metodo_pago: string,
  referencia_pago?: string,
  observaciones?: string
): DatosImpresion => {
  // Formatear productos
  const productos: ProductoImpresion[] = cart.map(item => ({
    cantidad: item.quantity,
    nombre: item.product.prodDescr,
    precio_unitario: Number(item.product.prodPrecioVenta),
    subtotal: item.subTotal,
    descuento: item.discountAmount
  }));

  // Calcular totales
  const subtotal = cart.reduce((sum, item) => sum + item.subTotal, 0);
  const descuento_total = cart.reduce((sum, item) => sum + item.discountAmount, 0);
  const total = cart.reduce((sum, item) => sum + item.total, 0);
  const saldo = total - adelanto;

  // Formatear fecha
  const fecha = new Date().toLocaleString('es-PE', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  });

  return {
    folio: ventaCreada.ventCod?.toString() || 'N/A',
    fecha: fecha,
    vendedor: currentUser?.usuNombreCom || currentUser?.usuNom || 'Vendedor',
    cliente: ventaCreada.nombre_cliente || 'Cliente General',
    productos: productos,
    subtotal: Number(subtotal.toFixed(2)),
    descuento_total: Number(descuento_total.toFixed(2)),
    total: Number(total.toFixed(2)),
    adelanto: Number(adelanto.toFixed(2)),
    saldo: Number(saldo.toFixed(2)),
    metodo_pago: adelanto > 0 ? metodo_pago : undefined,
    referencia_pago: referencia_pago || '',
    observaciones: observaciones || ''
  };
};

/**
 * Valida que los datos de impresión estén completos
 */
export const validarDatosImpresion = (datos: DatosImpresion): { valido: boolean; error?: string } => {
  if (!datos.productos || datos.productos.length === 0) {
    return { valido: false, error: 'No hay productos para imprimir' };
  }

  if (!datos.total || datos.total <= 0) {
    return { valido: false, error: 'El total de la venta debe ser mayor a 0' };
  }

  if (!datos.folio) {
    return { valido: false, error: 'Falta el folio de la venta' };
  }

  return { valido: true };
};

/**
 * Formatea el resultado de impresión para mostrar al usuario
 */
export const formatearMensajeImpresion = (resultado: {
  success: boolean;
  mensaje?: string;
  error?: string;
  sugerencia?: string;
}): string => {
  if (resultado.success) {
    return resultado.mensaje || '✅ Ticket impreso correctamente';
  }

  let mensaje = `❌ ${resultado.error || 'Error al imprimir'}`;
  
  if (resultado.sugerencia) {
    mensaje += `\n\n💡 ${resultado.sugerencia}`;
  }

  return mensaje;
};
