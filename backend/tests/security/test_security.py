import pytest
import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import Role

User = get_user_model()


# Suite de tests no funcionales de seguridad (NFSEC) para la API en su conjunto.
# NFSEC-01/02: control de acceso - todo endpoint protegido debe rechazar peticiones
# GET/POST/PUT/PATCH/DELETE sin token JWT (401), verificado sobre una lista amplia
# de endpoints (products, sales, clients, user, cash, suppliers, categories,
# opticalcenter).
# NFSEC-03/04: autorización por rol - un VENDEDOR no debe poder listar usuarios ni
# cajeros (endpoints exclusivos de GERENTE), debe recibir 403.
# NFSEC-05: un token JWT ya expirado (fabricado a mano con exp en el pasado) debe
# ser rechazado con 401.
# NFSEC-06/07: inyección SQL vía el parámetro de búsqueda (?search=) en productos
# y ventas; el sistema no debe romperse (solo 200 o 400 son aceptables) y si
# responde 200 los datos deben seguir teniendo forma válida - confirma que el ORM
# parametriza las consultas en vez de concatenar el input crudo.

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def gerente_role(db):
    return Role.objects.create(rolNom="GERENTE", rolDes="Gerente", rolEstado="ACTIVO", rolNivel=0)


@pytest.fixture
def vendedor_role(db):
    return Role.objects.create(rolNom="VENDEDOR", rolDes="Vendedor", rolEstado="ACTIVO", rolNivel=2)


@pytest.fixture
def gerente(db, gerente_role):
    user = User.objects.create_user(
        usuNom="gerente1",
        usuContra="Admin123!",
        usuEmail="gerente@test.com",
        usuNombreCom="Gerente Test",
        usuDNI="12345678",
        usuTel="999999991",
    )
    user.roles.add(gerente_role)
    return user


@pytest.fixture
def vendedor(db, vendedor_role):
    user = User.objects.create_user(
        usuNom="vendedor1",
        usuContra="Admin123!",
        usuEmail="vendedor@test.com",
        usuNombreCom="Vendedor Test",
        usuDNI="34567890",
        usuTel="999999993",
    )
    user.roles.add(vendedor_role)
    return user


@pytest.mark.django_db
class TestAccesoSinToken:
    """NFSEC 01-02: Endpoints protegidos deben rechazar peticiones sin token JWT"""

    @pytest.mark.parametrize("url", [
        "/api/products/",
        "/api/sales/ventas/",
        "/api/clients/client/",
        "/api/user/",
        "/api/user/current-user/",
        "/api/cash/",
        "/api/suppliers/",
        "/api/categories/",
        "/api/opticalcenter/",
    ])

    def test_NFSEC_01_get_sin_token_retorna_401(self, api_client, url):
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize("method,url", [
        ("post", "/api/products/"),
        ("post", "/api/sales/ventas/"),
        ("post", "/api/clients/client/"),
        ("put", "/api/user/update/1/"),
        ("patch", "/api/cash/opening/1/"),
        ("delete", "/api/user/delete/1/"),
    ])

    def test_NFSEC_02_metodos_sin_token_retornan_401(self, api_client, method, url):
        func = getattr(api_client, method)
        response = func(url, {}, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestVendedorNoAccesoGerente:
    """NFSEC 03-04: Vendedor no debe acceder a endpoints exclusivos de Gerente"""

    @pytest.fixture
    def vendedor_client(self, vendedor):
        client = APIClient()
        refresh = RefreshToken.for_user(vendedor)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        return client

    def test_NFSEC_03_vendedor_no_lista_usuarios(self, vendedor_client):
        response = vendedor_client.get("/api/user/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_NFSEC_04_vendedor_no_lista_cajeros(self, vendedor_client):
        response = vendedor_client.get("/api/user/list/cashier/")
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestTokenExpirado:
    """NFSEC 05: Token JWT expirado debe ser rechazado"""

    def test_NFSEC_05_token_expirado_retorna_401(self, api_client, gerente):
        payload = {
            settings.SIMPLE_JWT['USER_ID_CLAIM']: gerente.usuCod,
            'exp': datetime.now(timezone.utc) - timedelta(seconds=1),
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = api_client.get("/api/user/current-user/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestInyeccionSQL:
    """NFSEC 06-07: Sistema debe ser seguro contra inyección SQL en parámetros de búsqueda"""

    @pytest.fixture
    def gerente_client(self, gerente):
        client = APIClient()
        refresh = RefreshToken.for_user(gerente)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        return client

    @pytest.mark.parametrize("payload", [
        "'; DROP TABLE products_product; --",
        "' OR '1'='1",
        "' UNION SELECT * FROM users_user--",
        "'; DELETE FROM users_user WHERE '1'='1",
        "1' OR '1' = '1",
        "' OR 1=1--",
        "\" OR 1=1--",
        "' ORDER BY 1--",
        "1; SELECT * FROM users_user",
    ])
    def test_NFSEC_06_busqueda_producto_sql_injection(self, gerente_client, payload):
        response = gerente_client.get("/api/products/", {"search": payload})
        assert response.status_code in (status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST)
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert isinstance(data, (dict, list))

    @pytest.mark.parametrize("payload", [
        "'; DROP TABLE sales_venta; --",
        "' OR '1'='1",
        "' UNION SELECT * FROM users_user--",
    ])

    def test_NFSEC_07_busqueda_venta_sql_injection(self, gerente_client, payload):
        response = gerente_client.get("/api/sales/ventas/", {"search": payload})
        assert response.status_code in (status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST)
