import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError

# Tests del feature de Caja (Cash) y Apertura de Caja (CashOpening).
# Cubre: modelos (validaciones de clean(), constraint unique en cajNom, ciclo de vida
# de una apertura: crear, cerrar con cálculo de diferencia/monto esperado, anular, y
# reglas de "una apertura activa por caja/usuario"), serializers (campos expuestos y
# validación de datos), viewsets (CRUD completo + acciones custom: close, open,
# session_sales, by-cash) incluyendo control de acceso por rol, y resolución de urls.


@pytest.mark.django_db
class TestCashModel:
    # TEST: crear caja con todos los campos
    def test_create_cash(self):
        from users.models import User
        from cash.models import Cash
        user = User.objects.create_user(usuNom="cajero1", usuContra="pass", usuEmail="cajero1@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Principal", cajDes="Caja del local")
        assert caja.cajNom == "Caja Principal"
        assert caja.cajDes == "Caja del local"
        assert caja.usuCod == user
        assert caja.cajEstado == "ACTIVO"

    # TEST: str representation
    def test_str(self):
        from users.models import User
        from cash.models import Cash
        user = User.objects.create_user(usuNom="cajero2", usuContra="pass", usuEmail="cajero2@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Dos")
        assert str(caja) == "Caja Dos"

    # TEST: clean rechaza nombre menor a 3 caracteres
    def test_nombre_min_length(self):
        from users.models import User
        from cash.models import Cash
        user = User.objects.create_user(usuNom="cajero3", usuContra="pass", usuEmail="cajero3@test.com")
        caja = Cash(usuCod=user, cajNom="AB")
        with pytest.raises(ValidationError):
            caja.clean()

    # TEST: unique constraint en cajNom
    def test_unique_nombre(self):
        from users.models import User
        from cash.models import Cash
        from django.db import IntegrityError
        user = User.objects.create_user(usuNom="cajero4", usuContra="pass", usuEmail="cajero4@test.com")
        Cash.objects.create(usuCod=user, cajNom="Unica")
        with pytest.raises(IntegrityError):
            Cash.objects.create(usuCod=user, cajNom="Unica")

    # TEST: default estado is ACTIVO
    def test_default_estado(self):
        from users.models import User
        from cash.models import Cash
        user = User.objects.create_user(usuNom="cajero5", usuContra="pass", usuEmail="cajero5@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Default")
        assert caja.cajEstado == "ACTIVO"

    # TEST: tiene_apertura_activa False sin aperturas
    def test_tiene_apertura_activa_false(self):
        from users.models import User
        from cash.models import Cash
        user = User.objects.create_user(usuNom="cajero6", usuContra="pass", usuEmail="cajero6@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Sin Apertura")
        assert caja.tiene_apertura_activa is False

    # TEST: apertura_actual es None sin aperturas
    def test_apertura_actual_none(self):
        from users.models import User
        from cash.models import Cash
        user = User.objects.create_user(usuNom="cajero7", usuContra="pass", usuEmail="cajero7@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Sin Apertura 2")
        assert caja.apertura_actual is None

    # TEST: creacion sin descripcion (null)
    def test_create_cash_sin_descripcion(self):
        from users.models import User
        from cash.models import Cash
        user = User.objects.create_user(usuNom="cajero8", usuContra="pass", usuEmail="cajero8@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Sin Desc")
        assert caja.cajDes is None


@pytest.mark.django_db
class TestCashOpeningModel:
    # Ciclo de vida de una apertura: creación, cierre (cerrar_caja calcula diferencia
    # y monto esperado), anulación, y reglas que impiden duplicar apertura activa
    # en la misma caja o el mismo usuario.
    # TEST: crear apertura con todos los campos
    def test_create_opening(self):
        from users.models import User
        from cash.models import Cash, CashOpening
        user = User.objects.create_user(usuNom="cajero10", usuContra="pass", usuEmail="cajero10@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Apertura")
        apertura = CashOpening.objects.create(cajCod=caja, usuCod=user, cajaAperMontInicial=Decimal('500.00'))
        assert apertura.cajaAperMontInicial == Decimal('500.00')
        assert apertura.cajaAperEstado == "ABIERTA"
        assert apertura.cajCod == caja
        assert apertura.usuCod == user

    # TEST: str representation
    def test_str(self):
        from users.models import User
        from cash.models import Cash, CashOpening
        user = User.objects.create_user(usuNom="cajero11", usuContra="pass", usuEmail="cajero11@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Str")
        apertura = CashOpening.objects.create(cajCod=caja, usuCod=user, cajaAperMontInicial=Decimal('100.00'))
        assert str(apertura) == f"Apertura #{apertura.cajaAperCod} - Caja Str (ABIERTA)"

    # TEST: default estado es ABIERTA
    def test_default_estado(self):
        from users.models import User
        from cash.models import Cash, CashOpening
        user = User.objects.create_user(usuNom="cajero12", usuContra="pass", usuEmail="cajero12@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Default Apertura")
        apertura = CashOpening.objects.create(cajCod=caja, usuCod=user, cajaAperMontInicial=Decimal('200.00'))
        assert apertura.cajaAperEstado == "ABIERTA"

    # TEST: clean rechaza monto inicial negativo
    def test_monto_inicial_negativo(self):
        from users.models import User
        from cash.models import Cash, CashOpening
        user = User.objects.create_user(usuNom="cajero13", usuContra="pass", usuEmail="cajero13@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Negativo")
        with pytest.raises(ValidationError):
            apertura = CashOpening(cajCod=caja, usuCod=user, cajaAperMontInicial=Decimal('-50.00'))
            apertura.clean()

    # TEST: auto_now_add asigna fecha
    def test_auto_fecha(self):
        from users.models import User
        from cash.models import Cash, CashOpening
        user = User.objects.create_user(usuNom="cajero14", usuContra="pass", usuEmail="cajero14@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Fecha")
        apertura = CashOpening.objects.create(cajCod=caja, usuCod=user, cajaAperMontInicial=Decimal('300.00'))
        assert apertura.cajaApertuFechHora is not None

    # TEST: clean rechaza duplicado apertura activa misma caja
    def test_duplicado_apertura_misma_caja(self):
        from users.models import User
        from cash.models import Cash, CashOpening
        user = User.objects.create_user(usuNom="cajero15", usuContra="pass", usuEmail="cajero15@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Dup")
        CashOpening.objects.create(cajCod=caja, usuCod=user, cajaAperMontInicial=Decimal('100.00'))
        with pytest.raises(ValidationError):
            apertura2 = CashOpening(cajCod=caja, usuCod=user, cajaAperMontInicial=Decimal('200.00'))
            apertura2.clean()

    # TEST: cerrar_caja cambia estado y calcula montos
    def test_cerrar_caja(self):
        from users.models import User
        from cash.models import Cash, CashOpening
        user = User.objects.create_user(usuNom="cajero16", usuContra="pass", usuEmail="cajero16@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Cierre")
        apertura = CashOpening.objects.create(cajCod=caja, usuCod=user, cajaAperMontInicial=Decimal('1000.00'))
        apertura.cerrar_caja(monto_cierre=Decimal('1200.00'))
        apertura.refresh_from_db()
        assert apertura.cajaAperEstado == "CERRADA"
        assert apertura.cajaAperMontCierre == Decimal('1200.00')
        assert apertura.cajaAperFechaHorCierre is not None

    # TEST: cerrar_caja mantiene observaciones
    def test_cerrar_caja_con_observaciones(self):
        from users.models import User
        from cash.models import Cash, CashOpening
        user = User.objects.create_user(usuNom="cajero17", usuContra="pass", usuEmail="cajero17@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Cierre Obs")
        apertura = CashOpening.objects.create(cajCod=caja, usuCod=user, cajaAperMontInicial=Decimal('500.00'))
        apertura.cerrar_caja(monto_cierre=Decimal('500.00'), observaciones="Sin novedades")
        apertura.refresh_from_db()
        assert apertura.cajaAperObservacio == "Sin novedades"

    # TEST: cerrar_caja en apertura ya cerrada lanza error
    def test_cerrar_caja_ya_cerrada(self):
        from users.models import User
        from cash.models import Cash, CashOpening
        user = User.objects.create_user(usuNom="cajero18", usuContra="pass", usuEmail="cajero18@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Cierre Dup")
        apertura = CashOpening.objects.create(cajCod=caja, usuCod=user, cajaAperMontInicial=Decimal('300.00'))
        apertura.cerrar_caja(monto_cierre=Decimal('300.00'))
        with pytest.raises(ValidationError):
            apertura.cerrar_caja(monto_cierre=Decimal('400.00'))

    # TEST: anular cambia estado a ANULADA
    def test_anular(self):
        from users.models import User
        from cash.models import Cash, CashOpening
        user = User.objects.create_user(usuNom="cajero19", usuContra="pass", usuEmail="cajero19@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Anular")
        apertura = CashOpening.objects.create(cajCod=caja, usuCod=user, cajaAperMontInicial=Decimal('100.00'))
        apertura.anular(motivo="Prueba")
        apertura.refresh_from_db()
        assert apertura.cajaAperEstado == "ANULADA"
        assert "ANULADA: Prueba" in apertura.cajaAperObservacio

    # TEST: anular en apertura cerrada lanza error
    def test_anular_cerrada(self):
        from users.models import User
        from cash.models import Cash, CashOpening
        user = User.objects.create_user(usuNom="cajero20", usuContra="pass", usuEmail="cajero20@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Anular Cerrada")
        apertura = CashOpening.objects.create(cajCod=caja, usuCod=user, cajaAperMontInicial=Decimal('100.00'))
        apertura.cerrar_caja(monto_cierre=Decimal('100.00'))
        with pytest.raises(ValidationError):
            apertura.anular(motivo="No deberia")

    # TEST: total_ventas sin ventas devuelve 0
    def test_total_ventas_vacio(self):
        from users.models import User
        from cash.models import Cash, CashOpening
        user = User.objects.create_user(usuNom="cajero21", usuContra="pass", usuEmail="cajero21@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Ventas")
        apertura = CashOpening.objects.create(cajCod=caja, usuCod=user, cajaAperMontInicial=Decimal('100.00'))
        assert apertura.total_ventas == Decimal('0')

    # TEST: cantidad_ventas sin ventas devuelve 0
    def test_cantidad_ventas_vacio(self):
        from users.models import User
        from cash.models import Cash, CashOpening
        user = User.objects.create_user(usuNom="cajero22", usuContra="pass", usuEmail="cajero22@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Cant Ventas")
        apertura = CashOpening.objects.create(cajCod=caja, usuCod=user, cajaAperMontInicial=Decimal('100.00'))
        assert apertura.cantidad_ventas == 0

    # TEST: apertura sin observaciones es null
    def test_sin_observaciones(self):
        from users.models import User
        from cash.models import Cash, CashOpening
        user = User.objects.create_user(usuNom="cajero23", usuContra="pass", usuEmail="cajero23@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Sin Obs")
        apertura = CashOpening.objects.create(cajCod=caja, usuCod=user, cajaAperMontInicial=Decimal('50.00'))
        assert apertura.cajaAperObservacio is None

    # TEST: clean rechaza duplicate apertura activa mismo usuario
    def test_duplicado_apertura_mismo_usuario(self):
        from users.models import User
        from cash.models import Cash, CashOpening
        user = User.objects.create_user(usuNom="cajero24", usuContra="pass", usuEmail="cajero24@test.com")
        caja1 = Cash.objects.create(usuCod=user, cajNom="Caja Uno")
        caja2 = Cash.objects.create(usuCod=user, cajNom="Caja Dos")
        CashOpening.objects.create(cajCod=caja1, usuCod=user, cajaAperMontInicial=Decimal('100.00'))
        with pytest.raises(ValidationError):
            apertura2 = CashOpening(cajCod=caja2, usuCod=user, cajaAperMontInicial=Decimal('200.00'))
            apertura2.clean()

    # TEST: cerrar_caja calcula diferencia correcta
    def test_cerrar_caja_diferencia(self):
        from users.models import User
        from cash.models import Cash, CashOpening
        user = User.objects.create_user(usuNom="cajero25", usuContra="pass", usuEmail="cajero25@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Diferencia")
        apertura = CashOpening.objects.create(cajCod=caja, usuCod=user, cajaAperMontInicial=Decimal('1000.00'))
        apertura.cerrar_caja(monto_cierre=Decimal('1500.00'))
        apertura.refresh_from_db()
        assert apertura.cajaAperDiferencia == Decimal('500.00')
        assert apertura.cajaAperMontEsperado == Decimal('1000.00')

    # TEST: anular apertura con motivo vacio
    def test_anular_con_motivo_vacio(self):
        from users.models import User
        from cash.models import Cash, CashOpening
        user = User.objects.create_user(usuNom="cajero26", usuContra="pass", usuEmail="cajero26@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Anular Vacio")
        apertura = CashOpening.objects.create(cajCod=caja, usuCod=user, cajaAperMontInicial=Decimal('100.00'))
        apertura.anular(motivo="")
        apertura.refresh_from_db()
        assert apertura.cajaAperEstado == "ANULADA"

    # TEST: cerrar_caja con monto negativo
    def test_cerrar_caja_monto_negativo(self):
        from users.models import User
        from cash.models import Cash, CashOpening
        user = User.objects.create_user(usuNom="cajero27", usuContra="pass", usuEmail="cajero27@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Cierre Neg")
        apertura = CashOpening.objects.create(cajCod=caja, usuCod=user, cajaAperMontInicial=Decimal('500.00'))
        apertura.cerrar_caja(monto_cierre=Decimal('-100.00'))
        apertura.refresh_from_db()
        assert apertura.cajaAperEstado == "CERRADA"
        assert apertura.cajaAperDiferencia == Decimal('-600.00')


@pytest.mark.django_db
class TestCashSerializers:
    # TEST: CashSerializer con todos los campos
    def test_cash_serializer_all_fields(self):
        from users.models import User
        from cash.models import Cash
        from cash.serializers import CashSerializer
        user = User.objects.create_user(usuNom="cajero30", usuContra="pass", usuEmail="cajero30@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Serializer")
        serializer = CashSerializer(caja)
        assert serializer.data['cajNom'] == "Caja Serializer"
        assert serializer.data['cajCod'] == caja.cajCod
        assert serializer.data['usuCod'] == user.usuCod
        assert serializer.data['usuNom'] == user.usuNom
        assert serializer.data['cajEstado'] == "ACTIVO"

    # TEST: CashSerializer valid create data
    def test_cash_serializer_valid(self):
        from users.models import User
        from cash.serializers import CashSerializer
        user = User.objects.create_user(usuNom="cajero31", usuContra="pass", usuEmail="cajero31@test.com")
        data = {"usuCod": user.usuCod, "cajNom": "Nueva Caja", "cajEstado": "ACTIVO"}
        serializer = CashSerializer(data=data)
        assert serializer.is_valid()

    # TEST: CashSerializer invalid sin cajNom
    def test_cash_serializer_invalid_sin_nombre(self):
        from users.models import User
        from cash.serializers import CashSerializer
        user = User.objects.create_user(usuNom="cajero32", usuContra="pass", usuEmail="cajero32@test.com")
        data = {"usuCod": user.usuCod}
        serializer = CashSerializer(data=data)
        assert not serializer.is_valid()

    # TEST: CashOpeningSerializer con todos los campos
    def test_opening_serializer_all_fields(self):
        from users.models import User
        from cash.models import Cash, CashOpening
        from cash.serializers import CashOpeningSerializer
        user = User.objects.create_user(usuNom="cajero33", usuContra="pass", usuEmail="cajero33@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Serializer Opening")
        apertura = CashOpening.objects.create(cajCod=caja, usuCod=user, cajaAperMontInicial=Decimal('250.00'))
        serializer = CashOpeningSerializer(apertura)
        assert serializer.data['cajaAperMontInicial'] == "250.00"
        assert serializer.data['cajNom'] == "Caja Serializer Opening"
        assert serializer.data['usuNom'] == user.usuNom
        assert serializer.data['cajaAperEstado'] == "ABIERTA"
        assert 'usuCod' not in serializer.data or serializer.data.get('usuCod') is None

    # TEST: CashOpeningSerializer valid create data
    def test_opening_serializer_valid(self):
        from users.models import User
        from cash.models import Cash
        from cash.serializers import CashOpeningSerializer
        user = User.objects.create_user(usuNom="cajero34", usuContra="pass", usuEmail="cajero34@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Valid")
        data = {"cajCod": caja.cajCod, "cajaAperMontInicial": "100.00"}
        serializer = CashOpeningSerializer(data=data)
        assert serializer.is_valid()

    # TEST: CashOpeningSerializer invalid sin monto
    def test_opening_serializer_invalid_sin_monto(self):
        from cash.serializers import CashOpeningSerializer
        data = {}
        serializer = CashOpeningSerializer(data=data)
        assert not serializer.is_valid()


@pytest.mark.django_db
class TestCashViewSet:
    # CRUD del endpoint /api/cash/. Incluye caso de permisos: un usuario sin rol
    # asignado ve la lista vacía (test_list_sin_rol).
    # TEST: list sin autenticacion retorna 401
    def test_list_unauthenticated(self, api_client):
        resp = api_client.get("/api/cash/")
        assert resp.status_code == 401

    # TEST: list autenticado retorna 200
    def test_list_authenticated(self, api_client):
        from users.models import User
        user = User.objects.create_user(usuNom="cajero40", usuContra="pass", usuEmail="cajero40@test.com")
        api_client.force_authenticate(user=user)
        resp = api_client.get("/api/cash/")
        assert resp.status_code == 200

    # TEST: create cash
    def test_create_cash(self, api_client):
        from users.models import User, Role
        user = User.objects.create_user(usuNom="gerente40", usuContra="pass", usuEmail="gerente40@test.com")
        role = Role.objects.create(rolNom="GERENTE", rolDes="Gerente", rolNivel=0)
        user.roles.add(role)
        api_client.force_authenticate(user=user)
        data = {"usuCod": user.usuCod, "cajNom": "Caja Nueva", "cajEstado": "ACTIVO"}
        resp = api_client.post("/api/cash/", data, format="json")
        assert resp.status_code == 201
        assert resp.data["cajNom"] == "Caja Nueva"

    # TEST: retrieve cash
    def test_retrieve_cash(self, api_client):
        from users.models import User, Role
        from cash.models import Cash
        user = User.objects.create_user(usuNom="gerente41", usuContra="pass", usuEmail="gerente41@test.com")
        role = Role.objects.create(rolNom="GERENTE", rolDes="Gerente", rolNivel=0)
        user.roles.add(role)
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Retrieve")
        api_client.force_authenticate(user=user)
        resp = api_client.get(f"/api/cash/{caja.cajCod}/")
        assert resp.status_code == 200
        assert resp.data["cajNom"] == "Caja Retrieve"

    # TEST: update cash
    def test_update_cash(self, api_client):
        from users.models import User, Role
        from cash.models import Cash
        user = User.objects.create_user(usuNom="gerente42", usuContra="pass", usuEmail="gerente42@test.com")
        role = Role.objects.create(rolNom="GERENTE", rolDes="Gerente", rolNivel=0)
        user.roles.add(role)
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Update")
        api_client.force_authenticate(user=user)
        resp = api_client.put(f"/api/cash/{caja.cajCod}/", {"usuCod": user.usuCod, "cajNom": "Caja Actualizada", "cajEstado": "ACTIVO"}, format="json")
        assert resp.status_code == 200
        assert resp.data["cajNom"] == "Caja Actualizada"

    # TEST: partial update cash
    def test_partial_update_cash(self, api_client):
        from users.models import User, Role
        from cash.models import Cash
        user = User.objects.create_user(usuNom="gerente43", usuContra="pass", usuEmail="gerente43@test.com")
        role = Role.objects.create(rolNom="GERENTE", rolDes="Gerente", rolNivel=0)
        user.roles.add(role)
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Partial")
        api_client.force_authenticate(user=user)
        resp = api_client.patch(f"/api/cash/{caja.cajCod}/", {"cajDes": "Descripcion parcial"}, format="json")
        assert resp.status_code == 200
        assert resp.data["cajDes"] == "Descripcion parcial"

    # TEST: delete cash
    def test_destroy_cash(self, api_client):
        from users.models import User, Role
        from cash.models import Cash
        user = User.objects.create_user(usuNom="gerente44", usuContra="pass", usuEmail="gerente44@test.com")
        role = Role.objects.create(rolNom="GERENTE", rolDes="Gerente", rolNivel=0)
        user.roles.add(role)
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Delete")
        api_client.force_authenticate(user=user)
        resp = api_client.delete(f"/api/cash/{caja.cajCod}/")
        assert resp.status_code == 204

    # TEST: usuario sin rol ve lista vacia
    def test_list_sin_rol(self, api_client):
        from users.models import User
        from cash.models import Cash
        user = User.objects.create_user(usuNom="sinrol", usuContra="pass", usuEmail="sinrol@test.com")
        Cash.objects.create(usuCod=user, cajNom="Caja Invisible")
        api_client.force_authenticate(user=user)
        resp = api_client.get("/api/cash/")
        assert resp.status_code == 200
        assert len(resp.data) == 0


@pytest.mark.django_db
class TestCashOpeningViewSet:
    # CRUD de /api/cash/opening/ más las acciones custom: close (cerrar caja),
    # open (apertura actual del usuario), session_sales (ventas de la sesión
    # abierta) y by-cash (aperturas de una caja puntual).
    # TEST: list sin autenticacion retorna 401
    def test_list_unauthenticated(self, api_client):
        resp = api_client.get("/api/cash/opening/")
        assert resp.status_code == 401

    # TEST: list autenticado retorna 200
    def test_list_authenticated(self, api_client):
        from users.models import User
        user = User.objects.create_user(usuNom="cajero50", usuContra="pass", usuEmail="cajero50@test.com")
        api_client.force_authenticate(user=user)
        resp = api_client.get("/api/cash/opening/")
        assert resp.status_code == 200

    # TEST: create opening
    def test_create_opening(self, api_client):
        from users.models import User
        from cash.models import Cash
        user = User.objects.create_user(usuNom="cajero51", usuContra="pass", usuEmail="cajero51@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Crear Opening")
        api_client.force_authenticate(user=user)
        data = {"cajCod": caja.cajCod, "cajaAperMontInicial": "500.00"}
        resp = api_client.post("/api/cash/opening/", data, format="json")
        assert resp.status_code == 201
        assert resp.data["cajaAperMontInicial"] == "500.00"
        assert resp.data["cajaAperEstado"] == "ABIERTA"

    # TEST: retrieve opening
    def test_retrieve_opening(self, api_client):
        from users.models import User
        from cash.models import Cash, CashOpening
        user = User.objects.create_user(usuNom="cajero52", usuContra="pass", usuEmail="cajero52@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Retrieve Open")
        apertura = CashOpening.objects.create(cajCod=caja, usuCod=user, cajaAperMontInicial=Decimal('300.00'))
        api_client.force_authenticate(user=user)
        resp = api_client.get(f"/api/cash/opening/{apertura.cajaAperCod}/")
        assert resp.status_code == 200
        assert resp.data["cajaAperMontInicial"] == "300.00"

    # TEST: partial update opening
    def test_patch_opening(self, api_client):
        from users.models import User
        from cash.models import Cash, CashOpening
        user = User.objects.create_user(usuNom="cajero53", usuContra="pass", usuEmail="cajero53@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Patch Open")
        apertura = CashOpening.objects.create(cajCod=caja, usuCod=user, cajaAperMontInicial=Decimal('200.00'))
        api_client.force_authenticate(user=user)
        resp = api_client.patch(f"/api/cash/opening/{apertura.cajaAperCod}/", {"cajaAperObservacio": "Observacion"}, format="json")
        assert resp.status_code == 200

    # TEST: delete opening
    def test_destroy_opening(self, api_client):
        from users.models import User
        from cash.models import Cash, CashOpening
        user = User.objects.create_user(usuNom="cajero54", usuContra="pass", usuEmail="cajero54@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Delete Open")
        apertura = CashOpening.objects.create(cajCod=caja, usuCod=user, cajaAperMontInicial=Decimal('100.00'))
        api_client.force_authenticate(user=user)
        resp = api_client.delete(f"/api/cash/opening/{apertura.cajaAperCod}/")
        assert resp.status_code == 204

    # TEST: cerrar caja action
    def test_cerrar_caja_action(self, api_client):
        from users.models import User
        from cash.models import Cash, CashOpening
        user = User.objects.create_user(usuNom="cajero55", usuContra="pass", usuEmail="cajero55@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Close Action")
        CashOpening.objects.create(cajCod=caja, usuCod=user, cajaAperMontInicial=Decimal('1000.00'))
        api_client.force_authenticate(user=user)
        resp = api_client.post("/api/cash/opening/close/", {"cajaAperMontCierre": "1200.00"}, format="json")
        assert resp.status_code == 200

    # TEST: cerrar caja sin monto retorna 400
    def test_cerrar_caja_sin_monto(self, api_client):
        from users.models import User
        from cash.models import Cash, CashOpening
        user = User.objects.create_user(usuNom="cajero56", usuContra="pass", usuEmail="cajero56@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Close No Monto")
        CashOpening.objects.create(cajCod=caja, usuCod=user, cajaAperMontInicial=Decimal('500.00'))
        api_client.force_authenticate(user=user)
        resp = api_client.post("/api/cash/opening/close/", {}, format="json")
        assert resp.status_code == 400

    # TEST: cerrar caja sin apertura retorna 404
    def test_cerrar_caja_sin_apertura(self, api_client):
        from users.models import User
        user = User.objects.create_user(usuNom="cajero57", usuContra="pass", usuEmail="cajero57@test.com")
        api_client.force_authenticate(user=user)
        resp = api_client.post("/api/cash/opening/close/", {"cajaAperMontCierre": "100.00"}, format="json")
        assert resp.status_code == 404

    # TEST: abrir_actual retorna null sin apertura
    def test_abrir_actual_sin_apertura(self, api_client):
        from users.models import User
        user = User.objects.create_user(usuNom="cajero58", usuContra="pass", usuEmail="cajero58@test.com")
        api_client.force_authenticate(user=user)
        resp = api_client.get("/api/cash/opening/open/")
        assert resp.status_code == 200
        assert resp.data is None

    # TEST: abrir_actual retorna apertura existente
    def test_abrir_actual_con_apertura(self, api_client):
        from users.models import User
        from cash.models import Cash, CashOpening
        user = User.objects.create_user(usuNom="cajero59", usuContra="pass", usuEmail="cajero59@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Open Actual")
        CashOpening.objects.create(cajCod=caja, usuCod=user, cajaAperMontInicial=Decimal('100.00'))
        api_client.force_authenticate(user=user)
        resp = api_client.get("/api/cash/opening/open/")
        assert resp.status_code == 200
        assert resp.data["cajaAperEstado"] == "ABIERTA"

    # TEST: session_sales sin apertura retorna 400
    def test_session_sales_sin_apertura(self, api_client):
        from users.models import User
        user = User.objects.create_user(usuNom="cajero60", usuContra="pass", usuEmail="cajero60@test.com")
        api_client.force_authenticate(user=user)
        resp = api_client.get("/api/cash/opening/session_sales/")
        assert resp.status_code == 400

    # TEST: session_sales con apertura retorna 200
    def test_session_sales_con_apertura(self, api_client):
        from users.models import User
        from cash.models import Cash, CashOpening
        user = User.objects.create_user(usuNom="cajero61", usuContra="pass", usuEmail="cajero61@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Session Sales")
        CashOpening.objects.create(cajCod=caja, usuCod=user, cajaAperMontInicial=Decimal('500.00'))
        api_client.force_authenticate(user=user)
        resp = api_client.get("/api/cash/opening/session_sales/")
        assert resp.status_code == 200
        assert resp.data["total_ventas"] == 0.0
        assert resp.data["cantidad_ventas"] == 0

    # TEST: aperturas_por_caja retorna lista
    def test_aperturas_por_caja(self, api_client):
        from users.models import User
        from cash.models import Cash, CashOpening
        user = User.objects.create_user(usuNom="cajero62", usuContra="pass", usuEmail="cajero62@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja By Cash")
        CashOpening.objects.create(cajCod=caja, usuCod=user, cajaAperMontInicial=Decimal('100.00'))
        api_client.force_authenticate(user=user)
        resp = api_client.get(f"/api/cash/opening/by-cash/{caja.cajCod}/")
        assert resp.status_code == 200
        assert len(resp.data) == 1

    # TEST: create opening duplicado (misma caja) retorna 400
    def test_create_opening_duplicado_misma_caja(self, api_client):
        from users.models import User
        from cash.models import Cash, CashOpening
        user = User.objects.create_user(usuNom="cajero63", usuContra="pass", usuEmail="cajero63@test.com")
        caja = Cash.objects.create(usuCod=user, cajNom="Caja Dup Open")
        CashOpening.objects.create(cajCod=caja, usuCod=user, cajaAperMontInicial=Decimal('100.00'))
        api_client.force_authenticate(user=user)
        data = {"cajCod": caja.cajCod, "cajaAperMontInicial": "200.00"}
        resp = api_client.post("/api/cash/opening/", data, format="json")
        assert resp.status_code == 400


@pytest.mark.django_db
class TestCashUrls:
    # TEST: resolve cash list
    def test_cash_list_url(self):
        from django.urls import resolve
        resolver = resolve("/api/cash/")
        assert resolver.view_name == "cash-list"

    # TEST: resolve cash detail
    def test_cash_detail_url(self):
        from django.urls import resolve
        resolver = resolve("/api/cash/1/")
        assert resolver.view_name == "cash-detail"

    # TEST: resolve opening list
    def test_opening_list_url(self):
        from django.urls import resolve
        resolver = resolve("/api/cash/opening/")
        assert resolver.view_name == "cash-opening-list"

    # TEST: resolve opening detail
    def test_opening_detail_url(self):
        from django.urls import resolve
        resolver = resolve("/api/cash/opening/1/")
        assert resolver.view_name == "cash-opening-detail"

    # TEST: resolve cerrar_caja action
    def test_cerrar_caja_url(self):
        from django.urls import resolve
        resolver = resolve("/api/cash/opening/close/")
        assert resolver.view_name == "cash-opening-cerrar-caja"

    # TEST: resolve abrir_actual action
    def test_abrir_actual_url(self):
        from django.urls import resolve
        resolver = resolve("/api/cash/opening/open/")
        assert resolver.view_name == "cash-opening-abrir-actual"

    # TEST: resolve session_sales action
    def test_session_sales_url(self):
        from django.urls import resolve
        resolver = resolve("/api/cash/opening/session_sales/")
        assert resolver.view_name == "cash-opening-session-sales"

    # TEST: resolve aperturas_por_caja action
    def test_aperturas_por_caja_url(self):
        from django.urls import resolve
        resolver = resolve("/api/cash/opening/by-cash/1/")
        assert resolver.view_name == "cash-opening-aperturas-por-caja"
