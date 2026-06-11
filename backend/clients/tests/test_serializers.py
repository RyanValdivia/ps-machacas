import pytest
from clients.serializers import ClientSerializer, RecipeSerializer
from clients.models import Client, Optometrist


@pytest.mark.django_db
def test_client_serializer_creates_and_applies_model_save_behavior():
    """Valida que el serializador de clientes respete la lógica del modelo de convertir nombres a mayúsculas al guardar."""
    data = {'cliNumDoc': '99990000', 'cliNomCompleto': 'maria lopez'}
    serializer = ClientSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    client = serializer.save()
    # El save del modelo transforma el nombre a mayúsculas
    assert client.cliNomCompleto == 'MARIA LOPEZ'
    serialized = ClientSerializer(client)
    assert serialized.data['cliNomCompleto'] == 'MARIA LOPEZ'


@pytest.mark.django_db
def test_recipe_serializer_accepts_minimal_input():
    """Verifica que el serializador de recetas funcione correctamente enviando solo los campos mínimos obligatorios."""
    c = Client(cliNumDoc='1000', cliNomCompleto='Cliente')
    c.save()
    o = Optometrist(optNombre='Opt', optApellido='One')
    o.save()
    data = {'cliCod': c.cliCod, 'optCod': o.optCod}
    serializer = RecipeSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    recipe = serializer.save()
    assert recipe.cliCod == c
    assert recipe.optCod == o
