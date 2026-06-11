import pytest
from clients.models import Client


@pytest.mark.django_db
def test_create_client_view(auth_client):
    payload = {'cliNumDoc': '5555', 'cliNomCompleto': 'nombre prueba'}
    resp = auth_client.post('/api/clients/client/', payload, format='json')
    assert resp.status_code == 201
    assert resp.data['success'] is True
    assert resp.data['data']['cliNomCompleto'] == 'NOMBRE PRUEBA'


@pytest.mark.django_db
def test_update_client_view(auth_client):
    c = Client(cliNumDoc='6666', cliNomCompleto='antiguo')
    c.save()
    payload = {'cliNomCompleto': 'nuevo nombre'}
    resp = auth_client.put(f'/api/clients/client/{c.cliCod}/', payload, format='json')
    assert resp.status_code == 200
    assert resp.data['success'] is True
    assert resp.data['data']['cliNomCompleto'] == 'NUEVO NOMBRE'


@pytest.mark.django_db
def test_list_clients_pagination(auth_client):
    for i in range(15):
        Client(cliNumDoc=str(7000 + i), cliNomCompleto=f'Cliente {i}').save()
    resp = auth_client.get('/api/clients/client/')
    assert resp.status_code == 200
    # DRF devuelve paginación con 'results' por defecto; aceptar también la forma custom
    assert 'results' in resp.data or 'data' in resp.data


@pytest.mark.django_db
def test_buscar_cliente_por_documento_requires_numero(auth_client):
    resp = auth_client.get('/api/clients/buscar/?tipo=DNI')
    assert resp.status_code == 400
    assert resp.data['error'] == 'Número de documento requerido'


@pytest.mark.django_db
def test_buscar_cliente_por_documento_not_found(auth_client):
    resp = auth_client.get('/api/clients/buscar/?tipo=DNI&numero=0000')
    assert resp.status_code == 200
    assert resp.data['encontrado'] is False


@pytest.mark.django_db
def test_buscar_cliente_por_documento_multiple_objects(monkeypatch, auth_client):
    from clients.models import Client as ClientModel

    def fake_get(*args, **kwargs):
        raise ClientModel.MultipleObjectsReturned

    monkeypatch.setattr(ClientModel.objects, 'get', fake_get)
    resp = auth_client.get('/api/clients/buscar/?tipo=DNI&numero=dup')
    assert resp.status_code == 400
    assert 'múltiples' in resp.data.get('error', '').lower()
