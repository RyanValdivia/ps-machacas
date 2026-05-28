import { normalizeProduct } from "../../auth/utils/normalizeProduct";
import React, { useState, useEffect } from 'react';
import { Package, TrendingDown, Plus, Edit2, Trash2, ArrowUpDown } from 'lucide-react';
import DataTable from '../../components/Table/DataTable';
import type { Column } from '../../components/Table/DataTable';
import InventoryFilters from './components/InventoryFilters';
import ProductModal from './components/ProductModal';
import StockAdjustModal from './components/StockAdjustModal';
import productService from '../../auth/services/product/productService';
import Pagination from "../../components/Pagination/Pagination";
import type { 
  Product, 
  CreateProductDTO,
  InventoryFilters as IFilters,
  ProductCategory,
  Supplier 
} from '../../auth/types/product/product';
import {
  showSuccessToast,
  showErrorToast,
  showErrorAlert,
  showDeleteConfirmation,
  showLoading,
  closeLoading
} from '../../utils/sweetAlertConfig';
import './Inventory.css';

const Inventory: React.FC = () => {
  // Estados principales
  const [products, setProducts] = useState<Product[]>([]);
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Datos para filtros
  const [categories, setCategories] = useState<ProductCategory[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);

  // Estado de filtros
  const [filters, setFilters] = useState<IFilters>({
    search: '',
    filterLowStock: false,
    categoria: '',
    proveedor: '',
    material: '',
    genero: '',
    precioMin: '',
    precioMax: '',
    conStock: false,
    estado: '',
    tieneSobrelente: '',
  });

  // Modales
  const [isProductModalOpen, setIsProductModalOpen] = useState(false);
  const [isStockModalOpen, setIsStockModalOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  // Estados para paginación
  const [page, setPage] = useState(1);
  
  // PageSize dinámico según resolución
  const getPageSize = () => {
    if (typeof window !== 'undefined') {
      return window.innerWidth >= 1536 ? 9 : 9; // 9 productos para todas las resoluciones
    }
    return 9;
  };
  
  const [pageSize, setPageSize] = useState(getPageSize());
  const [totalCount, setTotalCount] = useState(0);
  const [nextPage, setNextPage] = useState<string | null>(null);
  const [prevPage, setPrevPage] = useState<string | null>(null);

  // Estados para estadísticas globales
  const [globalStats, setGlobalStats] = useState({
    totalProducts: 0,
    lowStockCount: 0,
    totalValue: 0,
    monturaCount: 0
  });

  // Ref para debounce de búsqueda
  const searchTimeoutRef = React.useRef<number | null>(null);

  // Ajustar pageSize al cambiar tamaño de ventana
  useEffect(() => {
    const handleResize = () => {
      const newPageSize = getPageSize();
      if (newPageSize !== pageSize) {
        setPageSize(newPageSize);
        setPage(1); // Reset a primera página al cambiar tamaño
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [pageSize]);


  useEffect(() => {
    loadData(page, filters.search);
  }, [page, pageSize]);

  // Cargar estadísticas globales
  useEffect(() => {
    loadGlobalStats();
  }, []);
  
  useEffect(() => {
    if (!filters.search) {  // Solo aplicar filtros si NO hay búsqueda
      applyFilters();
    }
  }, [filters.filterLowStock, filters.conStock, filters.categoria, filters.proveedor,
      filters.material, filters.genero, filters.estado, filters.tieneSobrelente,
      filters.precioMin, filters.precioMax, products]);

  useEffect(() => {
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    if (filters.search && filters.search.trim()) {
      const timeout = setTimeout(() => {
        setPage(1); 
        loadData(1, filters.search);
      }, 1000);
      searchTimeoutRef.current = timeout;
    } else if (filters.search === '') {
      // Solo recargar cuando el campo se vacía completamente
      const timeout = setTimeout(() => {
        loadData(page, '');
      }, 300); // Menor delay al limpiar
      searchTimeoutRef.current = timeout;
    }

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [filters.search]);

  const loadData = async (pageNumber: number = page, searchQuery: string = '') => {
    try {
      setLoading(true);
      setError('');

      const [productsData, categoriesData, suppliersData] = await Promise.all([
        productService.getAll(pageNumber, pageSize, searchQuery), // ✅ Ahora existe
        productService.getCategories(),
        productService.getSuppliers(),
      ]);
  
      const safeResults = Array.isArray(productsData.results)
        ? productsData.results.map(normalizeProduct)
      : [];

      setProducts(safeResults);
      setFilteredProducts(safeResults);

  
      setTotalCount(productsData.count);
      setNextPage(productsData.next);
      setPrevPage(productsData.previous);
  
      setCategories(categoriesData);
      setSuppliers(suppliersData);
    } catch (err) {
      console.error(err);
      setError('Error al cargar los datos del inventario');
      showErrorToast('Error al cargar los datos del inventario');
    } finally {
      setLoading(false);
    }
  };

  const loadGlobalStats = async () => {
    try {
      // Usar el nuevo endpoint de estadísticas optimizado
      const stats = await productService.getEstadisticas();
      
      setGlobalStats({
        totalProducts: stats.totalProducts,
        lowStockCount: stats.lowStockCount,
        totalValue: stats.totalValue,
        monturaCount: stats.monturaCount
      });
    } catch (err) {
      console.error('Error al cargar estadísticas globales:', err);
    }
  };
  
  const applyFilters = () => {
    let filtered = [...products];

    // Filtro de stock bajo
    if (filters.filterLowStock) {
      filtered = filtered.filter((item) => item.prodStock <= item.prodStockMin);
    }

    // Filtro con stock
    if (filters.conStock) {
      filtered = filtered.filter((item) => item.prodStock > 0);
    }

    // Filtro de categoría
    if (filters.categoria) {
      filtered = filtered.filter((item) => item.catproCod.toString() === filters.categoria);
    }

    // Filtro de proveedor
    if (filters.proveedor) {
      filtered = filtered.filter((item) => item.provCod.toString() === filters.proveedor);
    }

    // Filtro de material
    if (filters.material) {
      filtered = filtered.filter((item) => item.prodMate === filters.material);
    }

    // Filtro de género
    if (filters.genero) {
      filtered = filtered.filter((item) => item.prodGenero === filters.genero);
    }

    // Filtro de estado
    if (filters.estado) {
      filtered = filtered.filter((item) => item.prodEstado === filters.estado);
    }

    // Filtro de sobrelente
    if (filters.tieneSobrelente) {
      const tieneSobrelente = filters.tieneSobrelente === 'true';
      filtered = filtered.filter((item) => item.prodTieneSobrelente === tieneSobrelente);
    }

    // Filtro de precio mínimo
    if (filters.precioMin) {
      const minPrice = parseFloat(filters.precioMin);
      filtered = filtered.filter((item) => item.prodPrecioVenta >= minPrice);
    }

    // Filtro de precio máximo
    if (filters.precioMax) {
      const maxPrice = parseFloat(filters.precioMax);
      filtered = filtered.filter((item) => item.prodPrecioVenta <= maxPrice);
    }

    setFilteredProducts(filtered);
  };

  const handleCreateProduct = async (data: CreateProductDTO) => {
    try {
      await productService.create(data);
      await loadData(page, filters.search);
      await loadGlobalStats(); // Actualizar estadísticas
      setIsProductModalOpen(false);
      showSuccessToast('Producto creado exitosamente');
    } catch (error: any) {
      console.error('Error al crear producto:', error);
      const errorMessage = error.response?.data?.message || 
                          error.response?.data?.error || 
                          'Error al crear el producto';
      showErrorAlert('Error al Crear Producto', errorMessage);
      throw error;
    }
  };

  const handleUpdateProduct = async (data: CreateProductDTO) => {
    if (!selectedProduct) return;
    
    try {
      await productService.update(selectedProduct.prodCod, data);
      await loadData(page, filters.search);
      await loadGlobalStats(); // Actualizar estadísticas
      setIsProductModalOpen(false);
      setSelectedProduct(null);
      showSuccessToast('Producto actualizado exitosamente');
    } catch (error: any) {
      console.error('Error al actualizar producto:', error);
      const errorMessage = error.response?.data?.message || 
                          error.response?.data?.error || 
                          'Error al actualizar el producto';
      showErrorAlert('Error al Actualizar Producto', errorMessage);
      throw error;
    }
  };

  const handleEditProduct = (product: Product) => {
    setSelectedProduct(product);
    setIsProductModalOpen(true);
  };

  const handleDeleteProduct = async (product: Product) => {
    const result = await showDeleteConfirmation(product.prodDescr);
    
    if (!result.isConfirmed) {
      return;
    }

    try {
      showLoading('Eliminando producto...');
      await productService.delete(product.prodCod);
      closeLoading();
      await loadData(page, filters.search);
      await loadGlobalStats(); // Actualizar estadísticas
      showSuccessToast('Producto eliminado exitosamente');
    } catch (error: any) {
      closeLoading();
      console.error('Error al eliminar producto:', error);
      const errorMessage = error.response?.data?.message || 
                          error.response?.data?.error || 
                          'No se pudo eliminar el producto. Puede estar asociado a otras transacciones.';
      showErrorAlert('Error al Eliminar Producto', errorMessage);
    }
  };

  const handleAdjustStock = (product: Product) => {
    setSelectedProduct(product);
    setIsStockModalOpen(true);
  };

  const handleStockAdjust = async (productId: number, cantidad: number, tipo: 'entrada' | 'salida') => {
    try {
      await productService.ajustarStock(productId, cantidad, tipo);
      await loadData();
      await loadGlobalStats(); // Actualizar estadísticas
      const tipoTexto = tipo === 'entrada' ? 'agregado' : 'descontado';
      showSuccessToast(`Stock ${tipoTexto} exitosamente`);
    } catch (error: any) {
      console.error('Error al ajustar stock:', error);
      const errorMessage = error.response?.data?.message || 
                          error.response?.data?.error || 
                          'Error al ajustar el stock';
      showErrorAlert('Error al Ajustar Stock', errorMessage);
      throw error;
    }
  };

  // Definir columnas para la tabla
  const columns: Column<Product>[] = [
    {
      key: 'prodCode',
      label: 'Código',
      render: (row) => (
        <p className="text-xs 2xl:text-sm font-mono text-gray-900">{row.prodCode || 'N/A'}</p>
      )
    },
    {
      key: 'prodDescr',
      label: 'Descripción',
      render: (row) => (
        <div className="overflow-hidden">
          <p className="text-xs 2xl:text-sm font-medium text-gray-800 truncate 2xl:line-clamp-2" title={row.prodDescr}>
            {row.prodDescr}
          </p>
        </div>
      )
    },
    {
      key: 'prodMarca',
      label: 'Marca',
      render: (row) => (
        <p className="text-xs 2xl:text-sm text-gray-900">{row.prodMarca || 'N/A'}</p>
      )
    },
    {
      key: 'prodColor',
      label: 'Color',
      render: (row) => (
        <p className="text-xs 2xl:text-sm text-gray-700">
          {row.prodColor?.trim() ? row.prodColor : '—'}
        </p>
      )
    },
    {
      key: 'prodTalla',
      label: 'Modelo-Talla',
      render: (row) => (
        <p className="text-xs 2xl:text-sm text-gray-700">
          {row.prodTalla?.trim() ? row.prodTalla : '—'}
        </p>
      )
    },
    {
      key: 'genero_display',
      label: 'Género',
      render: (row) => (
        <p className="text-xs 2xl:text-sm text-gray-700">
          {row.genero_display || row.prodGenero || 'N/A'}
        </p>
      )
    },
    {
      key: 'prodStock',
      label: 'Stock',
      render: (row) => (
        <div className="text-center">
          <p
            className={`text-base 2xl:text-lg font-bold ${
              row.prodStock <= row.prodStockMin ? 'text-red-600' : 'text-green-600'
            }`}
          >
            {row.prodStock}
          </p>
          {row.prodStock <= row.prodStockMin && (
            <p className="text-[10px] 2xl:text-xs text-red-500">Bajo stock</p>
          )}
        </div>
      )
    },
    {
      key: 'prodPrecioVenta',
      label: 'Precio Venta',
      render: (row) => (
        <div className="text-center">
          <p className="text-xs 2xl:text-sm font-bold text-green-600">
            S/ {row.prodPrecioVenta.toFixed(2)}
          </p>
          <p className="text-[10px] 2xl:text-xs text-gray-500">
            Costo: S/ {row.prodCostoInv.toFixed(2)}
          </p>
        </div>
      )
    },
    {
      key: 'prodCod',
      label: 'Acciones',
      render: (row) => (
        <div className="flex items-center justify-center gap-1 2xl:gap-2">
          <button
            onClick={() => handleAdjustStock(row)}
            className="p-1.5 2xl:p-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-all hover:scale-110 shadow-sm"
            title="Ajustar stock"
          >
            <ArrowUpDown className="w-3.5 h-3.5 2xl:w-4 2xl:h-4" />
          </button>

          <button
            onClick={() => handleEditProduct(row)}
            className="p-1.5 2xl:p-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-all hover:scale-110 shadow-sm"
            title="Editar producto"
          >
            <Edit2 className="w-3.5 h-3.5 2xl:w-4 2xl:h-4" />
          </button>
          {/* 
          <button
            onClick={() => handleDeleteProduct(row)}
            className="p-1.5 2xl:p-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-all hover:scale-110 shadow-sm"
            title="Eliminar producto"
          >
            <Trash2 className="w-3.5 h-3.5 2xl:w-4 2xl:h-4" />
          </button>
          */}
        </div>
      )
    }
  ];

  // Pantalla de carga
  if (loading) {
    return (
      <div className="min-h-screen pt-10 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-500 mt-4">Cargando inventario...</p>
        </div>
      </div>
    );
  }

  // Pantalla de error
  if (error) {
    return (
      <div className="min-h-screen pt-10 flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 text-red-800 p-6 rounded-lg max-w-md">
          <h2 className="text-lg font-semibold mb-2">Error</h2>
          <p>{error}</p>
          <button
            onClick={() => loadData(page, filters.search)}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }


  return (
    <div className="min-h-screen pt-15 px-6 flex flex-col">
      {/* Header */}
      <div className="mb-4 2xl:mb-6 flex justify-between items-start">
        <div className="flex-1">
          <h2 className="text-2xl 2xl:text-3xl font-bold text-gray-800 mb-1 2xl:mb-2">
            Inventario de Productos
          </h2>
          <p className="text-sm 2xl:text-base text-gray-600">
            Gestiona tu inventario de productos
          </p>
        </div>

        <button
          onClick={() => {
            setSelectedProduct(null);
            setIsProductModalOpen(true);
          }}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
        >
          <Plus className="w-5 h-5" />
          Nuevo Producto
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3 2xl:gap-4 mb-4 2xl:mb-6">
        <div className="bg-white rounded-lg shadow p-3 2xl:p-4 border-l-4 border-purple-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs 2xl:text-sm text-gray-600">Monturas</p>
              <p className="text-xl 2xl:text-2xl font-bold text-gray-800">{globalStats.monturaCount}</p>
            </div>
            <Package className="w-7 h-7 2xl:w-8 2xl:h-8 text-purple-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-3 2xl:p-4 border-l-4 border-red-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs 2xl:text-sm text-gray-600">Stock Bajo</p>
              <p className="text-xl 2xl:text-2xl font-bold text-gray-800">{globalStats.lowStockCount}</p>
            </div>
            <TrendingDown className="w-7 h-7 2xl:w-8 2xl:h-8 text-red-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-3 2xl:p-4 border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs 2xl:text-sm text-gray-600">Valor Total</p>
              <p className="text-xl 2xl:text-2xl font-bold text-gray-800">S/ {globalStats.totalValue.toFixed(2)}</p>
            </div>
            <Package className="w-7 h-7 2xl:w-8 2xl:h-8 text-green-500" />
          </div>
        </div>

      </div>

      {/* Filters */}
      <div className="mb-4 2xl:mb-6">
        <InventoryFilters
          filters={filters}
          onFilterChange={setFilters}
          categories={categories}
          suppliers={suppliers}
        />
      </div>

      {/* Products Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden mb-4 inventory-table">
        <div className="overflow-x-auto">
          <DataTable columns={columns} data={filteredProducts} />
        </div>
      </div>

      <Pagination
        page={page}
        next={nextPage}
        previous={prevPage}
        onPageChange={setPage}
      />

      {/* Modals */}
      <ProductModal
        isOpen={isProductModalOpen}
        onClose={() => {
          setIsProductModalOpen(false);
          setSelectedProduct(null);
        }}
        onSave={selectedProduct ? handleUpdateProduct : handleCreateProduct}
        product={selectedProduct}
        categories={categories}
        suppliers={suppliers}
      />

      <StockAdjustModal
        isOpen={isStockModalOpen}
        onClose={() => {
          setIsStockModalOpen(false);
          setSelectedProduct(null);
        }}
        product={selectedProduct}
        onAdjust={handleStockAdjust}
      />
    </div>
  );
};

export default Inventory;