import React, { useState } from 'react';
import { Minus, Plus, Trash2, DollarSign, ShoppingCart } from 'lucide-react';
import type { CartItem } from '../../../../../auth/types/sale/sale';
interface ProductCartProps {
  cart: CartItem[];
  onUpdateQuantity: (index: number, newQuantity: number) => void;
  onUpdateDiscount?: (index: number, newDiscountAmount: number) => void;
  onRemoveItem: (index: number) => void;
}

const ProductCart: React.FC<ProductCartProps> = ({
  cart,
  onUpdateQuantity,
  onUpdateDiscount,
  onRemoveItem
}) => {
  const [editingDiscount, setEditingDiscount] = useState<number | null>(null);
  const [tempDiscount, setTempDiscount] = useState<string>('');

  // Helper para convertir precio a número de forma segura
  const parsePrice = (price: number | string | undefined): number => {
    if (typeof price === 'number') return price;
    if (typeof price === 'string') return parseFloat(price) || 0;
    return 0;
  };

  // Helper para truncar texto a 70 caracteres
  const truncateText = (text: string, maxLength: number = 70): string => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  const handleQuantityChange = (index: number, item: CartItem, change: number) => {
    const newQuantity = item.quantity + change;
    const maxStock = item.product.prodStock || 0;
    
    // Las lunas personalizadas no tienen límite de stock
    if (item.esLunaPersonalizada) {
      if (newQuantity >= 1) {
        onUpdateQuantity(index, newQuantity);
      }
    } else {
      if (newQuantity >= 1 && newQuantity <= maxStock) {
        onUpdateQuantity(index, newQuantity);
      }
    }
  };

  const handleDiscountClick = (index: number, item: CartItem) => {
    setEditingDiscount(index);
    setTempDiscount(item.discountAmount.toString());
  };

  const handleDiscountChange = (value: string) => {
    // Solo permitir números y un punto decimal
    if (/^\d*\.?\d*$/.test(value)) {
      setTempDiscount(value);
    }
  };

  const handleDiscountSave = (index: number) => {
    if (!onUpdateDiscount) return;
    
    const discountAmount = parseFloat(tempDiscount) || 0;
    // No puede ser negativo ni mayor al subtotal
    const validDiscount = Math.max(0, discountAmount);
    
    onUpdateDiscount(index, validDiscount);
    setEditingDiscount(null);
    setTempDiscount('');
  };

  const handleDiscountCancel = () => {
    setEditingDiscount(null);
    setTempDiscount('');
  };

  if (cart.length === 0) {
    return (
      <div className="h-full flex items-center justify-center px-3 md:px-6 py-4 md:py-8">
        <div className="text-center text-gray-500">
          <div className="w-20 h-20 md:w-30 md:h-30 bg-gradient-to-br from-gray-100 to-gray-200 rounded-2xl flex items-center justify-center mx-auto mb-2 md:mb-3">
            <ShoppingCart className="w-10 h-10 md:w-16 md:h-16 text-gray-400" strokeWidth={1.5} />
          </div>
          <p className="font-medium text-gray-600 text-base md:text-xl">Carrito vacío</p>
          <p className="text-xs md:text-sm mt-1 text-gray-500">Agrega productos para continuar</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="flex-1 flex flex-col min-h-0 h-full">
      {/* Header compacto */}
      <div className="px-3 md:px-6 py-2 md:py-4 border-b border-gray-100 bg-gradient-to-r from-gray-50 to-white flex-shrink-0">
        <div className="flex items-center justify-between">
          <h2 className="font-bold text-gray-800 text-sm md:text-base lg:text-lg">Productos seleccionados</h2>
          <span className="bg-gradient-to-r from-blue-500 to-blue-600 text-white text-xs md:text-sm font-bold px-2 md:px-3 py-1 md:py-1.5 rounded-full shadow-sm">
            {cart.length} {cart.length === 1 ? 'item' : 'items'}
          </span>
        </div>
      </div>

      {/* Lista de productos compacta con scroll */}
      <div className="flex-1 px-3 md:px-6 py-2 md:py-4 overflow-y-auto min-h-0">
        <div className="space-y-2 md:space-y-3">
          {cart.map((item, index) => {
            // Convertir precio de forma segura
            const precioVenta = parsePrice(item.product.prodPrecioVenta);
            
            // Generar key única: si es luna personalizada, usar índice + configuración
            // Si es producto normal, usar prodCod
            const uniqueKey = item.esLunaPersonalizada 
              ? `luna-${index}-${item.lunConfCod || 'unknown'}`
              : `product-${item.product.prodCod}`;
            
            return (
              <div 
                key={uniqueKey} 
                className="group flex items-center p-2 md:p-3 bg-white rounded-lg md:rounded-xl border border-gray-200 shadow-sm hover:shadow-md hover:border-blue-200 transition-all duration-200"
              >
                {/* Información principal compacta */}
                <div className="flex-1 min-w-0 mr-2 md:mr-4 p-1 md:p-2">
                  <div className="flex items-center gap-1 md:gap-2 mb-1 md:mb-2">
                    <h3 className="font-bold text-gray-900 text-xs md:text-sm lg:text-lg leading-tight flex-1 overflow-hidden" title={item.product.prodDescr}>
                      {truncateText(item.product.prodDescr, 70)}
                    </h3>
                    {item.discountAmount > 0 && (
                      <span className="bg-gradient-to-r from-red-500 to-red-600 text-white text-[10px] md:text-xs font-bold px-1.5 md:px-2 py-0.5 md:py-1 rounded-full whitespace-nowrap flex-shrink-0">
                        -S/ {item.discountAmount.toFixed(2)}
                      </span>
                    )}
                  </div>
                  
                  {item.esLunaPersonalizada ? (
                    // Luna personalizada - No mostrar código
                    <div className="mb-1 md:mb-2">
                      {/* Sin código, descripción está en el título */}
                    </div>
                  ) : (
                    // Info de producto normal
                    <div className="flex items-center gap-2 md:gap-4 mb-1 md:mb-2">
                      <span className="font-semibold text-gray-700 bg-gray-100 px-2 md:px-3 py-0.5 md:py-1 rounded-md text-xs md:text-sm">
                        {item.product.prodMarca}
                      </span>
                      {item.product.prodCode && (
                        <span className="text-[10px] md:text-xs text-gray-500 bg-gray-50 px-1.5 md:px-2 py-0.5 md:py-1 rounded font-mono hidden sm:inline">
                          {item.product.prodCode}
                        </span>
                      )}
                      {item.product.material_display && (
                        <span className="text-[10px] md:text-xs text-gray-600 bg-blue-50 px-1.5 md:px-2 py-0.5 md:py-1 rounded hidden md:inline">
                          {item.product.material_display}
                        </span>
                      )}
                    </div>
                  )}

                  <div className="flex items-center gap-2 md:gap-4">
                    <span className="font-bold text-blue-600 text-lg">
                      S/ {precioVenta.toFixed(2)}
                    </span>
                    {!item.esLunaPersonalizada && (
                      <span className="text-xs text-gray-500 bg-gray-50 px-2 py-1 rounded">
                        Stock: {item.product.prodStock}
                      </span>
                    )}

                    {/* Botón de descuento */}
                    {onUpdateDiscount && editingDiscount !== index && (
                      <button
                        onClick={() => handleDiscountClick(index, item)}
                        className="flex items-center gap-1 text-xs text-purple-600 bg-purple-50 px-2 py-1 rounded hover:bg-purple-100 transition-colors"
                        title="Aplicar descuento en soles"
                      >
                        <DollarSign className="w-3 h-3" />
                        {item.discountAmount > 0 ? `S/ ${item.discountAmount.toFixed(2)}` : 'Descuento'}
                      </button>
                    )}

                    {/* Editor de descuento */}
                    {onUpdateDiscount && editingDiscount === index && (
                      <div className="flex items-center gap-1">
                        <span className="text-xs text-gray-500">S/</span>
                        <input
                          type="text"
                          value={tempDiscount}
                          onChange={(e) => handleDiscountChange(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') handleDiscountSave(index);
                            if (e.key === 'Escape') handleDiscountCancel();
                          }}
                          className="w-20 px-2 py-1 text-xs border border-purple-300 rounded focus:outline-none focus:ring-1 focus:ring-purple-500"
                          placeholder="0.00"
                          autoFocus
                        />
                        <button
                          onClick={() => handleDiscountSave(index)}
                          className="px-2 py-1 text-xs bg-green-500 text-white rounded hover:bg-green-600"
                        >
                          ✓
                        </button>
                        <button
                          onClick={handleDiscountCancel}
                          className="px-2 py-1 text-xs bg-gray-400 text-white rounded hover:bg-gray-500"
                        >
                          ✕
                        </button>
                      </div>
                    )}
                  </div>

                  {/* Información adicional */}
                  {(item.product.prodColor || item.product.prodTalla || item.product.genero_display) && (
                    <div className="flex items-center gap-3 mt-2 text-xs text-gray-600">
                      {item.product.prodColor && (
                        <span className="bg-gray-50 px-2 py-1 rounded">
                          Color: {item.product.prodColor}
                        </span>
                      )}
                      {item.product.prodTalla && (
                        <span className="bg-gray-50 px-2 py-1 rounded">
                          Talla: {item.product.prodTalla}
                        </span>
                      )}
                      {item.product.genero_display && (
                        <span className="bg-gray-50 px-2 py-1 rounded">
                          {item.product.genero_display}
                        </span>
                      )}
                    </div>
                  )}
                </div>

                {/* Controles compactos */}
                <div className="flex items-center gap-2 md:gap-4 flex-shrink-0">
                  {/* Controles de cantidad */}
                  <div className="flex flex-col items-center gap-1 md:gap-2">
                    <div className="flex items-center gap-0.5 md:gap-1 bg-gray-100 rounded-lg p-0.5 md:p-1 border border-gray-300">
                      <button 
                        onClick={() => handleQuantityChange(index, item, -1)}
                        className={`w-6 h-6 md:w-8 md:h-8 flex items-center justify-center rounded-md transition-all ${
                          item.quantity <= 1 
                            ? 'bg-gray-300 text-gray-400 cursor-not-allowed' 
                            : 'bg-white text-gray-700 hover:bg-red-500 hover:text-white shadow-sm'
                        }`}
                        disabled={item.quantity <= 1}
                      >
                        <Minus className="w-2.5 h-2.5 md:w-3 md:h-3" />
                      </button>
                      
                      <span className="w-8 md:w-10 text-center font-bold text-gray-900 text-xs md:text-sm bg-white py-0.5 md:py-1 rounded mx-0.5 md:mx-1 border border-gray-200">
                        {item.quantity}
                      </span>
                      
                      <button 
                        onClick={() => handleQuantityChange(index, item, 1)}
                        className={`w-6 h-6 md:w-8 md:h-8 flex items-center justify-center rounded-md transition-all ${
                          (!item.esLunaPersonalizada && item.quantity >= item.product.prodStock)
                            ? 'bg-gray-300 text-gray-400 cursor-not-allowed' 
                            : 'bg-white text-gray-700 hover:bg-green-500 hover:text-white shadow-sm'
                        }`}
                        disabled={!item.esLunaPersonalizada && item.quantity >= item.product.prodStock}
                      >
                        <Plus className="w-2.5 h-2.5 md:w-3 md:h-3" />
                      </button>
                    </div>
                  </div>

                  {/* Total y eliminar */}
                  <div className="flex flex-col items-end gap-1 md:gap-2">
                    <div className="text-right">
                      {item.discountAmount > 0 ? (
                        <>
                          <span className="text-xs md:text-sm text-gray-500 line-through block">
                            S/ {item.subTotal.toFixed(2)} {/* CORREGIDO: usar subTotal en lugar de subtotal */}
                          </span>
                          <span className="font-bold text-green-600 text-base md:text-lg lg:text-xl block">
                            S/ {item.total.toFixed(2)}
                          </span>
                        </>
                      ) : (
                        <span className="font-bold text-gray-900 text-base md:text-lg lg:text-xl block">
                          S/ {item.total.toFixed(2)}
                        </span>
                      )}
                    </div>

                    <button 
                      onClick={() => onRemoveItem(index)}
                      className="flex items-center gap-0.5 md:gap-1 bg-red-500 text-white px-2 md:px-3 py-1.5 md:py-2 rounded-lg hover:bg-red-600 transition-all duration-200 shadow-sm hover:shadow-md text-xs md:text-sm font-medium"
                      title="Eliminar producto"
                    >
                      <Trash2 className="w-3 h-3 md:w-4 md:h-4" />
                      <span className="hidden sm:inline">Eliminar</span>
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default ProductCart;