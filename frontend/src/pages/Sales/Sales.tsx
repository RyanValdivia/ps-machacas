// Sales.tsx
import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Loader2, AlertCircle, Eye, Settings } from 'lucide-react';
import SaleFilter from './components/SalesFilter';
import type { FilterValues } from './components/SalesFilter';
import Pagination from '../../components/Pagination/Pagination';
import DataTable, { type Column } from '../../components/Table/DataTable';
import ModalDetallesVenta from './components/ModalDetallesVenta';
import ModalGestionarVenta from './components/ModalGestionarVenta';
import { saleService } from '../../auth/services/sale/saleService';
import type { VentaResponse } from '../../auth/types/sale/sale';
import { showErrorToast } from '../../utils/sweetAlertConfig';


const Sales = () => {
  const [searchParams] = useSearchParams();
  const [ventas, setVentas] = useState<VentaResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<FilterValues>({});
  
  // Estados de paginación
  const [page, setPage] = useState(1);
  const [next, setNext] = useState<string | null>(null);
  const [previous, setPrevious] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState(0);

  // Estados de modales
  const [modalDetallesAbierto, setModalDetallesAbierto] = useState(false);
  const [modalGestionarAbierto, setModalGestionarAbierto] = useState(false);
  const [ventaSeleccionada, setVentaSeleccionada] = useState<VentaResponse | null>(null);

  // Función para priorizar ventas según su estado
  const sortVentasByPriority = (ventas: VentaResponse[]) => {
    return [...ventas].sort((a, b) => {
      // Prioridad 1: Pedidos listos (ventEstadoRecoj === 'LISTO')
      if (a.ventEstadoRecoj === 'LISTO' && b.ventEstadoRecoj !== 'LISTO') return -1;
      if (b.ventEstadoRecoj === 'LISTO' && a.ventEstadoRecoj !== 'LISTO') return 1;
      
      // Prioridad 2: Pedidos pendientes de entregar (ventEstadoRecoj === 'PENDIENTE')
      if (a.ventEstadoRecoj === 'PENDIENTE' && b.ventEstadoRecoj !== 'PENDIENTE' && b.ventEstadoRecoj !== 'LISTO') return -1;
      if (b.ventEstadoRecoj === 'PENDIENTE' && a.ventEstadoRecoj !== 'PENDIENTE' && a.ventEstadoRecoj !== 'LISTO') return 1;
      
      // Prioridad 3: Pagos pendientes (ventEstado === 'PENDIENTE')
      if (a.ventEstado === 'PENDIENTE' && b.ventEstado !== 'PENDIENTE') return -1;
      if (b.ventEstado === 'PENDIENTE' && a.ventEstado !== 'PENDIENTE') return 1;
      
      // Por defecto, mantener orden original
      return 0;
    });
  };

  const fetchVentas = async (filterParams?: FilterValues, pageNum: number = 1) => {
    try {
      setLoading(true);
      setError(null);

      const params: Record<string, any> = {
        page: pageNum,
        page_size: 15 // Más ventas por página para tabla
      };
      
      if (filterParams?.search)         params.search = filterParams.search;
      if (filterParams?.estado)         params.estado = filterParams.estado;
      if (filterParams?.estado_pedido)  params.estado_pedido = filterParams.estado_pedido;
      if (filterParams?.fecha_desde)    params.fecha_desde = filterParams.fecha_desde;
      if (filterParams?.fecha_hasta)    params.fecha_hasta = filterParams.fecha_hasta;

      const data = await saleService.getAll(params);
      
      // Priorizar ventas pendientes
      const sortedVentas = sortVentasByPriority(data.results);
      
      setVentas(sortedVentas);
      setNext(data.next);
      setPrevious(data.previous);
      setTotalCount(data.count);
      setPage(pageNum);
    } catch (err: any) {
      console.error('Error al cargar ventas:', err);
      const errorMessage = err.response?.data?.message || 'Error al cargar las ventas';
      setError(errorMessage);
      showErrorToast(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const searchParam = searchParams.get('search');
    if (searchParam) {
      const initialFilters = { search: searchParam };
      setFilters(initialFilters);
      fetchVentas(initialFilters, 1);
    } else {
      fetchVentas();
    }
  }, [searchParams]);

  const handleFilterChange = (newFilters: FilterValues) => {
    setFilters(newFilters);
    setPage(1); // Resetear a página 1 al aplicar filtros
    fetchVentas(newFilters, 1);
  };

  const handleClearFilters = () => {
    setFilters({});
    setPage(1);
    fetchVentas({}, 1);
  };

  const handleVentaActualizada = () => {
    fetchVentas(filters, page);
  };

  const handlePageChange = (newPage: number) => {
    fetchVentas(filters, newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Funciones para manejar modales
  const handleVerDetalles = (venta: VentaResponse) => {
    setVentaSeleccionada(venta);
    setModalDetallesAbierto(true);
  };

  const handleGestionar = (venta: VentaResponse) => {
    setVentaSeleccionada(venta);
    setModalGestionarAbierto(true);
  };

  const handleCerrarModales = () => {
    setModalDetallesAbierto(false);
    setModalGestionarAbierto(false);
    setVentaSeleccionada(null);
  };

  // Funciones para obtener badges de estado
  const getEstadoPedidoBadge = (estado: string) => {
    const estados: Record<string, { label: string; className: string }> = {
      'PENDIENTE': { label: 'Pendiente Laboratorio', className: 'bg-yellow-100 text-yellow-800 border border-yellow-300' },
      'LISTO': { label: 'Listo para Entrega', className: 'bg-green-100 text-green-800 border border-green-300' },
      'ENTREGADO': { label: 'Entregado', className: 'bg-blue-100 text-blue-800 border border-blue-300' },
      'ANULADO': { label: 'Anulado', className: 'bg-red-100 text-red-800 border border-red-300' },
    };
    const config = estados[estado] || { label: estado, className: 'bg-gray-100 text-gray-800' };
    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold ${config.className}`}>
        {config.label}
      </span>
    );
  };

  const getEstadoPagoBadge = (estado: string) => {
    const estados: Record<string, { label: string; className: string }> = {
      'PENDIENTE': { label: 'Sin Pago', className: 'bg-red-100 text-red-800 border border-red-300' },
      'PAGADO': { label: 'Cancelado', className: 'bg-green-100 text-green-800 border border-green-300' },
      'PARCIAL': { label: 'Pago Parcial', className: 'bg-orange-100 text-orange-800 border border-orange-300' },
      'ANULADO': { label: 'Anulado', className: 'bg-gray-100 text-gray-800 border border-gray-300' },
    };
    const config = estados[estado] || { label: estado, className: 'bg-gray-100 text-gray-800' };
    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold ${config.className}`}>
        {config.label}
      </span>
    );
  };

   const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-PE', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Función para resaltar filas prioritarias
  const getRowClassName = (venta: VentaResponse) => {
    if (venta.ventEstadoRecoj === 'LISTO') {
      return 'bg-green-50 hover:bg-green-100 font-semibold';
    }
    if (venta.ventEstadoRecoj === 'PENDIENTE') {
      return 'bg-yellow-50 hover:bg-yellow-100 font-medium';
    }
    if (venta.ventEstado === 'PENDIENTE') {
      return 'bg-red-50 hover:bg-red-100';
    }
    return '';
  };

  // Definir las columnas de la tabla
  const columns: Column<VentaResponse>[] = [
    {
      key: 'ventCod',
      label: 'Código',
      render: (venta) => (
        <span className="font-mono text-gray-900">{venta.ventCod}</span>
      ),
    },
    {
      key: 'ventFecha',
      label: 'Fecha',
      render: (venta) => (
          <p className="">{formatDate(venta.ventFecha)}</p>
      ),
    },
    {
      key: 'nombre_cliente',
      label: 'Nombre',
      render: (venta) => (
        <div className="text-left">
          <div className="font-semibold text-gray-900">{venta.nombre_cliente}</div>
          {venta.cliente && (
            <div className="text-xs text-gray-500">{venta.cliente.cliTipoDoc}: {venta.cliente.cliNumDoc}</div>
          )}
        </div>
      ),
    },
    {
      key: 'ventEstadoRecoj',
      label: 'Estado Pedido',
      render: (venta) => getEstadoPedidoBadge(venta.ventEstadoRecoj),
    },
    {
      key: 'ventEstado',
      label: 'Estado Pago',
      render: (venta) => getEstadoPagoBadge(venta.ventEstado),
    },
    {
      key: 'ventSaldo',
      label: 'Saldo / Total',
      render: (venta) => (
        <div className="text-center">
          <div className="font-bold text-red-600">S/ {Number(venta.ventSaldo).toFixed(2)}</div>
          <div className="text-xs text-gray-600">Total: S/ {Number(venta.ventTotal).toFixed(2)}</div>
        </div>
      ),
    },
    {
      key: 'actions',
      label: 'Acciones',
      render: (venta) => (
        <div className="flex items-center justify-center gap-2" onClick={(e) => e.stopPropagation()}>
          <button
            onClick={() => handleVerDetalles(venta)}
            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            title="Ver detalle"
          >
            <Eye className="w-4 h-4" />
          </button>
          <button
            onClick={() => handleGestionar(venta)}
            className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
            title="Gestionar venta"
          >
            <Settings className="w-4 h-4" />
          </button>
        </div>
      ),
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50  pt-15 px-6">
      <div className="pt-10 px-10">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Ventas</h1>
          <p className="text-gray-600 mt-1">Gestiona y visualiza todas las ventas realizadas</p>
        </div>

        {/* Filtros */}
        <SaleFilter
          onFilterChange={handleFilterChange}
          onClearFilters={handleClearFilters}
          initialFilters={filters}
        />

        {/* Contenido Principal */}
        {loading ? (
          <div className="flex flex-col items-center justify-center py-16">
            <Loader2 className="w-12 h-12 text-[#3BAEDF] animate-spin mb-4" />
            <p className="text-gray-600">Cargando ventas...</p>
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 flex items-start space-x-3">
            <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-red-900 font-semibold mb-1">Error al cargar las ventas</h3>
              <p className="text-red-700">{error}</p>
              <button
                onClick={() => fetchVentas(filters)}
                className="mt-3 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
              >
                Reintentar
              </button>
            </div>
          </div>
        ) : ventas.length === 0 ? (
          <div className="bg-white border border-gray-200 rounded-lg p-12 text-center">
            <div className="max-w-md mx-auto">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <AlertCircle className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                No se encontraron ventas
              </h3>
              <p className="text-gray-600 mb-6">
                {Object.values(filters).some(v => v !== '')
                  ? 'No hay ventas que coincidan con los filtros aplicados.'
                  : 'Aún no se han registrado ventas en el sistema.'}
              </p>
              {Object.values(filters).some(v => v !== '') && (
                <button
                  onClick={handleClearFilters}
                  className="px-6 py-2 bg-[#3BAEDF] text-white rounded hover:bg-[#2A9DC9] transition-colors"
                >
                  Limpiar filtros
                </button>
              )}
            </div>
          </div>
        ) : (
          <>
            {/* Contador de resultados y leyenda */}
            <div className="mb-4">
              <div className="flex justify-between items-center mb-3">
                <div className="text-sm text-gray-600">
                  Mostrando <span className="font-semibold text-gray-900">{ventas.length}</span> de{' '}
                  <span className="font-semibold text-gray-900">{totalCount}</span>{' '}
                  {totalCount === 1 ? 'venta' : 'ventas'}
                </div>
                <div className="text-xs text-gray-500">
                  Página {page}
                </div>
              </div>
              
              {/* Leyenda de prioridades */}
              <div className="flex flex-wrap gap-3 text-xs bg-gray-50 p-3 rounded-lg border border-gray-200">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-green-50 border border-green-300 rounded"></div>
                  <span className="text-gray-700">Pedidos Listos (Prioridad Alta)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-yellow-50 border border-yellow-300 rounded"></div>
                  <span className="text-gray-700">Pedidos Pendientes</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-red-50 border border-red-300 rounded"></div>
                  <span className="text-gray-700">Pagos Pendientes</span>
                </div>
              </div>
            </div>

            {/* Tabla de Ventas */}
            <div className="mb-6 bg-white rounded-lg shadow-sm overflow-hidden">
              <DataTable 
                columns={columns} 
                data={ventas}
                getRowClassName={getRowClassName}
              />
            </div>

            {/* Paginación */}
            <Pagination
              page={page}
              next={next}
              previous={previous}
              onPageChange={handlePageChange}
            />
          </>
        )}
      </div>

      {/* Modales */}
      {ventaSeleccionada && (
        <>
          <ModalDetallesVenta
            venta={ventaSeleccionada}
            isOpen={modalDetallesAbierto}
            onClose={handleCerrarModales}
          />
          
          <ModalGestionarVenta
            venta={ventaSeleccionada}
            isOpen={modalGestionarAbierto}
            onClose={handleCerrarModales}
            onVentaActualizada={handleVentaActualizada}
          />
        </>
      )}
    </div>
  );
};

export default Sales;