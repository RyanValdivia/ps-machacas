import React, { useState } from 'react';
import ProductSearch from './components/ProductSearch';
import ProductCart from './components/ProductCart';
import TransactionPanel from './components/TransactionPanel';
import ModalConfiguradorLuna, { type LunaConfiguracionData } from './components/ModalConfiguradorLuna';
import { lunaService } from '../../../../auth/services/luna/lunaService';
import { printerService } from '../../../../auth/services/printer/printerService';
import { useNavigate, useOutletContext } from 'react-router-dom';
import { LogOut, CheckCircle, Eye } from "lucide-react";
import type { Product } from '../../../../auth/types/product/product';
import type { CartItem, FormaPago, TipoTarjeta, Customer, RegistrarPagoDTO } from '../../../../auth/types/sale/sale';
import { createCartItem, calculateSaleValues } from '../../../../auth/types/sale/sale';
import { saleService } from '../../../../auth/services/sale/saleService';
import type { User } from '../../../../auth/types/user';
import {
  showSuccessToast,
  showErrorToast,
  showWarningToast,
  showConfirmation,
  showSuccessAlert,
  showErrorAlert
} from '../../../../utils/sweetAlertConfig';

interface SalePointContext {
  currentUser: User | null;
  refreshOpenCash: () => void;
}

const SalePoint: React.FC = () => {
  const navigate = useNavigate();
  const { currentUser } = useOutletContext<SalePointContext>();
  const [cart, setCart] = useState<CartItem[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedVendor, setSelectedVendor] = useState<number | null>(null);
  const [processingSale, setProcessingSale] = useState(false);
  const [showLunaModal, setShowLunaModal] = useState(false);

  // ==================== AGREGAR PRODUCTO ====================
  const handleProductSelect = (product: Product) => {
    // Buscar si ya existe (solo productos normales, las lunas son siempre únicas)
    const existingItemIndex = cart.findIndex(item =>
      item.product.prodCod === product.prodCod && !item.esLunaPersonalizada
    );

    if (existingItemIndex !== -1) {
      // Incrementar cantidad si ya existe
      const existingItem = cart[existingItemIndex];
      const maxStock = product.prodStock || 0;

      if (existingItem.quantity >= maxStock) {
        showWarningToast(`Stock máximo alcanzado (${maxStock} unidades)`);
        return;
      }

      handleUpdateQuantity(existingItemIndex, existingItem.quantity + 1);
    } else {
      // Agregar nuevo producto
      const newItem = createCartItem(product, 1, 0);
      setCart([...cart, newItem]);
    }

    setSearchQuery('');
  };

  // ==================== AGREGAR LUNA PERSONALIZADA ====================
  const handleAddLuna = async (config: LunaConfiguracionData) => {
    try {
      // Obtener el producto dummy LUNA-PERS
      const productoDummy = await lunaService.getProductoDummy();

      if (!productoDummy) {
        showErrorToast('No se encontró el producto Luna Personalizada');
        return;
      }

      // Generar descripción formateada
      const partes = [config.materialNombre, config.tipoNombre];
      if (config.caracteristicasNombres.length > 0) {
        partes.push(config.caracteristicasNombres.join(', '));
      }
      const descripcionLuna = `Luna: ${partes.join(' - ')}`;

      // Precio final (manual o sugerido)
      const precioFinal = config.precioVentaManual || config.precioTotal;

      // Crear item del carrito
      const lunaProduct: Product = {
        ...productoDummy,
        prodDescr: descripcionLuna,
        prodPrecioVenta: precioFinal.toString()
      };

      const lunaItem: CartItem = {
        product: lunaProduct,
        quantity: 1,
        discountAmount: 0,
        subTotal: precioFinal,
        total: precioFinal,
        esLunaPersonalizada: true,
        lunConfCod: config.lunConfCod,
        lunaCaracteristicas: config.caracteristicasIds,
        lunaDescripcion: descripcionLuna
      };

      setCart([...cart, lunaItem]);
      setShowLunaModal(false);
      showSuccessToast('Luna agregada al carrito');
    } catch (error) {
      console.error('Error agregando luna:', error);
      showErrorToast('Error al agregar luna al carrito');
    }
  };

  // ==================== ACTUALIZAR CANTIDAD ====================
  const handleUpdateQuantity = (index: number, newQuantity: number) => {
    setCart(cart.map((item, i) => {
      if (i === index) {
        // Para lunas personalizadas, mantener los campos especiales
        if (item.esLunaPersonalizada) {
          const precio = Number(item.product.prodPrecioVenta);
          const subtotal = precio * newQuantity;
          const descuento = Math.min(item.discountAmount, subtotal);

          return {
            ...item,
            quantity: newQuantity,
            discountAmount: Number(descuento.toFixed(2)),
            subTotal: Number(subtotal.toFixed(2)),
            total: Number((subtotal - descuento).toFixed(2)),
          };
        }
        return createCartItem(item.product, newQuantity, item.discountAmount);
      }
      return item;
    }));
  };

  // ==================== ACTUALIZAR DESCUENTO (EN SOLES) ====================
  const handleUpdateDiscount = (index: number, newDiscountAmount: number) => {
    setCart(cart.map((item, i) => {
      if (i === index) {
        // Para lunas personalizadas, mantener los campos especiales
        if (item.esLunaPersonalizada) {
          const precio = Number(item.product.prodPrecioVenta);
          const subtotal = precio * item.quantity;
          const descuento = Math.min(newDiscountAmount, subtotal);

          return {
            ...item,
            discountAmount: Number(descuento.toFixed(2)),
            total: Number((subtotal - descuento).toFixed(2)),
          };
        }
        return createCartItem(item.product, item.quantity, newDiscountAmount);
      }
      return item;
    }));
  };

  // ==================== ELIMINAR PRODUCTO ====================
  const handleRemoveItem = (index: number) => {
    setCart(cart.filter((_, i) => i !== index));
  };

  // ==================== LIMPIAR CARRITO ====================
  const handleClearCart = async () => {
    if (cart.length === 0) return;

    const result = await showConfirmation(
      '¿Vaciar carrito?',
      'Se eliminarán todos los productos del carrito',
      'Sí, vaciar',
      'Cancelar'
    );

    if (result.isConfirmed) {
      setCart([]);
      showSuccessToast('Carrito vaciado');
    }
  };

  // ==================== CALCULAR TOTALES ====================
  const totals = calculateSaleValues(cart);

  // ==================== PROCESAR VENTA ====================
  const handleProcessSale = async (saleData: {
    customer: Customer | null;
    paymentMethod: FormaPago;
    vendorId: number | null;
    referenciaPago?: string;
    tipoTarjeta?: TipoTarjeta;
    adelanto?: number;
    observaciones?: string;
  }) => {
    try {
      setProcessingSale(true);

      // Validaciones
      if (cart.length === 0) {
        showWarningToast('El carrito está vacío');
        return;
      }

      if (!saleData.vendorId) {
        showWarningToast('Selecciona un vendedor');
        return;
      }

      const adelanto = saleData.adelanto || 0;

      if (adelanto < 0) {
        showWarningToast('El adelanto no puede ser negativo');
        return;
      }

      if (adelanto > totals.totalVenta) {
        showWarningToast('El adelanto no puede ser mayor al total de la venta');
        return;
      }

      // Preparar datos de la venta
      const ventaData: any = {
        ventObservaciones: saleData.observaciones || '',
        // Solo enviar método de pago si hay adelanto
        ventFormaPago: adelanto > 0 ? saleData.paymentMethod : '',
        ventReferenciaPago: adelanto > 0 ? (saleData.referenciaPago || '') : '',
        ventTarjetaTipo: adelanto > 0 ? saleData.tipoTarjeta : undefined,
        detalles: cart.map(item => {
          const detalle: any = {
            prodCod: item.product.prodCod,
            ventDetCantidad: item.quantity,
            ventDetDescuento: item.discountAmount
          };

          // Si es luna personalizada, agregar campos específicos
          if (item.esLunaPersonalizada) {
            detalle.esLunaPersonalizada = true;
            detalle.lunConfCod = item.lunConfCod;
            detalle.lunaCaracteristicas = item.lunaCaracteristicas || [];
            // El precio ya está en el producto por el override
            detalle.ventDetPrecioUni = Number(item.product.prodPrecioVenta);
          } else {
            detalle.ventDetPrecioUni = Number(item.product.prodPrecioVenta);
          }

          return detalle;
        })
      };

      // Enviar datos del cliente si tiene nombre (con o sin documento)
      if (saleData.customer && saleData.customer.cliNombreCom?.trim()) {
        ventaData.cliente = {
          cliDocTipo: saleData.customer.cliDocTipo || '',
          cliDocNum: saleData.customer.cliDocNum?.trim() || '',
          cliNomCompleto: saleData.customer.cliNombreCom.trim(),
          cliTelef: saleData.customer.cliTelef?.trim() || '',
        };
      }

      // Crear la venta
      const result = await saleService.createVentaConCliente(ventaData);
      console.log('✓ Respuesta del backend:', result);

      const ventaId = result.venta.ventCod;

      // Registrar pago/adelanto solo si hay monto
      if (adelanto > 0) {
        const pagoData: RegistrarPagoDTO = {
          monto: adelanto,
          forma_pago: saleData.paymentMethod,
          referencia_pago: saleData.referenciaPago || '',
          tarjeta_tipo: saleData.tipoTarjeta,
        };

        await saleService.registrarPago(ventaId, pagoData);
      }

      try {
        // Imprimir usando el ID de la venta (busca automáticamente en BD)
        const resultadoImpresion = await printerService.imprimirTicketPorId(ventaId);

        if (!resultadoImpresion.success) {
          // Venta creada pero error al imprimir
          console.warn('Error al imprimir:', resultadoImpresion);
          
          // Mensaje personalizado según el tipo de error
          let tituloAlerta = 'Venta guardada correctamente';
          let mensajeCompleto = `Venta #${ventaId} registrada exitosamente.\n\n` +
                                `Sin embargo, no se pudo imprimir el ticket:`;
                    
          await showSuccessAlert(tituloAlerta, mensajeCompleto);
        } else {
          // Todo correcto
          await showSuccessAlert(
            `Venta #${ventaId} registrada e impresa correctamente.`
          );
        }
      } catch (errorImpresion: any) {
        
        // Extraer información del error
        let mensajeError = 'No se pudo conectar con el sistema de impresión';
        let sugerencia = 'Verifica que el servidor esté funcionando correctamente';

        if (errorImpresion.response?.data) {
          mensajeError = errorImpresion.response.data.error || mensajeError;
          sugerencia = errorImpresion.response.data.sugerencia || sugerencia;
        } else if (errorImpresion.message) {
          mensajeError = errorImpresion.message;
        }

        await showSuccessAlert(
          'Venta guardada correctamente',
          `Venta #${ventaId} registrada exitosamente.\n\n` +
          `Problema con la impresión:\n\n`
        );
      }

      // Limpiar carrito (pero mantener vendedor seleccionado para próximas ventas)
      setCart([]);
      // NO resetear selectedVendor - mantener el usuario activo seleccionado

    } catch (error: any) {
      console.error('Error procesando venta:', error);
      console.error('Respuesta del backend:', JSON.stringify(error.response?.data, null, 2));

      let errorMessage = 'Error desconocido. Por favor, intenta de nuevo.';

      if (error.response?.data) {
        const errorData = error.response.data;

        // Manejar errores de validación del serializer
        if (typeof errorData === 'object' && !errorData.message && !errorData.detail) {
          // Es un objeto con errores de campos
          const errores = Object.entries(errorData)
            .map(([campo, mensajes]) => {
              if (Array.isArray(mensajes)) {
                return `${campo}: ${mensajes.join(', ')}`;
              }
              return `${campo}: ${mensajes}`;
            })
            .join('\n');
          errorMessage = `Errores de validación:\n${errores}`;
        } else if (typeof errorData === 'string') {
          errorMessage = errorData;
        } else if (errorData.message) {
          errorMessage = errorData.message;
        } else if (errorData.detail) {
          errorMessage = errorData.detail;
        } else {
          errorMessage = JSON.stringify(errorData);
        }
      } else if (error.message) {
        errorMessage = error.message;
      }

      showErrorAlert('Error al procesar la venta', errorMessage);
    } finally {
      setProcessingSale(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Área Principal */}
      <div className="flex-1 flex flex-col pt-2 md:pt-3 lg:pt-5 px-2 md:px-3 lg:px-5">
        <header className="px-1 pt-2 md:pt-4 lg:pt-6 rounded-t-lg">
          <div className="flex justify-between items-center">
            <div className="flex items-start justify-between w-full">
              <div className="pr-2 md:pr-4">
                <h1 className="text-xl md:text-2xl lg:text-3xl font-bold text-gray-800">Punto de Venta</h1>
                <p className="text-xs md:text-sm text-gray-500 mt-0.5 md:mt-1">Procesa ventas rápidamente</p>
              </div>

              <div className="flex items-center gap-1 md:gap-2 lg:gap-3">
                {/* Indicador de items */}
                {cart.length > 0 && (
                  <div className="flex items-center gap-1 md:gap-2 bg-blue-50 px-2 md:px-3 lg:px-4 py-1.5 md:py-2 rounded-lg border border-blue-200">
                    <CheckCircle className="w-4 h-4 md:w-5 md:h-5 text-blue-600" />
                    <div className="text-xs md:text-sm">
                      <span className="font-bold text-blue-900">{cart.length}</span>
                      <span className="text-blue-700 ml-1 hidden md:inline">
                        {cart.length === 1 ? 'producto' : 'productos'}
                      </span>
                    </div>
                  </div>
                )}

                {/* Limpiar carrito */}
                {cart.length > 0 && (
                  <button
                    onClick={handleClearCart}
                    className="px-2 md:px-3 lg:px-4 py-1.5 md:py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors text-xs md:text-sm font-medium"
                  >
                    <span className="hidden md:inline">Limpiar</span>
                    <span className="md:hidden">🗑️</span>
                  </button>
                )}

                {/* Botón Agregar Luna */}
                <button
                  onClick={() => setShowLunaModal(true)}
                  className="flex items-center gap-1 md:gap-2 px-2 md:px-3 py-1.5 md:py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-xs md:text-sm font-medium"
                >
                  <Eye className="w-4 h-4 md:w-4 md:h-4" />
                  <span className="hidden sm:inline">Luna</span>
                </button>

                {/* Cerrar caja */}
                <button
                  onClick={() => navigate("/sale-point/close-cash")}
                  className="flex items-center gap-1 md:gap-2 px-2 md:px-3 lg:px-4 py-1.5 md:py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors text-xs md:text-sm font-medium"
                >
                  <LogOut className="w-4 h-4 md:w-[18px] md:h-[18px]" />
                  <span className="hidden sm:inline">Cerrar Caja</span>
                </button>
              </div>
            </div>
          </div>

          {/* Procesando */}
          {processingSale && (
            <div className="mt-2 md:mt-3 lg:mt-4 flex items-center justify-center space-x-2 bg-blue-50 px-3 md:px-4 py-2 md:py-3 rounded-lg border border-blue-200">
              <div className="w-4 h-4 md:w-5 md:h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              <span className="text-xs md:text-sm lg:text-base text-blue-700 font-medium">Procesando venta...</span>
            </div>
          )}
        </header>

        {/* Búsqueda */}
        <ProductSearch
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          onProductSelect={handleProductSelect}
          onAddLunaClick={() => setShowLunaModal(true)}
        />

        {/* Carrito */}
        <div className="flex-1 overflow-hidden flex flex-col min-h-0">
          <ProductCart
            cart={cart}
            onUpdateQuantity={handleUpdateQuantity}
            onUpdateDiscount={handleUpdateDiscount}
            onRemoveItem={handleRemoveItem}
          />
        </div>
      </div>

      {/* Panel de Transacción - Responsive */}
      <div className="w-full md:w-96 lg:w-[380px] xl:w-[420px] flex-shrink-0">
        <TransactionPanel
          cart={cart}
          selectedVendor={selectedVendor}
          onVendorChange={setSelectedVendor}
          onProcessSale={handleProcessSale}
          totalVenta={totals.totalVenta}
          currentUser={currentUser}
        />
      </div>

      {/* Modal Configurador de Luna */}
      <ModalConfiguradorLuna
        isOpen={showLunaModal}
        onClose={() => setShowLunaModal(false)}
        onConfirm={handleAddLuna}
      />
    </div>
  );
};

export default SalePoint;