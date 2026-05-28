export interface ProductCategory {
  catproCod: number;
  catproCode: string;
  catproNom: string;
}

export interface Supplier {
  provCod: number;
  provRazSocial: string;
}

export interface Product {
  prodCod: number;
  prodCode: string;
  prodDescr: string;
  catproCod: number;
  categoria?: string;
  provCod: number;
  proveedor?: string;
  prodMarca: string;
  prodMate: string;
  material_display?: string;
  prodColor: string;
  prodTalla: string;
  prodGenero: string;
  genero_display?: string;
  prodTieneSobrelente?: boolean;
  prodForma?: string;
  prodDescripcionAdicional?: string;
  prodCostoInv: number;
  prodPrecioVenta: number;
  prodStock: number;
  prodStockMin: number;
  prodEstado: string;
  estado_display?: string;
  margen_ganancia?: number | null;
  ganancia_unitaria?: number;
  valor_total_stock?: number;
  created_at: string;
  updated_at: string;
}

export interface CreateProductDTO {
  catproCod: number;
  provCod: number;
  prodMarca?: string;
  prodMate?: string;
  prodColor?: string;
  prodTalla?: string;
  prodGenero?: string;
  prodTieneSobrelente?: boolean;
  prodForma?: string;
  prodDescripcionAdicional?: string;
  prodCostoInv: number;
  prodPrecioVenta: number;
  prodStock: number;
  prodStockMin: number;
  prodEstado?: string;
}

export interface UpdateProductDTO extends Partial<CreateProductDTO> {}

export interface InventoryFilters {
  search: string;
  filterLowStock: boolean;
  categoria: string;
  proveedor: string;
  material: string;
  genero: string;
  precioMin: string;
  precioMax: string;
  conStock: boolean;
  estado: string;
  tieneSobrelente: string;
}