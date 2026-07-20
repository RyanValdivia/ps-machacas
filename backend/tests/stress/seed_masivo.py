"""
seed_masivo.py — Generación masiva de datos para pruebas NF-STRESS-02 y NF-VOL-01.

Uso:
    python seed_masivo.py --count 1000
    python seed_masivo.py --count 100000

Requisitos:
    - Debe ejecutarse desde el directorio 'backend/'
    - Variables de entorno del .env deben estar disponibles (DB_HOST, DB_NAME, etc.)
    - Debe existir al menos un Supplier y la categoría ProductCategory con catproCode='AC'
"""

import os
import sys
import time

# Consola Windows (cp1252) no soporta emojis en print por defecto.
if hasattr(sys.stdout, "reconfigure"):
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
import random
import argparse
from pathlib import Path

# ---------------------------------------------------------------------------
# Bootstrap Django
# ---------------------------------------------------------------------------
# Agregar el directorio 'backend/' al path para que Django encuentre los módulos
BACKEND_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND_DIR))

# Cargar variables de entorno desde .env si existe
env_file = BACKEND_DIR / ".env"
if not env_file.exists():
    env_file = BACKEND_DIR / ".env.example"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "registrame.settings")

import django
django.setup()

# ---------------------------------------------------------------------------
# Importaciones de modelos (después de django.setup())
# ---------------------------------------------------------------------------
from django.db import transaction, connection
from products.models import Product
from categories.models import ProductCategory
from suppliers.models import Supplier

# Script de seeding (no es un Locust file) — genera datos masivos que las
# pruebas de carga necesitan como precondición, en vez de correr contra
# una BD casi vacía:
#   - `--count N`: crea N productos (modelo Product, categoría fija
#     catproCode='AC' = Accesorio, con un Supplier existente) vía
#     bulk_create en lotes de 500. Se usa con --count 1000 para
#     NF-STRESS-02 (búsquedas de inventario) y --count 100000 para
#     NF-VOL-01 (prueba de volumen), simulando un catálogo real grande.
#   - `--race-condition`: crea UN producto puntual con stock=1, insumo de
#     NF-STRESS-03 (10 usuarios compitiendo por el mismo producto).
#   - `--verificar-stock`: consulta el stock final de ese producto de
#     race condition tras correr la prueba, para confirmar que solo se
#     descontó una unidad.
# bulk_create no dispara Product.save(), así que prodDescr se arma a mano
# y prodCode queda en NULL (no afecta las búsquedas usadas en los tests).

# ---------------------------------------------------------------------------
# Datos de variedad para las pruebas
# ---------------------------------------------------------------------------
MARCAS = [
    "PEGASUS", "VIPSUAL", "CARLOS ROSSI", "TENDENCIA", "OZZY", "FEILLIS",
    "LUXOTTICA", "OAKLEY", "RAY-BAN", "CARRERA", "POLICE", "LACOSTE",
    "GUCCI", "PRADA", "ARMANI", "VERSACE", "DOLCE", "MONTBLANC",
    "BOSS", "CALVIN KLEIN", "TOMMY", "FOSSIL", "KENNETH COLE", "GUESS",
    "KATE SPADE", "MICHAEL KORS", "COACH", "TORY BURCH", "RALPH LAUREN",
    "DIESEL", "DSQUARED2", "MARC JACOBS", "TOM FORD", "BALENCIAGA",
]

COLORES = [
    "NEGRO", "PLATEADO", "DORADO", "AZUL", "MARRÓN", "VERDE", "ROJO",
    "ROSA", "BLANCO", "GRIS", "COBRE", "BRONCE", "NUDE", "TRANSPARENTE",
    "NEGRO PLATEADO", "NEGRO DORADO", "PLATEADO DORADO", "AZUL MARINO",
    "CAREY", "HAVANA", "TORTOISE", "GUNMETAL",
]

DESCRIPCIONES = [
    "Modelo clásico", "Edición limitada", "Diseño moderno", "Estilo vintage",
    "Perfil delgado", "Marco ligero", "Resistente al agua", "Antiarañazos",
    "UV 400", "Polarizado", "Doble puente", "Sin montura", "Montura completa",
    "Montura semiperfil", "Para deportes", "Para uso diario", "Con estuche",
    "Con paño de limpieza", "Certificado ANSI", "Certificado CE",
]


# ---------------------------------------------------------------------------
# Función principal de generación
# ---------------------------------------------------------------------------
def generar_productos(count: int) -> None:
    """
    Genera `count` productos de tipo ACCESORIO (catproCode='AC') en la BD.
    Usa bulk_create con batch de 500 para eficiencia.
    """
    print(f"\n🌱 Iniciando generación de {count:,} productos...")
    inicio = time.time()

    # Obtener dependencias necesarias
    try:
        cat_accesorio = ProductCategory.objects.get(catproCode="AC")
    except ProductCategory.DoesNotExist:
        print("❌ ERROR: No existe la categoría con catproCode='AC'.")
        print("   Por favor, crea la categoría 'Accesorio' antes de ejecutar este script.")
        sys.exit(1)

    proveedor = Supplier.objects.first()
    if not proveedor:
        print("❌ ERROR: No existe ningún Supplier en la base de datos.")
        print("   Por favor, crea al menos un proveedor antes de ejecutar este script.")
        sys.exit(1)

    print(f"   ✔ Categoría: {cat_accesorio.catproNom} (ID: {cat_accesorio.catproCod})")
    print(f"   ✔ Proveedor: {proveedor.provRazSocial} (ID: {proveedor.provCod})")

    # Generar en lotes para evitar problemas de memoria con 100k registros
    BATCH_SIZE = 500
    total_creados = 0
    lotes = (count + BATCH_SIZE - 1) // BATCH_SIZE

    for lote_num in range(lotes):
        batch_count = min(BATCH_SIZE, count - total_creados)
        productos_batch = []

        for i in range(batch_count):
            idx_global = total_creados + i + 1
            marca = random.choice(MARCAS)
            color = random.choice(COLORES)
            descripcion = random.choice(DESCRIPCIONES)

            # Generar datos del producto
            # Usamos Accesorios (catproCode=AC) porque no tienen restricciones
            # de marca/material/talla obligatorias (a diferencia de Monturas)
            precio_venta = round(random.uniform(15.00, 350.00), 2)
            costo_inv = round(precio_venta * random.uniform(0.3, 0.6), 2)
            stock = random.randint(1, 50)

            # Descripción única para poder identificar lotes
            descripcion_adicional = (
                f"{marca} {color} - {descripcion} [SEED-{idx_global:07d}]"
            )

            producto = Product(
                catproCod=cat_accesorio,
                provCod=proveedor,
                prodMarca=marca,
                prodMate="N",  # Accesorios: 'N' (No aplica)
                prodColor=color,
                prodDescripcionAdicional=descripcion_adicional,
                prodPrecioVenta=precio_venta,
                prodCostoInv=costo_inv,
                prodStock=stock,
                prodEstado="Active",
                prodGenero=random.choice(["Hombre", "Mujer", "Unisex"]),
            )
            productos_batch.append(producto)

        # Bulk create con skip_raw (la generación de prodCode y prodDescr
        # la hace el model.save(), pero bulk_create no llama a save().
        # Necesitamos manejar esto explícitamente.)
        #
        # NOTA: bulk_create NO llama a save() ni a generate_description().
        # Por eso usamos el campo prodDescripcionAdicional para la descripción
        # y asignamos prodDescr manualmente antes de insertar.
        for prod in productos_batch:
            # Generar descripción manualmente (igual que model.generate_description para accesorio)
            partes = []
            if prod.prodMarca:
                partes.append(prod.prodMarca.upper())
            descripcion_gen = " | ".join(partes) if partes else ""
            if prod.prodDescripcionAdicional:
                if descripcion_gen:
                    descripcion_gen += f" - {prod.prodDescripcionAdicional}"
                else:
                    descripcion_gen = prod.prodDescripcionAdicional
            prod.prodDescr = descripcion_gen.strip() if descripcion_gen else f"Producto seed {total_creados}"

        with transaction.atomic():
            # ignore_conflicts=False para ver errores reales
            Product.objects.bulk_create(productos_batch, batch_size=BATCH_SIZE)

        total_creados += batch_count
        porcentaje = (total_creados / count) * 100
        elapsed = time.time() - inicio
        velocidad = total_creados / elapsed if elapsed > 0 else 0
        print(
            f"   Lote {lote_num + 1}/{lotes} — {total_creados:,}/{count:,} "
            f"({porcentaje:.1f}%) — {velocidad:.0f} prod/seg"
        )

    # Nota: Los codigos de producto (prodCode) se generan secuencialmente
    # por el modelo al usar save(). Con bulk_create, quedan en NULL.
    # Esto es aceptable para pruebas de stress (no afecta búsquedas).
    # Si se requiere prodCode, ejecutar después:
    #   UPDATE product SET "prodCode" = CONCAT('SEED-', "prodCod") WHERE "prodCode" IS NULL;

    duracion = time.time() - inicio
    total_en_bd = Product.objects.count()
    print(f"\n✅ Generación completada en {duracion:.2f} segundos")
    print(f"   Productos creados ahora: {total_creados:,}")
    print(f"   Total en BD: {total_en_bd:,}")
    print(f"   Velocidad promedio: {total_creados / duracion:.0f} productos/seg")


def verificar_stock_race_condition() -> None:
    """
    Verifica el stock final del producto de race condition (NF-STRESS-03).
    Ejecuta SQL directo para mostrar evidencia de la prueba.
    """
    print("\n🔍 Verificación de stock final (NF-STRESS-03 — Race Condition)...")

    # Obtener el producto de menor stock (el de race condition)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                p."prodCod",
                p."prodDescr",
                p."prodStock",
                COUNT(vd."ventDetCod") AS ventas_realizadas
            FROM product p
            LEFT JOIN venta_detalle vd ON vd."prodCod_id" = p."prodCod"
                AND vd."ventDetAnulado" = false
            WHERE p."prodDescr" ILIKE '%RACE-CONDITION-SEED%'
            GROUP BY p."prodCod", p."prodDescr", p."prodStock"
            ORDER BY p."prodCod" DESC
            LIMIT 5;
        """)
        rows = cursor.fetchall()

    if not rows:
        print("   ⚠ No se encontró el producto de race condition (prodDescr ILIKE '%RACE-CONDITION-SEED%').")
        print("   Asegúrate de haber creado el producto con esa descripción antes de correr NF-STRESS-03.")
    else:
        print(f"\n   {'prodCod':>8} | {'prodStock':>10} | {'ventas_realizadas':>18} | prodDescr")
        print("   " + "-" * 80)
        for row in rows:
            prod_cod, prod_descr, prod_stock, ventas = row
            estado = "✅ CORRECTO" if prod_stock == 0 else "⚠ REVISAR"
            print(
                f"   {prod_cod:>8} | {prod_stock:>10} | {ventas:>18} | "
                f"{prod_descr[:40]}... {estado}"
            )


def crear_producto_race_condition() -> int:
    """
    Crea el producto especial para NF-STRESS-03 con stock=1.
    Retorna el prodCod del producto creado.
    """
    print("\n🎯 Creando producto para Race Condition (NF-STRESS-03)...")

    try:
        cat_accesorio = ProductCategory.objects.get(catproCode="AC")
    except ProductCategory.DoesNotExist:
        print("❌ ERROR: No existe la categoría con catproCode='AC'.")
        sys.exit(1)

    proveedor = Supplier.objects.first()
    if not proveedor:
        print("❌ ERROR: No existe ningún Supplier en la base de datos.")
        sys.exit(1)

    # Usar save() para que genere prodCode y prodDescr correctamente
    producto = Product(
        catproCod=cat_accesorio,
        provCod=proveedor,
        prodMarca="RACE",
        prodMate="N",
        prodColor="TEST",
        prodDescripcionAdicional="RACE-CONDITION-SEED stock=1",
        prodPrecioVenta=10.00,
        prodCostoInv=5.00,
        prodStock=1,
        prodEstado="Active",
        prodGenero="Unisex",
    )
    producto.save()

    print(f"   ✔ Producto creado: ID={producto.prodCod}, stock={producto.prodStock}")
    print(f"   ✔ Descripción: {producto.prodDescr}")
    print(f"   → Usa este ID en locustfile_pos.py: RACE_CONDITION_PRODUCT_ID = {producto.prodCod}")
    return producto.prodCod


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Generador masivo de datos para pruebas de stress",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python seed_masivo.py --count 1000
  python seed_masivo.py --count 100000
  python seed_masivo.py --race-condition
  python seed_masivo.py --verificar-stock
        """,
    )
    parser.add_argument(
        "--count",
        type=int,
        default=None,
        help="Número de productos a generar (ej: 1000 o 100000)",
    )
    parser.add_argument(
        "--race-condition",
        action="store_true",
        help="Crea un producto con stock=1 para la prueba NF-STRESS-03",
    )
    parser.add_argument(
        "--verificar-stock",
        action="store_true",
        help="Verifica el stock final después de la prueba NF-STRESS-03",
    )

    args = parser.parse_args()

    if args.race_condition:
        prod_id = crear_producto_race_condition()
        print(f"\n💡 Recuerda actualizar RACE_CONDITION_PRODUCT_ID = {prod_id} en locustfile_pos.py")
    elif args.verificar_stock:
        verificar_stock_race_condition()
    elif args.count is not None:
        if args.count <= 0:
            print("❌ ERROR: --count debe ser un número positivo.")
            sys.exit(1)
        generar_productos(args.count)
    else:
        parser.print_help()
        print("\n⚠ Debes especificar --count, --race-condition, o --verificar-stock.")
        sys.exit(1)


if __name__ == "__main__":
    main()
