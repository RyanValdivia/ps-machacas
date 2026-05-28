// Inventory/components/InventoryFilters.tsx

import React, { useState } from 'react';
import { Filter, X, ChevronDown, ChevronUp } from 'lucide-react';
import type {
  InventoryFilters as InventoryFiltersType,
  ProductCategory,
  Supplier,
} from '../../../auth/types/product/product';

interface InventoryFiltersProps {
  filters: InventoryFiltersType;
  onFilterChange: (filters: InventoryFiltersType) => void;
  categories: ProductCategory[];
  suppliers: Supplier[];
}

const MATERIAL_OPTIONS = [
  { value: '', label: 'Todos' },
  { value: 'A', label: 'Acetato' },
  { value: 'M', label: 'Metal' },
  { value: 'TR', label: 'TR' },
  { value: 'C', label: 'Carey' },
  { value: 'N', label: 'No aplica' },
];

const GENERO_OPTIONS = [
  { value: '', label: 'Todos' },
  { value: 'Hombre', label: 'Hombre' },
  { value: 'Mujer', label: 'Mujer' },
  { value: 'Unisex', label: 'Unisex' },
  { value: 'Nino', label: 'Niño' },
];

const ESTADO_OPTIONS = [
  { value: '', label: 'Todos' },
  { value: 'Active', label: 'Activo' },
  { value: 'Inactive', label: 'Inactivo' },
];

const SOBRELENTE_OPTIONS = [
  { value: '', label: 'Todos' },
  { value: 'true', label: 'Con Sobrelente' },
  { value: 'false', label: 'Sin Sobrelente' },
];

const InventoryFilters: React.FC<InventoryFiltersProps> = ({
  filters,
  onFilterChange,
  categories,
  suppliers,
}) => {
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleChange = (field: keyof InventoryFiltersType, value: any) => {
    onFilterChange({ ...filters, [field]: value });
  };

  const hasActiveFilters = () => {
    return (
      filters.categoria ||
      filters.proveedor ||
      filters.material ||
      filters.genero ||
      filters.precioMin ||
      filters.precioMax ||
      filters.conStock ||
      filters.estado ||
      filters.tieneSobrelente
    );
  };

  const clearAllFilters = () => {
    onFilterChange({
      search: filters.search,
      filterLowStock: filters.filterLowStock,
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
  };

  return (
    <div className="bg-white rounded-lg shadow">
      {/* Barra de filtros básicos */}
      <div className="p-4">
        <div className="flex flex-col lg:flex-row gap-3">
          {/* Búsqueda */}
          <div className="flex-1 relative">
            <input
              type="text"
              placeholder="Buscar por código (ej: M123, A456, TR789)..."
              value={filters.search}
              onChange={(e) => handleChange('search', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            />
            {filters.search && (
              <button
                onClick={() => handleChange('search', '')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                title="Limpiar búsqueda"
              >
                <X className="w-5 h-5" />
              </button>
            )}
          </div>

          {/* Botón Stock Bajo */}
          <button
            onClick={() => handleChange('filterLowStock', !filters.filterLowStock)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors whitespace-nowrap ${
              filters.filterLowStock
                ? 'bg-red-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {filters.filterLowStock ? 'Stock Bajo Activo' : 'Stock Bajo'}
          </button>

          {/* Botón Con Stock */}
          <button
            onClick={() => handleChange('conStock', !filters.conStock)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors whitespace-nowrap ${
              filters.conStock
                ? 'bg-green-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {filters.conStock ? 'Solo con Stock' : 'Con Stock'}
          </button>

          {/* Botón Filtros Avanzados */}
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors whitespace-nowrap ${
              showAdvanced || hasActiveFilters()
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <Filter className="w-4 h-4" />
            Filtros Avanzados
            {showAdvanced ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
            {hasActiveFilters() && !showAdvanced && (
              <span className="ml-1 bg-white text-blue-600 rounded-full w-5 h-5 flex items-center justify-center text-xs font-bold">
                !
              </span>
            )}
          </button>
        </div>
      </div>

      {/* Panel de filtros avanzados */}
      {showAdvanced && (
        <div className="border-t border-gray-200 p-4 bg-gray-50">
          <div className="mb-4 flex justify-between items-center">
            <h3 className="text-sm font-semibold text-gray-700">Filtros Avanzados</h3>
            {hasActiveFilters() && (
              <button
                onClick={clearAllFilters}
                className="flex items-center gap-1 text-sm text-red-600 hover:text-red-700 transition-colors"
              >
                <X className="w-4 h-4" />
                Limpiar filtros
              </button>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {/* Categoría */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Categoría
              </label>
              <select
                value={filters.categoria}
                onChange={(e) => handleChange('categoria', e.target.value)}
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              >
                <option value="">Todas las categorías</option>
                {categories.map((cat) => (
                  <option key={cat.catproCod} value={cat.catproCod}>
                    {cat.catproNom}
                  </option>
                ))}
              </select>
            </div>

            {/* Proveedor */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Proveedor
              </label>
              <select
                value={filters.proveedor}
                onChange={(e) => handleChange('proveedor', e.target.value)}
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              >
                <option value="">Todos los proveedores</option>
                {suppliers.map((sup) => (
                  <option key={sup.provCod} value={sup.provCod}>
                    {sup.provRazSocial}
                  </option>
                ))}
              </select>
            </div>

            {/* Material */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Material
              </label>
              <select
                value={filters.material}
                onChange={(e) => handleChange('material', e.target.value)}
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              >
                {MATERIAL_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Género */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Género
              </label>
              <select
                value={filters.genero}
                onChange={(e) => handleChange('genero', e.target.value)}
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              >
                {GENERO_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Estado */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Estado
              </label>
              <select
                value={filters.estado}
                onChange={(e) => handleChange('estado', e.target.value)}
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              >
                {ESTADO_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Sobrelente */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Sobrelente
              </label>
              <select
                value={filters.tieneSobrelente}
                onChange={(e) => handleChange('tieneSobrelente', e.target.value)}
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              >
                {SOBRELENTE_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Precio Mínimo */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Precio Mínimo (S/.)
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                placeholder="0.00"
                value={filters.precioMin}
                onChange={(e) => handleChange('precioMin', e.target.value)}
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              />
            </div>

            {/* Precio Máximo */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Precio Máximo (S/.)
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                placeholder="999.99"
                value={filters.precioMax}
                onChange={(e) => handleChange('precioMax', e.target.value)}
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              />
            </div>
          </div>

          {/* Indicador de filtros activos */}
          {hasActiveFilters() && (
            <div className="mt-4 flex flex-wrap gap-2">
              <span className="text-xs font-medium text-gray-600">Filtros activos:</span>
              {Object.entries(filters).map(([key, value]) => {
                if (!value || key === 'search' || key === 'filterLowStock') return null;
                return (
                  <span
                    key={key}
                    className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                  >
                    {key}
                    <button
                      onClick={() => handleChange(key as keyof InventoryFiltersType, '')}
                      className="hover:bg-blue-200 rounded-full p-0.5"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default InventoryFilters;