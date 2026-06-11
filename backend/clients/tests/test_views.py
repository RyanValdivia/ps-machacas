import pytest
from django.contrib.auth import get_user_model
from clients.models import Client, Optometrist, Recipe

User = get_user_model()

@pytest.fixture
def auth_client(api_client, db):
    """Fixture para proporcionar un cliente de API autenticado"""
    user = User.objects.create_user(usuNom="testadmin", usuEmail="admin@test.com", password="password123")
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
def test_update_client_view(auth_client):
    """Prueba la actualización parcial de los datos de un cliente existente."""
    c = Client(cliNumDoc='6666', cliNomCompleto='antiguo')
    c.save()
    payload = {'cliNomCompleto': 'nuevo nombre'}
    resp = auth_client.put(f'/api/clients/client/{c.cliCod}/', payload, format='json')
    assert resp.status_code == 200
    assert resp.data['success'] is True
    assert resp.data['data']['cliNomCompleto'] == 'NUEVO NOMBRE'


@pytest.mark.django_db
def test_list_clients_pagination(auth_client):
    """Verifica que el listado de clientes soporte paginación correctamente cuando hay múltiples registros."""
    for i in range(15):
        Client(cliNumDoc=str(7000 + i), cliNomCompleto=f'Cliente {i}').save()
    resp = auth_client.get('/api/clients/client/')
    assert resp.status_code == 200
    # DRF devuelve paginación con 'results' por defecto; aceptar también la forma custom
    assert 'results' in resp.data or 'data' in resp.data


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
def test_optometrist_viewset_crud(auth_client):
    """Prueba el flujo CRUD completo (crear, listar y actualizar) para el modelo de Optómetras."""
    # Test Create
    payload = {'optNombre': 'Carlos', 'optApellido': 'Santana'}
    resp = auth_client.post('/api/clients/optometrist/', payload)
    assert resp.status_code == 201
    opt_id = resp.data['data']['optCod']

    # Test List
    resp = auth_client.get('/api/clients/optometrist/')
    assert resp.status_code == 200
    assert len(resp.data['results']) >= 1

    # Test Update
    resp = auth_client.put(f'/api/clients/optometrist/{opt_id}/', {'optNombre': 'Carlos Alberto', 'optApellido': 'Santana'})
    assert resp.status_code == 200
    assert resp.data['data']['optNombre'] == 'Carlos Alberto'

@pytest.mark.django_db
def test_recipe_viewset_create_and_list(auth_client):
    """Prueba la creación de una receta médica y verifica el filtrado por código de cliente."""
    # Setup data
    client = Client.objects.create(cliNumDoc='999888', cliNomCompleto='Paciente Prueba')
    opt = Optometrist.objects.create(optNombre='Doc', optApellido='Prueba')
    
    # Test Create
    payload = {
        'cliCod': client.cliCod,
        'optCod': opt.optCod,
        'recObservaciones': 'Prueba de receta unitaria',
        'receDIP': 60
    }
    resp = auth_client.post('/api/clients/prescription/', payload)
    assert resp.status_code == 201
    assert resp.data['success'] is True

    # Test List with Filter
    resp = auth_client.get(f'/api/clients/prescription/?cliCod={client.cliCod}')
    assert resp.status_code == 200
    assert len(resp.data['results']) == 1
