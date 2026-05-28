from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.db.models import Q
from decimal import Decimal
from datetime import timedelta

from .models import Venta, VentaDetalle, Comprobante
from clients.models import Client
from .serializers import (
    VentaListSerializer,
    VentaDetailSerializer,
    VentaCreateSerializer,
    VentaUpdateSerializer,
    VentaDetalleSerializer,
    VentaDetalleCreateSerializer,
    PagoSerializer,
    ComprobanteSerializer
)
from .filters import VentaFilter

from rest_framework.pagination import PageNumberPagination

class VentaPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class VentaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para ventas
    
    Endpoints:
    - GET /api/ventas/ - Listar ventas
    - GET /api/ventas/{id}/ - Detalle de venta
    - POST /api/ventas/ - Crear venta
    - PUT /api/ventas/{id}/ - Actualizar venta
    - PATCH /api/ventas/{id}/ - Actualizar parcial
    - DELETE /api/ventas/{id}/ - Eliminar venta
    
    Filtros:
    - ?cliente_nombre=Juan
    - ?cliente_doc=12345678
    - ?vendedor=usuario
    - ?fecha_desde=2024-01-01
    - ?fecha_hasta=2024-12-31
    - ?estado=PAGADO
    - ?estado_pedido=ENTREGADO
    - ?forma_pago=EFECTIVO
    - ?total_min=100
    - ?total_max=1000
    - ?anuladas=false
    - ?con_saldo=true
    - ?search=busqueda (busca en ventCod, cliente, documento, vendedor)
    - ?ordering=-ventFecha
    """
    
    queryset = Venta.objects.select_related('cliCod', 'usuCod', 'cajaAperCod').prefetch_related('ventadetalle_set__prodCod').all()
    pagination_class = VentaPagination
    permission_classes = [IsAuthenticated]
    # ✅ REMOVIDO SearchFilter - solo usamos DjangoFilterBackend
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = VentaFilter
    
    # Campos de ordenamiento
    ordering_fields = ['ventFecha', 'ventTotal', 'ventEstado', 'ventEstadoRecoj']
    ordering = ['-ventFecha']
    
    def get_queryset(self):
        """
        Personaliza el queryset para búsqueda en múltiples campos
        """
        queryset = super().get_queryset()
        
        # Búsqueda personalizada usando el parámetro 'search'
        search = self.request.query_params.get('search', None)
        if search:
            # ✅ CORREGIDO: usuNom en lugar de username
            queryset = queryset.filter(
                Q(ventCod__icontains=search) |
                Q(cliCod__cliNomCompleto__icontains=search) |
                Q(cliCod__cliNumDoc__icontains=search) |
                Q(usuCod__usuNom__icontains=search) |
                Q(usuCod__usuNombreCom__icontains=search)
            ).distinct()
        
        return queryset
    
    def get_serializer_class(self):
        """Usa diferentes serializers segun la accion"""
        if self.action == 'list':
            return VentaListSerializer
        elif self.action == 'create':
            return VentaCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return VentaUpdateSerializer
        return VentaDetailSerializer
    
    @action(detail=True, methods=['post'])
    def registrar_pago(self, request, pk=None):
        """
        Registra un pago para la venta
        POST /api/ventas/{id}/registrar_pago/
        
        Body:
        {
            "monto": 100.00,
            "forma_pago": "EFECTIVO",
            "referencia_pago": "opcional",
            "tarjeta_tipo": "opcional"
        }
        """
        venta = self.get_object()
        serializer = PagoSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                resultado = venta.registrar_pago(
                    monto=serializer.validated_data['monto'],
                    forma_pago=serializer.validated_data['forma_pago'],
                    referencia_pago=serializer.validated_data.get('referencia_pago', ''),
                    tarjeta_tipo=serializer.validated_data.get('tarjeta_tipo', '')
                )
                
                # Actualizar el resultado con la venta completa
                venta.refresh_from_db()
                venta_serializer = VentaDetailSerializer(venta)
                resultado['venta'] = venta_serializer.data
                
                return Response(resultado, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def anular(self, request, pk=None):
        """
        Anula la venta
        POST /api/ventas/{id}/anular/
        
        Body:
        {
            "motivo": "Motivo de anulacion"
        }
        """
        venta = self.get_object()
        motivo = request.data.get('motivo', '')
        
        if not motivo:
            return Response(
                {'error': 'Debe proporcionar un motivo de anulacion'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            venta.anular_venta(motivo)
            serializer = self.get_serializer(venta)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def marcar_listo(self, request, pk=None):
        """
        Marca la venta como lista para recoger
        POST /api/ventas/{id}/marcar_listo/
        """
        venta = self.get_object()
        
        try:
            venta.marcar_listo_para_recoger()
            serializer = self.get_serializer(venta)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def marcar_entregado(self, request, pk=None):
        """
        Marca la venta como entregada
        POST /api/ventas/{id}/marcar_entregado/
        """
        venta = self.get_object()
        
        try:
            venta.marcar_entregado()
            serializer = self.get_serializer(venta)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        """
        Ventas pendientes de pago
        GET /api/ventas/pendientes/
        """
        ventas = self.get_queryset().filter(ventEstado__in=['PENDIENTE', 'PARCIAL'], ventAnulada=False)
        page = self.paginate_queryset(ventas)
        
        if page is not None:
            serializer = VentaListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = VentaListSerializer(ventas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def del_dia(self, request):
        """
        Ventas del dia actual
        GET /api/ventas/del_dia/
        """
        from django.utils import timezone
        hoy = timezone.now().date()
        
        ventas = self.get_queryset().filter(
            ventFecha__date=hoy,
            ventAnulada=False
        )
        
        serializer = VentaListSerializer(ventas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def estadisticas_dashboard(self, request):
        """
        Estadísticas COMPLETAS para el dashboard
        GET /api/ventas/estadisticas_dashboard/
        
        Query params:
        - periodo: 'dia', 'semana', 'mes', 'personalizado' (default: 'mes')
        - fecha_desde: YYYY-MM-DD (si periodo=personalizado)
        - fecha_hasta: YYYY-MM-DD (si periodo=personalizado)
        
        Retorna:
        - Ganancias por período (día, semana, mes)
        - Costos por proveedor (productos + lunas)
        - Top productos más vendidos
        - Ventas pendientes de pago
        - Estadísticas de lunas
        - Comparativas con períodos anteriores
        """
        from django.utils import timezone
        from django.db.models import Sum, Count, F, Q, Avg, DecimalField
        from django.db.models.functions import TruncDate, Coalesce
        from decimal import Decimal
        from datetime import datetime, timedelta
        from suppliers.models import Supplier
        from products.models import Product
        
        try:
            # ==================== 1. DETERMINAR PERÍODO ====================
            periodo = request.query_params.get('periodo', 'mes')
            # Usar localtime() para obtener la fecha en la zona horaria configurada (America/Lima)
            hoy = timezone.localtime(timezone.now()).date()
            
            print(f"🔍 DASHBOARD - Período solicitado: {periodo}")
            print(f"📅 Fecha de hoy (Lima): {hoy}")
            
            if periodo == 'dia':
                fecha_desde = hoy
                fecha_hasta = hoy
                fecha_desde_anterior = hoy - timedelta(days=1)
                fecha_hasta_anterior = hoy - timedelta(days=1)
            elif periodo == 'semana':
                fecha_desde = hoy - timedelta(days=hoy.weekday())  # Lunes
                fecha_hasta = hoy
                fecha_desde_anterior = fecha_desde - timedelta(days=7)
                fecha_hasta_anterior = fecha_hasta - timedelta(days=7)
            elif periodo == 'mes':
                fecha_desde = hoy.replace(day=1)
                fecha_hasta = hoy
                # Mes anterior
                primer_dia_mes_anterior = (fecha_desde - timedelta(days=1)).replace(day=1)
                ultimo_dia_mes_anterior = fecha_desde - timedelta(days=1)
                fecha_desde_anterior = primer_dia_mes_anterior
                fecha_hasta_anterior = ultimo_dia_mes_anterior
            else:  # personalizado
                fecha_desde_str = request.query_params.get('fecha_desde')
                fecha_hasta_str = request.query_params.get('fecha_hasta')
                if fecha_desde_str and fecha_hasta_str:
                    fecha_desde = datetime.strptime(fecha_desde_str, '%Y-%m-%d').date()
                    fecha_hasta = datetime.strptime(fecha_hasta_str, '%Y-%m-%d').date()
                    dias_diferencia = (fecha_hasta - fecha_desde).days + 1
                    fecha_desde_anterior = fecha_desde - timedelta(days=dias_diferencia)
                    fecha_hasta_anterior = fecha_desde - timedelta(days=1)
                else:
                    # Default a mes actual
                    fecha_desde = hoy.replace(day=1)
                    fecha_hasta = hoy
                    fecha_desde_anterior = (fecha_desde - timedelta(days=1)).replace(day=1)
                    fecha_hasta_anterior = fecha_desde - timedelta(days=1)
            
            print(f"📊 Período actual: {fecha_desde} a {fecha_hasta}")
            print(f"📊 Período anterior: {fecha_desde_anterior} a {fecha_hasta_anterior}")
            
            # ==================== 2. VENTAS DEL PERÍODO ACTUAL ====================
            ventas_periodo = Venta.objects.filter(
                ventFecha__date__gte=fecha_desde,
                ventFecha__date__lte=fecha_hasta,
                ventAnulada=False
            )
            
            print(f"🔍 Total ventas encontradas en período: {ventas_periodo.count()}")
            
            ventas_periodo_anterior = Venta.objects.filter(
                ventFecha__date__gte=fecha_desde_anterior,
                ventFecha__date__lte=fecha_hasta_anterior,
                ventAnulada=False
            )
            
            # ==================== 3. GANANCIAS GENERALES ====================
            # Total de ingresos
            ingresos_periodo = ventas_periodo.aggregate(total=Sum('ventTotal'))['total'] or Decimal('0')
            ingresos_anterior = ventas_periodo_anterior.aggregate(total=Sum('ventTotal'))['total'] or Decimal('0')
            
            # Cantidad de ventas
            cantidad_ventas = ventas_periodo.count()
            cantidad_ventas_anterior = ventas_periodo_anterior.count()
            
            # Ticket promedio
            ticket_promedio = ingresos_periodo / cantidad_ventas if cantidad_ventas > 0 else Decimal('0')
            
            # Variación porcentual
            variacion_ingresos = ((ingresos_periodo - ingresos_anterior) / ingresos_anterior * 100) if ingresos_anterior > 0 else Decimal('0')
            variacion_cantidad = ((cantidad_ventas - cantidad_ventas_anterior) / cantidad_ventas_anterior * 100) if cantidad_ventas_anterior > 0 else Decimal('0')
            
            # ==================== 4. COSTOS Y GANANCIAS POR PROVEEDOR ====================
            # Diccionario para consolidar egresos
            egresos_dict = {}
            
            # 4.1 Egresos por productos vendidos (EXCLUIR lunas personalizadas)
            detalles_productos = VentaDetalle.objects.filter(
                ventCod__in=ventas_periodo,
                prodCod__isnull=False,
                ventDetAnulado=False,
                prodCod__provCod__isnull=False,
                esLunaPersonalizada=False  # EXCLUIR lunas para evitar duplicados
            ).select_related('prodCod__provCod')
            
            print(f"🔍 Detalles de productos encontrados: {detalles_productos.count()}")
            
            for detalle in detalles_productos:
                prov_id = detalle.prodCod.provCod.provCod
                prov_nombre = detalle.prodCod.provCod.provRazSocial
                costo_unitario = detalle.prodCod.prodCostoInv
                cantidad = detalle.ventDetCantidad
                costo_total = costo_unitario * cantidad
                precio_venta = detalle.ventDetSubtotal
                
                if prov_id not in egresos_dict:
                    egresos_dict[prov_id] = {
                        'proveedor_id': prov_id,
                        'proveedor_nombre': prov_nombre,
                        'costo_productos': Decimal('0'),
                        'venta_productos': Decimal('0'),
                        'cantidad_productos': 0,
                        'costo_lunas': Decimal('0'),
                        'venta_lunas': Decimal('0'),
                        'cantidad_lunas': 0,
                    }
                
                egresos_dict[prov_id]['costo_productos'] += costo_total
                egresos_dict[prov_id]['venta_productos'] += Decimal(str(precio_venta))
                egresos_dict[prov_id]['cantidad_productos'] += cantidad
            
            # 4.2 Egresos por lunas personalizadas
            detalles_lunas = VentaDetalle.objects.filter(
                ventCod__in=ventas_periodo,
                esLunaPersonalizada=True,
                lunaLaboratorio__isnull=False,
                lunaCostoLaboratorio__isnull=False,
                ventDetAnulado=False
            ).select_related('lunaLaboratorio')
            
            print(f"🔍 Detalles de lunas personalizadas encontrados: {detalles_lunas.count()}")
            
            for detalle in detalles_lunas:
                prov_id = detalle.lunaLaboratorio.provCod
                prov_nombre = detalle.lunaLaboratorio.provRazSocial
                costo = detalle.lunaCostoLaboratorio or Decimal('0')
                precio_venta = detalle.ventDetSubtotal
                
                if prov_id not in egresos_dict:
                    egresos_dict[prov_id] = {
                        'proveedor_id': prov_id,
                        'proveedor_nombre': prov_nombre,
                        'costo_productos': Decimal('0'),
                        'venta_productos': Decimal('0'),
                        'cantidad_productos': 0,
                        'costo_lunas': Decimal('0'),
                        'venta_lunas': Decimal('0'),
                        'cantidad_lunas': 0,
                    }
                
                egresos_dict[prov_id]['costo_lunas'] += costo
                egresos_dict[prov_id]['venta_lunas'] += Decimal(str(precio_venta))
                egresos_dict[prov_id]['cantidad_lunas'] += detalle.ventDetCantidad
            
            # Calcular totales y ganancias
            proveedores_stats = []
            total_costos = Decimal('0')
            total_ganancias = Decimal('0')
            
            for prov_id, data in egresos_dict.items():
                costo_total = data['costo_productos'] + data['costo_lunas']
                venta_total = data['venta_productos'] + data['venta_lunas']
                ganancia = venta_total - costo_total
                margen = (ganancia / venta_total * 100) if venta_total > 0 else Decimal('0')
                
                total_costos += costo_total
                total_ganancias += ganancia
                
                proveedores_stats.append({
                    'proveedor_id': prov_id,
                    'proveedor_nombre': data['proveedor_nombre'],
                    'costo_productos': float(data['costo_productos']),
                    'venta_productos': float(data['venta_productos']),
                    'cantidad_productos': data['cantidad_productos'],
                    'costo_lunas': float(data['costo_lunas']),
                    'venta_lunas': float(data['venta_lunas']),
                    'cantidad_lunas': data['cantidad_lunas'],
                    'costo_total': float(costo_total),
                    'venta_total': float(venta_total),
                    'ganancia': float(ganancia),
                    'margen_porcentaje': float(margen)
                })
            
            # Ordenar por ganancia descendente
            proveedores_stats.sort(key=lambda x: x['ganancia'], reverse=True)
            
            # ==================== 5. TOP PRODUCTOS MÁS VENDIDOS ====================
            top_productos = VentaDetalle.objects.filter(
                ventCod__in=ventas_periodo,
                ventDetAnulado=False,
                esLunaPersonalizada=False,
                prodCod__isnull=False
            ).values(
                'prodCod__prodDescr',
                'prodCod__prodMarca',
                'prodCod__prodCode'
            ).annotate(
                cantidad_vendida=Sum('ventDetCantidad'),
                total_ingresos=Sum('ventDetSubtotal')
            ).order_by('-cantidad_vendida')[:10]
            
            # ==================== 6. ESTADÍSTICAS DE LUNAS ====================
            total_lunas = VentaDetalle.objects.filter(
                ventCod__ventAnulada=False,
                esLunaPersonalizada=True,
                ventDetAnulado=False
            ).count()
            
            lunas_con_laboratorio = VentaDetalle.objects.filter(
                ventCod__ventAnulada=False,
                esLunaPersonalizada=True,
                ventDetAnulado=False,
                lunaLaboratorio__isnull=False
            ).count()
            
            lunas_pendientes = total_lunas - lunas_con_laboratorio
            
            # ==================== 7. VENTAS PENDIENTES DE PAGO ====================
            ventas_pendientes_qs = ventas_periodo.filter(
                Q(ventEstado='PENDIENTE') | Q(ventEstado='PARCIAL')
            ).select_related('cliCod')
            
            ventas_pendientes_stats = {
                'cantidad': ventas_pendientes_qs.count(),
                'saldo_total': ventas_pendientes_qs.aggregate(total=Sum('ventSaldo'))['total'] or Decimal('0')
            }
            
            # Lista de ventas pendientes con detalles
            from sales.serializers import VentaListSerializer
            ventas_pendientes_list = VentaListSerializer(ventas_pendientes_qs[:20], many=True).data
            
            # ==================== 8. VENTAS POR DÍA (PARA GRÁFICO) ====================
            ventas_por_dia = ventas_periodo.annotate(
                fecha=TruncDate('ventFecha')
            ).values('fecha').annotate(
                total=Sum('ventTotal'),
                cantidad=Count('ventCod')
            ).order_by('fecha')
            
            # ==================== 9. VENTAS POR VENDEDOR ====================
            ventas_vendedor = ventas_periodo.values(
                'usuCod__usuCod',
                'usuCod__usuNombreCom'
            ).annotate(
                cantidad_ventas=Count('ventCod'),
                total_vendido=Sum('ventTotal'),
                promedio_venta=Avg('ventTotal')
            ).order_by('-total_vendido')
            
            ventas_vendedor_list = [
                {
                    'vendedor_id': item['usuCod__usuCod'],
                    'vendedor_nombre': item['usuCod__usuNombreCom'],
                    'cantidad_ventas': item['cantidad_ventas'],
                    'total_vendido': float(item['total_vendido'] or 0),
                    'promedio_venta': float(item['promedio_venta'] or 0)
                }
                for item in ventas_vendedor
            ]
            
            # ==================== 10. VENTAS POR CAJA ====================
            ventas_caja = ventas_periodo.values(
                'cajaAperCod__cajCod__cajCod',
                'cajaAperCod__cajCod__cajNom'
            ).annotate(
                cantidad_ventas=Count('ventCod'),
                total_ventas=Sum('ventTotal')
            ).order_by('-total_ventas')
            
            # Calcular total para porcentaje de participación
            total_ventas_cajas = sum(item['total_ventas'] or 0 for item in ventas_caja)
            
            ventas_caja_list = [
                {
                    'caja_id': item['cajaAperCod__cajCod__cajCod'],
                    'caja_nombre': item['cajaAperCod__cajCod__cajNom'] or 'Sin caja',
                    'cantidad_ventas': item['cantidad_ventas'],
                    'total_ventas': float(item['total_ventas'] or 0),
                    'porcentaje_participacion': float((item['total_ventas'] or 0) / total_ventas_cajas * 100) if total_ventas_cajas > 0 else 0
                }
                for item in ventas_caja
            ]
            
            # ==================== 11. RESUMEN FINAL ====================
            margen_general = (total_ganancias / ingresos_periodo * 100) if ingresos_periodo > 0 else Decimal('0')
            
            # ==================== 12. VENTAS PENDIENTES DE ENTREGA ====================
            # Ventas LISTAS para entregar
            ventas_listas = ventas_periodo.filter(
                ventEstadoRecoj='LISTO'
            ).select_related('cliCod').order_by('-ventFecha')[:30]
            
            ventas_listas_data = []
            for venta in ventas_listas:
                # Obtener productos de la venta
                detalles = venta.ventadetalle_set.select_related('prodCod').all()[:3]
                productos_str = ', '.join([d.prodCod.prodDescr for d in detalles if d.prodCod])
                if venta.ventadetalle_set.count() > 3:
                    productos_str += '...'
                
                ventas_listas_data.append({
                    'ventCod': venta.ventCod,
                    'ventFecha': venta.ventFecha.isoformat(),
                    'cliCod__cliNombreCom': venta.cliCod.cliNomCompleto if venta.cliCod else 'Sin cliente',
                    'ventTotal': float(venta.ventTotal),
                    'ventSaldo': float(venta.ventSaldo),
                    'ventEstadoRecoj': venta.ventEstadoRecoj,
                    'productos': productos_str
                })
            
            # Ventas PENDIENTES (aún no listas)
            ventas_pendientes = ventas_periodo.filter(
                ventEstadoRecoj='PENDIENTE'
            ).select_related('cliCod').order_by('-ventFecha')[:30]
            
            ventas_pendientes_data = []
            for venta in ventas_pendientes:
                # Obtener productos de la venta
                detalles = venta.ventadetalle_set.select_related('prodCod').all()[:3]
                productos_str = ', '.join([d.prodCod.prodDescr for d in detalles if d.prodCod])
                if venta.ventadetalle_set.count() > 3:
                    productos_str += '...'
                
                ventas_pendientes_data.append({
                    'ventCod': venta.ventCod,
                    'ventFecha': venta.ventFecha.isoformat(),
                    'cliCod__cliNombreCom': venta.cliCod.cliNomCompleto if venta.cliCod else 'Sin cliente',
                    'ventTotal': float(venta.ventTotal),
                    'ventSaldo': float(venta.ventSaldo),
                    'ventEstadoRecoj': venta.ventEstadoRecoj,
                    'productos': productos_str
                })
            
            return Response({
                'periodo': {
                    'tipo': periodo,
                    'fecha_desde': str(fecha_desde),
                    'fecha_hasta': str(fecha_hasta),
                    'dias': (fecha_hasta - fecha_desde).days + 1
                },
                'resumen_general': {
                    'ingresos_totales': float(ingresos_periodo),
                    'costos_totales': float(total_costos),
                    'ganancias_totales': float(total_ganancias),
                    'margen_general': float(margen_general),
                    'cantidad_ventas': cantidad_ventas,
                    'ticket_promedio': float(ticket_promedio),
                    'variacion_ingresos': float(variacion_ingresos),
                    'variacion_cantidad': float(variacion_cantidad)
                },
                'proveedores': proveedores_stats,
                'top_productos': list(top_productos),
                'estadisticas_lunas': {
                    'total_lunas': total_lunas,
                    'lunas_con_laboratorio': lunas_con_laboratorio,
                    'lunas_pendientes': lunas_pendientes,
                    'porcentaje_completado': round((lunas_con_laboratorio / total_lunas * 100) if total_lunas > 0 else 0, 2)
                },
                'ventas_pendientes': {
                    'cantidad': ventas_pendientes_stats['cantidad'],
                    'saldo_total': float(ventas_pendientes_stats['saldo_total']),
                    'ventas': ventas_pendientes_list
                },
                'ventas_por_dia': [
                    {
                        'fecha': item['fecha'].strftime('%Y-%m-%d'),
                        'total': float(item['total']),
                        'cantidad': item['cantidad']
                    }
                    for item in ventas_por_dia
                ],
                'ventas_vendedor': ventas_vendedor_list,
                'ventas_caja': ventas_caja_list,
                'ventas_listas': ventas_listas_data,
                'ventas_pendientes': ventas_pendientes_data
            })
            
        except Exception as e:
            import traceback
            print("ERROR en estadisticas_dashboard:", str(e))
            traceback.print_exc()
            return Response({
                'error': str(e),
                'detail': 'Error al generar estadísticas'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def comprobante(self, request, pk=None):
        """
        Obtiene el comprobante de la venta
        GET /api/ventas/{id}/comprobante/
        """
        venta = self.get_object()
        
        if not hasattr(venta, 'comprobante'):
            return Response(
                {'error': 'La venta no tiene comprobante generado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ComprobanteSerializer(venta.comprobante)
        return Response(serializer.data)


    def create(self, request, *args, **kwargs):
        """
        Crea una venta, buscando o creando el cliente automáticamente
        """
        try:
            with transaction.atomic():
                # Obtener datos del cliente desde el request
                cliente_data = request.data.get('cliente', {})
                doc_tipo = cliente_data.get('cliDocTipo', 'DNI')
                doc_num = cliente_data.get('cliDocNum', '').strip()
                nombre_completo = cliente_data.get('cliNomCompleto', '').strip()
                
                cliente = None
                cliente_creado = False
                
                # ✅ CASO 1: Si tiene documento (y no es vacío), buscar o crear con documento
                if doc_num and len(doc_num) > 0:
                    try:
                        # Intentar encontrar cliente existente
                        cliente = Client.objects.get(
                            cliTipoDoc=doc_tipo,
                            cliNumDoc=doc_num
                        )
                    
                    except Client.DoesNotExist:
                        # Crear nuevo cliente solo si tiene nombre
                        if nombre_completo:
                            cliente = Client.objects.create(
                                cliTipoDoc=doc_tipo,
                                cliNumDoc=doc_num,
                                cliNomCompleto=nombre_completo.upper().strip(),
                                cliTelef=cliente_data.get('cliTelef', ''),
                            )
                            cliente_creado = True
                
                # ✅ CASO 2: Si NO tiene documento pero SÍ tiene nombre, crear cliente sin documento
                elif nombre_completo:
                    cliente = Client.objects.create(
                        cliTipoDoc=None,
                        cliNumDoc=None,
                        cliNomCompleto=nombre_completo.upper().strip(),
                        cliTelef=cliente_data.get('cliTelef', ''),
                    )
                    cliente_creado = True
                
                # ✅ CASO 3: Si no tiene ni documento ni nombre → cliente queda None (Cliente Generico)
                
                # Preparar datos de la venta
                venta_data = {
                    'cliCod': cliente.cliCod if cliente else None,
                    'ventObservaciones': request.data.get('ventObservaciones', ''),
                    'ventFormaPago': request.data.get('ventFormaPago', 'EFECTIVO'),
                    'ventReferenciaPago': request.data.get('ventReferenciaPago', ''),
                    'ventTarjetaTipo': request.data.get('ventTarjetaTipo', ''),
                    'ventAdelanto': Decimal(str(request.data.get('ventAdelanto', 0))),
                    'detalles': request.data.get('detalles', [])
                }
                
                # Usar el serializer para crear la venta
                serializer = VentaCreateSerializer(
                    data=venta_data,
                    context={'request': request}
                )
                serializer.is_valid(raise_exception=True)
                venta = serializer.save()
                
                # Respuesta con información adicional
                response_serializer = VentaDetailSerializer(venta)
                return Response({
                    'venta': response_serializer.data,
                    'cliente_creado': cliente_creado,
                    'cliente_id': cliente.cliCod if cliente else None,
                    'mensaje': 'Venta creada exitosamente'
                }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class VentaDetalleViewSet(viewsets.ModelViewSet):
    """
    ViewSet para detalles de venta
    """
    queryset = VentaDetalle.objects.select_related('ventCod', 'prodCod').all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return VentaDetalleCreateSerializer
        return VentaDetalleSerializer
    
    @action(detail=True, methods=['post'])
    def anular_detalle(self, request, pk=None):
        """
        Anula un detalle de venta
        POST /api/ventas-detalle/{id}/anular_detalle/
        """
        detalle = self.get_object()
        
        if detalle.ventDetAnulado:
            return Response(
                {'error': 'El detalle ya esta anulado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                detalle.devolver_stock()
                detalle.ventDetAnulado = True
                detalle.save()
                
                # Recalcular totales de la venta
                detalle.ventCod.calcular_totales()
                detalle.ventCod.save()
            
            serializer = self.get_serializer(detalle)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['patch'])
    def actualizar_laboratorio(self, request, pk=None):
        """
        Actualiza los datos del laboratorio de una luna personalizada
        PATCH /api/ventas-detalle/{id}/actualizar_laboratorio/
        
        Body:
        {
            "lunaLaboratorio": 5,  // ID del proveedor
            "lunaCostoLaboratorio": 150.00
        }
        """
        detalle = self.get_object()
        
        if detalle.ventDetAnulado:
            return Response(
                {'error': 'No se puede actualizar un detalle anulado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not detalle.esLunaPersonalizada:
            return Response(
                {'error': 'Solo se pueden actualizar datos de laboratorio en lunas personalizadas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from suppliers.models import Supplier
            from django.db import models
            
            laboratorio_id = request.data.get('lunaLaboratorio')
            costo = request.data.get('lunaCostoLaboratorio')
            
            # Validar y asignar laboratorio (ahora es ForeignKey)
            if laboratorio_id:
                try:
                    laboratorio = Supplier.objects.get(pk=laboratorio_id, provEstado='Active')
                except Supplier.DoesNotExist:
                    return Response(
                        {'error': 'Proveedor no encontrado o inactivo'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                laboratorio = None
            
            # Preparar campos para actualizar
            update_fields = {}
            if laboratorio_id:
                update_fields['lunaLaboratorio'] = laboratorio
            if costo is not None:
                update_fields['lunaCostoLaboratorio'] = Decimal(str(costo))
            
            # Usar update directo para evitar validaciones de caja
            VentaDetalle.objects.filter(pk=detalle.pk).update(**update_fields)
            
            # Recargar el objeto actualizado
            detalle.refresh_from_db()
            
            serializer = self.get_serializer(detalle)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# ==================== ENDPOINTS DE IMPRESIÓN ====================
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .printer import ImpresoraTermica


@csrf_exempt
@require_http_methods(["POST"])
def imprimir_ticket(request):
    """
    API endpoint para imprimir tickets
    
    POST /api/sales/imprimir/
    Body: {
        "venta_id": 123,  // Opcional: si se envía, busca la venta en BD
        "folio": "001234",
        "fecha": "2024-02-06 15:30",
        "productos": [...],
        "total": 100.00,
        ...
    }
    """
    try:
        # Parsear datos
        datos_request = json.loads(request.body)
        
        # Si viene venta_id, buscar la venta en BD
        if datos_request.get('venta_id'):
            try:
                venta = Venta.objects.get(ventCod=datos_request['venta_id'])
                
                # Construir datos desde la venta en BD
                datos_venta = {
                    'folio': str(venta.ventCod),
                    'fecha': venta.ventFecha.strftime('%Y-%m-%d %H:%M:%S') if venta.ventFecha else '',
                    'vendedor': venta.usuCod.usuNombreCom if venta.usuCod else '',
                    'cliente': venta.cliCod.cliNomCompleto if venta.cliCod else 'Cliente General',
                    'productos': [],
                    'subtotal': float(venta.ventSubTotal),
                    'descuento': float(venta.ventDescuento),
                    'total': float(venta.ventTotal),
                    'adelanto': float(venta.ventAdelanto or 0),
                    'saldo': float(venta.ventSaldo or 0),
                    'metodo_pago': venta.ventFormaPago or '',
                    'referencia_pago': venta.ventReferenciaPago or '',
                    'observaciones': venta.ventObservaciones or ''
                }
                
                # Agregar detalles
                for detalle in venta.ventadetalle_set.all():
                    # Construir nombre del producto con detalles de luna si es personalizada
                    nombre_producto = detalle.prodCod.prodDescr if detalle.prodCod else 'Producto'
                    
                    if detalle.esLunaPersonalizada:
                        # Para lunas personalizadas, solo decir "LUNAS"
                        nombre_producto = "LUNAS"
                        
                        detalles_luna = []
                        if detalle.lunaMaterial:
                            detalles_luna.append(detalle.lunaMaterial)
                        if detalle.lunaTipo:
                            detalles_luna.append(detalle.lunaTipo)
                        if detalle.lunaCaracteristicas:
                            detalles_luna.append(detalle.lunaCaracteristicas)
                        
                        if detalles_luna:
                            nombre_producto = f"{nombre_producto}\n{', '.join(detalles_luna)}"
                    
                    producto = {
                        'cantidad': detalle.ventDetCantidad,
                        'nombre': nombre_producto,
                        'precio_unitario': float(detalle.ventDetPrecioUni),
                        'subtotal': float(detalle.ventDetSubtotal),
                        'descuento': float(detalle.ventDetDescuento)
                    }
                    datos_venta['productos'].append(producto)
                    
            except Venta.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Venta no encontrada'
                }, status=404)
        else:
            # Usar datos enviados directamente
            datos_venta = datos_request
        
        # Validar datos mínimos
        if not datos_venta.get('productos'):
            return JsonResponse({
                'success': False,
                'error': '📋 No hay productos para imprimir',
                'sugerencia': 'No se puede imprimir un ticket sin productos'
            }, status=400)
        
        if not datos_venta.get('total'):
            return JsonResponse({
                'success': False,
                'error': '💰 Falta el total de la venta',
                'sugerencia': 'No se puede imprimir un ticket sin total'
            }, status=400)
        
        # Crear instancia de impresora
        # NOTA: Cambia "ADVANCE 8010" por el nombre exacto de tu impresora
        try:
            impresora = ImpresoraTermica(nombre_impresora="ADVANCE 8010")
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': '❌ Error al inicializar impresora',
                'sugerencia': f'No se pudo conectar con la impresora: {str(e)}',
                'tipo_error': 'ERROR_INICIALIZACION'
            }, status=500)
        
        # Imprimir
        resultado = impresora.imprimir_ticket_venta(datos_venta)
        
        # Retornar resultado con código apropiado
        if resultado['success']:
            return JsonResponse(resultado, status=200)
        else:
            # Error de impresión pero no es error del servidor
            # La venta ya está guardada, solo falló la impresión
            return JsonResponse(resultado, status=200)  # 200 porque la operación se completó, solo falló la impresión
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '📝 Formato de datos incorrecto',
            'sugerencia': 'Los datos enviados no son válidos. Contacta a soporte técnico.'
        }, status=400)
    except Venta.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '🔍 Venta no encontrada',
            'sugerencia': 'No se encontró la venta en el sistema. Verifica el número de venta.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': '❌ Error inesperado',
            'sugerencia': f'Ocurrió un error: {str(e)}\n\nContacta a soporte técnico si el problema persiste.',
            'tipo_error': 'ERROR_SISTEMA'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def test_impresora(request):
    """
    Endpoint de prueba para verificar conexión con impresora
    
    GET /api/sales/imprimir/test/
    """
    try:
        impresora = ImpresoraTermica(nombre_impresora="ADVANCE 8010")
        resultado = impresora.test_impresora()
        
        # Siempre devolver 200 para que el frontend pueda manejar el error
        return JsonResponse(resultado, status=200)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': '❌ Error al inicializar impresora',
            'sugerencia': f'No se pudo conectar con la impresora: {str(e)}\n\n' +
                        '📝 Verifica:\n' +
                        '1. Que la impresora esté encendida\n' +
                        '2. Que esté conectada al computador\n' +
                        '3. El nombre de la impresora en la configuración',
            'tipo_error': 'ERROR_INICIALIZACION'
        }, status=200)
