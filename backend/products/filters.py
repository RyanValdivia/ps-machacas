import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    """Filtros personalizados para productos"""
    
    # Filtros de busqueda
    codigo = django_filters.CharFilter(field_name='prodCode', lookup_expr='icontains')
    marca = django_filters.CharFilter(field_name='prodMarca', lookup_expr='icontains')
    descripcion = django_filters.CharFilter(field_name='prodDescr', lookup_expr='icontains')
    
    # Filtros exactos
    categoria = django_filters.NumberFilter(field_name='catproCod')
    proveedor = django_filters.NumberFilter(field_name='provCod')
    material = django_filters.ChoiceFilter(field_name='prodMate', choices=Product.MATERIAL_CHOICES)
    estado = django_filters.ChoiceFilter(field_name='prodEstado', choices=Product.STATUS_CHOICES)
    genero = django_filters.CharFilter(field_name='prodGenero')
    
    # Filtros de rango
    precio_min = django_filters.NumberFilter(field_name='prodPrecioVenta', lookup_expr='gte')
    precio_max = django_filters.NumberFilter(field_name='prodPrecioVenta', lookup_expr='lte')
    costo_min = django_filters.NumberFilter(field_name='prodCostoInv', lookup_expr='gte')
    costo_max = django_filters.NumberFilter(field_name='prodCostoInv', lookup_expr='lte')
    stock_min = django_filters.NumberFilter(field_name='prodStock', lookup_expr='gte')
    stock_max = django_filters.NumberFilter(field_name='prodStock', lookup_expr='lte')
    
    # Filtro booleano para stock bajo
    stock_bajo = django_filters.BooleanFilter(method='filter_stock_bajo')
    
    class Meta:
        model = Product
        fields = [
            'codigo', 'marca', 'descripcion',
            'categoria', 'proveedor', 'material', 'estado', 'genero',
            'precio_min', 'precio_max', 'costo_min', 'costo_max',
            'stock_min', 'stock_max', 'stock_bajo'
        ]
    
    def filter_stock_bajo(self, queryset, name, value):
        """Filtra productos con stock bajo o igual al minimo"""
        if value:
            from django.db.models import F
            return queryset.filter(prodStock__lte=F('prodStockMin'))
        return queryset