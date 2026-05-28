import django_filters
from django.utils import timezone
from datetime import timedelta
from .models import Client

class ClientFilter(django_filters.FilterSet):
    """Filtros personalizados para clientes"""
    
    # Filtro de tipo de documento
    cliTipoDoc = django_filters.ChoiceFilter(
        field_name='cliTipoDoc',
        choices=Client.TIPO_DOCUMENTO_CHOICES
    )
    
    # Filtros de edad (calculados desde fecha de nacimiento)
    edad_min = django_filters.NumberFilter(method='filter_edad_min')
    edad_max = django_filters.NumberFilter(method='filter_edad_max')
    
    class Meta:
        model = Client
        fields = ['cliTipoDoc', 'edad_min', 'edad_max']
    
    def filter_edad_min(self, queryset, name, value):
        """Filtra clientes con edad mayor o igual a la especificada"""
        if value is not None and value != '':
            try:
                edad = int(value)
                # Calcular la fecha máxima de nacimiento para tener al menos esa edad
                # Usamos 365.25 para considerar años bisiestos
                fecha_max_nacimiento = timezone.now().date() - timedelta(days=int(edad * 365.25))
                return queryset.filter(cliFechaNac__lte=fecha_max_nacimiento, cliFechaNac__isnull=False)
            except (ValueError, TypeError):
                pass
        return queryset
    
    def filter_edad_max(self, queryset, name, value):
        """Filtra clientes con edad menor o igual a la especificada"""
        if value is not None and value != '':
            try:
                edad = int(value)
                # Calcular la fecha mínima de nacimiento para tener como máximo esa edad
                # Usamos 365.25 para considerar años bisiestos
                fecha_min_nacimiento = timezone.now().date() - timedelta(days=int((edad + 1) * 365.25))
                return queryset.filter(cliFechaNac__gte=fecha_min_nacimiento, cliFechaNac__isnull=False)
            except (ValueError, TypeError):
                pass
        return queryset
