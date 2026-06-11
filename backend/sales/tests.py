from django.test import TestCase
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta


class TestVentaModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        from categories.models import ProductCategory
        from suppliers.models import Supplier
        from products.models import Product
        from users.models import User
        from clients.models import Client
        from cash.models import Cash, CashOpening
        from sales.models import Venta, VentaDetalle
        cls.categoria, _ = ProductCategory.objects.get_or_create(catproCode="MO", defaults={"catproNom": "Monturas"})
        cls.proveedor = Supplier.objects.create(provRazSocial="Proveedor Test", provRuc="12345678901", provTele="999888777")
        cls.producto = Product.objects.create(
            catproCod=cls.categoria, provCod=cls.proveedor,
            prodDescr="Producto Test", prodMarca="MARCA",
            prodPrecioVenta=Decimal("100.00"), prodCostoInv=Decimal("50.00"), prodStock=10,
            prodMate="A", prodTalla="54-18-140",
        )
        cls.usuario = User.objects.create(
            usuNom="vendedor1", usuEmail="vendedor1@test.com",
            usuNombreCom="Vendedor Uno", password="testpass123",
        )
        cls.cliente = Client.objects.create(cliTipoDoc="DNI", cliNumDoc="12345678", cliNomCompleto="Cliente Test")
        cls.caja = Cash.objects.create(cajNom="Caja Principal", usuCod=cls.usuario)
        cls.apertura_caja = CashOpening.objects.create(cajCod=cls.caja, usuCod=cls.usuario, cajaAperMontInicial=Decimal("500.00"))
        cls.venta = Venta.objects.create(usuCod=cls.usuario, cliCod=cls.cliente, cajaAperCod=cls.apertura_caja)
        cls.venta.ventSubTotal = Decimal("200.00")
        cls.venta.ventDescuento = Decimal("20.00")
        cls.venta.ventTotal = Decimal("180.00")
        cls.venta.ventSaldo = Decimal("180.00")
        cls.venta.ventAdelanto = Decimal("0.00")
        cls.venta.save()
        cls.detalle = VentaDetalle.objects.create(
            ventCod=cls.venta, prodCod=cls.producto,
            ventDetCantidad=2, ventDetPrecioUni=Decimal("100.00"),
            ventDetSubtotal=Decimal("200.00"), ventDetDescuento=Decimal("20.00"),
            ventDetTotal=Decimal("180.00"),
        )

    # TEST: anular venta correctamente
    def test_anular_venta(self):
        from products.models import Product
        stock_antes = Product.objects.get(pk=self.producto.pk).prodStock
        self.venta.anular_venta("Test anulacion")
        self.venta.refresh_from_db()
        assert self.venta.ventAnulada is True
        assert self.venta.ventEstado == "ANULADO"
        assert self.venta.ventEstadoRecoj == "ANULADO"
        assert self.venta.ventTotal == Decimal("0")
        assert self.venta.ventSubTotal == Decimal("0")
        assert self.venta.ventMotivoAnulacion == "Test anulacion"
        assert Product.objects.get(pk=self.producto.pk).prodStock == stock_antes + 2

    # TEST: anular venta ya anulada
    def test_anular_venta_ya_anulada(self):
        self.venta.ventAnulada = True
        self.venta.save()
        with self.assertRaises(ValidationError) as ctx:
            self.venta.anular_venta("otra")
        assert "ya esta anulada" in str(ctx.exception)

    # TEST: anular venta entregada
    def test_anular_venta_entregada(self):
        self.venta.ventEstadoRecoj = "ENTREGADO"
        self.venta.save()
        with self.assertRaises(ValidationError) as ctx:
            self.venta.anular_venta("motivo")
        assert "No se puede anular una venta ya entregada" in str(ctx.exception)

    # TEST: establecer estado pedido con lunas personalizadas
    def test_establecer_estado_pedido_con_lunas(self):
        from sales.models import VentaDetalle
        VentaDetalle.objects.create(
            ventCod=self.venta, prodCod=self.producto,
            ventDetCantidad=1, ventDetPrecioUni=Decimal("50.00"),
            ventDetSubtotal=Decimal("50.00"), ventDetTotal=Decimal("50.00"),
            esLunaPersonalizada=True, lunaMaterial="ORGANICO", lunaTipo="MONOFOCAL",
        )
        self.venta.establecer_estado_pedido_automatico()
        assert self.venta.ventEstadoRecoj == "PENDIENTE"

    # TEST: establecer estado pedido sin lunas, saldo cero
    def test_establecer_estado_pedido_sin_lunas_saldo_cero(self):
        self.venta.ventSaldo = Decimal("0")
        self.venta.establecer_estado_pedido_automatico()
        assert self.venta.ventEstadoRecoj == "ENTREGADO"

    # TEST: establecer estado pedido sin lunas, saldo positivo
    def test_establecer_estado_pedido_sin_lunas_saldo_positivo(self):
        self.venta.ventSaldo = Decimal("50.00")
        self.venta.establecer_estado_pedido_automatico()
        assert self.venta.ventEstadoRecoj == "LISTO"

    # TEST: establecer estado pedido no cambia venta anulada
    def test_establecer_estado_pedido_anulada(self):
        self.venta.ventAnulada = True
        self.venta.ventEstadoRecoj = "ANULADO"
        self.venta.establecer_estado_pedido_automatico()
        assert self.venta.ventEstadoRecoj == "ANULADO"

    # TEST: marcar listo para recoger
    def test_marcar_listo_para_recoger(self):
        self.venta.marcar_listo_para_recoger()
        self.venta.refresh_from_db()
        assert self.venta.ventEstadoRecoj == "LISTO"

    # TEST: marcar listo falla si anulada
    def test_marcar_listo_anulada(self):
        self.venta.ventAnulada = True
        self.venta.save()
        with self.assertRaises(ValidationError) as ctx:
            self.venta.marcar_listo_para_recoger()
        assert "anulada" in str(ctx.exception)

    # TEST: marcar entregado correctamente
    def test_marcar_entregado(self):
        self.venta.ventSaldo = Decimal("0")
        self.venta.save()
        self.venta.marcar_entregado()
        self.venta.refresh_from_db()
        assert self.venta.ventEstadoRecoj == "ENTREGADO"
        assert self.venta.ventFechaEntrega == timezone.now().date()

    # TEST: marcar entregado falla con saldo pendiente
    def test_marcar_entregado_con_saldo(self):
        self.venta.ventSaldo = Decimal("50.00")
        self.venta.save()
        with self.assertRaises(ValidationError) as ctx:
            self.venta.marcar_entregado()
        assert "saldo pendiente" in str(ctx.exception)

    # TEST: marcar entregado falla si anulada
    def test_marcar_entregado_anulada(self):
        self.venta.ventAnulada = True
        self.venta.save()
        with self.assertRaises(ValidationError) as ctx:
            self.venta.marcar_entregado()
        assert "anulada" in str(ctx.exception)

    # TEST: calcular totales desde detalles
    def test_calcular_totales(self):
        self.venta.calcular_totales()
        assert self.venta.ventSubTotal == Decimal("200.00")
        assert self.venta.ventDescuento == Decimal("20.00")
        assert self.venta.ventTotal == Decimal("180.00")
        assert self.venta.ventSaldo == Decimal("180.00")

    # TEST: calcular totales sin detalles resetea
    def test_calcular_totales_sin_detalles(self):
        self.detalle.delete()
        self.venta.calcular_totales()
        assert self.venta.ventSubTotal == Decimal("0")
        assert self.venta.ventDescuento == Decimal("0")
        assert self.venta.ventTotal == Decimal("0")
        assert self.venta.ventSaldo == Decimal("0")
        assert self.venta.ventEstado == "PENDIENTE"

    # TEST: _actualizar_estado pendiente
    def test_actualizar_estado_pendiente(self):
        self.venta.ventTotal = Decimal("0")
        self.venta.ventSaldo = Decimal("0")
        self.venta.ventAdelanto = Decimal("0")
        self.venta._actualizar_estado()
        assert self.venta.ventEstado == "PENDIENTE"

    # TEST: _actualizar_estado pagado
    def test_actualizar_estado_pagado(self):
        self.venta.ventTotal = Decimal("180.00")
        self.venta.ventSaldo = Decimal("0")
        self.venta.ventAdelanto = Decimal("180.00")
        self.venta._actualizar_estado()
        assert self.venta.ventEstado == "PAGADO"

    # TEST: _actualizar_estado parcial
    def test_actualizar_estado_parcial(self):
        self.venta.ventTotal = Decimal("180.00")
        self.venta.ventSaldo = Decimal("80.00")
        self.venta.ventAdelanto = Decimal("100.00")
        self.venta._actualizar_estado()
        assert self.venta.ventEstado == "PARCIAL"

    # TEST: _actualizar_estado anulado
    def test_actualizar_estado_anulado(self):
        self.venta.ventAnulada = True
        self.venta._actualizar_estado()
        assert self.venta.ventEstado == "ANULADO"

    # TEST: registrar pago completo genera comprobante
    def test_registrar_pago(self):
        self.venta.ventTotal = Decimal("180.00")
        self.venta.ventSaldo = Decimal("180.00")
        self.venta.save()
        resultado = self.venta.registrar_pago(monto=Decimal("180.00"), forma_pago="EFECTIVO")
        self.venta.refresh_from_db()
        assert self.venta.ventAdelanto == Decimal("180.00")
        assert self.venta.ventSaldo == Decimal("0")
        assert resultado["estado"] == "PAGADO"
        assert "comprobante" in resultado

    # TEST: registrar pago parcial no genera comprobante
    def test_registrar_pago_parcial(self):
        self.venta.ventTotal = Decimal("180.00")
        self.venta.ventSaldo = Decimal("180.00")
        self.venta.save()
        resultado = self.venta.registrar_pago(monto=Decimal("100.00"), forma_pago="YAPE")
        self.venta.refresh_from_db()
        assert self.venta.ventAdelanto == Decimal("100.00")
        assert self.venta.ventSaldo == Decimal("80.00")
        assert resultado["estado"] == "PARCIAL"
        assert "comprobante" not in resultado

    # TEST: registrar pago excede saldo
    def test_registrar_pago_excede_saldo(self):
        self.venta.ventSaldo = Decimal("50.00")
        self.venta.save()
        with self.assertRaises(ValidationError) as ctx:
            self.venta.registrar_pago(monto=Decimal("100.00"), forma_pago="EFECTIVO")
        assert "excede el saldo" in str(ctx.exception)

    # TEST: registrar pago monto cero
    def test_registrar_pago_monto_cero(self):
        with self.assertRaises(ValidationError) as ctx:
            self.venta.registrar_pago(monto=Decimal("0"), forma_pago="EFECTIVO")
        assert "debe ser mayor a cero" in str(ctx.exception)

    # TEST: registrar pago en venta anulada
    def test_registrar_pago_venta_anulada(self):
        self.venta.ventAnulada = True
        self.venta.save()
        with self.assertRaises(ValidationError) as ctx:
            self.venta.registrar_pago(monto=Decimal("50.00"), forma_pago="EFECTIVO")
        assert "anulada" in str(ctx.exception)

    # TEST: registrar pago sin caja abierta
    def test_registrar_pago_sin_caja(self):
        self.apertura_caja.cajaAperEstado = 'CERRADA'
        self.apertura_caja.save()
        with self.assertRaises(ValidationError) as ctx:
            self.venta.registrar_pago(monto=Decimal("50.00"), forma_pago="EFECTIVO")
        assert "No hay una sesion de caja abierta" in str(ctx.exception)

    # TEST: save asigna caja automaticamente
    def test_save_asigna_caja(self):
        from users.models import User
        from sales.models import Venta
        user = User.objects.create(usuNom="test2", usuEmail="test2@test.com", usuNombreCom="Test2", password="pass")
        v = Venta(usuCod=user)
        assert v.cajaAperCod is None
        v.save()
        v.refresh_from_db()
        assert v.cajaAperCod == self.apertura_caja

    # TEST: nombre_cliente property
    def test_nombre_cliente_property(self):
        assert self.venta.nombre_cliente == self.cliente.cliNomCompleto

    # TEST: nombre_cliente property sin cliente
    def test_nombre_cliente_sin_cliente(self):
        from sales.models import Venta
        v = Venta.objects.create(usuCod=self.usuario, cajaAperCod=self.apertura_caja)
        assert v.nombre_cliente == "Cliente Generico"


class TestVentaDetalleModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        from categories.models import ProductCategory
        from suppliers.models import Supplier
        from products.models import Product
        from users.models import User
        from cash.models import Cash, CashOpening
        from sales.models import Venta, VentaDetalle
        cls.categoria, _ = ProductCategory.objects.get_or_create(catproCode="AC", defaults={"catproNom": "Accesorios"})
        cls.proveedor = Supplier.objects.create(provRazSocial="Prov Test", provRuc="98765432101", provTele="999888111")
        cls.producto = Product.objects.create(
            catproCod=cls.categoria, provCod=cls.proveedor,
            prodDescr="Producto Test", prodMarca="MARCA",
            prodPrecioVenta=Decimal("100.00"), prodCostoInv=Decimal("50.00"), prodStock=10,
        )
        cls.usuario = User.objects.create(usuNom="testdet", usuEmail="testdet@test.com", usuNombreCom="Test", password="pass")
        cls.caja = Cash.objects.create(cajNom="Caja Det", usuCod=cls.usuario)
        cls.apertura = CashOpening.objects.create(cajCod=cls.caja, usuCod=cls.usuario, cajaAperMontInicial=Decimal("100"))
        cls.venta = Venta.objects.create(usuCod=cls.usuario, cajaAperCod=cls.apertura)
        cls.detalle = VentaDetalle.objects.create(
            ventCod=cls.venta, prodCod=cls.producto,
            ventDetCantidad=2, ventDetPrecioUni=Decimal("100.00"),
            ventDetSubtotal=Decimal("200.00"), ventDetDescuento=Decimal("20.00"),
            ventDetTotal=Decimal("180.00"),
        )

    # TEST: detalle calcular totales
    def test_detalle_calcular_totales(self):
        self.detalle._calcular_totales()
        assert self.detalle.ventDetSubtotal == Decimal("200.00")
        assert self.detalle.ventDetTotal == Decimal("180.00")

    # TEST: detalle copiar datos desde producto
    def test_detalle_copiar_datos_producto(self):
        self.detalle.ventDetPrecioUni = None
        self.detalle.ventDetDescripcion = ""
        self.detalle.ventDetMarca = ""
        self.detalle._copiar_datos_producto()
        assert self.detalle.ventDetPrecioUni == Decimal("100.00")
        assert self.detalle.ventDetDescripcion == self.producto.prodDescr
        assert self.detalle.ventDetMarca == "MARCA"

    # TEST: detalle copiar datos luna personalizada completa
    def test_detalle_copiar_datos_luna_personalizada(self):
        from sales.models import VentaDetalle
        d = VentaDetalle(
            ventCod=self.venta, prodCod=self.producto, ventDetCantidad=1,
            ventDetPrecioUni=Decimal("200.00"), esLunaPersonalizada=True,
            lunaMaterial="ORGANICO", lunaTipo="MONOFOCAL",
            lunaCaracteristicas="Blue Block, Antireflejo",
        )
        d._copiar_datos_producto()
        assert "LUNA" in d.ventDetDescripcion
        assert "ORGANICO" in d.ventDetDescripcion
        assert "MONOFOCAL" in d.ventDetDescripcion
        assert d.ventDetMarca == "PERSONALIZADO"

    # TEST: detalle copiar datos luna incompleta
    def test_detalle_copiar_datos_luna_incompleta(self):
        from sales.models import VentaDetalle
        d = VentaDetalle(
            ventCod=self.venta, prodCod=self.producto,
            ventDetCantidad=1, esLunaPersonalizada=True,
        )
        d._copiar_datos_producto()
        assert d.ventDetDescripcion == "LUNA PERSONALIZADA"
        assert d.ventDetMarca == "PERSONALIZADO"

    # TEST: detalle devolver stock
    def test_detalle_devolver_stock(self):
        from products.models import Product
        stock_antes = Product.objects.get(pk=self.producto.pk).prodStock
        self.detalle.devolver_stock()
        assert Product.objects.get(pk=self.producto.pk).prodStock == stock_antes + 2

    # TEST: detalle validar stock insuficiente
    def test_detalle_validar_stock_insuficiente(self):
        from sales.models import VentaDetalle
        self.producto.prodStock = 1
        self.producto.save()
        d = VentaDetalle(ventCod=self.venta, prodCod=self.producto, ventDetCantidad=5, ventDetPrecioUni=Decimal("10.00"))
        with self.assertRaises(ValidationError) as ctx:
            d.clean()
        assert "Stock insuficiente" in str(ctx.exception)

    # TEST: detalle validar stock suficiente
    def test_detalle_validar_stock_suficiente(self):
        from sales.models import VentaDetalle
        d = VentaDetalle(ventCod=self.venta, prodCod=self.producto, ventDetCantidad=1, ventDetPrecioUni=Decimal("10.00"))
        d.clean()

    # TEST: detalle no valida stock para luna personalizada
    def test_detalle_validar_stock_luna(self):
        from sales.models import VentaDetalle
        d = VentaDetalle(
            ventCod=self.venta, prodCod=self.producto,
            ventDetCantidad=999, ventDetPrecioUni=Decimal("200.00"),
            esLunaPersonalizada=True,
        )
        d.clean()

    # TEST: detalle save actualiza stock
    def test_detalle_save_actualiza_stock(self):
        from products.models import Product
        from sales.models import VentaDetalle
        stock_antes = Product.objects.get(pk=self.producto.pk).prodStock
        VentaDetalle.objects.create(
            ventCod=self.venta, prodCod=self.producto,
            ventDetCantidad=3, ventDetPrecioUni=Decimal("50.00"),
        )
        assert Product.objects.get(pk=self.producto.pk).prodStock == stock_antes - 3

    # TEST: detalle save luna personalizada no descuenta stock
    def test_detalle_save_luna_no_resta_stock(self):
        from products.models import Product
        from sales.models import VentaDetalle
        stock_antes = Product.objects.get(pk=self.producto.pk).prodStock
        VentaDetalle.objects.create(
            ventCod=self.venta, prodCod=self.producto,
            ventDetCantidad=1, ventDetPrecioUni=Decimal("200.00"),
            esLunaPersonalizada=True,
        )
        assert Product.objects.get(pk=self.producto.pk).prodStock == stock_antes


class TestComprobanteModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        from categories.models import ProductCategory
        from suppliers.models import Supplier
        from products.models import Product
        from users.models import User
        from clients.models import Client
        from cash.models import Cash, CashOpening
        from sales.models import Venta
        cls.categoria, _ = ProductCategory.objects.get_or_create(catproCode="LUNA", defaults={"catproNom": "Lunas"})
        cls.proveedor = Supplier.objects.create(provRazSocial="Prov Comp", provRuc="11111111111", provTele="999888222")
        cls.producto = Product.objects.create(
            catproCod=cls.categoria, provCod=cls.proveedor,
            prodDescr="Producto", prodMarca="M",
            prodPrecioVenta=Decimal("50.00"), prodStock=5,
        )
        cls.usuario = User.objects.create(usuNom="compusr", usuEmail="comp@test.com", usuNombreCom="Comp User", password="pass")
        cls.cliente = Client.objects.create(cliTipoDoc="DNI", cliNumDoc="87654321", cliNomCompleto="Comp Cliente")
        cls.caja = Cash.objects.create(cajNom="Caja Comp", usuCod=cls.usuario)
        cls.apertura = CashOpening.objects.create(cajCod=cls.caja, usuCod=cls.usuario, cajaAperMontInicial=Decimal("100"))
        cls.venta = Venta.objects.create(usuCod=cls.usuario, cliCod=cls.cliente, cajaAperCod=cls.apertura)
        cls.venta.ventSubTotal = Decimal("100.00")
        cls.venta.ventDescuento = Decimal("10.00")
        cls.venta.ventTotal = Decimal("90.00")
        cls.venta.ventSaldo = Decimal("0")
        cls.venta.save()

    # TEST: comprobante asignar correlativo inicial
    def test_comprobante_correlativo_inicial(self):
        from sales.models import Comprobante
        c = Comprobante(ventCod=self.venta)
        c._asignar_correlativo()
        assert c.comprCorrelativo == 1
        assert c.comprSerie == "NV01"

    # TEST: comprobante asignar correlativo siguiente
    def test_comprobante_correlativo_siguiente(self):
        from sales.models import Comprobante, Venta
        from users.models import User
        Comprobante.objects.create(ventCod=self.venta)
        user2 = User.objects.create(usuNom="compusr2", usuEmail="comp2@test.com", usuNombreCom="Comp2", password="pass")
        venta2 = Venta.objects.create(usuCod=user2, cajaAperCod=self.apertura)
        c2 = Comprobante(ventCod=venta2)
        c2._asignar_correlativo()
        assert c2.comprCorrelativo == 2

    # TEST: comprobante copiar datos de venta con cliente
    def test_comprobante_copiar_datos_venta(self):
        from sales.models import Comprobante
        c = Comprobante(ventCod=self.venta)
        c._copiar_datos_venta()
        assert c.comprNombreCliente == self.cliente.cliNomCompleto
        assert c.comprDocumentoCliente == f"DNI: {self.cliente.cliNumDoc}"
        assert c.comprSubtotal == self.venta.ventSubTotal
        assert c.comprDescuento == self.venta.ventDescuento
        assert c.comprTotal == self.venta.ventTotal

    # TEST: comprobante copiar datos de venta sin cliente
    def test_comprobante_copiar_datos_venta_sin_cliente(self):
        from sales.models import Venta, Comprobante
        v = Venta.objects.create(usuCod=self.usuario, cajaAperCod=self.apertura)
        c = Comprobante(ventCod=v)
        c._copiar_datos_venta()
        assert c.comprNombreCliente == "Cliente Generico"
        assert c.comprDocumentoCliente == ""

    # TEST: comprobante completo property
    def test_comprobante_completo_property(self):
        from sales.models import Comprobante
        c = Comprobante.objects.create(ventCod=self.venta)
        expected = f"NV01-{str(c.comprCorrelativo).zfill(8)}"
        assert c.comprobante_completo == expected


class TestSerializers(TestCase):
    # TEST: VentaDetalleCreateSerializer cantidad cero
    def test_serializer_valida_cantidad_cero(self):
        from sales.serializers import VentaDetalleCreateSerializer
        s = VentaDetalleCreateSerializer(data={"ventDetCantidad": 0})
        assert not s.is_valid()
        assert "ventDetCantidad" in s.errors

    # TEST: PagoSerializer monto cero
    def test_pago_serializer_valida_monto(self):
        from sales.serializers import PagoSerializer
        s = PagoSerializer(data={"monto": 0, "forma_pago": "EFECTIVO"})
        assert not s.is_valid()

    # TEST: PagoSerializer forma_pago invalida
    def test_pago_serializer_valida_forma_pago(self):
        from sales.serializers import PagoSerializer
        s = PagoSerializer(data={"monto": 100, "forma_pago": "INVALIDO"})
        assert not s.is_valid()

    # TEST: VentaCreateSerializer detalles vacios
    def test_venta_create_serializer_valida_detalles(self):
        from sales.serializers import VentaCreateSerializer
        s = VentaCreateSerializer(data={"detalles": []})
        assert not s.is_valid()
        assert "detalles" in s.errors

    # TEST: LunaCaracteristicasField conversion
    def test_luna_caracteristicas_field_conversion(self):
        from sales.serializers import LunaCaracteristicasField
        field = LunaCaracteristicasField()
        assert field.to_internal_value([]) == ""
        assert field.to_internal_value("texto") == "texto"
        assert field.to_internal_value(None) == ""


class TestFilters(TestCase):
    @classmethod
    def setUpTestData(cls):
        from categories.models import ProductCategory
        from suppliers.models import Supplier
        from products.models import Product
        from users.models import User
        from clients.models import Client
        from cash.models import Cash, CashOpening
        from sales.models import Venta
        cls.categoria, _ = ProductCategory.objects.get_or_create(catproCode="FT", defaults={"catproNom": "Filtros"})
        cls.proveedor = Supplier.objects.create(provRazSocial="Prov Filtro", provRuc="22222222222", provTele="999888333")
        cls.producto = Product.objects.create(
            catproCod=cls.categoria, provCod=cls.proveedor,
            prodDescr="Filtro", prodMarca="F",
            prodPrecioVenta=Decimal("10.00"), prodStock=5,
        )
        cls.usuario = User.objects.create(usuNom="filtro", usuEmail="filtro@test.com", usuNombreCom="Filtro User", password="pass")
        cls.cliente = Client.objects.create(cliTipoDoc="DNI", cliNumDoc="11111111", cliNomCompleto="Filtro Cliente")
        cls.caja = Cash.objects.create(cajNom="Caja Filtro", usuCod=cls.usuario)
        cls.apertura = CashOpening.objects.create(cajCod=cls.caja, usuCod=cls.usuario, cajaAperMontInicial=Decimal("100"))
        cls.venta = Venta.objects.create(usuCod=cls.usuario, cliCod=cls.cliente, cajaAperCod=cls.apertura)
        cls.venta.ventTotal = Decimal("100.00")
        cls.venta.ventSaldo = Decimal("100.00")
        cls.venta.ventFormaPago = "EFECTIVO"
        cls.venta.save()

    # TEST: VentaFilter cliente_nombre
    def test_filter_cliente_nombre(self):
        from sales.filters import VentaFilter
        from sales.models import Venta
        f = VentaFilter(data={"cliente_nombre": "Filtro Cliente"}, queryset=Venta.objects.all())
        assert f.is_valid()
        assert self.venta.ventCod in [v.ventCod for v in f.qs]

    # TEST: VentaFilter cliente_nombre sin match
    def test_filter_cliente_nombre_sin_match(self):
        from sales.filters import VentaFilter
        from sales.models import Venta
        f = VentaFilter(data={"cliente_nombre": "No Existe"}, queryset=Venta.objects.all())
        assert f.is_valid()
        assert f.qs.count() == 0

    # TEST: VentaFilter cliente_doc
    def test_filter_cliente_doc(self):
        from sales.filters import VentaFilter
        from sales.models import Venta
        f = VentaFilter(data={"cliente_doc": "11111111"}, queryset=Venta.objects.all())
        assert f.is_valid()
        assert self.venta.ventCod in [v.ventCod for v in f.qs]

    # TEST: VentaFilter estado
    def test_filter_estado(self):
        from sales.filters import VentaFilter
        from sales.models import Venta
        f = VentaFilter(data={"estado": "PENDIENTE"}, queryset=Venta.objects.all())
        assert f.is_valid()
        assert self.venta.ventCod in [v.ventCod for v in f.qs]

    # TEST: VentaFilter con_saldo true
    def test_filter_con_saldo_true(self):
        from sales.filters import VentaFilter
        from sales.models import Venta
        f = VentaFilter(data={"con_saldo": True}, queryset=Venta.objects.all())
        assert f.is_valid()
        assert f.qs.count() == 1

    # TEST: VentaFilter con_saldo false
    def test_filter_con_saldo_false(self):
        from sales.filters import VentaFilter
        from sales.models import Venta
        self.venta.ventSaldo = Decimal("0")
        self.venta.save()
        f = VentaFilter(data={"con_saldo": False}, queryset=Venta.objects.all())
        assert f.is_valid()
        assert f.qs.count() == 1
