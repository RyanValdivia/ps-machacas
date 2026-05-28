import { Package, AlertTriangle } from 'lucide-react';

interface Product {
  prodCod: number;
  prodDescr: string;
  prodMarca: string;
  prodStock: number;
  prodPrecioVenta: string;
}

interface ProductsTableProps {
  products: Product[];
  title: string;
  type: 'low-stock' | 'no-stock';
}

const ProductsTable = ({ products, title, type }: ProductsTableProps) => {
  const isEmpty = !products || products.length === 0;

  // Helper para formatear montos
  const formatMonto = (value: any): string => {
    const num = typeof value === 'string' ? parseFloat(value) : value;
    return isNaN(num) ? '0.00' : num.toFixed(2);
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center space-x-2 mb-4">
        <AlertTriangle className={`w-5 h-5 ${type === 'no-stock' ? 'text-red-500' : 'text-orange-500'}`} />
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <span className={`ml-auto px-3 py-1 rounded-full text-sm font-semibold ${
          type === 'no-stock' ? 'bg-red-100 text-red-700' : 'bg-orange-100 text-orange-700'
        }`}>
          {products.length}
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b-2 border-gray-200">
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Producto</th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Marca</th>
              <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700">Stock</th>
              <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">Precio</th>
            </tr>
          </thead>
          <tbody>
            {isEmpty ? (
              <tr>
                <td colSpan={4} className="py-12 text-center">
                  <div className="flex flex-col items-center justify-center text-gray-400">
                    <Package className="w-16 h-16 mb-3 opacity-30" />
                    <p className="text-lg font-medium">No hay productos</p>
                    <p className="text-sm mt-1">
                      {type === 'no-stock' ? 'Todos los productos tienen stock' : 'No hay productos con stock bajo'}
                    </p>
                  </div>
                </td>
              </tr>
            ) : (
              products.map((product, idx) => (
                <tr key={product.prodCod} className={`border-b border-gray-100 hover:bg-gray-50 transition-colors ${
                  idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'
                }`}>
                  <td className="py-3 px-4 text-sm text-gray-900 font-medium">{product.prodDescr}</td>
                  <td className="py-3 px-4 text-sm text-gray-600">{product.prodMarca || 'Sin marca'}</td>
                  <td className="py-3 px-4 text-center">
                    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-sm font-semibold ${
                      product.prodStock === 0 
                        ? 'bg-red-100 text-red-700' 
                        : product.prodStock < 5 
                        ? 'bg-orange-100 text-orange-700' 
                        : 'bg-yellow-100 text-yellow-700'
                    }`}>
                      {product.prodStock}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right text-sm font-semibold text-gray-900">
                    S/ {formatMonto(product.prodPrecioVenta)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ProductsTable;
