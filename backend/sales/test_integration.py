import pytest
from decimal import Decimal
from rest_framework import status
from django.contrib.auth import get_user_model
from users.models import Role
from clients.models import Client
from suppliers.models import Supplier
from categories.models import ProductCategory
from products.models import Product
from cash.models import Cash, CashOpening
from sales.models import Venta

User = get_user_model()

@pytest.fixture
def manager_role(db):
    return Role.objects.create(rolNom="GERENTE", rolDes="Gerente", rolEstado="ACTIVO", rolNivel=0)

@pytest.fixture
def test_user(manager_role):
    u = User.objects.create_user(
        usuNom="integrador1", usuContra="intpass123", usuEmail="i@t.com",
        usuNombreCom="Integrador Test", usuDNI="22222222", usuTel="999999988",
    )
    u.roles.add(manager_role)
    return u

@pytest.fixture
def auth_client(api_client, test_user):
    api_client.force_authenticate(user=test_user)
    return api_client

@pytest.fixture
def category(db):
    cat, _ = ProductCategory.objects.get_or_create(
        catproCode="INT",
        defaults={"catproNom": "Integracion"},
    )
    return cat

@pytest.fixture
def supplier(db):
    return Supplier.objects.create(provRazSocial="Prov Integracion", provRuc="11111111112")

@pytest.fixture
def product(category, supplier):
    return Product.objects.create(
        catproCod=category,
        provCod=supplier,
        prodDescr="Prod Integracion",
        prodMarca="INTEGRACION",
        prodCostoInv=Decimal("10.00"),
        prodPrecioVenta=Decimal("20.00"),
        prodStock=5, # Stock inicial de 5
    )

@pytest.fixture
def cash_register(test_user):
    return Cash.objects.create(usuCod=test_user, cajNom="Caja Integracion")

@pytest.fixture
def cash_session(cash_register, test_user):
    return CashOpening.objects.create(
        cajCod=cash_register,
        usuCod=test_user,
        cajaAperMontInicial=Decimal("200.00"),
        cajaAperEstado="ABIERTA",
    )


@pytest.mark.django_db
@pytest.mark.integration
class TestSalesIntegration:

    def test_int_01_venta_descuenta_stock(self, auth_client, product, cash_session):
        """
        INT-01: Registrar una venta de un producto con stock limitado.
        Verifica que el stock disminuya.
        """
        initial_stock = product.prodStock # 5
        
        response = auth_client.post("/api/sales/ventas/", {
            "ventFormaPago": "EFECTIVO",
            "detalles": [
                {
                    "prodCod": product.prodCod,
                    "ventDetCantidad": 2,
                    "ventDetPrecioUni": "20.00",
                    "ventDetDescuento": 0,
                }
            ]
        }, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        product.refresh_from_db()
        assert product.prodStock == initial_stock - 2

    def test_int_02_venta_insuficiente_stock_rollback(self, auth_client, product, cash_session):
        """
        INT-02: Intentar registrar una venta con stock insuficiente.
        Verifica que ocurra un rollback y no se descuente stock.
        """
        initial_stock = product.prodStock # 5

        response = auth_client.post("/api/sales/ventas/", {
            "ventFormaPago": "EFECTIVO",
            "detalles": [
                {
                    "prodCod": product.prodCod,
                    "ventDetCantidad": 10, # Mayor que 5
                    "ventDetPrecioUni": "20.00",
                    "ventDetDescuento": 0,
                }
            ]
        }, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        product.refresh_from_db()
        assert product.prodStock == initial_stock

    def test_int_03_venta_actualiza_saldo_caja(self, auth_client, product, cash_session):
        """
        INT-03: Registrar una venta con caja activa.
        Verifica que se asocie a la caja abierta y actualice las ventas de la sesión.
        """
        assert cash_session.total_ventas == Decimal("0")
        assert cash_session.cantidad_ventas == 0

        # Crear venta
        response = auth_client.post("/api/sales/ventas/", {
            "ventFormaPago": "EFECTIVO",
            "detalles": [
                {
                    "prodCod": product.prodCod,
                    "ventDetCantidad": 1,
                    "ventDetPrecioUni": "20.00",
                    "ventDetDescuento": 0,
                }
            ]
        }, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        venta_id = response.data['venta']['ventCod']

        # Registrar pago de la venta
        pay_response = auth_client.post(f"/api/sales/ventas/{venta_id}/registrar_pago/", {
            "monto": 20.00,
            "forma_pago": "EFECTIVO"
        }, format="json")
        assert pay_response.status_code == status.HTTP_200_OK

        cash_session.refresh_from_db()
        assert cash_session.total_ventas == Decimal("20.00")
        assert cash_session.cantidad_ventas == 1

    def test_int_04_venta_sin_caja_activa_falla(self, auth_client, product):
        """
        INT-04: Intentar registrar una venta y realizar pago sin caja abierta.
        Verifica que la API rechace el pago con un error 400.
        """
        # Crear venta (sin caja, al no tener pago inicial se crea como pendiente)
        response = auth_client.post("/api/sales/ventas/", {
            "ventFormaPago": "EFECTIVO",
            "detalles": [
                {
                    "prodCod": product.prodCod,
                    "ventDetCantidad": 1,
                    "ventDetPrecioUni": "20.00",
                    "ventDetDescuento": 0,
                }
            ]
        }, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        venta_id = response.data['venta']['ventCod']

        # Aseguramos que no haya cajas abiertas para el usuario
        CashOpening.objects.filter(cajaAperEstado="ABIERTA").update(cajaAperEstado="CERRADA")

        # Intentar pagar
        pay_response = auth_client.post(f"/api/sales/ventas/{venta_id}/registrar_pago/", {
            "monto": 20.00,
            "forma_pago": "EFECTIVO"
        }, format="json")

        assert pay_response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in pay_response.data


@pytest.mark.django_db
@pytest.mark.integration
class TestAuthenticationAndProxyIntegration:

    def test_int_05_jwt_autenticacion(self, api_client, test_user):
        """
        INT-05: Validar flujo JWT.
        Obtener token con credenciales, y realizar consulta autenticada.
        """
        # 1. Solicitar tokens
        response = api_client.post("/api/user/token/", {
            "usuNom": "integrador1",
            "usuContra": "intpass123"
        }, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

        access_token = response.data["access"]

        # 2. Intentar acceder a endpoint protegido con token obtenido
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        user_response = api_client.get("/api/user/current-user/")
        assert user_response.status_code == status.HTTP_200_OK
        assert user_response.data["usuNom"] == "integrador1"

    def test_int_06_proxy_dni_requiere_auth(self, api_client):
        """
        INT-06: Validar que el proxy DNI requiera autenticación.
        """
        response = api_client.get("/api/proxy/dni?numero=77777777")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_int_07_proxy_dni_parametro_invalido(self, auth_client):
        """
        INT-07: Validar comportamiento del proxy DNI con número inválido.
        """
        response = auth_client.get("/api/proxy/dni?numero=123")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data

    def test_int_08_permisos_por_nivel(self, api_client, db):
        """
        INT-08: Validar que un usuario con rol Vendedor (nivel 2) no pueda
        acceder a endpoints administrativos como listar usuarios.
        """
        vendedor_role = Role.objects.create(rolNom="VENDEDOR", rolDes="Vendedor", rolEstado="ACTIVO", rolNivel=2)
        vendedor_user = User.objects.create_user(
            usuNom="vendedor_int", usuContra="vendpass123", usuEmail="v@t.com",
            usuNombreCom="Vendedor Integracion", usuDNI="33333333", usuTel="999999977"
        )
        vendedor_user.roles.add(vendedor_role)
        
        api_client.force_authenticate(user=vendedor_user)
        response = api_client.get("/api/user/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_int_09_proxy_ruc_requiere_auth(self, api_client):
        """
        INT-09: Validar que el proxy RUC requiera autenticación.
        """
        response = api_client.get("/api/proxy/ruc?numero=11111111112")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_int_10_proxy_ruc_parametro_invalido(self, auth_client):
        """
        INT-10: Validar comportamiento del proxy RUC con número inválido.
        """
        response = auth_client.get("/api/proxy/ruc?numero=123")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
