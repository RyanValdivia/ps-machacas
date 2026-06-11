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


# ==================== VENTA DETALLE TESTS ====================

# TEST: detalle calcular totales
def test_detalle_calcular_totales(venta_detalle):
    venta_detalle._calcular_totales()
    assert venta_detalle.ventDetSubtotal == Decimal("200.00")
    assert venta_detalle.ventDetTotal == Decimal("180.00")


# TEST: detalle copiar datos desde producto
def test_detalle_copiar_datos_producto(venta_detalle, producto):
    venta_detalle.ventDetPrecioUni = None
    venta_detalle.ventDetDescripcion = ""
    venta_detalle._copiar_datos_producto()
    assert venta_detalle.ventDetPrecioUni == Decimal("100.00")
    assert venta_detalle.ventDetDescripcion == producto.prodDescr
    assert venta_detalle.ventDetMarca == "MARCA"


# TEST: detalle copiar datos luna personalizada completa
def test_detalle_copiar_datos_luna_personalizada(venta, producto):
    from sales.models import VentaDetalle
    d = VentaDetalle(
        ventCod=venta,
        prodCod=producto,
        ventDetCantidad=1,
        ventDetPrecioUni=Decimal("200.00"),
        esLunaPersonalizada=True,
        lunaMaterial="ORGANICO",
        lunaTipo="MONOFOCAL",
        lunaCaracteristicas="Blue Block, Antireflejo",
    )
    d._copiar_datos_producto()
    assert "LUNA" in d.ventDetDescripcion
    assert "ORGANICO" in d.ventDetDescripcion
    assert "MONOFOCAL" in d.ventDetDescripcion
    assert d.ventDetMarca == "PERSONALIZADO"


# TEST: detalle copiar datos luna personalizada incompleta
def test_detalle_copiar_datos_luna_incompleta(venta, producto):
    from sales.models import VentaDetalle
    d = VentaDetalle(
        ventCod=venta,
        prodCod=producto,
        ventDetCantidad=1,
        esLunaPersonalizada=True,
    )
    d._copiar_datos_producto()
    assert d.ventDetDescripcion == "LUNA PERSONALIZADA"
    assert d.ventDetMarca == "PERSONALIZADO"


# TEST: detalle devolver stock
def test_detalle_devolver_stock(venta_detalle, producto):
    producto.refresh_from_db()
    stock_antes = producto.prodStock
    venta_detalle.devolver_stock()
    producto.refresh_from_db()
    assert producto.prodStock == stock_antes + 2


# TEST: detalle validar stock insuficiente
def test_detalle_validar_stock_insuficiente(venta, producto):
    from sales.models import VentaDetalle
    producto.prodStock = 1
    producto.save()
    d = VentaDetalle(
        ventCod=venta,
        prodCod=producto,
        ventDetCantidad=5,
        ventDetPrecioUni=Decimal("10.00"),
    )
    with pytest.raises(ValidationError, match="Stock insuficiente"):
        d.clean()


# TEST: detalle validar stock suficiente
def test_detalle_validar_stock_suficiente(venta, producto):
    from sales.models import VentaDetalle
    d = VentaDetalle(
        ventCod=venta,
        prodCod=producto,
        ventDetCantidad=1,
        ventDetPrecioUni=Decimal("10.00"),
    )
    d.clean()


# TEST: detalle no valida stock para luna personalizada
def test_detalle_validar_stock_luna(venta, producto):
    from sales.models import VentaDetalle
    d = VentaDetalle(
        ventCod=venta,
        prodCod=producto,
        ventDetCantidad=999,
        ventDetPrecioUni=Decimal("200.00"),
        esLunaPersonalizada=True,
    )
    d.clean()


# TEST: detalle save actualiza stock
def test_detalle_save_actualiza_stock(venta, producto):
    from sales.models import VentaDetalle
    producto.refresh_from_db()
    stock_antes = producto.prodStock
    d = VentaDetalle.objects.create(
        ventCod=venta,
        prodCod=producto,
        ventDetCantidad=3,
        ventDetPrecioUni=Decimal("50.00"),
    )
    producto.refresh_from_db()
    assert producto.prodStock == stock_antes - 3


# TEST: detalle save luna personalizada no descuenta stock
def test_detalle_save_luna_no_resta_stock(venta, producto):
    from sales.models import VentaDetalle
    producto.refresh_from_db()
    stock_antes = producto.prodStock
    VentaDetalle.objects.create(
        ventCod=venta,
        prodCod=producto,
        ventDetCantidad=1,
        ventDetPrecioUni=Decimal("200.00"),
        esLunaPersonalizada=True,
    )
    producto.refresh_from_db()
    assert producto.prodStock == stock_antes


# ==================== COMPROBANTE TESTS ====================

# TEST: comprobante asignar correlativo inicial
def test_comprobante_correlativo_inicial(venta):
    from sales.models import Comprobante
    c = Comprobante(ventCod=venta)
    c._asignar_correlativo()
    assert c.comprCorrelativo == 1
    assert c.comprSerie == "NV01"


# TEST: comprobante asignar correlativo siguiente
def test_comprobante_correlativo_siguiente(venta):
    from sales.models import Comprobante
    c1 = Comprobante.objects.create(ventCod=venta)
    venta2 = Venta.objects.get(pk=venta.pk)
    # Need a different venta for second comprobante
    from users.models import User
    from cash.models import CashOpening
    user2 = User.objects.create(usuNom="test3", usuEmail="test3@test.com", usuNombreCom="Test3", password="pass")
    co = CashOpening.objects.first()
    venta2 = venta.__class__.objects.create(usuCod=user2, cajaAperCod=co)
    c2 = Comprobante(ventCod=venta2)
    c2._asignar_correlativo()
    assert c2.comprCorrelativo == 2


# TEST: comprobante copiar datos de venta con cliente
def test_comprobante_copiar_datos_venta(venta, cliente):
    from sales.models import Comprobante
    c = Comprobante(ventCod=venta)
    c._copiar_datos_venta()
    assert c.comprNombreCliente == cliente.cliNomCompleto
    assert c.comprDocumentoCliente == f"DNI: {cliente.cliNumDoc}"
    assert c.comprSubtotal == venta.ventSubTotal
    assert c.comprDescuento == venta.ventDescuento
    assert c.comprTotal == venta.ventTotal


# TEST: comprobante copiar datos de venta sin cliente
def test_comprobante_copiar_datos_venta_sin_cliente(usuario, apertura_caja):
    from sales.models import Venta, Comprobante
    v = Venta.objects.create(usuCod=usuario, cajaAperCod=apertura_caja)
    c = Comprobante(ventCod=v)
    c._copiar_datos_venta()
    assert c.comprNombreCliente == "Cliente Generico"
    assert c.comprDocumentoCliente == ""


# TEST: comprobante completo property
def test_comprobante_completo_property(venta):
    from sales.models import Comprobante
    c = Comprobante.objects.create(ventCod=venta)
    assert c.comprobante_completo == f"NV01-{str(c.comprCorrelativo).zfill(8)}"


# ==================== SERIALIZER TESTS ====================

# TEST: VentaDetalleCreateSerializer validate cantidad
def test_serializer_valida_cantidad_cero():
    from sales.serializers import VentaDetalleCreateSerializer
    s = VentaDetalleCreateSerializer(data={"ventDetCantidad": 0})
    assert not s.is_valid()
    assert "ventDetCantidad" in s.errors


# TEST: VentaDetalleCreateSerializer validate stock insuficiente
def test_serializer_valida_stock(producto):
    from sales.serializers import VentaDetalleCreateSerializer
    producto.prodStock = 0
    producto.save()
    data = {
        "prodCod": producto.prodCod,
        "ventDetCantidad": 1,
        "esLunaPersonalizada": False,
    }
    s = VentaDetalleCreateSerializer(data=data)
    assert not s.is_valid()
    assert "ventDetCantidad" in s.errors


# TEST: VentaDetalleCreateSerializer requiere precio para lunas
def test_serializer_luna_requiere_precio(producto):
    from sales.serializers import VentaDetalleCreateSerializer
    data = {
        "prodCod": producto.prodCod,
        "ventDetCantidad": 1,
        "esLunaPersonalizada": True,
    }
    s = VentaDetalleCreateSerializer(data=data)
    assert not s.is_valid()
    assert "ventDetPrecioUni" in s.errors


# TEST: PagoSerializer valida monto
def test_pago_serializer_valida_monto():
    from sales.serializers import PagoSerializer
    s = PagoSerializer(data={"monto": 0, "forma_pago": "EFECTIVO"})
    assert not s.is_valid()


# TEST: PagoSerializer valida forma_pago
def test_pago_serializer_valida_forma_pago():
    from sales.serializers import PagoSerializer
    s = PagoSerializer(data={"monto": 100, "forma_pago": "INVALIDO"})
    assert not s.is_valid()


# TEST: VentaCreateSerializer valida detalles vacios
def test_venta_create_serializer_valida_detalles():
    from sales.serializers import VentaCreateSerializer
    s = VentaCreateSerializer(data={"detalles": []})
    assert not s.is_valid()
    assert "detalles" in s.errors


# TEST: LunaCaracteristicasField convierte array a string
def test_luna_caracteristicas_field_to_internal_value_lista_vacia():
    from sales.serializers import LunaCaracteristicasField
    field = LunaCaracteristicasField()
    assert field.to_internal_value([]) == ""
    assert field.to_internal_value("texto") == "texto"
    assert field.to_internal_value(None) == ""


# ==================== FILTER TESTS ====================

# TEST: VentaFilter cliente_nombre
def test_filter_cliente_nombre(venta, cliente):
    from sales.filters import VentaFilter
    from sales.models import Venta
    qs = Venta.objects.all()
    f = VentaFilter(data={"cliente_nombre": "Cliente Test"}, queryset=qs)
    assert f.is_valid()
    assert venta.ventCod in [v.ventCod for v in f.qs]


# TEST: VentaFilter cliente_nombre sin match
def test_filter_cliente_nombre_sin_match(venta):
    from sales.filters import VentaFilter
    from sales.models import Venta
    qs = Venta.objects.all()
    f = VentaFilter(data={"cliente_nombre": "No Existe"}, queryset=qs)
    assert f.is_valid()
    assert f.qs.count() == 0


# TEST: VentaFilter cliente_doc
def test_filter_cliente_doc(venta, cliente):
    from sales.filters import VentaFilter
    from sales.models import Venta
    qs = Venta.objects.all()
    f = VentaFilter(data={"cliente_doc": "12345678"}, queryset=qs)
    assert f.is_valid()
    assert venta.ventCod in [v.ventCod for v in f.qs]


# TEST: VentaFilter vendedor
def test_filter_vendedor(venta, usuario):
    from sales.filters import VentaFilter
    from sales.models import Venta
    qs = Venta.objects.all()
    f = VentaFilter(data={"vendedor": "vendedor1"}, queryset=qs)
    assert f.is_valid()
    assert venta.ventCod in [v.ventCod for v in f.qs]


# TEST: VentaFilter estado
def test_filter_estado(venta):
    from sales.filters import VentaFilter
    from sales.models import Venta
    qs = Venta.objects.all()
    f = VentaFilter(data={"estado": "PENDIENTE"}, queryset=qs)
    assert f.is_valid()
    assert venta.ventCod in [v.ventCod for v in f.qs]


# TEST: VentaFilter con_saldo true
def test_filter_con_saldo_true(venta):
    from sales.filters import VentaFilter
    from sales.models import Venta
    venta.ventSaldo = Decimal("100.00")
    venta.save()
    qs = Venta.objects.all()
    f = VentaFilter(data={"con_saldo": True}, queryset=qs)
    assert f.is_valid()
    assert f.qs.count() == 1


# TEST: VentaFilter con_saldo false
def test_filter_con_saldo_false(venta):
    from sales.filters import VentaFilter
    from sales.models import Venta
    venta.ventSaldo = Decimal("0")
    venta.save()
    qs = Venta.objects.all()
    f = VentaFilter(data={"con_saldo": False}, queryset=qs)
    assert f.is_valid()
    assert f.qs.count() == 1


# TEST: VentaFilter forma_pago
def test_filter_forma_pago(venta):
    from sales.filters import VentaFilter
    from sales.models import Venta
    venta.ventFormaPago = "EFECTIVO"
    venta.save()
    qs = Venta.objects.all()
    f = VentaFilter(data={"forma_pago": "EFECTIVO"}, queryset=qs)
    assert f.is_valid()
    assert venta.ventCod in [v.ventCod for v in f.qs]


# TEST: VentaFilter total_min
def test_filter_total_min(venta):
    from sales.filters import VentaFilter
    from sales.models import Venta
    venta.ventTotal = Decimal("180.00")
    venta.save()
    qs = Venta.objects.all()
    f = VentaFilter(data={"total_min": 100}, queryset=qs)
    assert f.is_valid()
    assert venta.ventCod in [v.ventCod for v in f.qs]


# TEST: VentaFilter total_max
def test_filter_total_max(venta):
    from sales.filters import VentaFilter
    from sales.models import Venta
    venta.ventTotal = Decimal("180.00")
    venta.save()
    qs = Venta.objects.all()
    f = VentaFilter(data={"total_max": 200}, queryset=qs)
    assert f.is_valid()
    assert venta.ventCod in [v.ventCod for v in f.qs]


# TEST: VentaFilter anuladas
def test_filter_anuladas(venta):
    from sales.filters import VentaFilter
    from sales.models import Venta
    qs = Venta.objects.all()
    f = VentaFilter(data={"anuladas": False}, queryset=qs)
    assert f.is_valid()
    assert venta.ventCod in [v.ventCod for v in f.qs]


# TEST: VentaFilter fecha_desde y fecha_hasta
def test_filter_fechas(venta):
    from sales.filters import VentaFilter
    from sales.models import Venta
    desde = (timezone.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    hasta = (timezone.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    qs = Venta.objects.all()
    f = VentaFilter(data={"fecha_desde": desde, "fecha_hasta": hasta}, queryset=qs)
    assert f.is_valid()
    assert venta.ventCod in [v.ventCod for v in f.qs]
