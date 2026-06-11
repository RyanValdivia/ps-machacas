import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

pytestmark = pytest.mark.django_db


# ==================== FIXTURES ====================

@pytest.fixture
def categoria():
    from categories.models import ProductCategory
    return ProductCategory.objects.create(catproCode="MO", catproNom="Monturas")


@pytest.fixture
def proveedor():
    from suppliers.models import Supplier
    return Supplier.objects.create(provRazSocial="Proveedor Test", provRuc="12345678901", provTele="999888777")


@pytest.fixture
def producto(categoria, proveedor):
    from products.models import Product
    return Product.objects.create(
        catproCod=categoria,
        provCod=proveedor,
        prodDescr="Producto Test",
        prodMarca="MARCA",
        prodPrecioVenta=Decimal("100.00"),
        prodCostoInv=Decimal("50.00"),
        prodStock=10,
    )


@pytest.fixture
def usuario():
    from users.models import User
    return User.objects.create(
        usuNom="vendedor1",
        usuEmail="vendedor1@test.com",
        usuNombreCom="Vendedor Uno",
        password="testpass123",
    )


@pytest.fixture
def cliente():
    from clients.models import Client
    return Client.objects.create(
        cliTipoDoc="DNI",
        cliNumDoc="12345678",
        cliNomCompleto="Cliente Test",
    )


@pytest.fixture
def caja(usuario):
    from cash.models import Cash
    return Cash.objects.create(cajNom="Caja Principal", usuCod=usuario)


@pytest.fixture
def apertura_caja(caja, usuario):
    from cash.models import CashOpening
    return CashOpening.objects.create(
        cajCod=caja,
        usuCod=usuario,
        cajaAperMontInicial=Decimal("500.00"),
    )


@pytest.fixture
def venta(usuario, cliente, apertura_caja):
    from sales.models import Venta
    v = Venta.objects.create(
        usuCod=usuario,
        cliCod=cliente,
        cajaAperCod=apertura_caja,
        ventObservaciones="Test venta",
    )
    v.ventSubTotal = Decimal("200.00")
    v.ventDescuento = Decimal("20.00")
    v.ventTotal = Decimal("180.00")
    v.ventSaldo = Decimal("180.00")
    v.ventAdelanto = Decimal("0.00")
    v.save()
    return v


@pytest.fixture
def venta_detalle(venta, producto):
    from sales.models import VentaDetalle
    d = VentaDetalle.objects.create(
        ventCod=venta,
        prodCod=producto,
        ventDetCantidad=2,
        ventDetPrecioUni=Decimal("100.00"),
        ventDetSubtotal=Decimal("200.00"),
        ventDetDescuento=Decimal("20.00"),
        ventDetTotal=Decimal("180.00"),
    )
    return d


# ==================== VENTA MODEL TESTS ====================

# TEST: anular venta correctamente
def test_anular_venta(venta, venta_detalle, producto):
    producto.refresh_from_db()
    stock_antes = producto.prodStock
    venta.anular_venta("Test anulacion")
    venta.refresh_from_db()
    assert venta.ventAnulada is True
    assert venta.ventEstado == "ANULADO"
    assert venta.ventEstadoRecoj == "ANULADO"
    assert venta.ventTotal == Decimal("0")
    assert venta.ventSubTotal == Decimal("0")
    assert venta.ventMotivoAnulacion == "Test anulacion"
    producto.refresh_from_db()
    assert producto.prodStock == stock_antes + 2


# TEST: anular venta ya anulada
def test_anular_venta_ya_anulada(venta):
    venta.ventAnulada = True
    venta.save()
    with pytest.raises(ValidationError, match="ya esta anulada"):
        venta.anular_venta("otra")


# TEST: anular venta entregada
def test_anular_venta_entregada(venta):
    venta.ventEstadoRecoj = "ENTREGADO"
    venta.save()
    with pytest.raises(ValidationError, match="No se puede anular una venta ya entregada"):
        venta.anular_venta("motivo")


# TEST: establecer estado pedido con lunas personalizadas
def test_establecer_estado_pedido_con_lunas(venta, producto):
    from sales.models import VentaDetalle
    VentaDetalle.objects.create(
        ventCod=venta,
        prodCod=producto,
        ventDetCantidad=1,
        ventDetPrecioUni=Decimal("50.00"),
        ventDetSubtotal=Decimal("50.00"),
        ventDetTotal=Decimal("50.00"),
        esLunaPersonalizada=True,
        lunaMaterial="ORGANICO",
        lunaTipo="MONOFOCAL",
    )
    venta.establecer_estado_pedido_automatico()
    assert venta.ventEstadoRecoj == "PENDIENTE"


# TEST: establecer estado pedido sin lunas y saldo cero
def test_establecer_estado_pedido_sin_lunas_saldo_cero(venta):
    venta.ventSaldo = Decimal("0")
    venta.establecer_estado_pedido_automatico()
    assert venta.ventEstadoRecoj == "ENTREGADO"


# TEST: establecer estado pedido sin lunas y saldo positivo
def test_establecer_estado_pedido_sin_lunas_saldo_positivo(venta):
    venta.ventSaldo = Decimal("50.00")
    venta.establecer_estado_pedido_automatico()
    assert venta.ventEstadoRecoj == "LISTO"


# TEST: establecer estado pedido venta anulada
def test_establecer_estado_pedido_anulada(venta):
    venta.ventAnulada = True
    venta.ventEstadoRecoj = "ANULADO"
    venta.establecer_estado_pedido_automatico()
    assert venta.ventEstadoRecoj == "ANULADO"


# TEST: marcar listo para recoger
def test_marcar_listo_para_recoger(venta):
    venta.marcar_listo_para_recoger()
    venta.refresh_from_db()
    assert venta.ventEstadoRecoj == "LISTO"


# TEST: marcar listo venta anulada
def test_marcar_listo_anulada(venta):
    venta.ventAnulada = True
    venta.save()
    with pytest.raises(ValidationError, match="anulada"):
        venta.marcar_listo_para_recoger()


# TEST: marcar entregado
def test_marcar_entregado(venta):
    venta.ventSaldo = Decimal("0")
    venta.save()
    venta.marcar_entregado()
    venta.refresh_from_db()
    assert venta.ventEstadoRecoj == "ENTREGADO"
    assert venta.ventFechaEntrega == timezone.now().date()


# TEST: marcar entregado con saldo pendiente
def test_marcar_entregado_con_saldo(venta):
    venta.ventSaldo = Decimal("50.00")
    venta.save()
    with pytest.raises(ValidationError, match="saldo pendiente"):
        venta.marcar_entregado()


# TEST: marcar entregado venta anulada
def test_marcar_entregado_anulada(venta):
    venta.ventAnulada = True
    venta.save()
    with pytest.raises(ValidationError, match="anulada"):
        venta.marcar_entregado()


# TEST: calcular totales desde detalles
def test_calcular_totales(venta, venta_detalle):
    venta.calcular_totales()
    assert venta.ventSubTotal == Decimal("200.00")
    assert venta.ventDescuento == Decimal("20.00")
    assert venta.ventTotal == Decimal("180.00")
    assert venta.ventSaldo == Decimal("180.00")


# TEST: calcular totales sin detalles (reset)
def test_calcular_totales_sin_detalles(venta, venta_detalle):
    venta_detalle.delete()
    venta.calcular_totales()
    assert venta.ventSubTotal == Decimal("0")
    assert venta.ventDescuento == Decimal("0")
    assert venta.ventTotal == Decimal("0")
    assert venta.ventSaldo == Decimal("0")
    assert venta.ventEstado == "PENDIENTE"


# TEST: _actualizar_estado pendiente (saldo 0, total 0)
def test_actualizar_estado_pendiente(venta):
    venta.ventTotal = Decimal("0")
    venta.ventSaldo = Decimal("0")
    venta.ventAdelanto = Decimal("0")
    venta._actualizar_estado()
    assert venta.ventEstado == "PENDIENTE"


# TEST: _actualizar_estado pagado
def test_actualizar_estado_pagado(venta):
    venta.ventTotal = Decimal("180.00")
    venta.ventSaldo = Decimal("0")
    venta.ventAdelanto = Decimal("180.00")
    venta._actualizar_estado()
    assert venta.ventEstado == "PAGADO"


# TEST: _actualizar_estado parcial
def test_actualizar_estado_parcial(venta):
    venta.ventTotal = Decimal("180.00")
    venta.ventSaldo = Decimal("80.00")
    venta.ventAdelanto = Decimal("100.00")
    venta._actualizar_estado()
    assert venta.ventEstado == "PARCIAL"


# TEST: _actualizar_estado anulado
def test_actualizar_estado_anulado(venta):
    venta.ventAnulada = True
    venta._actualizar_estado()
    assert venta.ventEstado == "ANULADO"


# TEST: registrar pago completo
def test_registrar_pago(venta, apertura_caja):
    venta.ventTotal = Decimal("180.00")
    venta.ventSaldo = Decimal("180.00")
    venta.cajaAperCod = apertura_caja
    venta.save()
    resultado = venta.registrar_pago(
        monto=Decimal("180.00"),
        forma_pago="EFECTIVO",
    )
    venta.refresh_from_db()
    assert venta.ventAdelanto == Decimal("180.00")
    assert venta.ventSaldo == Decimal("0")
    assert resultado["estado"] == "PAGADO"
    assert "comprobante" in resultado


# TEST: registrar pago parcial
def test_registrar_pago_parcial(venta, apertura_caja):
    venta.ventTotal = Decimal("180.00")
    venta.ventSaldo = Decimal("180.00")
    venta.cajaAperCod = apertura_caja
    venta.save()
    resultado = venta.registrar_pago(
        monto=Decimal("100.00"),
        forma_pago="YAPE",
    )
    venta.refresh_from_db()
    assert venta.ventAdelanto == Decimal("100.00")
    assert venta.ventSaldo == Decimal("80.00")
    assert resultado["estado"] == "PARCIAL"
    assert "comprobante" not in resultado


# TEST: registrar pago excede saldo
def test_registrar_pago_excede_saldo(venta, apertura_caja):
    venta.ventSaldo = Decimal("50.00")
    venta.cajaAperCod = apertura_caja
    venta.save()
    with pytest.raises(ValidationError, match="excede el saldo"):
        venta.registrar_pago(monto=Decimal("100.00"), forma_pago="EFECTIVO")


# TEST: registrar pago monto cero
def test_registrar_pago_monto_cero(venta, apertura_caja):
    venta.cajaAperCod = apertura_caja
    venta.save()
    with pytest.raises(ValidationError, match="debe ser mayor a cero"):
        venta.registrar_pago(monto=Decimal("0"), forma_pago="EFECTIVO")


# TEST: registrar pago en venta anulada
def test_registrar_pago_venta_anulada(venta):
    venta.ventAnulada = True
    venta.save()
    with pytest.raises(ValidationError, match="anulada"):
        venta.registrar_pago(monto=Decimal("50.00"), forma_pago="EFECTIVO")


# TEST: registrar pago sin caja abierta
def test_registrar_pago_sin_caja(venta):
    venta.ventSaldo = Decimal("50.00")
    venta.cajaAperCod = None
    venta.save()
    with pytest.raises(ValidationError, match="No hay una sesion de caja abierta"):
        venta.registrar_pago(monto=Decimal("50.00"), forma_pago="EFECTIVO")


# TEST: save asigna caja automaticamente
def test_save_asigna_caja(apertura_caja):
    from users.models import User
    from sales.models import Venta
    user = User.objects.create(
        usuNom="test2", usuEmail="test2@test.com",
        usuNombreCom="Test2", password="pass",
    )
    v = Venta(usuCod=user)
    assert v.cajaAperCod is None
    v.save()
    v.refresh_from_db()
    assert v.cajaAperCod == apertura_caja


# TEST: nombre_cliente property
def test_nombre_cliente_property(venta, cliente):
    assert venta.nombre_cliente == cliente.cliNomCompleto


# TEST: nombre_cliente property sin cliente
def test_nombre_cliente_sin_cliente(venta, usuario, apertura_caja):
    from sales.models import Venta
    v = Venta.objects.create(usuCod=usuario, cajaAperCod=apertura_caja)
    assert v.nombre_cliente == "Cliente Generico"

