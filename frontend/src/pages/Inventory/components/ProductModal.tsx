import React, { useState, useEffect } from 'react';
import Modal from '../../../components/Modal/modal';
import type { Product, CreateProductDTO, ProductCategory, Supplier } from '../../../auth/types/product/product';
import { showWarningToast } from '../../../utils/sweetAlertConfig';

interface ProductModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (data: CreateProductDTO) => Promise<void>;
  product?: Product | null;
  categories: ProductCategory[];
  suppliers: Supplier[];
}

const MATERIAL_CHOICES = [
  { value: 'A', label: 'Acetato' },
  { value: 'M', label: 'Metal' },
  { value: 'TR', label: 'TR' },
  { value: 'C', label: 'Carey' },
  { value: 'N', label: 'No aplica' },
];

const GENERO_CHOICES = [
  { value: 'Hombre', label: 'Hombre' },
  { value: 'Mujer', label: 'Mujer' },
  { value: 'Unisex', label: 'Unisex' },
  { value: 'Nino', label: 'Niño' },
];

const ProductModal: React.FC<ProductModalProps> = ({
  isOpen,
  onClose,
  onSave,
  product,
  categories,
  suppliers,
}) => {
  const [formData, setFormData] = useState<CreateProductDTO>({
    catproCod: 0,
    provCod: 0,
    prodMarca: '',
    prodMate: 'N',
    prodColor: '',
    prodTalla: '',
    prodGenero: 'Unisex',
    prodTieneSobrelente: false,
    prodForma: '',
    prodDescripcionAdicional: '',
    prodCostoInv: 0,
    prodPrecioVenta: 0,
    prodStock: 1,
    prodStockMin: 0,
    prodEstado: 'Active',
  });

  // Estado adicional para los valores de display (pueden ser string vacío)
  const [displayValues, setDisplayValues] = useState({
    prodCostoInv: '',
    prodPrecioVenta: '',
    prodStock: '1',  // Stock inicial en 1
    prodStockMin: '',
  });

  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const safeCategories = Array.isArray(categories) ? categories : [];
  const safeSuppliers = Array.isArray(suppliers) ? suppliers : [];
  
  // Función para obtener ID de la categoría Montura por defecto
  const getMonturaDefaultId = (): number => {
    const montura = safeCategories.find(cat => cat.catproCode === 'MO');
    return montura ? montura.catproCod : 0;
  };
  
  // Función para mapear material display a valor
  const mapMaterialToValue = (materialDisplay: string): string => {
    const materialMap: Record<string, string> = {
      'Acetato': 'A',
      'Metal': 'M',
      'TR': 'TR',
      'Carey': 'C'
    };
    return materialMap[materialDisplay] || 'N';
  };

  // Función para obtener ID de categoría por nombre
  const getCategoryIdByName = (categoryName: string): number => {
    const category = safeCategories.find(cat => cat.catproNom === categoryName);
    return category ? category.catproCod : 0;
  };

  // Función para obtener ID de proveedor por nombre
  const getSupplierIdByName = (supplierName: string): number => {
    const supplier = safeSuppliers.find(sup => sup.provRazSocial === supplierName);
    return supplier ? supplier.provCod : 0;
  };

  // Cargar datos del producto si se está editando
  useEffect(() => {
    if (product) {
      console.log('=== PRODUCTO COMPLETO PARA DEBUG ===');
    console.log('Objeto producto:', product);
    console.log('Propiedades del producto:', Object.keys(product));
    
    // Buscar campos relacionados con color y talla
    const colorFields = Object.keys(product).filter(key => 
      key.toLowerCase().includes('color')
    );
    const tallaFields = Object.keys(product).filter(key => 
      key.toLowerCase().includes('talla') || key.toLowerCase().includes('size')
    );
    
    console.log('Campos de color encontrados:', colorFields);
    console.log('Campos de talla encontrados:', tallaFields);
    
    console.log('=== FIN DEBUG ===');
      
      let catproCodValue = 0;
      let provCodValue = 0;
      
      // Opción 1: Si vienen directamente en el producto
      if (product.catproCod !== undefined) {
        catproCodValue = Number(product.catproCod) || 0;
      } 
      // Opción 2: Si tenemos nombre de categoría
      else if (product.categoria) {
        catproCodValue = getCategoryIdByName(product.categoria);
      }
      
      // Opción 1: Si viene directamente
      if (product.provCod !== undefined) {
        provCodValue = Number(product.provCod) || 0;
      }
      // Opción 2: Si tenemos nombre de proveedor (necesitarías esta propiedad)
      else if ((product as any).proveedor) {
        provCodValue = getSupplierIdByName((product as any).proveedor);
      }
      // Opción 3: Por defecto usar el proveedor genérico si existe
      else {
        const genericSupplier = safeSuppliers.find(sup => 
          sup.provRazSocial === "Proveedor Genérico"
        );
        provCodValue = genericSupplier ? genericSupplier.provCod : 0;
      }
      
      // Mapear material si viene en material_display
      let prodMateValue = 'N';
      if ((product as any).material_display) {
        prodMateValue = mapMaterialToValue((product as any).material_display);
      } else if (product.prodMate) {
        prodMateValue = product.prodMate;
      }
      
      // Mapear estado si viene en estado_display
      let prodEstadoValue = 'Active';
      if ((product as any).estado_display) {
        prodEstadoValue = (product as any).estado_display === 'Activo' ? 'Active' : 'Inactive';
      } else if (product.prodEstado) {
        prodEstadoValue = product.prodEstado;
      }
      
      setFormData({
        catproCod: catproCodValue,
        provCod: provCodValue,
        prodMarca: product.prodMarca || '',
        prodMate: prodMateValue,
        prodColor: product.prodColor || '',
        prodTalla: product.prodTalla || '',
        prodGenero: product.prodGenero || 'Unisex',
        prodTieneSobrelente: product.prodTieneSobrelente || false,
        prodForma: product.prodForma || '',
        prodDescripcionAdicional: product.prodDescripcionAdicional || '',
        prodCostoInv: product.prodCostoInv || 0,
        prodPrecioVenta: product.prodPrecioVenta || 0,
        prodStock: product.prodStock || 1,
        prodStockMin: product.prodStockMin || 0,
        prodEstado: prodEstadoValue,
      });

      // Actualizar displayValues con los valores del producto
      setDisplayValues({
        prodCostoInv: product.prodCostoInv ? product.prodCostoInv.toString() : '',
        prodPrecioVenta: product.prodPrecioVenta ? product.prodPrecioVenta.toString() : '',
        prodStock: product.prodStock ? product.prodStock.toString() : '',
        prodStockMin: product.prodStockMin ? product.prodStockMin.toString() : '',
      });
      
      console.log('FormData después de mapear:', {
        catproCod: catproCodValue,
        provCod: provCodValue,
        prodMarca: product.prodMarca,
      });
    } else {
      // Resetear formulario para nuevo producto con categoría Montura por defecto
      const monturaId = getMonturaDefaultId();
      setFormData({
        catproCod: monturaId,
        provCod: 0,
        prodMarca: '',
        prodMate: 'N',
        prodColor: '',
        prodTalla: '',
        prodGenero: 'Unisex',
        prodTieneSobrelente: false,
        prodForma: '',
        prodDescripcionAdicional: '',
        prodCostoInv: 0,
        prodPrecioVenta: 0,
        prodStock: 1,
        prodStockMin: 0,
        prodEstado: 'Active',
      });

      // Resetear displayValues para nuevo producto (campos vacíos excepto stock)
      setDisplayValues({
        prodCostoInv: '',
        prodPrecioVenta: '',
        prodStock: '1',  // Stock inicial en 1
        prodStockMin: '',
      });
    }
    setErrors({});
  }, [product, categories, suppliers]);

  const handleChange = (field: keyof CreateProductDTO, value: any) => {
    // Convertir marca a mayúsculas
    if (field === 'prodMarca' && typeof value === 'string') {
      value = value.toUpperCase();
    }
    
    // Manejar campos numéricos especiales (costo, precio, stock)
    if (field === 'prodCostoInv' || field === 'prodPrecioVenta' || field === 'prodStock' || field === 'prodStockMin') {
      // Actualizar displayValue (lo que se muestra en el input)
      setDisplayValues(prev => ({ ...prev, [field]: value }));
      
      // Convertir a número para formData
      const numValue = value === '' ? 0 : (field === 'prodStock' || field === 'prodStockMin' ? parseInt(value) : parseFloat(value));
      setFormData(prev => ({ ...prev, [field]: isNaN(numValue) ? 0 : numValue }));
    }
    // Convertir a número si es necesario
    else if (field === 'catproCod' || field === 'provCod') {
      const numValue = Number(value) || 0;
      setFormData(prev => {
        const newData = { ...prev, [field]: numValue };
        
        // Si cambia la categoría a accesorio, forzar material a 'N'
        if (field === 'catproCod') {
          const categoria = safeCategories.find(c => c.catproCod === numValue);
          if (categoria?.catproCode === 'AC') {
            newData.prodMate = 'N';
          }
        }
        
        return newData;
      });
    } else {
      setFormData(prev => ({ ...prev, [field]: value }));
    }
    
    // Limpiar error del campo
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.catproCod) {
      newErrors.catproCod = 'Selecciona una categoría';
    }

    if (!formData.provCod) {
      newErrors.provCod = 'Selecciona un proveedor';
    }

    // Validaciones específicas por categoría
    const categoria = safeCategories.find(c => c.catproCod === formData.catproCod);
    if (categoria) {
      const esMontura = categoria.catproCode === 'MO';
      const esAccesorio = categoria.catproCode === 'AC';

      if (esMontura) {
        if (!formData.prodMarca || formData.prodMarca.trim().length < 2) {
          newErrors.prodMarca = 'La marca es obligatoria para monturas (mínimo 2 caracteres)';
        }
        if (formData.prodMate === 'N') {
          newErrors.prodMate = 'Selecciona un material para monturas';
        }
        if (!formData.prodTalla) {
          newErrors.prodTalla = 'La talla es obligatoria para monturas';
        }
      }

      if (esAccesorio && formData.prodMate !== 'N') {
        newErrors.prodMate = 'Los accesorios deben tener material "No aplica"';
      }
    }

    if (formData.prodCostoInv < 0) {
      newErrors.prodCostoInv = 'El costo no puede ser negativo';
    }

    if (formData.prodPrecioVenta < 0) {
      newErrors.prodPrecioVenta = 'El precio no puede ser negativo';
    }

    if (formData.prodStock < 0) {
      newErrors.prodStock = 'El stock no puede ser negativo';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      showWarningToast('Por favor completa todos los campos obligatorios');
      return;
    }

    setLoading(true);
    try {
      await onSave(formData);
      onClose();
    } catch (error: any) {
      console.error('Error al guardar producto:', error);
      if (error.response?.data) {
        setErrors(error.response.data);
      }
      // El error ya se muestra en Inventory.tsx con SweetAlert2
    } finally {
      setLoading(false);
    }
  };

  const selectedCategory = safeCategories.find(c => c.catproCod === formData.catproCod);
  const esMontura = selectedCategory?.catproCode === 'MO';
  const esAccesorio = selectedCategory?.catproCode === 'AC';

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={product ? 'Editar Producto' : 'Nuevo Producto'}
      size="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-3 lg:space-y-4">
        {/* Sección: Información General */}
        <div>
          <h3 className="text-xs lg:text-sm font-semibold text-gray-800 mb-2 pb-1.5 border-b border-gray-200">
            Información General
          </h3>
          
          {/* Categoría y Proveedor */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-2.5 lg:gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Categoría *
              </label>
              <select
                value={formData.catproCod || 0}
                onChange={(e) => handleChange('catproCod', e.target.value)}
                className={`w-full px-2.5 py-1.5 text-xs lg:text-sm border rounded-md focus:ring-2 focus:ring-blue-500 outline-none transition-colors ${
                  errors.catproCod ? 'border-red-500' : 'border-gray-300'
                }`}
              >
                <option value={0}>Seleccionar categoría</option>
                {safeCategories.map((cat) => (
                  <option key={cat.catproCod} value={cat.catproCod}>
                    {cat.catproNom}
                  </option>
                ))}
              </select>
              {errors.catproCod && (
                <p className="text-red-500 text-[10px] mt-0.5">{errors.catproCod}</p>
              )}
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Proveedor *
              </label>
              <select
                value={formData.provCod || 0}
                onChange={(e) => handleChange('provCod', e.target.value)}
                className={`w-full px-2.5 py-1.5 text-xs lg:text-sm border rounded-md focus:ring-2 focus:ring-blue-500 outline-none transition-colors ${
                  errors.provCod ? 'border-red-500' : 'border-gray-300'
                }`}
              >
                <option value={0}>Seleccionar proveedor</option>
                {safeSuppliers.map((sup) => (
                  <option key={sup.provCod} value={sup.provCod}>
                    {sup.provRazSocial}
                  </option>
                ))}
              </select>
              {errors.provCod && (
                <p className="text-red-500 text-[10px] mt-0.5">{errors.provCod}</p>
              )}
            </div>
          </div>
        </div>

        {/* Campos específicos para MONTURAS */}
        {esMontura && (
          <div>
            <h3 className="text-xs lg:text-sm font-semibold text-gray-800 mb-2 pb-1.5 border-b border-gray-200">
              Características de la Montura
            </h3>
            
            {/* Marca */}
            <div className="mb-2.5">
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Marca *
              </label>
              <input
                type="text"
                value={formData.prodMarca}
                onChange={(e) => handleChange('prodMarca', e.target.value)}
                placeholder="Ej: Ray-Ban"
                className={`w-full px-2.5 py-1.5 text-xs lg:text-sm border rounded-md focus:ring-2 focus:ring-blue-500 outline-none transition-colors ${
                  errors.prodMarca ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.prodMarca && (
                <p className="text-red-500 text-[10px] mt-0.5">{errors.prodMarca}</p>
              )}
            </div>

            {/* Material y Género */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-2.5 lg:gap-3 mb-2.5">
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  Material *
                </label>
                <select
                  value={formData.prodMate}
                  onChange={(e) => handleChange('prodMate', e.target.value)}
                  className={`w-full px-2.5 py-1.5 text-xs lg:text-sm border rounded-md focus:ring-2 focus:ring-blue-500 outline-none transition-colors ${
                    errors.prodMate ? 'border-red-500' : 'border-gray-300'
                  }`}
                >
                  {MATERIAL_CHOICES.map((mat) => (
                    <option key={mat.value} value={mat.value}>
                      {mat.label}
                    </option>
                  ))}
                </select>
                {errors.prodMate && (
                  <p className="text-red-500 text-[10px] mt-0.5">{errors.prodMate}</p>
                )}
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  Género
                </label>
                <select
                  value={formData.prodGenero}
                  onChange={(e) => handleChange('prodGenero', e.target.value)}
                  className="w-full px-2.5 py-1.5 text-xs lg:text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 outline-none transition-colors"
                >
                  {GENERO_CHOICES.map((gen) => (
                    <option key={gen.value} value={gen.value}>
                      {gen.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Talla y Color */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-2.5 lg:gap-3 mb-2.5">
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  Modelo - Talla *
                </label>
                <input
                  type="text"
                  value={formData.prodTalla}
                  onChange={(e) => handleChange('prodTalla', e.target.value)}
                  placeholder="Ej: 54-18-140"
                  className={`w-full px-2.5 py-1.5 text-xs lg:text-sm border rounded-md focus:ring-2 focus:ring-blue-500 outline-none transition-colors ${
                    errors.prodTalla ? 'border-red-500' : 'border-gray-300'
                  }`}
                />
                {errors.prodTalla && (
                  <p className="text-red-500 text-[10px] mt-0.5">{errors.prodTalla}</p>
                )}
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  Color
                </label>
                <input
                  type="text"
                  value={formData.prodColor}
                  onChange={(e) => handleChange('prodColor', e.target.value)}
                  placeholder="Ej: Negro"
                  className="w-full px-2.5 py-1.5 text-xs lg:text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 outline-none transition-colors"
                />
              </div>
            </div>

            {/* Forma y Sobrelente */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-2.5 lg:gap-3">
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  Forma
                </label>
                <input
                  type="text"
                  value={formData.prodForma}
                  onChange={(e) => handleChange('prodForma', e.target.value)}
                  placeholder="Ej: Redondo, Cuadrado, Aviador"
                  className="w-full px-2.5 py-1.5 text-xs lg:text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 outline-none transition-colors"
                />
              </div>

              <div className="flex items-center pt-1 lg:pt-2">
                <input
                  type="checkbox"
                  id="sobrelente"
                  checked={formData.prodTieneSobrelente}
                  onChange={(e) => handleChange('prodTieneSobrelente', e.target.checked)}
                  className="w-3.5 h-3.5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <label htmlFor="sobrelente" className="ml-2 text-xs lg:text-sm font-medium text-gray-700">
                  Tiene Sobrelente
                </label>
              </div>
            </div>

            {/* Descripción Adicional */}
            <div className="mt-2.5">
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Descripción Adicional
              </label>
              <textarea
                value={formData.prodDescripcionAdicional}
                onChange={(e) => handleChange('prodDescripcionAdicional', e.target.value)}
                placeholder="Información adicional del producto"
                rows={2}
                className="w-full px-2.5 py-1.5 text-xs lg:text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 outline-none transition-colors resize-none"
              />
            </div>
          </div>
        )}

        {/* Campos específicos para ACCESORIOS (solo campos básicos) */}
        {esAccesorio && (
          <div>
            <h3 className="text-xs lg:text-sm font-semibold text-gray-800 mb-2 pb-1.5 border-b border-gray-200">
              Descripción del Accesorio
            </h3>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Descripción Adicional
              </label>
              <textarea
                value={formData.prodDescripcionAdicional}
                onChange={(e) => handleChange('prodDescripcionAdicional', e.target.value)}
                placeholder="Descripción del accesorio"
                rows={2}
                className="w-full px-2.5 py-1.5 text-xs lg:text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 outline-none transition-colors resize-none"
              />
            </div>
          </div>
        )}

        {/* Precios - Se muestran siempre */}
        <div>
          <h3 className="text-xs lg:text-sm font-semibold text-gray-800 mb-2 pb-1.5 border-b border-gray-200">
            Precios y Stock
          </h3>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-2.5 lg:gap-3 mb-2.5">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Costo (S/.) *
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                value={displayValues.prodCostoInv}
                onChange={(e) => handleChange('prodCostoInv', e.target.value)}
                placeholder="0.00"
                className={`w-full px-2.5 py-1.5 text-xs lg:text-sm border rounded-md focus:ring-2 focus:ring-blue-500 outline-none transition-colors ${
                  errors.prodCostoInv ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.prodCostoInv && (
                <p className="text-red-500 text-[10px] mt-0.5">{errors.prodCostoInv}</p>
              )}
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Precio Venta (S/.) *
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                value={displayValues.prodPrecioVenta}
                onChange={(e) => handleChange('prodPrecioVenta', e.target.value)}
                placeholder="0.00"
                className={`w-full px-2.5 py-1.5 text-xs lg:text-sm border rounded-md focus:ring-2 focus:ring-blue-500 outline-none transition-colors ${
                  errors.prodPrecioVenta ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.prodPrecioVenta && (
                <p className="text-red-500 text-[10px] mt-0.5">{errors.prodPrecioVenta}</p>
              )}
            </div>
          </div>

          {/* Stock */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-2.5 lg:gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Stock Actual *
              </label>
              <input
                type="number"
                min="0"
                value={displayValues.prodStock}
                onChange={(e) => handleChange('prodStock', e.target.value)}
                placeholder="1"
                className={`w-full px-2.5 py-1.5 text-xs lg:text-sm border rounded-md focus:ring-2 focus:ring-blue-500 outline-none transition-colors ${
                  errors.prodStock ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.prodStock && (
                <p className="text-red-500 text-[10px] mt-0.5">{errors.prodStock}</p>
              )}
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Stock Mínimo
              </label>
              <input
                type="number"
                min="0"
                value={displayValues.prodStockMin}
                onChange={(e) => handleChange('prodStockMin', e.target.value)}
                placeholder="0"
                className="w-full px-2.5 py-1.5 text-xs lg:text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 outline-none transition-colors"
              />
            </div>
          </div>
        </div>

        {/* Botones */}
        <div className="flex flex-col sm:flex-row justify-end gap-2 lg:gap-2.5 pt-3 lg:pt-4 border-t border-gray-200">
          <button
            type="button"
            onClick={onClose}
            className="px-4 lg:px-5 py-1.5 lg:py-2 text-xs lg:text-sm text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors font-medium"
            disabled={loading}
          >
            Cancelar
          </button>
          <button
            type="submit"
            className="px-4 lg:px-5 py-1.5 lg:py-2 text-xs lg:text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium shadow-sm hover:shadow-md"
            disabled={loading}
          >
            {loading ? 'Guardando...' : product ? 'Actualizar' : 'Crear Producto'}
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default ProductModal;