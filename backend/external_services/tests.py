import pytest
from django.contrib.auth.models import User
from rest_framework import status
from unittest.mock import patch, Mock


@pytest.fixture
def authenticated_client(api_client):
    user = User.objects.create_user(username='testuser', password='testpass')
    api_client.force_authenticate(user=user)
    return api_client


@pytest.mark.django_db
class TestConsultarDNI:
    # TEST: GET sin autenticacion retorna 401
    def test_unauthenticated(self, api_client):
        r = api_client.get('/api/proxy/dni', {'numero': '12345678'})
        assert r.status_code == status.HTTP_401_UNAUTHORIZED

    # TEST: GET sin numero retorna 400
    def test_sin_numero(self, authenticated_client):
        r = authenticated_client.get('/api/proxy/dni')
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Debe proporcionar' in r.data['error']

    # TEST: GET con formato invalido retorna 400
    def test_formato_invalido(self, authenticated_client):
        r = authenticated_client.get('/api/proxy/dni', {'numero': 'abc'})
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert 'DNI inv' in r.data['error']

    # TEST: GET con menos de 8 digitos retorna 400
    def test_longitud_invalida(self, authenticated_client):
        r = authenticated_client.get('/api/proxy/dni', {'numero': '1234567'})
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    # TEST: GET con 8 digitos exitoso
    @patch('requests.get')
    def test_consulta_exitosa(self, mock_get, authenticated_client):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'numero': '12345678', 'nombre': 'JUAN PEREZ'}
        mock_get.return_value = mock_response
        r = authenticated_client.get('/api/proxy/dni', {'numero': '12345678'})
        assert r.status_code == status.HTTP_200_OK
        assert r.data['nombre'] == 'JUAN PEREZ'

    # TEST: GET con 404 retorna error
    @patch('requests.get')
    def test_no_encontrado(self, mock_get, authenticated_client):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        r = authenticated_client.get('/api/proxy/dni', {'numero': '12345678'})
        assert r.status_code == status.HTTP_404_NOT_FOUND
        assert 'no encontrado' in r.data['error']

    # TEST: GET con 429 retorna error rate limit
    @patch('requests.get')
    def test_rate_limit(self, mock_get, authenticated_client):
        mock_response = Mock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response
        r = authenticated_client.get('/api/proxy/dni', {'numero': '12345678'})
        assert r.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert 'L' in r.data['error']

    # TEST: GET con otro status code retorna 503
    @patch('requests.get')
    def test_otro_error(self, mock_get, authenticated_client):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        r = authenticated_client.get('/api/proxy/dni', {'numero': '12345678'})
        assert r.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

    # TEST: GET con timeout retorna 504
    @patch('requests.get')
    def test_timeout(self, mock_get, authenticated_client):
        from requests.exceptions import Timeout
        mock_get.side_effect = Timeout()
        r = authenticated_client.get('/api/proxy/dni', {'numero': '12345678'})
        assert r.status_code == status.HTTP_504_GATEWAY_TIMEOUT
        assert 'Tiempo de espera' in r.data['error']

    # TEST: GET con connection error retorna 503
    @patch('requests.get')
    def test_connection_error(self, mock_get, authenticated_client):
        from requests.exceptions import ConnectionError
        mock_get.side_effect = ConnectionError()
        r = authenticated_client.get('/api/proxy/dni', {'numero': '12345678'})
        assert r.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert 'Error de conexi' in r.data['error']

    # TEST: GET con excepcion inesperada retorna 500
    @patch('requests.get')
    def test_error_inesperado(self, mock_get, authenticated_client):
        mock_get.side_effect = Exception("Algo salio mal")
        r = authenticated_client.get('/api/proxy/dni', {'numero': '12345678'})
        assert r.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert 'inesperado' in r.data['error']


@pytest.mark.django_db
class TestConsultarRUC:
    # TEST: GET sin autenticacion retorna 401
    def test_unauthenticated(self, api_client):
        r = api_client.get('/api/proxy/ruc', {'numero': '20123456789'})
        assert r.status_code == status.HTTP_401_UNAUTHORIZED

    # TEST: GET sin numero retorna 400
    def test_sin_numero(self, authenticated_client):
        r = authenticated_client.get('/api/proxy/ruc')
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Debe proporcionar' in r.data['error']

    # TEST: GET con formato invalido retorna 400
    def test_formato_invalido(self, authenticated_client):
        r = authenticated_client.get('/api/proxy/ruc', {'numero': 'abc'})
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert 'RUC inv' in r.data['error']

    # TEST: GET con menos de 11 digitos retorna 400
    def test_longitud_invalida(self, authenticated_client):
        r = authenticated_client.get('/api/proxy/ruc', {'numero': '1234567890'})
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    # TEST: GET con 11 digitos exitoso
    @patch('requests.get')
    def test_consulta_exitosa(self, mock_get, authenticated_client):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'numero': '20123456789', 'nombre': 'EMPRESA SAC'}
        mock_get.return_value = mock_response
        r = authenticated_client.get('/api/proxy/ruc', {'numero': '20123456789'})
        assert r.status_code == status.HTTP_200_OK
        assert r.data['nombre'] == 'EMPRESA SAC'

    # TEST: GET con 404 retorna error
    @patch('requests.get')
    def test_no_encontrado(self, mock_get, authenticated_client):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        r = authenticated_client.get('/api/proxy/ruc', {'numero': '20123456789'})
        assert r.status_code == status.HTTP_404_NOT_FOUND
        assert 'no encontrado' in r.data['error']

    # TEST: GET con 429 retorna error rate limit
    @patch('requests.get')
    def test_rate_limit(self, mock_get, authenticated_client):
        mock_response = Mock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response
        r = authenticated_client.get('/api/proxy/ruc', {'numero': '20123456789'})
        assert r.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    # TEST: GET con otro status code retorna 500
    @patch('requests.get')
    def test_otro_error(self, mock_get, authenticated_client):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        r = authenticated_client.get('/api/proxy/ruc', {'numero': '20123456789'})
        assert r.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    # TEST: GET con timeout retorna 504
    @patch('requests.get')
    def test_timeout(self, mock_get, authenticated_client):
        from requests.exceptions import Timeout
        mock_get.side_effect = Timeout()
        r = authenticated_client.get('/api/proxy/ruc', {'numero': '20123456789'})
        assert r.status_code == status.HTTP_504_GATEWAY_TIMEOUT
        assert 'Tiempo de espera' in r.data['error']

    # TEST: GET con connection error retorna 503
    @patch('requests.get')
    def test_connection_error(self, mock_get, authenticated_client):
        from requests.exceptions import ConnectionError
        mock_get.side_effect = ConnectionError()
        r = authenticated_client.get('/api/proxy/ruc', {'numero': '20123456789'})
        assert r.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert 'Error de conexi' in r.data['error']

    # TEST: GET con excepcion inesperada retorna 500
    @patch('requests.get')
    def test_error_inesperado(self, mock_get, authenticated_client):
        mock_get.side_effect = Exception("Error raro")
        r = authenticated_client.get('/api/proxy/ruc', {'numero': '20123456789'})
        assert r.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
