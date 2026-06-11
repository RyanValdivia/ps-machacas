import pytest
from django.utils import timezone
from datetime import timedelta
from clients.models import Client, Optometrist, Recipe


@pytest.mark.django_db
def test_client_save_uppercase_and_str():
    c = Client(cliNumDoc='12345678', cliNomCompleto='  juan pérez  ')
    c.save()
    assert c.cliNomCompleto == 'JUAN PÉREZ'
    assert str(c) == 'JUAN PÉREZ (12345678)'


@pytest.mark.django_db
def test_optometrist_str():
    o = Optometrist(optNombre='Ana', optApellido='Lopez')
    o.save()
    assert str(o) == 'Ana Lopez'


@pytest.mark.django_db
def test_recipe_str_requires_relations():
    c = Client(cliNumDoc='2222', cliNomCompleto='cliente')
    c.save()
    o = Optometrist(optNombre='Pedro', optApellido='Gomez')
    o.save()
    r = Recipe(cliCod=c, optCod=o)
    r.save()
    assert str(r) == f"Recipe {r.recCod}"
