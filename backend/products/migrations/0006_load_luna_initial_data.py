from django.db import migrations
from decimal import Decimal

def load_luna_initial_data(apps, schema_editor):
    """
    Carga datos iniciales para el sistema de lunas personalizadas:
    - 5 Materiales
    - 3 Tipos
    - 8 Características
    - 15 Configuraciones (Matriz 5x3)
    - 1 Categoría LU (Lunas)
    - 1 Producto Dummy
    """
    LunaMaterial = apps.get_model('products', 'LunaMaterial')
    LunaTipo = apps.get_model('products', 'LunaTipo')
    LunaCaracteristica = apps.get_model('products', 'LunaCaracteristica')
    LunaConfiguracion = apps.get_model('products', 'LunaConfiguracion')
    ProductCategory = apps.get_model('categories', 'ProductCategory')
    Product = apps.get_model('products', 'Product')
    Supplier = apps.get_model('suppliers', 'Supplier')
    
    # ==================== 1. CREAR MATERIALES ====================
    materiales_data = [
        {'nombre': 'NK', 'descripcion': 'Material NK'},
        {'nombre': 'Policarbonato', 'descripcion': 'Material ligero y resistente'},
        {'nombre': 'Resina', 'descripcion': 'Material de resina'},
        {'nombre': 'Cristal', 'descripcion': 'Material tradicional de alta calidad'},
        {'nombre': 'Otros', 'descripcion': 'Otros materiales'},
    ]
    
    materiales = {}
    for mat_data in materiales_data:
        material, created = LunaMaterial.objects.get_or_create(
            lunMatNombre=mat_data['nombre'],
            defaults={'lunMatDescripcion': mat_data['descripcion']}
        )
        materiales[mat_data['nombre']] = material
        if created:
            print(f"✓ Material creado: {mat_data['nombre']}")
    
    # ==================== 2. CREAR TIPOS ====================
    tipos_data = [
        {'nombre': 'Monofocal', 'descripcion': 'Corrección para una distancia'},
        {'nombre': 'Bifocal', 'descripcion': 'Corrección para dos distancias'},
        {'nombre': 'Multifocal', 'descripcion': 'Corrección para múltiples distancias'},
    ]
    
    tipos = {}
    for tipo_data in tipos_data:
        tipo, created = LunaTipo.objects.get_or_create(
            lunTipNombre=tipo_data['nombre'],
            defaults={'lunTipDescripcion': tipo_data['descripcion']}
        )
        tipos[tipo_data['nombre']] = tipo
        if created:
            print(f"✓ Tipo creado: {tipo_data['nombre']}")
    
    # ==================== 3. CREAR CARACTERÍSTICAS ====================
    caracteristicas_data = [
        {'nombre': 'Blue Block', 'precio': Decimal('30.00'), 'descripcion': 'Filtro luz azul'},
        {'nombre': 'UV400', 'precio': Decimal('20.00'), 'descripcion': 'Protección UV completa'},
        {'nombre': 'AR', 'precio': Decimal('40.00'), 'descripcion': 'Anti-reflejo'},
        {'nombre': 'Fotocromatico', 'precio': Decimal('80.00'), 'descripcion': 'Se oscurece con luz solar'},
        {'nombre': 'Polarizado', 'precio': Decimal('60.00'), 'descripcion': 'Elimina deslumbramiento'},
        {'nombre': 'Alto Indice', 'precio': Decimal('50.00'), 'descripcion': 'Lentes más delgados'},
        {'nombre': 'Digital', 'precio': Decimal('45.00'), 'descripcion': 'Protección luz digital'},
        {'nombre': 'Coloreado', 'precio': Decimal('35.00'), 'descripcion': 'Luna con color personalizado'},
    ]
    
    for car_data in caracteristicas_data:
        caracteristica, created = LunaCaracteristica.objects.get_or_create(
            lunCarNombre=car_data['nombre'],
            defaults={
                'lunCarPrecioAdicional': car_data['precio'],
                'lunCarDescripcion': car_data['descripcion']
            }
        )
        if created:
            print(f"✓ Característica creada: {car_data['nombre']} (+S/{car_data['precio']})")
    
    # ==================== 4. CREAR CONFIGURACIONES (MATRIZ 5x3) ====================
    # Precios base según Material x Tipo
    precios_matriz = {
        ('NK', 'Monofocal'): Decimal('100.00'),
        ('NK', 'Bifocal'): Decimal('180.00'),
        ('NK', 'Multifocal'): Decimal('280.00'),
        
        ('Policarbonato', 'Monofocal'): Decimal('120.00'),
        ('Policarbonato', 'Bifocal'): Decimal('200.00'),
        ('Policarbonato', 'Multifocal'): Decimal('300.00'),
        
        ('Resina', 'Monofocal'): Decimal('90.00'),
        ('Resina', 'Bifocal'): Decimal('160.00'),
        ('Resina', 'Multifocal'): Decimal('250.00'),
        
        ('Cristal', 'Monofocal'): Decimal('110.00'),
        ('Cristal', 'Bifocal'): Decimal('190.00'),
        ('Cristal', 'Multifocal'): Decimal('290.00'),
        
        ('Otros', 'Monofocal'): Decimal('80.00'),
        ('Otros', 'Bifocal'): Decimal('150.00'),
        ('Otros', 'Multifocal'): Decimal('240.00'),
    }
    
    configuraciones_creadas = 0
    for (mat_nombre, tipo_nombre), precio in precios_matriz.items():
        config, created = LunaConfiguracion.objects.get_or_create(
            lunMatCod=materiales[mat_nombre],
            lunTipCod=tipos[tipo_nombre],
            defaults={'lunConfPrecioBase': precio}
        )
        if created:
            configuraciones_creadas += 1
            print(f"✓ Configuración creada: {mat_nombre} - {tipo_nombre} (S/{precio})")
    
    print(f"\n✓ Total configuraciones creadas: {configuraciones_creadas}/15")
    
    # ==================== 5. CREAR CATEGORÍA LUNAS ====================
    # Intentar obtener categoría existente LUNA o crear LU
    try:
        categoria_luna = ProductCategory.objects.get(catproCode='LUNA')
        print(f"✓ Categoría existente encontrada: LUNA - {categoria_luna.catproNom}")
        # Actualizar campo
        categoria_luna.catproRequiereInventario = False
        categoria_luna.save()
    except ProductCategory.DoesNotExist:
        # Crear nueva con código LU
        categoria_luna, created = ProductCategory.objects.get_or_create(
            catproCode='LU',
            defaults={
                'catproNom': 'Lunas',
                'catproRequiereInventario': False
            }
        )
        if created:
            print(f"✓ Categoría creada: LU - Lunas (sin control de inventario)")
        else:
            categoria_luna.catproRequiereInventario = False
            categoria_luna.save()
            print(f"✓ Categoría actualizada: LU - Lunas")
    
    # ==================== 6. CREAR PRODUCTO DUMMY ====================
    try:
        proveedor_interno = Supplier.objects.get(provRuc='00000000000')
    except Supplier.DoesNotExist:
        proveedor_interno = Supplier.objects.filter(provEstado='Active').first()
        if not proveedor_interno:
            print("⚠ No se encontró proveedor. Se debe crear manualmente.")
            return
    
    producto_luna, created = Product.objects.get_or_create(
        prodCode='LUNA-PERS',
        defaults={
            'catproCod': categoria_luna,
            'provCod': proveedor_interno,
            'prodDescr': 'LUNA PERSONALIZADA',
            'prodMarca': 'PERSONALIZADO',
            'prodMate': 'N',
            'prodColor': '',
            'prodTalla': '',
            'prodGenero': 'Unisex',
            'prodTieneSobrelente': False,
            'prodForma': '',
            'prodDescripcionAdicional': 'Producto genérico para lunas con configuración personalizada. NO consume stock.',
            'prodCostoInv': Decimal('0.00'),
            'prodPrecioVenta': Decimal('0.00'),
            'prodStock': 9999,
            'prodStockMin': 0,
            'prodEstado': 'Active'
        }
    )
    
    if created:
        print(f"✓ Producto dummy creado: LUNA-PERS (ID: {producto_luna.prodCod})")
    else:
        print(f"✓ Producto dummy ya existe: LUNA-PERS (ID: {producto_luna.prodCod})")


def reverse_luna_initial_data(apps, schema_editor):
    """Elimina todos los datos iniciales de lunas"""
    LunaMaterial = apps.get_model('products', 'LunaMaterial')
    LunaTipo = apps.get_model('products', 'LunaTipo')
    LunaCaracteristica = apps.get_model('products', 'LunaCaracteristica')
    LunaConfiguracion = apps.get_model('products', 'LunaConfiguracion')
    ProductCategory = apps.get_model('categories', 'ProductCategory')
    Product = apps.get_model('products', 'Product')
    
    # Eliminar en orden inverso para respetar dependencias
    Product.objects.filter(prodCode='LUNA-PERS').delete()
    ProductCategory.objects.filter(catproCode='LU').delete()
    LunaConfiguracion.objects.all().delete()
    LunaCaracteristica.objects.all().delete()
    LunaTipo.objects.all().delete()
    LunaMaterial.objects.all().delete()
    
    print("✓ Datos iniciales de lunas eliminados")


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_add_luna_models'),
        ('categories', '0004_add_requiere_inventario_field'),
        ('suppliers', '0005_create_internal_supplier'),
        ('sales', '0004_ventadetalle_eslunapersonalizada_and_more'),
    ]

    operations = [
        migrations.RunPython(load_luna_initial_data, reverse_luna_initial_data),
    ]
