from products.models import Product
from categories.models import ProductCategory
from suppliers.models import Supplier


def run():
    # Categorías reales
    cat_montura = ProductCategory.objects.get(catproCode="MO")
    cat_accesorio = ProductCategory.objects.get(catproCode="AC")

    proveedor = Supplier.objects.first()
    if not proveedor:
        raise Exception("No existe ningún proveedor en la BD")

    # ======================
    # MONTURAS (ORDEN INVERTIDO)
    # ======================
    monturas = [
        # marca, material, talla, color, forma, sobrelente, descripcion, stock
        ("PEGASUS", "M", "52-19", "DORADA", "",
         False, "PG M3047", 1),

        ("PEGASUS", "M", "56-18", "DORADA", "AVIADOR",
         False, "PG M3052 Doble Puente", 1),

        ("VIPSUAL", "M", "53-18-145", "DORADO", "",
         False, "VM2508", 1),

        ("VIPSUAL", "M", "55-18-145", "DORADO", "",
         False, "VM2509", 2),

        ("CARLOS ROSSI", "M", "53-18-145", "NEGRO PLATEADO", "",
         False, "73088", 1),

        ("CARLOS ROSSI", "M", "51-18-143", "PLATEADO", "HEXAGONAL",
         False, "73083", 1),

        ("CARLOS ROSSI", "M", "51-18-143", "PLATEADO DORADO", "HEXAGONAL",
         False, "73083", 1),

        ("CARLOS ROSSI", "M", "51-18-143", "NEGRO PLATEADO", "HEXAGONAL",
         False, "73083", 1),

        ("CARLOS ROSSI", "M", "51-18-143", "NEGRO DORADO", "HEXAGONAL",
         False, "73083", 1),

        ("CARLOS ROSSI", "M", "51-18-143", "NEGRO", "HEXAGONAL",
         False, "73083", 1),

        ("TENDENCIA", "M", "54-17-142", "DORADO NUDE", "",
         False, "C5 Biselado al aire", 1),

        ("OZZY", "M", "55-16-140", "NEGRO BLANCO DORADO", "POLIGONAL",
         False, "HZ8001 C5", 1),

        ("OZZY", "M", "52-18-140", "NEGRO ROSA PLATEADO", "",
         False, "HZ8003 C4", 1),

        ("FEILLIS", "M", "56-15-144", "NEGRO", "AVIADOR",
         True, "8015 Doble Puente - 4 Sobrelentes", 1),
    ]

    for (
        marca, mate, talla, color, forma,
        sobrelente, descripcion, stock
    ) in monturas:

        Product.objects.create(
            catproCod=cat_montura,
            provCod=proveedor,
            prodMarca=marca,
            prodMate=mate,
            prodTalla=talla,
            prodColor=color,
            prodForma=forma,
            prodTieneSobrelente=sobrelente,
            prodDescripcionAdicional=descripcion,
            prodStock=stock,
            prodCostoInv=0,
            prodPrecioVenta=0,
        )

    # ======================
    # ACCESORIO (AL FINAL)
    # ======================
    Product.objects.create(
        catproCod=cat_accesorio,
        provCod=proveedor,
        prodDescripcionAdicional="LUNA PERSONALIZADA",
        prodMarca="",
        prodMate="N",
        prodStock=1,
        prodCostoInv=0,
        prodPrecioVenta=0,
    )

    print("✔ Productos creados en orden correcto (ascendente real)")
