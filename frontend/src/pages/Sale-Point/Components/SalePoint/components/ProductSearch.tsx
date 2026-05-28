import React, { useState, useEffect, useRef } from 'react';
import { Loader, Barcode, } from 'lucide-react';
import type { Product } from '../../../../../auth/types/product/product';
import productService from '../../../../../auth/services/product/productService';
import { showWarningToast } from '../../../../../utils/sweetAlertConfig';

interface ProductSearchProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  onProductSelect: (product: Product) => void;
  onAddLunaClick?: () => void;
}

const ProductSearch: React.FC<ProductSearchProps> = ({
  searchQuery,
  onSearchChange,
  onProductSelect,
}) => {
  const [loading, setLoading] = useState(false);
  const [searchResults, setSearchResults] = useState<Product[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const searchTimeoutRef = useRef<number | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Búsqueda en tiempo real con debounce
  useEffect(() => {
    // Limpiar timeout anterior
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    if (searchQuery.trim()) {
      const timeout = setTimeout(() => {
        performSearch(searchQuery);
      }, 300); // 300ms debounce

      searchTimeoutRef.current = timeout;
    } else {
      setSearchResults([]);
    }

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [searchQuery]);

  const performSearch = async (query: string) => {
    try {
      setLoading(true);
      
      // Búsqueda SOLO por código (que empiece con el query)
      const results = await productService.search(query);
      
      // Filtrar: solo activos con stock + que el código EMPIECE con el query
      const activeResults = results.filter(product => 
        product.prodEstado === 'Active' && 
        product.prodStock > 0 &&
        product.prodCode.toUpperCase().startsWith(query.toUpperCase())
      );
      
      // Ordenar: primero coincidencias exactas, luego por código
      const sortedResults = activeResults.sort((a, b) => {
        const aExact = a.prodCode.toUpperCase() === query.toUpperCase() ? 0 : 1;
        const bExact = b.prodCode.toUpperCase() === query.toUpperCase() ? 0 : 1;
        
        if (aExact !== bExact) return aExact - bExact;
        return a.prodCode.localeCompare(b.prodCode);
      });
      
      setSearchResults(sortedResults);
      setSelectedIndex(0); // Reset selección al primer resultado
      
    } catch (error) {
      console.error('Error en búsqueda:', error);
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleProductSelect = (product: Product) => {
    const hasStock = product.prodStock > 0;
    
    if (!hasStock) {
      showWarningToast(`El producto "${product.prodDescr}" no tiene stock disponible.`);
      return;
    }
    
    onProductSelect(product);
    onSearchChange('');
    setSearchResults([]);
    setSelectedIndex(0);
    
    // Volver a enfocar el input después de agregar
    setTimeout(() => inputRef.current?.focus(), 100);
  };

  // Manejar teclas (Enter y flechas)
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (searchResults.length === 0) return;

    switch (e.key) {
      case 'Enter':
        e.preventDefault();
        // Seleccionar el producto en el índice actual
        handleProductSelect(searchResults[selectedIndex]);
        break;
        
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev < searchResults.length - 1 ? prev + 1 : prev
        );
        break;
        
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => prev > 0 ? prev - 1 : 0);
        break;
        
      case 'Escape':
        e.preventDefault();
        onSearchChange('');
        setSearchResults([]);
        setSelectedIndex(0);
        break;
    }
  };

  return (
    <div className="px-2 md:px-4 lg:px-6 xl:px-8 py-2 md:py-4 relative">
      {/* Buscador de productos */}
      <div className="relative">
        <Barcode className="absolute left-2 md:left-3 top-1/2 transform -translate-y-1/2 text-blue-500 w-4 h-4 md:w-5 md:h-5" />
        
        <input
          ref={inputRef}
          type="text"
          placeholder="Buscar por código..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value.toUpperCase())}
          onKeyDown={handleKeyDown}
          className="w-full pl-8 md:pl-10 pr-3 md:pr-4 py-2 md:py-3 border-2 border-gray-300 rounded-lg transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-200 text-sm md:text-base"
          autoFocus
        />
        
        {loading && (
          <Loader className="absolute right-2 md:right-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4 md:w-5 md:h-5 animate-spin" />
        )}
        
        {/* Indicador de resultados */}
        {!loading && searchQuery && searchResults.length > 0 && (
          <div className="absolute right-2 md:right-3 top-1/2 transform -translate-y-1/2 bg-blue-100 text-blue-700 text-[10px] md:text-xs px-1.5 md:px-2.5 py-0.5 md:py-1 rounded-full font-medium">
            {searchResults.length} {searchResults.length === 1 ? 'resultado' : 'resultados'}
          </div>
        )}
      </div>
      
      {/* Ayuda de atajos */}
      {searchResults.length > 0 && (
        <div className="mt-1 md:mt-2 text-[10px] md:text-xs text-gray-500 flex items-center gap-2 md:gap-4">
          <span className="flex items-center gap-0.5 md:gap-1">
            <kbd className="px-1 md:px-2 py-0.5 bg-gray-100 border border-gray-300 rounded text-[10px] md:text-xs font-mono">Enter</kbd>
            <span className="hidden sm:inline">Agregar</span>
          </span>
          <span className="flex items-center gap-0.5 md:gap-1">
            <kbd className="px-1 md:px-2 py-0.5 bg-gray-100 border border-gray-300 rounded text-[10px] md:text-xs font-mono">↑↓</kbd>
            <span className="hidden sm:inline">Navegar</span>
          </span>
          <span className="flex items-center gap-0.5 md:gap-1">
            <kbd className="px-1 md:px-2 py-0.5 bg-gray-100 border border-gray-300 rounded text-[10px] md:text-xs font-mono">Esc</kbd>
            <span className="hidden sm:inline">Cerrar</span>
          </span>
        </div>
      )}

      {/* Resultados de búsqueda */}
      {searchQuery && searchResults.length > 0 && (
        <div className="absolute left-4 sm:left-6 lg:left-8 right-4 sm:right-6 lg:right-8 mt-2 bg-white border-2 border-blue-200 rounded-lg shadow-2xl z-50 max-h-96 overflow-y-auto">
          {searchResults.map((product, index) => (
            <ProductResultItem 
              key={product.prodCod} 
              product={product} 
              onSelect={handleProductSelect}
              isExactCodeMatch={product.prodCode.toUpperCase() === searchQuery.toUpperCase()}
              isSelected={index === selectedIndex}
            />
          ))}
        </div>
      )}

      {/* Sin resultados */}
      {searchQuery && !loading && searchResults.length === 0 && (
        <div className="absolute left-4 sm:left-6 lg:left-8 right-4 sm:right-6 lg:right-8 mt-2 bg-white border border-gray-200 rounded-lg shadow-xl z-50 p-6 text-center text-gray-500">
          <Barcode className="w-10 h-10 mx-auto mb-3 text-gray-400" />
          <p className="font-medium">No se encontró producto con código: <span className="font-bold text-gray-700">{searchQuery}</span></p>
          <p className="text-sm mt-1">El código debe coincidir desde el inicio</p>
          <p className="text-xs mt-2 text-gray-400">Ej: "MO-12" encuentra "MO-123", "MO-1234"</p>
        </div>
      )}
    </div>
  );
};

// Helper para convertir precio a número de forma segura
const parsePrice = (price: number | string | undefined): number => {
  if (typeof price === 'number') return price;
  if (typeof price === 'string') return parseFloat(price) || 0;
  return 0;
};

// Componente para mostrar cada resultado
const ProductResultItem: React.FC<{ 
  product: Product; 
  onSelect: (product: Product) => void;
  isExactCodeMatch?: boolean;
  isSelected?: boolean;
}> = ({ product, onSelect, isExactCodeMatch, isSelected }) => {
  const hasStock = product.prodStock > 0;
  
  const handleClick = () => {
    if (!hasStock) {
      showWarningToast(`El producto "${product.prodDescr}" no tiene stock disponible.`);
      return;
    }
    onSelect(product);
  };

  // Convertir precios a número de forma segura
  const precioVenta = parsePrice(product.prodPrecioVenta);
  
  return (
    <div
      className={`p-3 sm:p-4 cursor-pointer border-b border-gray-100 last:border-b-0 transition-all duration-100 ${
        isSelected 
          ? 'bg-blue-100 border-l-4 border-l-blue-500' 
          : hasStock 
            ? 'hover:bg-blue-50 bg-white' 
            : 'bg-gray-50 hover:bg-gray-100 text-gray-500 cursor-not-allowed'
      }`}
      onClick={handleClick}
    >
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 sm:gap-4">
        {/* Descripción y Código */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <h4 className={`font-semibold ${hasStock ? 'text-gray-900' : 'text-gray-600'} text-sm sm:text-base`}>
              {product.prodDescr.length > 50 ? product.prodDescr.substring(0, 50) + '...' : product.prodDescr}
            </h4>
            {isExactCodeMatch && hasStock && (
              <span className="bg-green-50 text-green-700 text-xs px-2 py-0.5 rounded-full border border-green-200 whitespace-nowrap font-medium">
                ✓ Exacto
              </span>
            )}
            {isSelected && (
              <span className="bg-blue-600 text-white text-xs px-2 py-0.5 rounded-full whitespace-nowrap font-medium">
                Seleccionado
              </span>
            )}
          </div>
          
          <div className="flex items-center gap-2 sm:gap-3 text-xs sm:text-sm text-gray-500 flex-wrap">
            {/* Código */}
            <div className="flex items-center gap-1">
              <Barcode className="w-3.5 h-3.5 flex-shrink-0" />
              <span className="font-mono font-bold text-blue-600">{product.prodCode}</span>
            </div>
            
            {/* Categoría */}
            {product.categoria && (
              <span className="text-xs bg-gray-100 px-2 py-0.5 rounded">
                {product.categoria}
              </span>
            )}
            
            {/* Marca */}
            <span className={`font-medium ${hasStock ? 'text-gray-700' : 'text-gray-500'}`}>
              {product.prodMarca}
            </span>
          </div>
        </div>

        {/* Precio y Stock */}
        <div className="flex items-center gap-3 sm:gap-4">
          {/* Precio */}
          <div className="text-left sm:text-right">
            <p className={`font-bold text-base sm:text-lg ${hasStock ? 'text-blue-600' : 'text-gray-400'}`}>
              S/ {precioVenta.toFixed(2)}
            </p>
          </div>

          {/* Stock */}
          <div className="text-right">
          {!hasStock ? (
            <span className="bg-red-50 text-red-700 text-xs px-2 sm:px-3 py-1 sm:py-1.5 rounded-full font-medium border border-red-200 whitespace-nowrap">
              Sin stock
            </span>
          ) : product.prodStock <= product.prodStockMin ? (
            <div className="text-center">
              <span className="bg-yellow-50 text-yellow-700 text-xs px-2 sm:px-3 py-1 sm:py-1.5 rounded-full font-medium border border-yellow-200 whitespace-nowrap block">
                Bajo
              </span>
              <p className="text-xs text-gray-600 mt-1">{product.prodStock}</p>
            </div>
          ) : (
            <div className="text-center">
              <span className="bg-green-50 text-green-700 text-xs px-2 sm:px-3 py-1 sm:py-1.5 rounded-full font-medium border border-green-200 whitespace-nowrap block">
                Stock
              </span>
              <p className="text-xs text-gray-600 mt-1">{product.prodStock}</p>
            </div>
          )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductSearch;