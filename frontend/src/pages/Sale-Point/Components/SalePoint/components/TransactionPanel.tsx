import React, { useState, useEffect } from 'react';
import { 
  Banknote, CreditCard, Loader, 
  Smartphone, CheckCircle, AlertCircle, Loader2, User 
} from 'lucide-react';
import type { 
  Customer, 
  FormaPago, 
  CartItem, 
  TipoDocumento,
  TipoTarjeta
} from '../../../../../auth/types/sale/sale';
import { getSellers } from '../../../../../auth/services/userService';
import { consultarDni } from '../../../../../services/reniec/reniecService';
import { buscarClientePorDocumento } from '../../../../../services/clientService';
import type { Client } from '../../../../../types/client';
import type { User as UserType } from '../../../../../auth/types/user';
import { 
  showWarningToast, 
  showConfirmation 
} from '../../../../../utils/sweetAlertConfig';
import TicketPreview from './TicketPreview';

interface TransactionPanelProps {
  cart: CartItem[];
  selectedVendor: number | null;
  onVendorChange: (vendorId: number | null) => void;
  onProcessSale: (saleData: {
    customer: Customer | null;
    paymentMethod: FormaPago;
    vendorId: number | null;
    referenciaPago?: string;
    tipoTarjeta?: TipoTarjeta;
    adelanto?: number;
    observaciones?: string;
  }) => void;
  totalVenta: number;
  currentUser: UserType | null;
}

interface Vendor {
  id: number;
  name: string;
  role: string;
}

interface TipoComprobante {
  value: '01' | '03';
  label: string;
  description: string;
}

const TransactionPanel: React.FC<TransactionPanelProps> = ({
  cart,
  selectedVendor,
  onVendorChange,
  onProcessSale,
  totalVenta,
  currentUser
}) => {
  // Estados internos
  const [showCustomerDetails, setShowCustomerDetails] = useState(true);
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [paymentMethod, setPaymentMethod] = useState<FormaPago>('EFECTIVO');
  const [tipoComprobante, setTipoComprobante] = useState<'01' | '03'>('03');
  const [referenciaPago, setReferenciaPago] = useState('');
  const [tipoTarjeta, setTipoTarjeta] = useState<TipoTarjeta | undefined>(undefined);
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [loadingVendors, setLoadingVendors] = useState(false);
  const [adelanto, setAdelanto] = useState(0);
  const [consultandoDni, setConsultandoDni] = useState(false);
  const [dniEncontrado, setDniEncontrado] = useState(false);
  const [errorDni, setErrorDni] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [observaciones, setObservaciones] = useState('');

  const [clienteExistente, setClienteExistente] = useState<Client | null>(null);
  const [buscandoCliente, setBuscandoCliente] = useState(false);
  const [clienteNoEncontrado, setClienteNoEncontrado] = useState(false);
  const [showTicketPreview, setShowTicketPreview] = useState(false);

  const saldoPendiente = Math.max(0, totalVenta - adelanto);

  // Función unificada de búsqueda: BD → RENIEC → Manual
  const buscarClienteCompleto = async (tipoDoc: TipoDocumento, numDoc: string) => {
    const longitudMinima = tipoDoc === 'RUC' ? 11 : 8;
    
    if (!numDoc || numDoc.length < longitudMinima) {
      setClienteExistente(null);
      setClienteNoEncontrado(false);
      setDniEncontrado(false);
      setErrorDni(null);
      return;
    }

    try {
      // PASO 1: Buscar en Base de Datos
      setBuscandoCliente(true);
      setClienteNoEncontrado(false);
      setErrorDni(null);
      setDniEncontrado(false);
      
      const resultado = await buscarClientePorDocumento(tipoDoc, numDoc);
      
      if (resultado.encontrado && resultado.cliente) {
        setClienteExistente(resultado.cliente);
        setClienteNoEncontrado(false);
        
        setCustomer({
          cliCod: resultado.cliente.cliCod,
          cliNombreCom: resultado.cliente.cliNomCompleto,
          cliDocTipo: resultado.cliente.cliTipoDoc as TipoDocumento,
          cliDocNum: resultado.cliente.cliNumDoc,
          cliTelef: resultado.cliente.cliTelef || ''
        });
        
        setBuscandoCliente(false);
        return; // Termina aquí si encontró en BD
      }
      
      // PASO 2: Si no encontró en BD y es DNI, buscar en RENIEC
      if (tipoDoc === 'DNI') {
        setBuscandoCliente(false);
        setConsultandoDni(true);
        
        try {
          const persona = await consultarDni(numDoc);
          
          setDniEncontrado(true);
          setClienteNoEncontrado(false);
          
          setCustomer(prev => prev ? {
            ...prev,
            cliNombreCom: persona.nombreCompleto || prev.cliNombreCom
          } : {
            cliNombreCom: persona.nombreCompleto,
            cliDocTipo: 'DNI',
            cliDocNum: numDoc,
            cliDireccion: '',
            cliTelef: ''
          });
          
          setConsultandoDni(false);
          return;
        } catch (errorReniec: any) {
          setErrorDni(errorReniec.message || 'No se pudo consultar en RENIEC');
          setDniEncontrado(false);
          setConsultandoDni(false);
          
          // Limpiar el nombre cuando no se encuentra en RENIEC
          setCustomer(prev => prev ? {
            ...prev,
            cliNombreCom: ''
          } : null);
        }
      }
      
      // PASO 3: No encontrado en ningún lado - Ingreso manual
      setClienteExistente(null);
      setClienteNoEncontrado(true);
      
      // Limpiar el nombre para que el usuario lo ingrese manualmente
      setCustomer(prev => prev ? {
        ...prev,
        cliNombreCom: ''
      } : null);
      
    } catch (error: any) {
      setClienteExistente(null);
      setClienteNoEncontrado(true);
      setErrorDni(error.message || 'Error al buscar cliente');
      
      // Limpiar el nombre cuando hay error en la búsqueda
      setCustomer(prev => prev ? {
        ...prev,
        cliNombreCom: ''
      } : null);
    } finally {
      setBuscandoCliente(false);
      setConsultandoDni(false);
    }
  };

  useEffect(() => {
    const fetchVendors = async () => {
      try {
        setLoadingVendors(true);
        const response = await getSellers();
        
        const vendorsData: Vendor[] = response.map((user: any) => ({
          id: user.usuCod,
          name: user.usuNombreCom || user.usuNom || 'Usuario sin nombre',
          role: user.roles?.some((role: any) => role.rolNom === 'VENDEDOR') ? 'Vendedor' : 'Usuario'
        }));
        
        // Si el usuario actual no está en la lista de vendedores, agregarlo
        if (currentUser && currentUser.usuCod) {
          const usuarioActualEnLista = vendorsData.find(v => v.id === currentUser.usuCod);
          if (!usuarioActualEnLista) {
            // Agregar el usuario actual a la lista
            const rolActual = currentUser.roles?.map(r => r.rolNom).join(', ') || 'Usuario';
            vendorsData.unshift({
              id: currentUser.usuCod,
              name: currentUser.usuNombreCom || currentUser.usuNom || 'Usuario sin nombre',
              role: rolActual
            });
          }
        }
        
        setVendors(vendorsData);
        
        // Establecer el usuario actual como vendedor por defecto si no hay uno seleccionado
        if (!selectedVendor && currentUser && currentUser.usuCod) {
          onVendorChange(currentUser.usuCod);
        }
      } catch (error) {
        console.error('Error cargando vendedores:', error);
        setVendors([]);
      } finally {
        setLoadingVendors(false);
      }
    };

    fetchVendors();
    // Solo ejecutar cuando cambie currentUser, no cuando cambie selectedVendor
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentUser]);

  // Re-seleccionar usuario actual si selectedVendor se resetea a null
  useEffect(() => {
    if (!selectedVendor && currentUser && currentUser.usuCod) {
      onVendorChange(currentUser.usuCod);
    }
  }, [selectedVendor, currentUser, onVendorChange]);

  useEffect(() => {
    if (customer?.cliDocTipo === 'RUC') {
      setTipoComprobante('01');
    } else {
      setTipoComprobante('03');
    }
  }, [customer?.cliDocTipo]);

  // useEffect unificado para búsqueda con debounce
  useEffect(() => {
    const buscarConDebounce = async () => {
      if (customer?.cliDocNum && customer?.cliDocTipo) {
        const longitudMinima = customer.cliDocTipo === 'RUC' ? 11 : 8;
        
        if (customer.cliDocNum.length === longitudMinima) {
          await buscarClienteCompleto(customer.cliDocTipo, customer.cliDocNum);
        } else {
          // Resetear estados si no tiene la longitud completa
          setClienteExistente(null);
          setClienteNoEncontrado(false);
          setDniEncontrado(false);
          setErrorDni(null);
        }
      } else {
        setClienteExistente(null);
        setClienteNoEncontrado(false);
        setDniEncontrado(false);
        setErrorDni(null);
      }
    };

    const timer = setTimeout(buscarConDebounce, 800);
    return () => clearTimeout(timer);
  }, [customer?.cliDocNum, customer?.cliDocTipo]);

  useEffect(() => {
    // Resetear campos cuando cambie el método de pago
    setTipoTarjeta(undefined);
    setReferenciaPago('');
  }, [paymentMethod]);

  const handleAdelantoChange = (value: number) => {
    const nuevoValor = Math.max(0, Math.min(totalVenta, value));
    setAdelanto(Number(nuevoValor.toFixed(2)));
  };

  const handleAdelantoInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseFloat(e.target.value) || 0;
    handleAdelantoChange(value);
  };

  const handlePercentageClick = (percentage: number) => {
    const nuevoAdelanto = totalVenta * (percentage / 100);
    handleAdelantoChange(nuevoAdelanto);
  };

  const getComprobanteOptions = (): TipoComprobante[] => {
    if (customer?.cliDocTipo === 'RUC') {
      return [
        { value: '01', label: 'FACTURA', description: 'Para RUC' }
      ];
    } else {
      return [
        { value: '03', label: 'BOLETA', description: 'Para DNI/CE' },
        //{ value: '01', label: 'FACTURA', description: 'Si el cliente solicita' }
      ];
    }
  };

  const updateCustomer = (updates: Partial<Customer>) => {
    setCustomer(prev => {
      if (!prev) {
        return {
          cliNombreCom: updates.cliNombreCom || '',
          cliDocTipo: updates.cliDocTipo || 'DNI',
          cliDocNum: updates.cliDocNum || '',
          cliDireccion: updates.cliDireccion || ''
        };
      }
      return { ...prev, ...updates };
    });
  };

  const handleProcessSale = async () => {
    if (cart.length === 0) {
      showWarningToast('El carrito está vacío');
      return;
    }

    if (!selectedVendor) {
      showWarningToast('Selecciona un vendedor');
      return;
    }

    if (tipoComprobante === '01') {
      if (!customer?.cliNombreCom?.trim()) {
        showWarningToast('El nombre o razón social es obligatorio para emitir una Factura');
        return;
      }
      if (!customer?.cliDocNum?.trim()) {
        showWarningToast('El número de documento es obligatorio para emitir una Factura');
        return;
      }
      if (!customer?.cliDireccion?.trim()) {
        showWarningToast('La dirección es obligatoria para emitir una Factura');
        return;
      }
    }

    if (tipoComprobante === '01' && customer?.cliDocTipo !== 'RUC') {
      const result = await showConfirmation(
        'Confirmación de Factura',
        `Las facturas normalmente se emiten con RUC. ¿Deseas continuar con ${customer?.cliDocTipo}?`,
        'Sí, continuar',
        'Cancelar'
      );
      
      if (!result.isConfirmed) return;
    }

    if (adelanto > totalVenta) {
      showWarningToast('El adelanto no puede ser mayor al total de la venta');
      return;
    }

    // Mostrar vista previa del ticket
    setShowTicketPreview(true);
  };

  const handleConfirmSale = async () => {
    setShowTicketPreview(false);
    
    try {
      setIsProcessing(true);
      
      await onProcessSale({
        customer,
        paymentMethod,
        vendorId: selectedVendor,
        referenciaPago,
        tipoTarjeta,
        adelanto,
        observaciones
      });

      setAdelanto(0);
      setCustomer(null);
      setReferenciaPago('');
      setTipoTarjeta(undefined);
      setObservaciones('');
      
    } catch (error) {
      console.error('Error en handleConfirmSale:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const comprobanteOptions = getComprobanteOptions();

  // Obtener el nombre del vendedor seleccionado
  const selectedVendorName = vendors.find(v => v.id === selectedVendor)?.name || 'Sin vendedor';

  return (
    <div className="w-full md:w-96 lg:w-[380px] xl:w-[420px] bg-white border-l border-gray-200 flex flex-col shadow-lg h-screen overflow-hidden">
      
      <div className="p-2 md:p-3 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-white flex-shrink-0">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-bold text-gray-800 text-sm md:text-base lg:text-lg">Panel de Venta</h3>
            <p className="text-[10px] md:text-xs text-gray-500 mt-0.5 hidden md:block">Complete los datos para procesar</p>
          </div>
          <div className="flex items-center space-x-1 md:space-x-2">
            {loadingVendors ? (
              <div className="flex items-center text-[10px] md:text-xs text-gray-500">
                <Loader className="w-3 h-3 animate-spin mr-1" />
                <span className="hidden md:inline">Cargando...</span>
              </div>
            ) : (
              <select
                value={selectedVendor ?? ''}
                onChange={(e) => onVendorChange(e.target.value ? Number(e.target.value) : null)}
                className="text-[10px] md:text-xs font-semibold border-2 border-blue-600 rounded-lg px-1.5 md:px-2 py-1 md:py-1.5
                         bg-blue-50 text-blue-700 shadow-sm hover:shadow-md 
                         focus:outline-none focus:ring-2 focus:ring-blue-400 transition-all
                         min-w-[100px] md:min-w-[140px]"
                disabled={vendors.length === 0}
              >
                <option value="">VENDEDOR</option>
                {vendors.map((vendor) => (
                  <option key={vendor.id} value={vendor.id}>
                    {vendor.name}
                  </option>
                ))}
              </select>
            )}
            
            {selectedVendor && (
              <div className="w-2 h-2 md:w-2.5 md:h-2.5 bg-green-500 rounded-full animate-pulse" title="Vendedor seleccionado"></div>
            )}
          </div>
        </div>
        
        {vendors.length === 0 && !loadingVendors && (
          <div className="mt-1 md:mt-2 text-[10px] md:text-xs text-red-500 flex items-center">
            <AlertCircle className="w-3 h-3 mr-1" />
            Sin vendedores disponibles
          </div>
        )}
      </div>

      {/* Detalles del Cliente */}
      <div className="p-2 md:p-3 border-b border-gray-200 bg-white flex-shrink-0">
        <button
          onClick={() => setShowCustomerDetails(!showCustomerDetails)}
          className="flex justify-between items-center w-full p-1.5 md:p-2 rounded-lg transition-colors hover:bg-gray-50"
        >
          <div className="flex items-center space-x-1.5 md:space-x-2">
            <User className="w-3 h-3 md:w-4 md:h-4 text-gray-600" />
            <span className="font-bold text-gray-700 text-xs md:text-sm">DATOS DEL CLIENTE</span>
            {customer?.cliNombreCom && (
              <span className="text-[10px] md:text-xs text-green-600 bg-green-100 px-1.5 md:px-2 py-0.5 rounded-full">
                ✓ 
              </span>
            )}
          </div>
          <span className="text-gray-500 text-[10px] md:text-xs font-medium">
            {showCustomerDetails ? 'Ocultar' : 'Mostrar'}
          </span>
        </button>
        
        {showCustomerDetails && (
          <div className="mt-1.5 md:mt-2 space-y-1.5 md:space-y-2.5 animate-fade-in">
            {/* Tipo de Comprobante */}
            {comprobanteOptions.length > 1 && (
              <div className="bg-gray-100 p-1.5 md:p-2.5 rounded-md border border-gray-200">
                <label className="block text-[10px] md:text-xs font-medium text-gray-700 mb-1 md:mb-1.5">
                  Tipo de Comprobante
                </label>
                <div className="flex space-x-1.5 md:space-x-2">
                  {comprobanteOptions.map((option) => (
                    <button
                      key={option.value}
                      onClick={() => setTipoComprobante(option.value)}
                      className={`flex-1 flex flex-col items-center justify-center p-1 md:p-1.5 rounded border text-[10px] md:text-xs font-medium transition ${
                        tipoComprobante === option.value
                          ? 'bg-blue-500 border-blue-600 text-white shadow-sm'
                          : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      <span>{option.label}</span>
                      <span className="text-[9px] md:text-[10px] opacity-75 hidden md:inline">{option.description}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Nombre del Cliente */}
            <div>
              <label className="block text-[10px] md:text-xs font-medium text-gray-600 mb-0.5 md:mb-1">
                Apellido - Nombre completo
                {clienteNoEncontrado && customer?.cliDocNum && (
                  <span className="text-red-500 ml-1">* (Requerido)</span>
                )}
              </label>
              <input
                type="text"
                placeholder="Ingrese nombre del cliente"
                value={customer?.cliNombreCom || ''}
                onChange={(e) => updateCustomer({ cliNombreCom: e.target.value.toUpperCase() })}
                className={`w-full p-1.5 md:p-2 text-xs md:text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition uppercase ${
                  clienteNoEncontrado && customer?.cliDocNum && !customer?.cliNombreCom?.trim()
                    ? 'border-red-300 bg-red-50'
                    : 'border-gray-300'
                }`}
              />
              {clienteNoEncontrado && customer?.cliDocNum && !customer?.cliNombreCom?.trim() && (
                <p className="text-[9px] md:text-[10px] text-red-600 mt-0.5 md:mt-1">
                  Debe ingresar el nombre del cliente
                </p>
              )}
            </div>

            {/* Documento con búsqueda */}
            <div>
              <label className="block text-[10px] md:text-xs font-medium text-gray-600 mb-0.5 md:mb-1">
                Documento de identidad
              </label>
              <div className="flex space-x-1.5 md:space-x-2">
                <select 
                  value={customer?.cliDocTipo || 'DNI'}
                  onChange={(e) => {
                    updateCustomer({ 
                      cliDocTipo: e.target.value as TipoDocumento,
                      cliDocNum: '',
                      cliNombreCom: ''
                    });
                    // Resetear todos los estados de búsqueda
                    setClienteExistente(null);
                    setClienteNoEncontrado(false);
                    setDniEncontrado(false);
                    setErrorDni(null);
                    setConsultandoDni(false);
                    setBuscandoCliente(false);
                  }}
                  className="w-1/3 p-1.5 md:p-2 text-xs md:text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition"
                >
                  <option value="DNI">DNI</option>
                  <option value="RUC">RUC</option>
                  <option value="CE">CE</option>
                </select>
                
                <div className="relative flex-1">
                  <input
                    type="text"
                    placeholder={customer?.cliDocTipo === 'RUC' ? '11 dígitos' : '8 dígitos'}
                    value={customer?.cliDocNum || ''}
                    onChange={(e) => {
                      const value = e.target.value.replace(/\D/g, '');
                      const maxLength = customer?.cliDocTipo === 'RUC' ? 11 : 8;
                      updateCustomer({ cliDocNum: value.slice(0, maxLength) });
                    }}
                    className="w-full p-1.5 md:p-2 pr-7 md:pr-8 text-xs md:text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition"
                    maxLength={customer?.cliDocTipo === 'RUC' ? 11 : 8}
                  />
                  
                  {/* Indicadores de estado en el input */}
                  {customer?.cliDocNum && customer.cliDocNum.length >= 8 && (
                    <div className="absolute right-1.5 md:right-2 top-1/2 -translate-y-1/2">
                      {(buscandoCliente || consultandoDni) && (
                        <Loader2 className="w-3 h-3 md:w-4 md:h-4 text-blue-500 animate-spin" />
                      )}
                      {clienteExistente && !buscandoCliente && !consultandoDni && (
                        <CheckCircle className="w-3 h-3 md:w-4 md:h-4 text-green-500" />
                      )}
                      {dniEncontrado && !consultandoDni && !clienteExistente && (
                        <CheckCircle className="w-3 h-3 md:w-4 md:h-4 text-green-500" />
                      )}
                      {clienteNoEncontrado && !buscandoCliente && !consultandoDni && !clienteExistente && !dniEncontrado && (
                        <AlertCircle className="w-3 h-3 md:w-4 md:h-4 text-blue-500" />
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Dirección (obligatorio para Facturas) */}
            {(tipoComprobante === '01' || customer?.cliDocTipo === 'RUC') && (
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">
                  Dirección <span className="text-red-500">*</span>
                  <span className="text-[10px] text-gray-500 ml-1">(Requerido para Factura)</span>
                </label>
                <input
                  type="text"
                  placeholder="Ingrese la dirección completa"
                  value={customer?.cliDireccion || ''}
                  onChange={(e) => updateCustomer({ cliDireccion: e.target.value })}
                  className="w-full p-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition"
                />
              </div>
            )}
          </div>
        )}
      </div>
      
      {/* Resumen de Venta */}
      <div className="flex-1 p-2 md:p-3 space-y-2 md:space-y-3 overflow-y-auto bg-gradient-to-b from-white to-gray-50">
        <h3 className="font-bold text-gray-800 text-sm md:text-base mb-1.5 md:mb-2">RESUMEN DE VENTA</h3>

        {/* Totales */}
        <div className="space-y-1 md:space-y-1.5 pt-1.5 md:pt-2 border-t border-gray-300">
          <div className="flex justify-between text-gray-600 text-xs md:text-sm">
            <span>Subtotal</span>
            <span className="font-medium">S/ {totalVenta.toFixed(2)}</span>
          </div>
          
          <div className="flex justify-between text-sm md:text-base font-bold text-gray-800">
            <span>TOTAL</span>
            <span>S/ {totalVenta.toFixed(2)}</span>
          </div>
        </div>

        {/* Sección de Adelanto */}
        <div className="pt-1.5 md:pt-2 border-t border-gray-300">
          <label className="block text-[10px] md:text-xs font-semibold text-gray-700 mb-1 md:mb-1.5">
            Adelanto <span className="text-gray-500 font-normal text-[9px] md:text-[10px]">(Opcional)</span>
          </label>
          
          {/* Input de adelanto */}
          <div className="relative mb-1.5 md:mb-2">
            <span className="absolute left-2 md:left-2.5 top-1/2 -translate-y-1/2 text-gray-600 font-medium text-xs md:text-sm">
              S/
            </span>
            <input
              type="number"
              min="0"
              max={totalVenta}
              step="0.01"
              value={adelanto || ''}
              onChange={handleAdelantoInput}
              className="w-full pl-7 md:pl-8 pr-3 py-1.5 md:py-2 text-xs md:text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition"
              placeholder="0.00"
            />
          </div>
          
          {/* Botones de porcentaje */}
          <div className="grid grid-cols-5 gap-1 md:gap-1.5 mb-1.5 md:mb-2">
            {[0, 25, 50, 75, 100].map((perc) => (
              <button
                key={perc}
                onClick={() => perc === 0 ? handleAdelantoChange(0) : handlePercentageClick(perc)}
                className={`px-1.5 md:px-2 py-1 md:py-1.5 text-[9px] md:text-[10px] border rounded-lg transition-colors font-medium ${
                  perc === 0 
                    ? 'border-red-300 text-red-600 hover:bg-red-50' 
                    : 'border-blue-300 text-blue-600 hover:bg-blue-50'
                }`}
              >
                {perc === 0 ? 'Limp' : `${perc}%`}
              </button>
            ))}
          </div>
          
          {/* Resumen de adelanto */}
          {adelanto > 0 && (
            <div className="mt-1.5 md:mt-2 space-y-1 md:space-y-1.5 bg-blue-50 p-1.5 md:p-2 rounded-lg border border-blue-200">
              <div className="flex justify-between text-[10px] md:text-xs">
                <span className="text-gray-700">Adelanto:</span>
                <span className="font-bold text-blue-700">S/ {adelanto.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-[10px] md:text-xs">
                <span className="text-gray-700">Saldo:</span>
                <span className="font-bold text-gray-800">S/ {saldoPendiente.toFixed(2)}</span>
              </div>
              {adelanto === totalVenta && (
                <div className="flex items-center text-[9px] md:text-[10px] text-green-600 font-medium mt-1 md:mt-1.5 p-1 md:p-1.5 bg-green-50 rounded">
                  <CheckCircle className="w-2.5 h-2.5 md:w-3 md:h-3 mr-1 md:mr-1.5" />
                  Pagado completamente
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Métodos de Pago */}
      <div className="px-2 md:px-3 pb-2 md:pb-3 bg-white flex-shrink-0">
        <label className="block text-[10px] md:text-xs font-semibold text-gray-700 mb-1 md:mb-1.5">
          Método de Pago
        </label>
        <div className="grid grid-cols-3 gap-1 md:gap-1.5">
          {[
            { value: 'EFECTIVO', label: 'Efectivo', icon: Banknote, color: 'green' },
            { value: 'YAPE', label: 'Yape', icon: Smartphone, color: 'indigo' },
            { value: 'VISA', label: 'Visa', icon: CreditCard, color: 'blue' }
          ].map((method) => (
            <button
              key={method.value}
              onClick={() => setPaymentMethod(method.value as FormaPago)}
              className={`flex flex-col items-center justify-center p-1 md:p-1.5 border rounded-lg transition text-[9px] md:text-[10px] font-medium ${
                paymentMethod === method.value
                  ? `bg-${method.color}-500 border-${method.color}-600 text-white shadow-sm`
                  : 'bg-white border-gray-300 text-gray-600 hover:bg-gray-50'
              }`}
            >
              <method.icon className="w-3 h-3 md:w-4 md:h-4 mb-0.5" />
              <span>{method.label}</span>
            </button>
          ))}
        </div>

        {/* Sin campos adicionales - todo se registra en el cierre de caja */}
      </div>

      {/* Observaciones */}
      <div className="p-2 md:p-3 border-t border-gray-200 bg-white flex-shrink-0">
        <label className="block text-[10px] md:text-xs font-semibold text-gray-700 mb-1 md:mb-1.5">
          Observaciones
        </label>
        <textarea
          placeholder="Notas sobre la venta..."
          value={observaciones}
          onChange={(e) => setObservaciones(e.target.value)}
          rows={2}
          className="w-full p-1.5 md:p-2 text-[10px] md:text-xs border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition resize-none"
        />
      </div>

      <div className="p-2 md:p-3 border-t border-gray-200 bg-gray-50 flex-shrink-0">
        <button
          onClick={handleProcessSale}
          disabled={cart.length === 0 || !selectedVendor || isProcessing}
          className={`w-full py-2 md:py-3 rounded-lg font-bold text-sm md:text-base transition-all shadow-md hover:shadow-lg
            ${isProcessing 
              ? 'bg-gray-400 cursor-not-allowed' 
              : 'bg-[#3BAEDF] hover:bg-[#2a9bc9] text-white'
            } flex items-center justify-center space-x-1.5 md:space-x-2`}
        >
          {isProcessing ? (
            <>
              <Loader2 className="w-4 h-4 md:w-5 md:h-5 animate-spin" />
              <span>Procesando...</span>
            </>
          ) : (
            <>
              <CheckCircle className="w-4 h-4 md:w-5 md:h-5" />
              <span>Procesar Venta</span>
            </>
          )}
        </button>
        
      </div>

      {/* Ticket Preview Modal */}
      <TicketPreview
        isOpen={showTicketPreview}
        onClose={() => setShowTicketPreview(false)}
        onConfirm={handleConfirmSale}
        cart={cart}
        customer={customer}
        paymentMethod={paymentMethod}
        adelanto={adelanto}
        totalVenta={totalVenta}
        vendorName={selectedVendorName}
        observaciones={observaciones}
      />
    </div>
  );
};

export default TransactionPanel;