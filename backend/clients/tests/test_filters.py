import pytest
from django.utils import timezone
from datetime import timedelta
from clients.models import Client
from clients.filters import ClientFilter

# Tests de ClientFilter (django-filter) para el endpoint de clientes.
# Cubre: filtro directo por cliTipoDoc (DNI/RUC), filtros calculados edad_min/edad_max
# (derivan la fecha de nacimiento límite a partir de la edad y comparan contra
# cliFechaNac), y el manejo defensivo de filter_edad_min/filter_edad_max cuando el
# valor recibido es no numérico, vacío o None: en esos casos el queryset debe
# devolverse sin alterar.


@pytest.mark.django_db
def test_cliTipoDoc_filter():
    """Prueba que el filtro por tipo de documento (DNI/RUC) retorne los registros correspondientes."""
    c = Client(cliNumDoc='9001', cliTipoDoc='RUC', cliNomCompleto='X')
    c.save()
    qs = Client.objects.all()
    f = ClientFilter({'cliTipoDoc': 'RUC'}, queryset=qs)
    assert c in f.qs


@pytest.mark.django_db
def test_edad_min_filter_includes_expected():
    """Valida que el filtro de edad mínima incluya a los clientes cuya fecha de nacimiento cumpla con el criterio."""
    today = timezone.now().date()
    edad = 30
    birth = today - timedelta(days=int(edad * 365.25))
    c = Client(cliNumDoc='9002', cliNomCompleto='Y', cliFechaNac=birth)
    c.save()
    qs = Client.objects.all()
    f = ClientFilter({'edad_min': str(edad)}, queryset=qs)
    assert c in f.qs


@pytest.mark.django_db
def test_edad_max_filter_includes_expected():
    """Valida que el filtro de edad máxima incluya correctamente a los clientes dentro del rango de edad especificado."""
    today = timezone.now().date()
    edad = 20
    birth = today - timedelta(days=int(edad * 365.25))
    c = Client(cliNumDoc='9003', cliNomCompleto='Z', cliFechaNac=birth)
    c.save()
    qs = Client.objects.all()
    f = ClientFilter({'edad_max': str(edad)}, queryset=qs)
    assert c in f.qs



@pytest.mark.django_db
def test_edad_min_filter_with_invalid_value():
    """Verifica que el filtro de edad mínima ignore valores no numéricos."""
    qs = Client.objects.all()
    f = ClientFilter({}, queryset=qs)

    result = f.filter_edad_min(qs, 'edad_min', 'no_es_numero')

    assert result.count() == qs.count()

@pytest.mark.django_db
def test_edad_max_filter_with_invalid_value():
    """Verifica que el filtro de edad máxima ignore valores no numéricos."""
    qs = Client.objects.all()
    f = ClientFilter({}, queryset=qs)

    result = f.filter_edad_max(qs, 'edad_max', 'no_es_numero')

    assert result.count() == qs.count()

@pytest.mark.django_db
def test_edad_min_filter_with_empty_value():
    """Verifica que el filtro de edad mínima no altere el queryset cuando recibe un valor vacío."""
    qs = Client.objects.all()
    f = ClientFilter({}, queryset=qs)

    result = f.filter_edad_min(qs, 'edad_min', '')

    assert result.count() == qs.count()

@pytest.mark.django_db
def test_edad_min_filter_with_none_value():
    """Verifica que el filtro de edad mínima no altere el queryset cuando recibe None."""
    qs = Client.objects.all()
    f = ClientFilter({}, queryset=qs)

    result = f.filter_edad_min(qs, 'edad_min', None)

    assert result.count() == qs.count()
