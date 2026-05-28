import api from "../api";
import type { 
  Product, 
  CreateProductDTO, 
  UpdateProductDTO, 
  ProductCategory, 
  Supplier 
} from "../../types/product/product";

export interface PaginatedResponse<T> {
  count: number;          // Total de productos en la BD
  next: string | null;    // URL de la siguiente página
  previous: string | null; // URL de la página anterior
  results: T[];           // Productos de la página actual
}

export const productService = {
  // Listar todos los productos con búsqueda opcional
  getAll: async (page: number = 1, pageSize: number = 50, search?: string): Promise<PaginatedResponse<Product>> => {
    const params: any = {
      page: page,
      page_size: pageSize
    };
    
    if (search && search.trim()) {
      params.search = search.trim();
    }
    
    const response = await api.get('/products/', { params });
    return response.data;
  },

  // Buscar productos (DEPRECATED - Usar getAll con search param)
  search: async (query: string): Promise<Product[]> => {
    const response = await api.get(`/products/?search=${encodeURIComponent(query)}`);
    return response.data.results || response.data;
  },

  // Obtener producto por ID
  getById: async (id: number): Promise<Product> => {
    const response = await api.get(`/products/${id}/`);
    return response.data;
  },

  // Crear producto
  create: async (data: CreateProductDTO): Promise<Product> => {
    const response = await api.post('/products/', data);
    return response.data;
  },

  // Actualizar producto
  update: async (id: number, data: UpdateProductDTO): Promise<Product> => {
    const response = await api.put(`/products/${id}/`, data);
    return response.data;
  },

  // Actualización parcial
  partialUpdate: async (id: number, data: Partial<UpdateProductDTO>): Promise<Product> => {
    const response = await api.patch(`/products/${id}/`, data);
    return response.data;
  },

  // Eliminar producto
  delete: async (id: number): Promise<void> => {
    await api.delete(`/products/${id}/`);
  },

  // Ajustar stock
  ajustarStock: async (id: number, cantidad: number, tipo: 'entrada' | 'salida'): Promise<Product> => {
    const response = await api.post(`/products/${id}/ajustar_stock/`, {
      cantidad,
      tipo
    });
    return response.data;
  },

  // Solo monturas
  getMonturas: async (): Promise<Product[]> => {
    const response = await api.get('/products/monturas/');
    return response.data.results || response.data;
  },

  // Solo accesorios
  getAccesorios: async (): Promise<Product[]> => {
    const response = await api.get('/products/accesorios/');
    return response.data.results || response.data;
  },

  // Productos con stock bajo
  getStockBajo: async (): Promise<Product[]> => {
    const response = await api.get('/products/stock_bajo/');
    return response.data;
  },

  // Obtener estadísticas globales del inventario
  getEstadisticas: async (): Promise<{
    totalProducts: number;
    lowStockCount: number;
    totalValue: number;
    monturaCount: number;
  }> => {
    const response = await api.get('/products/estadisticas/');
    return response.data;
  },

  // Obtener categorías
  getCategories: async (): Promise<ProductCategory[]> => {
    const response = await api.get('/categories/categories/');
    return response.data.results ?? response.data;
  },

  // Obtener proveedores
  getSuppliers: async (): Promise<Supplier[]> => {
    const response = await api.get('/suppliers/');
    return response.data.results || response.data;
  }
};

export default productService;