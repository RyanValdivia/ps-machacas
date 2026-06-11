import pytest
from django.utils import timezone
from datetime import timedelta
from clients.models import Client
from clients.filters import ClientFilter


@pytest.mark.django_db
def test_cliTipoDoc_filter():
    c = Client(cliNumDoc='9001', cliTipoDoc='RUC', cliNomCompleto='X')
    c.save()
    qs = Client.objects.all()
    f = ClientFilter({'cliTipoDoc': 'RUC'}, queryset=qs)
    assert c in f.qs


@pytest.mark.django_db
def test_edad_min_filter_includes_expected():
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
    today = timezone.now().date()
    edad = 20
    birth = today - timedelta(days=int(edad * 365.25))
    c = Client(cliNumDoc='9003', cliNomCompleto='Z', cliFechaNac=birth)
    c.save()
    qs = Client.objects.all()
    f = ClientFilter({'edad_max': str(edad)}, queryset=qs)
    assert c in f.qs
