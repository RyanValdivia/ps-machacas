// types/sale/sale.ts
// ─── Enums base (coinciden con el modelo Django) ───────────────────────────

export type EstadoVenta = 'PENDIENTE' | 'PAGADO' | 'PARCIAL' | 'ANULADO';
export type EstadoPedido = 'PENDIENTE' | 'LISTO' | 'ENTREGADO' | 'ANULADO';
export type FormaPago = 'EFECTIVO' | 'YAPE' | 'VISA';
export type TipoTarjeta = 'VISA';
export type TipoDocumento = 'DNI' | 'RUC' | 'CE';

// ─── Cliente ────────────────────────────────────────────────────────────────

export interface Cliente {
  cliCod: number;
  cliNomCompleto: string;
  cliNumDoc: string;
  cliTipoDoc: string;
  nombre_completo: string;
}

export interface VentaResponse {
  ventCod: number;
  ventFecha: string;

  // Cliente nested (viene de ClienteSimpleSerializer)
  cliente: {
    cliCod: number;
    cliNomCompleto: string;  // campo del modelo Client
    cliNumDoc: string;
    cliTipoDoc: string;
    nombre_completo: string; // SerializerMethodField
  } | null;                  // puede ser null si es "Cliente Generico"

  nombre_cliente: string;    // property del modelo: nombre del cliente o "Cliente Generico"
  vendedor: string;          // username del usuario

  ventTotal: number;
  ventAdelanto: number;
  ventSaldo: number;

  ventEstado: EstadoVenta;
  estado_pago_display: string;      // "Pendiente", "Pagado", "Pago Parcial", "Anulado"

  ventEstadoRecoj: EstadoPedido;
  estado_pedido_display: string;    // "Pendiente", "En Laboratorio", "Listo para recoger", "Entregado", "Anulado"

  ventAnulada: boolean;
}

// ─── Venta (detalle completo) ───────────────────────────────────────────────
// Coincide con VentaDetailSerializer

export interface VentaDetalle {
  ventDetCod: number;
  prodCod: number;
  producto?: {
    prodCod: number;
    prodCode: string;
    prodDescr: string;
    prodMarca: string;
    prodPrecioVenta: string;
    prodStock: number;
    categoria?: string;
  };
  ventDetCantidad: number;
  ventDetPrecioUni: string | number;
  ventDetSubtotal: string | number;
  ventDetDescuento: string | number;
  ventDetTotal: string | number;
  ventDetDescripcion: string;
  ventDetMarca?: string;
  ventDetAnulado: boolean;
  
  // Campos de luna personalizada
  esLunaPersonalizada?: boolean;
  lunaMaterial?: string;
  lunaTipo?: string;
  lunaCaracteristicas?: string;
  lunaLaboratorio?: number;  // Ahora es ID del proveedor
  lunaLaboratorio_nombre?: string;  // Nombre del proveedor
  lunaLaboratorio_id?: number;  // ID del proveedor (alias)
  lunaCostoLaboratorio?: number;
}

export interface Venta {
  ventCod: number;
  ventFecha: string;
  ventFechaEntrega?: string;

  usuCod: number;
  vendedor: string;

  cliCod?: number;
  cliente?: {
    cliCod: number;
    cliNomCompleto: string;
    cliNumDoc: string;
    cliTipoDoc: string;
    nombre_completo: string;
  } | null;
  nombre_cliente: string;

  cajaAperCod?: number;

  ventSubTotal: number;
  ventDescuento: number;
  ventTotal: number;
  ventAdelanto: number;
  ventSaldo: number;

  ventEstado: EstadoVenta;
  estado_pago_display: string;

  ventEstadoRecoj: EstadoPedido;
  estado_pedido_display: string;

  ventFormaPago: FormaPago;
  forma_pago_display: string;
  ventReferenciaPago?: string;
  ventTarjetaTipo?: TipoTarjeta;

  ventObservaciones?: string;
  ventAnulada: boolean;
  ventMotivoAnulacion?: string;

  detalles: VentaDetalle[];
}

// ─── Paginación ─────────────────────────────────────────────────────────────

export interface PaginatedVentasResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: VentaResponse[];   // ← results contiene VentaResponse[]
}

// ─── DTOs de escritura ──────────────────────────────────────────────────────

export interface CreateVentaDTO {
  cliCod?: number;
  ventObservaciones?: string;
  ventFormaPago: FormaPago;
  ventReferenciaPago?: string;
  ventTarjetaTipo?: TipoTarjeta;

  detalles: {
    prodCod: number;
    ventDetCantidad: number;
    ventDetPrecioUni: number;
    ventDetDescuento: number;
  }[];
}

export interface RegistrarPagoDTO {
  monto: number;
  forma_pago: FormaPago;
  referencia_pago?: string;
  tarjeta_tipo?: TipoTarjeta;
}

// ─── Filtros ────────────────────────────────────────────────────────────────

export interface VentaFilters {
  page?: number;
  page_size?: number;
  
  // Filtros de búsqueda
  search?: string;  // Búsqueda general (ventCod, cliente, documento, vendedor)
  cliente_nombre?: string;
  cliente_doc?: string;
  vendedor?: string;
  
  // Filtros de fecha
  fecha_desde?: string;
  fecha_hasta?: string;
  fecha_entrega?: string;
  
  // Filtros de estado
  estado?: EstadoVenta;
  estado_pedido?: string;  // Coincide con el filtro del backend
  forma_pago?: FormaPago;
  
  // Filtros de monto
  total_min?: number;
  total_max?: number;
  
  // Filtros booleanos
  anuladas?: boolean;
  con_saldo?: boolean;
  
  // Ordenamiento
  ordering?: string;
}

// ─── Pago ───────────────────────────────────────────────────────────────────

export interface PagoResponse {
  mensaje: string;
  saldo_actual: number;
  estado: EstadoVenta;
  comprobante?: string;
  venta?: Venta;
}

// ─── Respuesta de creación de venta con cliente ────────────────────────────

export interface CreateVentaConClienteResponse {
  venta: Venta;
  cliente_creado: boolean;
  cliente_id: number | null;
  mensaje: string;
}

// ─── Comprobante ────────────────────────────────────────────────────────────

export interface ComprobanteDetalle {
  comprDetCod: number;
  comprDetDescripcion: string;
  comprDetCantidad: number;
  comprDetPrecioUni: number;
  comprDetSubtotal: number;
  comprDetDescuento: number;
  comprDetTotal: number;
}

export interface Comprobante {
  comprCod: number;
  comprSerie: string;
  comprCorrelativo: number;
  comprobante_completo: string;
  comprFechaEmision: string;

  comprNombreCliente: string;
  comprDocumentoCliente?: string;

  comprSubtotal: number;
  comprDescuento: number;
  comprTotal: number;

  comprAnulado: boolean;
  detalles: ComprobanteDetalle[];
}

// ─── Cart (local, no viene del backend) ─────────────────────────────────────

import type { Product } from "../product/product";

export interface Customer {
  cliCod?: number;
  cliNombreCom: string;
  cliDocTipo: TipoDocumento;
  cliDocNum: string;
  cliDireccion?: string;
  cliTelef?: string;
}

export interface CartItem {
  product: Product;
  quantity: number;
  discountAmount: number;
  subTotal: number;
  total: number;
  
  // Para lunas personalizadas
  esLunaPersonalizada?: boolean;
  lunConfCod?: number;  // ID de la configuración
  lunaCaracteristicas?: number[];  // IDs de características seleccionadas
  lunaDescripcion?: string;  // Descripción formateada para mostrar
}

export const createCartItem = (
  product: Product,
  quantity: number = 1,
  discountAmount: number = 0
): CartItem => {
  const precio = Number(product.prodPrecioVenta);
  const subtotal = precio * quantity;
  const descuento = Math.min(discountAmount, subtotal);

  return {
    product,
    quantity,
    discountAmount: Number(descuento.toFixed(2)),
    subTotal: Number(subtotal.toFixed(2)),
    total: Number((subtotal - descuento).toFixed(2)),
  };
};

export const calculateSaleValues = (cart: CartItem[]) => {
  let totalVenta = 0;
  let totalDescuento = 0;

  cart.forEach(item => {
    totalVenta += item.total;
    totalDescuento += item.discountAmount;
  });

  return {
    subtotalSinDescuento: Number((totalVenta + totalDescuento).toFixed(2)),
    totalDescuento: Number(totalDescuento.toFixed(2)),
    totalVenta: Number(totalVenta.toFixed(2)),
  };
};