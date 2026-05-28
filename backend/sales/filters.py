import django_filters
from .models import Venta
from django.db.models import Q


class VentaFilter(django_filters.FilterSet):
    # Filtros de busqueda
    cliente_nombre = django_filters.CharFilter(method='filter_cliente_nombre')
    cliente_doc = django_filters.CharFilter(field_name='cliCod__cliNumDoc', lookup_expr='icontains')
    vendedor = django_filters.CharFilter(method='filter_vendedor')
    
    # Filtros de fecha
    fecha_desde = django_filters.DateFilter(field_name='ventFecha', lookup_expr='gte')
    fecha_hasta = django_filters.DateFilter(field_name='ventFecha', lookup_expr='lte')
    fecha_entrega = django_filters.DateFilter(field_name='ventFechaEntrega')
    
    # Filtros de estado
    estado = django_filters.ChoiceFilter(field_name='ventEstado', choices=Venta.ESTADO_VENTA)
    estado_pedido = django_filters.ChoiceFilter(field_name='ventEstadoRecoj', choices=Venta.ESTADO_PEDIDO)
    forma_pago = django_filters.ChoiceFilter(field_name='ventFormaPago', choices=Venta.FORMA_PAGO)
    
    # Filtros de monto
    total_min = django_filters.NumberFilter(field_name='ventTotal', lookup_expr='gte')
    total_max = django_filters.NumberFilter(field_name='ventTotal', lookup_expr='lte')
    
    # Filtros booleanos
    anuladas = django_filters.BooleanFilter(field_name='ventAnulada')
    con_saldo = django_filters.BooleanFilter(method='filter_con_saldo')
    
    class Meta:
        model = Venta
        fields = [
            'cliente_nombre', 'cliente_doc', 'vendedor',
            'fecha_desde', 'fecha_hasta', 'fecha_entrega',
            'estado', 'estado_pedido', 'forma_pago',
            'total_min', 'total_max', 'anuladas', 'con_saldo'
        ]
    
    def filter_cliente_nombre(self, queryset, name, value):
        """Buscar por nombre completo del cliente"""
        return queryset.filter(cliCod__cliNomCompleto__icontains=value)
    
    def filter_vendedor(self, queryset, name, value):
        """Buscar por username del vendedor"""
        return queryset.filter(
            Q(usuCod__usuNom__icontains=value) |
            Q(usuCod__usuNombreCom__icontains=value)
        )
    
    def filter_con_saldo(self, queryset, name, value):
        if value:
            return queryset.filter(ventSaldo__gt=0)
        return queryset.filter(ventSaldo=0)