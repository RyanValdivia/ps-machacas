from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from decimal import Decimal
from .models import Product, LunaMaterial, LunaTipo, LunaCaracteristica, LunaConfiguracion
from .serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateUpdateSerializer,
    LunaMaterialSerializer,
    LunaTipoSerializer,
    LunaCaracteristicaSerializer,
    LunaConfiguracionSerializer
)
from .filters import ProductFilter
from rest_framework.pagination import PageNumberPagination


class ProductPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProductViewSet(viewsets.ModelViewSet):
    pagination_class = ProductPagination

    queryset = Product.objects.select_related('catproCod', 'provCod').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    
    # Campos de busqueda para ?search=
    search_fields = ['prodCode', 'prodMarca', 'prodDescr', 'prodColor', 'prodTalla']
    
    # Campos permitidos para ordenar con ?ordering=
    ordering_fields = [
        'prodCode', 'prodMarca', 'prodPrecioVenta', 'prodCostoInv',
        'prodStock', 'created_at', 'updated_at'
    ]
    ordering = ['-created_at']  # Orden por defecto
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer

    def list(self, request, *args, **kwargs):
        """Override list para búsqueda solo por código con ordenamiento numérico natural"""
        from django.db.models import Q, Case, When, Value, IntegerField, CharField, F
        from django.db.models.functions import Length, Cast, Substr
        import re
        
        search_query = request.query_params.get('search', '').strip()
        
        if search_query:
            queryset = self.get_queryset()
            
            # Búsqueda SOLO por código - Exacto o que EMPIECE con el término
            search_filter = (
                Q(prodCode__iexact=search_query) |
                Q(prodCode__istartswith=search_query)
            )
            
            queryset = queryset.filter(search_filter)
            
            # Extraer letra y número para ordenamiento numérico
            queryset = queryset.annotate(
                # Prioridad de búsqueda
                search_priority=Case(
                    When(prodCode__iexact=search_query, then=Value(1)),
                    When(prodCode__istartswith=search_query, then=Value(2)),
                    default=Value(3),
                    output_field=IntegerField()
                ),
                # Longitud del código para ordenar primero los más cortos
                code_length=Length('prodCode')
            ).order_by('search_priority', 'code_length', 'prodCode')
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        
        return super().list(request, *args, **kwargs)


    @action(detail=False, methods=['get'])
    def monturas(self, request):
        monturas = self.get_queryset().filter(catproCod__catproCode='MO')
        
        # Aplicar filtros
        filterset = self.filter_queryset(monturas)
        
        page = self.paginate_queryset(filterset)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(filterset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def accesorios(self, request):
        accesorios = self.get_queryset().filter(catproCod__catproCode='AC')
        
        filterset = self.filter_queryset(accesorios)
        
        page = self.paginate_queryset(filterset)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(filterset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stock_bajo(self, request):
        from django.db.models import F
        productos = self.get_queryset().filter(prodStock__lte=F('prodStockMin'))
        
        serializer = ProductListSerializer(productos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Obtener estadísticas globales del inventario sin paginación
        GET /api/products/estadisticas/

        Solo cuenta productos con stock > 0
        """
        from django.db.models import F, Sum
        from decimal import Decimal
        
        queryset = self.get_queryset()
        
        # Total de productos con stock > 0
        total_products = queryset.filter(prodStock__gt=0).count()
        
        # Productos con stock bajo (stock <= stockMin Y stock > 0)
        low_stock_count = queryset.filter(
            prodStock__lte=F('prodStockMin'),
        ).count()
        
        # Valor total del inventario (costo * stock) solo productos con stock
        total_value = queryset.filter(prodStock__gt=0).aggregate(
            total=Sum(F('prodCostoInv') * F('prodStock'))
        )['total'] or Decimal('0.00')
        
        # Contar monturas con stock > 0 (categoría MO)
        montura_count = queryset.filter(
            catproCod__catproCode='MO',
            prodStock__gt=0
        ).count()
        
        return Response({
            'totalProducts': total_products,
            'lowStockCount': low_stock_count,
            'totalValue': float(total_value),
            'monturaCount': montura_count
        })
    
    @action(detail=True, methods=['post'])
    def ajustar_stock(self, request, pk=None):
        producto = self.get_object()
        cantidad = request.data.get('cantidad')
        tipo = request.data.get('tipo', 'entrada')
        
        if cantidad is None:
            return Response(
                {'error': 'Debes proporcionar la cantidad'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cantidad = int(cantidad)
        except ValueError:
            return Response(
                {'error': 'La cantidad debe ser un numero'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if tipo == 'entrada':
            producto.prodStock += cantidad
        elif tipo == 'salida':
            if producto.prodStock < cantidad:
                return Response(
                    {'error': 'Stock insuficiente'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            producto.prodStock -= cantidad
        else:
            return Response(
                {'error': 'Tipo debe ser "entrada" o "salida"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        producto.save()
        serializer = ProductDetailSerializer(producto)
        return Response(serializer.data)


# ==========================================
# ViewSets para Lunas Personalizadas
# ==========================================

class LunaMaterialViewSet(viewsets.ReadOnlyModelViewSet):
    """API para obtener materiales de lunas"""
    queryset = LunaMaterial.objects.all()
    serializer_class = LunaMaterialSerializer
    pagination_class = None  # Sin paginación para catálogos pequeños


class LunaTipoViewSet(viewsets.ReadOnlyModelViewSet):
    """API para obtener tipos de lunas"""
    queryset = LunaTipo.objects.all()
    serializer_class = LunaTipoSerializer
    pagination_class = None


class LunaCaracteristicaViewSet(viewsets.ReadOnlyModelViewSet):
    """API para obtener características de lunas"""
    queryset = LunaCaracteristica.objects.all()
    serializer_class = LunaCaracteristicaSerializer
    pagination_class = None


class LunaConfiguracionViewSet(viewsets.ReadOnlyModelViewSet):
    """API para configuraciones de lunas"""
    queryset = LunaConfiguracion.objects.select_related('lunMatCod', 'lunTipCod').all()
    serializer_class = LunaConfiguracionSerializer
    pagination_class = None
    
    @action(detail=False, methods=['get'])
    def buscar(self, request):
        """
        Buscar configuración por material y tipo
        GET /api/lunas/configuracion/buscar/?material=1&tipo=2
        """
        material_id = request.query_params.get('material')
        tipo_id = request.query_params.get('tipo')
        
        if not material_id or not tipo_id:
            return Response(
                {'error': 'Se requieren parámetros material y tipo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            config = LunaConfiguracion.objects.select_related(
                'lunMatCod', 'lunTipCod'
            ).get(lunMatCod_id=material_id, lunTipCod_id=tipo_id)
            
            serializer = self.get_serializer(config)
            return Response(serializer.data)
        except LunaConfiguracion.DoesNotExist:
            return Response(
                {'error': 'No se encontró configuración para esa combinación'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def calcular_precio(self, request):
        """
        Calcular precio total de una luna personalizada
        POST /api/lunas/configuracion/calcular_precio/
        Body: {
            "configuracion_id": 1,
            "caracteristicas_ids": [1, 3, 5]
        }
        """
        configuracion_id = request.data.get('configuracion_id')
        caracteristicas_ids = request.data.get('caracteristicas_ids', [])
        
        if not configuracion_id:
            return Response(
                {'error': 'Se requiere configuracion_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            config = LunaConfiguracion.objects.get(pk=configuracion_id)
            precio_base = config.lunConfPrecioBase
            
            # Sumar precios adicionales de características
            precio_adicional = Decimal('0.00')
            if caracteristicas_ids:
                caracteristicas = LunaCaracteristica.objects.filter(
                    lunCarCod__in=caracteristicas_ids
                )
                precio_adicional = sum(
                    c.lunCarPrecioAdicional for c in caracteristicas
                )
            
            precio_total = precio_base + precio_adicional
            
            return Response({
                'precio_base': float(precio_base),
                'precio_adicional': float(precio_adicional),
                'precio_total': float(precio_total)
            })
        except LunaConfiguracion.DoesNotExist:
            return Response(
                {'error': 'Configuración no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def producto_dummy(self, request):
        """
        Obtener el producto dummy para lunas personalizadas
        GET /api/lunas/configuracion/producto_dummy/
        """
        try:
            # Buscar por código primero (más específico)
            producto = Product.objects.get(prodCode='LUNA-PERS')
        except Product.DoesNotExist:
            # Si no existe, buscar por categoría
            try:
                producto = Product.objects.filter(
                    catproCod__catproCode='LUNA'
                ).first()
                if not producto:
                    return Response(
                        {'error': 'Producto dummy de lunas no encontrado'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            except Exception:
                return Response(
                    {'error': 'Error buscando producto dummy'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        serializer = ProductDetailSerializer(producto)
        return Response(serializer.data)