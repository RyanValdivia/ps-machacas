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
