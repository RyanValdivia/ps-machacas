import pytest
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from decimal import Decimal

from .models import (
    Product, LunaMaterial, LunaTipo, LunaCaracteristica, LunaConfiguracion
)
from .serializers import (
    ProductListSerializer, ProductDetailSerializer,
    ProductCreateUpdateSerializer, LunaMaterialSerializer,
    LunaTipoSerializer, LunaCaracteristicaSerializer, LunaConfiguracionSerializer
)
from users.models import User, Role
from suppliers.models import Supplier
from categories.models import ProductCategory


@pytest.fixture
def logistica_role(db):
    """Rol Nivel 3 (Logística)"""
    return Role.objects.create(
        rolNom='LOGISTICA',
        rolDes='Área de Inventario',
        rolNivel=3
    )


@pytest.fixture
def gerente_role(db):
    """Rol Nivel 1 (Gerente)"""
    return Role.objects.create(
        rolNom='GERENTE',
        rolDes='Acceso total',
        rolNivel=1
    )


@pytest.fixture
def logistica_user(logistica_role):
    """Usuario con rol de logística"""
    user = User.objects.create_user(
        usuNom='logistica',
        usuEmail='logistica@test.com',
        usuContra='logistica123',
        usuNombreCom='Logistica User',
        usuDNI='12345678'
    )
    user.roles.add(logistica_role)
    return user


@pytest.fixture
def gerente_user(gerente_role):
    """Usuario gerente"""
    user = User.objects.create_user(
        usuNom='gerente',
        usuEmail='gerente@test.com',
        usuContra='gerente123',
        usuNombreCom='Gerente General',
        usuDNI='87654321'
    )
    user.roles.add(gerente_role)
    return user


@pytest.fixture
def logistica_client(logistica_user):
    """Cliente autenticado como logística"""
    client = APIClient()
    refresh = RefreshToken.for_user(logistica_user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


@pytest.fixture
def gerente_client(gerente_user):
    """Cliente autenticado como gerente"""
    client = APIClient()
    refresh = RefreshToken.for_user(gerente_user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


@pytest.fixture
def supplier(db):
    """Proveedor de prueba"""
    return Supplier.objects.create(
        provRuc='20123456789',
        provRazSocial='PROVEEDOR OPTICA SAC',
        provDirec='AV. PRINCIPAL 123',
        provCiu='LIMA',
        provTele='987654321',
        provEmail='contacto@optica.com'
    )


@pytest.fixture
def categoria_montura(db):
    """Categoría Montura"""
    cat, _ = ProductCategory.objects.get_or_create(
        catproNom='Monturas',
        catproCode='MO'
    )
    return cat


@pytest.fixture
def categoria_accesorio(db):
    """Categoría Accesorio"""
    cat, _ = ProductCategory.objects.get_or_create(
        catproNom='Accesorios',
        catproCode='AC'
    )
    return cat


@pytest.fixture
def montura_data(supplier, categoria_montura):
    """Datos válidos para una montura"""
    return {
        'catproCod': categoria_montura,
        'provCod': supplier,
        'prodMarca': 'RAY-BAN',
        'prodMate': 'A',
        'prodColor': 'NEGRO',
        'prodTalla': '54-18-140',
        'prodCostoInv': Decimal('50.00'),
        'prodPrecioVenta': Decimal('100.00'),
        'prodStock': 10,
        'prodGenero': 'Hombre',
        'prodForma': 'Cuadrado'
    }


@pytest.fixture
def accesorio_data(supplier, categoria_accesorio):
    """Datos válidos para un accesorio"""
    return {
        'catproCod': categoria_accesorio,
        'provCod': supplier,
        'prodMarca': 'OPTICA',
        'prodDescripcionAdicional': 'Estuche premium',
        'prodCostoInv': Decimal('10.00'),
        'prodPrecioVenta': Decimal('25.00'),
        'prodStock': 50
    }


# ==================== PRODUCT MODEL TESTS ====================

class TestProductModel:
    """Tests para el modelo Product"""

    @pytest.mark.django_db
    def test_create_montura(self, montura_data):
        """Crear montura válida"""
        product = Product.objects.create(**montura_data)
        assert product.prodCode  # Se genera automáticamente
        assert product.prodDescr  # Se genera automáticamente
        assert product.es_montura() is True
        assert product.es_accesorio() is False
        assert product.prodMarca == 'RAY-BAN'  # Se guarda en mayúsculas

    @pytest.mark.django_db
    def test_create_accesorio(self, accesorio_data):
        """Crear accesorio válido"""
        product = Product.objects.create(**accesorio_data)
        assert product.prodCode
        assert product.prodDescr
        assert product.es_accesorio() is True
        assert product.es_montura() is False
        assert product.prodMate == 'N'  # Se fuerza para accesorios

    @pytest.mark.django_db
    def test_product_str(self, montura_data):
        """__str__ retorna descripción"""
        product = Product.objects.create(**montura_data)
        assert str(product) == product.prodDescr

    @pytest.mark.django_db
    def test_negative_costo_inv(self, montura_data):
        """Costo negativo - ValidationError"""
        montura_data['prodCostoInv'] = Decimal('-10.00')
        product = Product(**montura_data)
        with pytest.raises(ValidationError) as exc:
            product.full_clean()
        assert 'prodCostoInv' in str(exc.value)

    @pytest.mark.django_db
    def test_negative_precio_venta(self, montura_data):
        """Precio venta negativo - ValidationError"""
        montura_data['prodPrecioVenta'] = Decimal('-5.00')
        product = Product(**montura_data)
        with pytest.raises(ValidationError) as exc:
            product.full_clean()
        assert 'prodPrecioVenta' in str(exc.value)

    @pytest.mark.django_db
    def test_negative_stock(self, montura_data):
        """Stock negativo - ValidationError"""
        montura_data['prodStock'] = -1
        product = Product(**montura_data)
        with pytest.raises(ValidationError) as exc:
            product.full_clean()
        assert 'prodStock' in str(exc.value)

    @pytest.mark.django_db
    def test_montura_without_marca(self, montura_data):
        """Montura sin marca - ValidationError"""
        montura_data['prodMarca'] = ''
        product = Product(**montura_data)
        with pytest.raises(ValidationError) as exc:
            product.full_clean()
        assert 'prodMarca' in str(exc.value)

    @pytest.mark.django_db
    def test_montura_marca_too_short(self, montura_data):
        """Montura con marca muy corta - ValidationError"""
        montura_data['prodMarca'] = 'A'
        product = Product(**montura_data)
        with pytest.raises(ValidationError) as exc:
            product.full_clean()
        assert 'prodMarca' in str(exc.value)

    @pytest.mark.django_db
    def test_montura_without_material(self, montura_data):
        """Montura sin material válido - ValidationError"""
        montura_data['prodMate'] = 'N'
        product = Product(**montura_data)
        with pytest.raises(ValidationError) as exc:
            product.full_clean()
        assert 'prodMate' in str(exc.value)

    @pytest.mark.django_db
    def test_montura_without_talla(self, montura_data):
        """Montura sin talla - ValidationError"""
        montura_data['prodTalla'] = ''
        product = Product(**montura_data)
        with pytest.raises(ValidationError) as exc:
            product.full_clean()
        assert 'prodTalla' in str(exc.value)

    @pytest.mark.django_db
    def test_accesorio_with_material(self, accesorio_data):
        """Accesorio con material no N - ValidationError"""
        accesorio_data['prodMate'] = 'A'
        product = Product(**accesorio_data)
        with pytest.raises(ValidationError) as exc:
            product.full_clean()
        assert 'prodMate' in str(exc.value)

    @pytest.mark.django_db
    def test_marca_uppercase(self, montura_data):
        """Marca se guarda en mayúsculas"""
        montura_data['prodMarca'] = 'ray-ban'
        product = Product.objects.create(**montura_data)
        assert product.prodMarca == 'RAY-BAN'

    @pytest.mark.django_db
    def test_generate_montura_code(self, montura_data):
        """Generar código de montura"""
        product = Product.objects.create(**montura_data)
        # Formato: material + numero (sin guion, sin ceros)
        assert product.prodCode.startswith('A')  # Material A

    @pytest.mark.django_db
    def test_generate_accesorio_code(self, accesorio_data):
        """Generar código de accesorio"""
        product = Product.objects.create(**accesorio_data)
        # Formato: numero secuencial
        assert product.prodCode.isdigit()

    @pytest.mark.django_db
    def test_generate_montura_description(self, montura_data):
        """Generar descripción de montura"""
        product = Product.objects.create(**montura_data)
        # Formato: Marca | Talla Color Forma
        assert 'RAY-BAN' in product.prodDescr
        assert '54-18-140' in product.prodDescr

    @pytest.mark.django_db
    def test_generate_montura_description_with_sobrelente(self, montura_data):
        """Descripción de montura con sobrelente"""
        montura_data['prodTieneSobrelente'] = True
        product = Product.objects.create(**montura_data)
        assert '[Con Sobrelente]' in product.prodDescr

    @pytest.mark.django_db
    def test_generate_accesorio_description(self, accesorio_data):
        """Generar descripción de accesorio"""
        product = Product.objects.create(**accesorio_data)
        assert 'OPTICA' in product.prodDescr or 'Estuche' in product.prodDescr

    @pytest.mark.django_db
    def test_update_description_on_save(self, montura_data):
        """Descripción se actualiza al modificar campos"""
        product = Product.objects.create(**montura_data)
        old_desc = product.prodDescr
        product.prodColor = 'ROJO'
        product.save()
        assert product.prodDescr != old_desc
        assert 'ROJO' in product.prodDescr

    @pytest.mark.django_db
    def test_margen_ganancia(self, montura_data):
        """Calcular margen de ganancia"""
        montura_data['prodCostoInv'] = Decimal('50.00')
        montura_data['prodPrecioVenta'] = Decimal('100.00')
        product = Product.objects.create(**montura_data)
        assert product.margen_ganancia == 100.0

    @pytest.mark.django_db
    def test_margen_ganancia_zero_costo(self, montura_data):
        """Margen con costo 0"""
        montura_data['prodCostoInv'] = Decimal('0.00')
        product = Product.objects.create(**montura_data)
        assert product.margen_ganancia == 0

    @pytest.mark.django_db
    def test_ganancia_unitaria(self, montura_data):
        """Calcular ganancia unitaria"""
        montura_data['prodCostoInv'] = Decimal('50.00')
        montura_data['prodPrecioVenta'] = Decimal('100.00')
        product = Product.objects.create(**montura_data)
        assert product.ganancia_unitaria == Decimal('50.00')

    @pytest.mark.django_db
    def test_valor_total_stock(self, montura_data):
        """Calcular valor total del stock"""
        montura_data['prodCostoInv'] = Decimal('50.00')
        montura_data['prodStock'] = 10
        product = Product.objects.create(**montura_data)
        assert product.valor_total_stock == Decimal('500.00')

    @pytest.mark.django_db
    def test_all_materials_valid(self, montura_data):
        """Todos los materiales son válidos para montura"""
        for material in ['A', 'M', 'TR', 'C']:
            montura_data['prodMate'] = material
            product = Product.objects.create(**montura_data)
            assert product.prodMate == material

    @pytest.mark.django_db
    def test_all_generos_valid(self, montura_data):
        """Todos los géneros son válidos"""
        for genero in ['Hombre', 'Mujer', 'Unisex', 'Nino']:
            montura_data['prodGenero'] = genero
            product = Product.objects.create(**montura_data)
            assert product.prodGenero == genero


# ==================== LUNA MODEL TESTS ====================

class TestLunaModels:
    """Tests para modelos de lunas"""

    @pytest.mark.django_db
    def test_create_luna_material(self):
        """Crear material de luna"""
        material = LunaMaterial.objects.create(
            lunMatNombre='CR-39',
            lunMatDescripcion='Material orgánico'
        )
        assert str(material) == 'CR-39'

    @pytest.mark.django_db
    def test_create_luna_tipo(self):
        """Crear tipo de luna"""
        tipo = LunaTipo.objects.create(
            lunTipNombre='Progresivo',
            lunTipDescripcion='Lente progresivo'
        )
        assert str(tipo) == 'Progresivo'

    @pytest.mark.django_db
    def test_create_luna_caracteristica(self):
        """Crear característica de luna"""
        caracteristica = LunaCaracteristica.objects.create(
            lunCarNombre='Anti-Reflect',
            lunCarDescripcion='Capa antireflectante',
            lunCarPrecioAdicional=Decimal('25.00')
        )
        assert 'Anti-Reflect' in str(caracteristica)
        assert '25.00' in str(caracteristica)

    @pytest.mark.django_db
    def test_create_luna_configuracion(self):
        """Crear configuración de luna"""
        material = LunaMaterial.objects.create(lunMatNombre='Trivex')
        tipo = LunaTipo.objects.create(lunTipNombre='Progresivo')
        config = LunaConfiguracion.objects.create(
            lunMatCod=material,
            lunTipCod=tipo,
            lunConfPrecioBase=Decimal('50.00')
        )
        assert 'Trivex' in str(config)
        assert 'Progresivo' in str(config)

    @pytest.mark.django_db
    def test_luna_configuracion_unique_together(self):
        """Configuración única por material-tipo"""
        material = LunaMaterial.objects.create(lunMatNombre='Trivex')
        tipo = LunaTipo.objects.create(lunTipNombre='Progresivo')
        LunaConfiguracion.objects.create(
            lunMatCod=material,
            lunTipCod=tipo,
            lunConfPrecioBase=Decimal('50.00')
        )
        # Duplicado debe fallar
        with pytest.raises(ValidationError):  # unique_together
            config2 = LunaConfiguracion(
                lunMatCod=material,
                lunTipCod=tipo,
                lunConfPrecioBase=Decimal('60.00')
            )
            config2.full_clean()

    @pytest.mark.django_db
    def test_luna_configuracion_precio_negativo(self):
        """Configuración con precio negativo - ValidationError"""
        material = LunaMaterial.objects.create(lunMatNombre='Trivex')
        tipo = LunaTipo.objects.create(lunTipNombre='Progresivo')
        config = LunaConfiguracion(
            lunMatCod=material,
            lunTipCod=tipo,
            lunConfPrecioBase=Decimal('-10.00')
        )
        with pytest.raises(ValidationError) as exc:
            config.full_clean()
        assert 'lunConfPrecioBase' in str(exc.value)


# ==================== SERIALIZER TESTS ====================

class TestProductSerializers:
    """Tests para serializers de productos"""

    @pytest.mark.django_db
    def test_product_list_serializer(self, montura_data):
        """ListSerializer para productos"""
        product = Product.objects.create(**montura_data)
        serializer = ProductListSerializer(product)
        data = serializer.data
        assert 'prodCod' in data
        assert 'prodCode' in data
        assert 'prodDescr' in data
        assert 'prodMarca' in data
        assert 'prodStock' in data
        assert 'prodPrecioVenta' in data
        assert 'categoria' in data

    @pytest.mark.django_db
    def test_product_detail_serializer(self, montura_data):
        """DetailSerializer para productos"""
        product = Product.objects.create(**montura_data)
        serializer = ProductDetailSerializer(product)
        data = serializer.data
        assert 'prodCod' in data
        assert 'categoria' in data
        assert 'proveedor' in data

    @pytest.mark.django_db
    def test_product_create_serializer_valid(self, montura_data):
        """Serializer para crear producto"""
        data = {
            'catproCod': montura_data['catproCod'].catproCod,
            'provCod': montura_data['provCod'].provCod,
            'prodMarca': 'OAKLEY',
            'prodMate': 'M',
            'prodColor': 'PLATA',
            'prodTalla': '52-16-140',
            'prodCostoInv': '60.00',
            'prodPrecioVenta': '120.00',
            'prodStock': 15
        }
        serializer = ProductCreateUpdateSerializer(data=data)
        assert serializer.is_valid()

    @pytest.mark.django_db
    def test_luna_material_serializer(self):
        """Serializer para material de luna"""
        material = LunaMaterial.objects.create(lunMatNombre='CR-39')
        serializer = LunaMaterialSerializer(material)
        assert serializer.data['lunMatNombre'] == 'CR-39'

    @pytest.mark.django_db
    def test_luna_tipo_serializer(self):
        """Serializer para tipo de luna"""
        tipo = LunaTipo.objects.create(lunTipNombre='Progresivo')
        serializer = LunaTipoSerializer(tipo)
        assert serializer.data['lunTipNombre'] == 'Progresivo'

    @pytest.mark.django_db
    def test_luna_caracteristica_serializer(self):
        """Serializer para característica de luna"""
        caracteristica = LunaCaracteristica.objects.create(
            lunCarNombre='Anti-Reflect',
            lunCarPrecioAdicional=Decimal('25.00')
        )
        serializer = LunaCaracteristicaSerializer(caracteristica)
        assert serializer.data['lunCarNombre'] == 'Anti-Reflect'

    @pytest.mark.django_db
    def test_luna_configuracion_serializer(self):
        """Serializer para configuración de luna"""
        material = LunaMaterial.objects.create(lunMatNombre='Trivex')
        tipo = LunaTipo.objects.create(lunTipNombre='Progresivo')
        config = LunaConfiguracion.objects.create(
            lunMatCod=material,
            lunTipCod=tipo,
            lunConfPrecioBase=Decimal('50.00')
        )
        serializer = LunaConfiguracionSerializer(config)
        assert serializer.data['lunConfPrecioBase'] == '50.00'


# ==================== VIEW TESTS ====================

class TestProductViewSet:
    """Tests para ProductViewSet"""

    @pytest.mark.django_db
    def test_list_products_unauthenticated(self, api_client):
        """Listar sin autenticar - 401"""
        response = api_client.get('/api/products/')
        assert response.status_code == 401

    @pytest.mark.django_db
    def test_list_products_authenticated(self, logistica_client, montura_data):
        """Listar con autenticación - 200"""
        Product.objects.create(**montura_data)
        response = logistica_client.get('/api/products/')
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_list_products_search_by_code(self, logistica_client, montura_data):
        """Buscar por código"""
        product = Product.objects.create(**montura_data)
        response = logistica_client.get(f'/api/products/?search={product.prodCode}')
        assert response.status_code == 200
        assert len(response.data['results']) >= 1

    @pytest.mark.django_db
    def test_list_products_search_by_marca(self, logistica_client, montura_data):
        """Buscar por marca"""
        Product.objects.create(**montura_data)
        response = logistica_client.get('/api/products/?search=RAY-BAN')
        assert response.status_code == 200
        assert len(response.data['results']) >= 1

    @pytest.mark.django_db
    def test_retrieve_product(self, logistica_client, montura_data):
        """Obtener producto específico"""
        product = Product.objects.create(**montura_data)
        response = logistica_client.get(f'/api/products/{product.prodCod}/')
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_create_product_unauthenticated(self, api_client, montura_data):
        """Crear sin autenticar - 401"""
        response = api_client.post('/api/products/', {})
        assert response.status_code == 401

    @pytest.mark.django_db
    def test_create_product_authenticated(self, logistica_client, montura_data):
        """Crear con autenticación - 201"""
        data = {
            'catproCod': montura_data['catproCod'].catproCod,
            'provCod': montura_data['provCod'].provCod,
            'prodMarca': 'OAKLEY',
            'prodMate': 'M',
            'prodColor': 'PLATA',
            'prodTalla': '52-16-140',
            'prodCostoInv': '60.00',
            'prodPrecioVenta': '120.00',
            'prodStock': 15
        }
        response = logistica_client.post('/api/products/', data)
        assert response.status_code == 201

    @pytest.mark.django_db
    def test_update_product(self, logistica_client, montura_data):
        """Actualizar producto - 200"""
        product = Product.objects.create(**montura_data)
        data = {
            'catproCod': montura_data['catproCod'].catproCod,
            'provCod': montura_data['provCod'].provCod,
            'prodMarca': 'OAKLEY',
            'prodMate': 'M',
            'prodColor': 'PLATA',
            'prodTalla': '52-16-140',
            'prodCostoInv': '60.00',
            'prodPrecioVenta': '120.00',
            'prodStock': 15
        }
        response = logistica_client.put(f'/api/products/{product.prodCod}/', data)
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_delete_product(self, logistica_client, montura_data):
        """Eliminar producto - 204"""
        product = Product.objects.create(**montura_data)
        response = logistica_client.delete(f'/api/products/{product.prodCod}/')
        assert response.status_code == 204


class TestProductActions:
    """Tests para acciones personalizadas de ProductViewSet"""

    @pytest.mark.django_db
    def test_monturas_action(self, logistica_client, montura_data, accesorio_data):
        """Acción monturas() retorna solo monturas"""
        Product.objects.create(**montura_data)
        Product.objects.create(**accesorio_data)
        response = logistica_client.get('/api/products/monturas/')
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['prodMate'] != 'N'  # No es accesorio

    @pytest.mark.django_db
    def test_accesorios_action(self, logistica_client, montura_data, accesorio_data):
        """Acción accesorios() retorna solo accesorios"""
        Product.objects.create(**montura_data)
        Product.objects.create(**accesorio_data)
        response = logistica_client.get('/api/products/accesorios/')
        assert response.status_code == 200
        assert len(response.data) == 1

    @pytest.mark.django_db
    def test_stock_bajo_action(self, logistica_client, montura_data):
        """Acción stock_bajo() retorna productos bajo mínimo"""
        montura_data['prodStock'] = 5
        montura_data['prodStockMin'] = 10
        Product.objects.create(**montura_data)
        response = logistica_client.get('/api/products/stock_bajo/')
        assert response.status_code == 200
        assert len(response.data) == 1

    @pytest.mark.django_db
    def test_estadisticas_action(self, logistica_client, montura_data, accesorio_data):
        """Acción estadisticas() retorna métricas"""
        Product.objects.create(**montura_data)
        Product.objects.create(**accesorio_data)
        response = logistica_client.get('/api/products/estadisticas/')
        assert response.status_code == 200
        assert 'totalProducts' in response.data
        assert 'lowStockCount' in response.data
        assert 'totalValue' in response.data
        assert 'monturaCount' in response.data

    @pytest.mark.django_db
    def test_ajustar_stock_action(self, logistica_client, montura_data):
        """Acción ajustar_stock() modifica stock"""
        product = Product.objects.create(**montura_data)
        response = logistica_client.post(
            f'/api/products/{product.prodCod}/ajustar_stock/',
            {'stock': 20}
        )
        assert response.status_code == 200
        assert response.data['prodStock'] == 20


class TestLunaViewSets:
    """Tests para ViewSets de lunas"""

    @pytest.mark.django_db
    def test_luna_material_list(self, logistica_client):
        """Listar materiales de luna"""
        LunaMaterial.objects.create(lunMatNombre='Trivex')
        response = logistica_client.get('/api/lunas/materiales/')
        assert response.status_code == 200
        assert len(response.data) >= 1

    @pytest.mark.django_db
    def test_luna_tipo_list(self, logistica_client):
        """Listar tipos de luna"""
        LunaTipo.objects.create(lunTipNombre='Progresivo')
        response = logistica_client.get('/api/lunas/tipos/')
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_luna_caracteristica_list(self, logistica_client):
        """Listar características de luna"""
        LunaCaracteristica.objects.create(
            lunCarNombre='Anti-Reflect',
            lunCarPrecioAdicional=Decimal('25.00')
        )
        response = logistica_client.get('/api/lunas/caracteristicas/')
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_luna_configuracion_list(self, logistica_client):
        """Listar configuraciones de luna"""
        material = LunaMaterial.objects.create(lunMatNombre='Trivex')
        tipo = LunaTipo.objects.create(lunTipNombre='Progresivo')
        LunaConfiguracion.objects.create(
            lunMatCod=material,
            lunTipCod=tipo,
            lunConfPrecioBase=Decimal('50.00')
        )
        response = logistica_client.get('/api/lunas/configuracion/')
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_create_luna_material(self, logistica_client):
        """Crear material de luna"""
        response = logistica_client.post(
            '/api/lunas/materiales/',
            {'lunMatNombre': 'Trivex', 'lunMatDescripcion': 'Material ligero'}
        )
        assert response.status_code == 201

    @pytest.mark.django_db
    def test_create_luna_configuracion(self, logistica_client):
        """Crear configuración de luna"""
        material = LunaMaterial.objects.create(lunMatNombre='Trivex')
        tipo = LunaTipo.objects.create(lunTipNombre='Progresivo')
        response = logistica_client.post(
            '/api/lunas/configuracion/',
            {
                'lunMatCod': material.lunMatCod,
                'lunTipCod': tipo.lunTipCod,
                'lunConfPrecioBase': '50.00'
            }
        )
        assert response.status_code == 201


# ==================== PERMISSION TESTS ====================

class TestProductPermissions:
    """Tests de permisos para productos"""

    @pytest.mark.django_db
    def test_logistica_can_access(self, logistica_client):
        """Logística puede acceder"""
        response = logistica_client.get('/api/products/')
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_gerente_can_access(self, gerente_client):
        """Gerente puede acceder"""
        response = gerente_client.get('/api/products/')
        assert response.status_code == 200
