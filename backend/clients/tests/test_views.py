import pytest
from django.test import override_settings
from django.contrib.auth import get_user_model
from clients.models import Client, Optometrist, Recipe

User = get_user_model()

@pytest.fixture
def auth_client(api_client, db):
    """Fixture para proporcionar un cliente de API autenticado"""
    user = User.objects.create_user(
        usuNom="testadmin",
        usuEmail="admin@test.com",
        usuContra="password123"
    )
    api_client.force_authenticate(user=user)
    return api_client

@pytest.mark.django_db
def test_create_client_view(auth_client):
    """Prueba la creación de un cliente a través de la API y verifica que el nombre se transforme a mayúsculas."""
    payload = {'cliNumDoc': '5555', 'cliNomCompleto': 'nombre prueba'}
    resp = auth_client.post('/api/clients/client/', payload, format='json')
    assert resp.status_code == 201
    assert resp.data['success'] is True
    assert resp.data['data']['cliNomCompleto'] == 'NOMBRE PRUEBA'

@pytest.mark.django_db
def test_create_client_validation_error(auth_client):
    """Cubre la línea de respuesta de error en la creación de clientes (e.g. falta nombre)."""
    payload = {'cliNumDoc': '1111'}  # Payload inválido por falta de cliNomCompleto
    resp = auth_client.post('/api/clients/client/', payload, format='json')
    assert resp.status_code == 400
    assert resp.data['success'] is False
    assert 'cliNomCompleto' in resp.data['errors']

@pytest.mark.django_db
def test_update_client_view(auth_client):
    """Prueba la actualización de los datos de un cliente existente."""
    c = Client(cliNumDoc='6666', cliNomCompleto='antiguo')
    c.save()
    payload = {'cliNomCompleto': 'nuevo nombre'}
    resp = auth_client.put(f'/api/clients/client/{c.cliCod}/', payload, format='json')
    assert resp.status_code == 200
    assert resp.data['success'] is True
    assert resp.data['data']['cliNomCompleto'] == 'NUEVO NOMBRE'

@pytest.mark.django_db
def test_update_client_validation_error(auth_client):
    """Cubre la línea de respuesta de error en la actualización de clientes."""
    c = Client.objects.create(cliNomCompleto="Test")
    resp = auth_client.put(f'/api/clients/client/{c.cliCod}/', {'cliNomCompleto': ''}, format='json')
    assert resp.status_code == 400
    assert resp.data['success'] is False

@pytest.mark.django_db
def test_list_clients_pagination(auth_client):
    """Verifica que el listado de clientes soporte paginación correctamente cuando hay múltiples registros."""
    for i in range(15):
        Client(cliNumDoc=str(7000 + i), cliNomCompleto=f'Cliente {i}').save()
    resp = auth_client.get('/api/clients/client/', {'page': 1})
    assert resp.status_code == 200
    # Al solicitar explícitamente la página, forzamos la ejecución del bloque de paginación
    assert 'results' in resp.data

@pytest.mark.django_db
def test_buscar_cliente_por_documento_default_tipo(auth_client):
    """Verifica que la búsqueda use 'DNI' por defecto si no se especifica el parámetro de tipo."""
    Client.objects.create(cliTipoDoc='DNI', cliNumDoc='123', cliNomCompleto='TEST DEFAULT')
    resp = auth_client.get('/api/clients/buscar/?numero=123')
    assert resp.status_code == 200
    assert resp.data['encontrado'] is True
    assert resp.data['cliente']['cliNumDoc'] == '123'

@pytest.mark.django_db
def test_buscar_cliente_por_documento_requires_numero(auth_client):
    """Valida que el endpoint de búsqueda devuelva un error 400 si falta el parámetro del número de documento."""
    resp = auth_client.get('/api/clients/buscar/?tipo=DNI')
    assert resp.status_code == 400
    assert resp.data['error'] == 'Número de documento requerido'


@pytest.mark.django_db
def test_buscar_cliente_por_documento_not_found(auth_client):
    """Verifica que el sistema responda correctamente (encontrado: False) cuando el cliente no existe."""
    resp = auth_client.get('/api/clients/buscar/?tipo=DNI&numero=0000')
    assert resp.status_code == 200
    assert resp.data['encontrado'] is False


@pytest.mark.django_db
def test_buscar_cliente_por_documento_multiple_objects(monkeypatch, auth_client):
    """Prueba el manejo de excepciones cuando se encuentran múltiples registros con el mismo documento."""
    from clients.models import Client as ClientModel

    def fake_get(*args, **kwargs):
        raise ClientModel.MultipleObjectsReturned

    monkeypatch.setattr(ClientModel.objects, 'get', fake_get)
    resp = auth_client.get('/api/clients/buscar/?tipo=DNI&numero=dup')
    assert resp.status_code == 400
    assert 'múltiples' in resp.data.get('error', '').lower()

@pytest.mark.django_db
def test_create_optometrist_view(auth_client):
    """Verifica la creación de un optómetra mediante la API."""
    payload = {
        'optNombre': 'Carlos',
        'optApellido': 'Santana'
    }

    resp = auth_client.post('/api/clients/optometrist/', payload)

    assert resp.status_code == 201
    assert resp.data['success'] is True
    assert resp.data['data']['optNombre'] == 'Carlos'

@pytest.mark.django_db
def test_create_optometrist_validation_error(auth_client):
    """Verifica que la creación de un optómetra falle si no se envía el nombre."""
    resp = auth_client.post('/api/clients/optometrist/', {'optApellido': 'Solo Apellido'})
    assert resp.status_code == 400
    assert resp.data['success'] is False

@pytest.mark.django_db
def test_list_optometrists_view(auth_client):
    """Verifica que el listado de optómetras funcione (cubre el flujo sin paginación)."""
    Optometrist.objects.create(
        optNombre='Ana',
        optApellido='Lopez'
    )
    resp = auth_client.get('/api/clients/optometrist/')
    assert resp.status_code == 200
    assert len(resp.data['data']) >= 1

@pytest.mark.django_db
def test_update_optometrist_validation_error(auth_client):
    """Verifica que la actualización de un optómetra falle con datos inválidos."""
    opt = Optometrist.objects.create(optNombre='A', optApellido='B')
    resp = auth_client.put(f'/api/clients/optometrist/{opt.optCod}/', {'optNombre': ''})
    assert resp.status_code == 400
    assert resp.data['success'] is False

@pytest.mark.django_db
def test_delete_optometrist_view(auth_client):
    """Verifica la eliminación de un optómetra."""
    opt = Optometrist.objects.create(optNombre='Eliminar', optApellido='Test')
    resp = auth_client.delete(f'/api/clients/optometrist/{opt.optCod}/')
    assert resp.status_code == 204
    assert Optometrist.objects.filter(optCod=opt.optCod).count() == 0


@pytest.mark.django_db
def test_update_optometrist_view(auth_client):
    """Verifica la actualización de un optómetra existente."""
    opt = Optometrist.objects.create(
        optNombre='Carlos',
        optApellido='Santana'
    )

    payload = {
        'optNombre': 'Carlos Alberto',
        'optApellido': 'Santana'
    }

    resp = auth_client.put(
        f'/api/clients/optometrist/{opt.optCod}/',
        payload
    )

    assert resp.status_code == 200
    assert resp.data['data']['optNombre'] == 'Carlos Alberto'

@pytest.mark.django_db
def test_create_recipe_view(auth_client):
    """Verifica la creación exitosa de una receta médica."""
    client = Client.objects.create(
        cliNumDoc='999888',
        cliNomCompleto='Paciente Prueba'
    )
    opt = Optometrist.objects.create(
        optNombre='Doc',
        optApellido='Prueba'
    )
    payload = {
        'cliCod': client.cliCod,
        'optCod': opt.optCod,
        'recObservaciones': 'Prueba de receta unitaria',
        'receDIP': 60
    }
    resp = auth_client.post(
        '/api/clients/prescription/',
        payload
    )
    assert resp.status_code == 201
    assert resp.data['success'] is True

@pytest.mark.django_db
def test_create_recipe_validation_error(auth_client):
    """Verifica que la creación de una receta falle si el cliente no existe."""
    payload = {'cliCod': 99999, 'optCod': 1}
    resp = auth_client.post('/api/clients/prescription/', payload)
    assert resp.status_code == 400
    assert resp.data['success'] is False

@pytest.mark.django_db
def test_update_recipe_view(auth_client):
    """Verifica la actualización de una receta existente."""
    c = Client.objects.create(cliNumDoc='999', cliNomCompleto='P')
    o = Optometrist.objects.create(optNombre='D', optApellido='P')
    r = Recipe.objects.create(cliCod=c, optCod=o)
    payload = {'cliCod': c.cliCod, 'optCod': o.optCod, 'recEstado': 'Inactivo'}
    resp = auth_client.put(f'/api/clients/prescription/{r.recCod}/', payload)
    assert resp.status_code == 200
    assert resp.data['data']['recEstado'] == 'Inactivo'

@pytest.mark.django_db
def test_update_recipe_validation_error(auth_client):
    """Verifica que la actualización de una receta falle con IDs de relación inválidos."""
    c = Client.objects.create(cliNumDoc='999', cliNomCompleto='P')
    o = Optometrist.objects.create(optNombre='D', optApellido='P')
    r = Recipe.objects.create(cliCod=c, optCod=o)
    resp = auth_client.put(f'/api/clients/prescription/{r.recCod}/', {'cliCod': 'invalido'})
    assert resp.status_code == 400

@pytest.mark.django_db
def test_delete_recipe_view(auth_client):
    """Verifica la eliminación de una receta."""
    c = Client.objects.create(cliNumDoc='999', cliNomCompleto='P')
    o = Optometrist.objects.create(optNombre='D', optApellido='P')
    r = Recipe.objects.create(cliCod=c, optCod=o)
    resp = auth_client.delete(f'/api/clients/prescription/{r.recCod}/')
    assert resp.status_code == 204

@pytest.mark.django_db
def test_list_recipe_filtered_by_client(auth_client):
    """Verifica el listado de recetas y el filtrado por cliente (cubre flujo sin paginación)."""
    client = Client.objects.create(
        cliNumDoc='999888',
        cliNomCompleto='Paciente Prueba'
    )

    opt = Optometrist.objects.create(
        optNombre='Doc',
        optApellido='Prueba'
    )

    Recipe.objects.create(
        cliCod=client,
        optCod=opt,
        recObservaciones='Receta de prueba'
    )

    resp = auth_client.get(
        f'/api/clients/prescription/?cliCod={client.cliCod}'
    )

    assert resp.status_code == 200
    assert len(resp.data['data']) == 1


# Tests adicionales para mejorar cobertura

@pytest.mark.django_db
def test_update_client_all_fields(auth_client):
    """Prueba actualización completa de cliente con todos los campos."""
    c = Client.objects.create(cliNumDoc='7777', cliNomCompleto='Original')
    payload = {
        'cliTipoDoc': 'RUC',
        'cliNumDoc': '20222222222',
        'cliNomCompleto': 'Actualizado Total',
        'cliTelef': '999888777',
        'cliFechaNac': '1995-10-20'
    }
    resp = auth_client.put(f'/api/clients/client/{c.cliCod}/', payload, format='json')
    assert resp.status_code == 200
    assert resp.data['data']['cliTipoDoc'] == 'RUC'
    assert resp.data['data']['cliNumDoc'] == '20222222222'


@pytest.mark.django_db
def test_partial_update_client(auth_client):
    """Prueba actualización parcial de cliente (PATCH)."""
    c = Client.objects.create(cliNumDoc='8888', cliNomCompleto='Parcial')
    resp = auth_client.patch(f'/api/clients/client/{c.cliCod}/', {'cliTelef': '555-1234'}, format='json')
    assert resp.status_code == 200
    assert resp.data['data']['cliTelef'] == '555-1234'


@pytest.mark.django_db
def test_delete_client(auth_client):
    """Prueba eliminación de cliente."""
    c = Client.objects.create(cliNomCompleto='Eliminar')
    resp = auth_client.delete(f'/api/clients/client/{c.cliCod}/')
    assert resp.status_code == 204
    assert not Client.objects.filter(cliCod=c.cliCod).exists()


@pytest.mark.django_db
def test_list_clients_with_pagination(auth_client):
    """Prueba listado de clientes con paginación."""
    # Crear más de 10 clientes para activar paginación
    for i in range(15):
        Client.objects.create(cliNumDoc=f'{10000+i}', cliNomCompleto=f'Cliente {i}')

    resp = auth_client.get('/api/clients/client/')
    assert resp.status_code == 200
    assert 'results' in resp.data
    assert len(resp.data['results']) == 10  # page_size
    assert resp.data['count'] == 15


@pytest.mark.django_db
def test_list_clients_without_pagination(auth_client):
    """Prueba listado sin paginación (cuando hay pocos resultados)."""
    for i in range(5):
        Client.objects.create(cliNumDoc=f'{20000+i}', cliNomCompleto=f'Few {i}')

    resp = auth_client.get('/api/clients/client/')
    assert resp.status_code == 200
    assert 'data' in resp.data
    assert len(resp.data['data']) == 5


@pytest.mark.django_db
def test_partial_update_optometrist(auth_client):
    """Prueba actualización parcial de optómetra."""
    opt = Optometrist.objects.create(optNombre='Juan', optApellido='Perez')
    resp = auth_client.patch(f'/api/clients/optometrist/{opt.optCod}/', {'optNombre': 'Carlos'})
    assert resp.status_code == 200
    assert resp.data['data']['optNombre'] == 'Carlos'


@pytest.mark.django_db
def test_partial_update_recipe(auth_client):
    """Prueba actualización parcial de receta."""
    c = Client.objects.create(cliNumDoc='9999', cliNomCompleto='Pac')
    o = Optometrist.objects.create(optNombre='Dr', optApellido='Test')
    r = Recipe.objects.create(cliCod=c, optCod=o, recEstado='Activo')

    resp = auth_client.patch(f'/api/clients/prescription/{r.recCod}/', {'recEstado': 'Inactivo'})
    assert resp.status_code == 200
    assert resp.data['data']['recEstado'] == 'Inactivo'


@pytest.mark.django_db
def test_list_recipe_without_pagination(auth_client):
    """Prueba listado de recetas sin paginación."""
    c = Client.objects.create(cliNumDoc='1111', cliNomCompleto='Paciente')
    o = Optometrist.objects.create(optNombre='Dr', optApellido='Receta')

    for i in range(3):
        Recipe.objects.create(cliCod=c, optCod=o)

    resp = auth_client.get('/api/clients/prescription/')
    assert resp.status_code == 200
    assert len(resp.data['data']) == 3


@pytest.mark.django_db
def test_client_search_by_name(auth_client):
    """Prueba búsqueda de cliente por nombre."""
    Client.objects.create(cliNumDoc='3333', cliNomCompleto='Juan Perez')
    Client.objects.create(cliNumDoc='4444', cliNomCompleto='Maria Lopez')

    resp = auth_client.get('/api/clients/client/', {'search': 'Juan'})
    assert resp.status_code == 200
    assert any('JUAN PEREZ' in c.get('cliNomCompleto', '') for c in resp.data.get('results', resp.data.get('data', [])))


@pytest.mark.django_db
def test_client_search_by_document(auth_client):
    """Prueba búsqueda de cliente por documento."""
    Client.objects.create(cliNumDoc='5555', cliNomCompleto='Buscar Doc')

    resp = auth_client.get('/api/clients/client/', {'search': '5555'})
    assert resp.status_code == 200
    results = resp.data.get('results', resp.data.get('data', []))
    assert any('5555' in c.get('cliNumDoc', '') for c in results)


