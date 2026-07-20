import pytest
from django.utils import timezone
from datetime import timedelta
from clients.models import Client, Optometrist, Recipe

# Tests de modelos del app clients: Client, Optometrist y Recipe.
# Cubre: normalización de cliNomCompleto a mayúsculas en Client.save() y su __str__,
# __str__ de Optometrist (nombre + apellido), y creación de Recipe con sus relaciones
# obligatorias (cliente, optómetra) validando su __str__.


@pytest.mark.django_db
def test_client_save_uppercase_and_str():
    """Valida que el nombre del cliente se guarde en mayúsculas y que el método __str__ devuelva el formato correcto."""
    c = Client(cliNumDoc='12345678', cliNomCompleto='  juan pérez  ')
    c.save()
    assert c.cliNomCompleto == 'JUAN PÉREZ'
    assert str(c) == 'JUAN PÉREZ (12345678)'


@pytest.mark.django_db
def test_optometrist_str():
    """Verifica que la representación en cadena del Optómetra sea la combinación de su nombre y apellido."""
    o = Optometrist(optNombre='Ana', optApellido='Lopez')
    o.save()
    assert str(o) == 'Ana Lopez'


@pytest.mark.django_db
def test_recipe_str_requires_relations():
    """Comprueba que la receta se cree correctamente con sus relaciones obligatorias y valide su método __str__."""
    c = Client(cliNumDoc='2222', cliNomCompleto='cliente')
    c.save()
    o = Optometrist(optNombre='Pedro', optApellido='Gomez')
    o.save()
    r = Recipe(cliCod=c, optCod=o)
    r.save()
    assert str(r) == f"Recipe {r.recCod}"
