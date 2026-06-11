import pytest
from django.urls import reverse
from unittest.mock import patch
import requests
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def auth_client(api_client, db):
    """Fixture para proporcionar un cliente de API autenticado para servicios externos"""
    user = User.objects.create_user(usuNom="proxyuser", usuEmail="proxy@test.com", password="password123")
    api_client.force_authenticate(user=user)
    return api_client

@pytest.mark.django_db
@patch('requests.get')
def test_consultar_dni_success(mock_get, auth_client):
    """Prueba una consulta exitosa de DNI"""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"dni": "12345678", "nombres": "JUAN"}
    url = reverse('consultar_dni') + "?numero=12345678"
    resp = auth_client.get(url)
    assert resp.status_code == 200
    assert resp.data['nombres'] == "JUAN"

@pytest.mark.django_db
def test_consultar_dni_invalid_format(auth_client):
    """Valida rechazo de DNI con formato incorrecto"""
    url = reverse('consultar_dni') + "?numero=123"
    resp = auth_client.get(url)
    assert resp.status_code == 400

@pytest.mark.django_db
@patch('requests.get')
def test_consultar_dni_not_found(mock_get, auth_client):
    """Cubre error 404 de la API de DNI"""
    mock_get.return_value.status_code = 404
    url = reverse('consultar_dni') + "?numero=00000000"
    resp = auth_client.get(url)
    assert resp.status_code == 404

@pytest.mark.django_db
@patch('requests.get')
def test_consultar_dni_rate_limit(mock_get, auth_client):
    """Cubre error 429 (Límites) en DNI"""
    mock_get.return_value.status_code = 429
    url = reverse('consultar_dni') + "?numero=12345678"
    resp = auth_client.get(url)
    assert resp.status_code == 429

@pytest.mark.django_db
@patch('requests.get')
def test_consultar_dni_unexpected_error(mock_get, auth_client):
    """Cubre códigos de estado no manejados específicamente en DNI"""
    mock_get.return_value.status_code = 500
    url = reverse('consultar_dni') + "?numero=12345678"
    resp = auth_client.get(url)
    assert resp.status_code == 503

@pytest.mark.django_db
@patch('requests.get')
def test_consultar_dni_timeout(mock_get, auth_client):
    """Cubre timeout en consulta DNI"""
    mock_get.side_effect = requests.exceptions.Timeout
    url = reverse('consultar_dni') + "?numero=12345678"
    resp = auth_client.get(url)
    assert resp.status_code == 504

@pytest.mark.django_db
@patch('requests.get')
def test_consultar_dni_connection_error(mock_get, auth_client):
    """Cubre error de conexión en DNI"""
    mock_get.side_effect = requests.exceptions.ConnectionError
    url = reverse('consultar_dni') + "?numero=12345678"
    resp = auth_client.get(url)
    assert resp.status_code == 503

@pytest.mark.django_db
@patch('requests.get')
def test_consultar_dni_generic_exception(mock_get, auth_client):
    """Cubre excepciones inesperadas en DNI"""
    mock_get.side_effect = Exception("Falla crítica")
    url = reverse('consultar_dni') + "?numero=12345678"
    resp = auth_client.get(url)
    assert resp.status_code == 500

@pytest.mark.django_db
@patch('requests.get')
def test_consultar_ruc_success(mock_get, auth_client):
    """Prueba consulta exitosa de RUC"""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"ruc": "20123456789", "razonSocial": "TEST"}
    url = reverse('consultar_ruc') + "?numero=20123456789"
    resp = auth_client.get(url)
    assert resp.status_code == 200

@pytest.mark.django_db
def test_consultar_ruc_missing_number(auth_client):
    """Valida RUC faltante"""
    resp = auth_client.get(reverse('consultar_ruc'))
    assert resp.status_code == 400

@pytest.mark.django_db
def test_consultar_ruc_invalid_format(auth_client):
    """Valida RUC con formato incorrecto (no 11 dígitos)"""
    url = reverse('consultar_ruc') + "?numero=123"
    resp = auth_client.get(url)
    assert resp.status_code == 400

@pytest.mark.django_db
@patch('requests.get')
def test_consultar_ruc_error_responses(mock_get, auth_client):
    """Prueba múltiples respuestas de error en RUC (429, 500, Timeout, Connection)"""
    base_url = reverse('consultar_ruc') + "?numero=20123456789"
    
    # 429
    mock_get.return_value.status_code = 429
    assert auth_client.get(base_url).status_code == 429
    
    # Otros errores (500)
    mock_get.return_value.status_code = 500
    assert auth_client.get(base_url).status_code == 500

    # Timeout
    mock_get.side_effect = requests.exceptions.Timeout
    assert auth_client.get(base_url).status_code == 504

    # Connection Error
    mock_get.side_effect = requests.exceptions.ConnectionError
    assert auth_client.get(base_url).status_code == 503

    # Generic Exception
    mock_get.side_effect = Exception("Crash")
    assert auth_client.get(base_url).status_code == 500
