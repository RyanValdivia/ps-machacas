from rest_framework import serializers
from .models import Product, LunaMaterial, LunaTipo, LunaCaracteristica, LunaConfiguracion
from categories.models import ProductCategory
from suppliers.models import Supplier

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['catproCod', 'catproCode', 'catproNom']

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['provCod', 'provRazSocial']

class ProductListSerializer(serializers.ModelSerializer):
    """Serializer para listado de productos (incluye campos necesarios para inventario)"""
    categoria = serializers.CharField(source='catproCod.catproNom', read_only=True)
    proveedor = serializers.CharField(source='provCod.provRazSocial', read_only=True)
    material_display = serializers.CharField(source='get_prodMate_display', read_only=True)
    genero_display = serializers.CharField(source='get_prodGenero_display', read_only=True)
    estado_display = serializers.CharField(source='get_prodEstado_display', read_only=True)
    margen_ganancia = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            # Identificadores
            'prodCod',
            'prodCode',
            'prodDescr',
            
            # Relaciones básicas
            'catproCod',
            'categoria',
            'provCod',
            'proveedor',
            
            # Atributos del producto
            'prodMarca',
            'prodMate',
            'material_display',
            'prodColor',
            'prodTalla',
            'prodGenero',
            'genero_display',
            'prodTieneSobrelente',
            'prodForma',
            'prodDescripcionAdicional',
            
            # Precios y stock
            'prodCostoInv',
            'prodPrecioVenta',
            'prodStock',
            'prodStockMin',
            
            # Estado
            'prodEstado',
            'estado_display',
            
            # Propiedades calculadas
            'margen_ganancia',
            'created_at',
            'updated_at',
        ]

class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer para detalle completo del producto"""
    catproCod_detail = ProductCategorySerializer(source='catproCod', read_only=True)
    provCod_detail = SupplierSerializer(source='provCod', read_only=True)
    material_display = serializers.CharField(source='get_prodMate_display', read_only=True)
    genero_display = serializers.CharField(source='get_prodGenero_display', read_only=True)
    estado_display = serializers.CharField(source='get_prodEstado_display', read_only=True)
    
    # Propiedades calculadas
    margen_ganancia = serializers.ReadOnlyField()
    ganancia_unitaria = serializers.ReadOnlyField()
    valor_total_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'prodCod',
            'prodCode',
            'prodDescr',
            'catproCod',
            'catproCod_detail',
            'provCod',
            'provCod_detail',
            'prodMarca',
            'prodMate',
            'material_display',
            'prodColor',
            'prodTalla',
            'prodGenero',
            'genero_display',
            'prodTieneSobrelente',
            'prodForma',
            'prodDescripcionAdicional',
            'prodCostoInv',
            'prodPrecioVenta',
            'prodStock',
            'prodStockMin',
            'prodEstado',
            'estado_display',
            'margen_ganancia',
            'ganancia_unitaria',
            'valor_total_stock',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['prodCode', 'prodDescr', 'created_at', 'updated_at']

class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear y actualizar productos"""
    
    class Meta:
        model = Product
        fields = [
            'catproCod',
            'provCod',
            'prodMarca',
            'prodMate',
            'prodColor',
            'prodTalla',
            'prodGenero',
            'prodTieneSobrelente',
            'prodForma',
            'prodDescripcionAdicional',
            'prodCostoInv',
            'prodPrecioVenta',
            'prodStock',
            'prodStockMin',
            'prodEstado',
        ]
    
    def validate(self, data):
        """Validaciones personalizadas"""
        categoria = data.get('catproCod')
        material = data.get('prodMate')
        marca = data.get('prodMarca')
        talla = data.get('prodTalla')
        
        if categoria:
            es_montura = categoria.catproCode == 'MO'
            es_accesorio = categoria.catproCode == 'AC'
            
            if es_montura:
                if not marca or len(marca.strip()) < 2:
                    raise serializers.ValidationError({
                        'prodMarca': 'Marca obligatoria para monturas (minimo 2 caracteres)'
                    })
                if material == 'N':
                    raise serializers.ValidationError({
                        'prodMate': 'Debes seleccionar un material para monturas (A, M, TR o C)'
                    })
                if not talla:
                    raise serializers.ValidationError({
                        'prodTalla': 'Talla obligatoria para monturas'
                    })
            
            if es_accesorio:
                if material != 'N':
                    raise serializers.ValidationError({
                        'prodMate': 'Los accesorios deben tener material "No aplica"'
                    })
        
        return data


# ==========================================
# Serializers para Lunas Personalizadas
# ==========================================

class LunaMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = LunaMaterial
        fields = ['lunMatCod', 'lunMatNombre', 'lunMatDescripcion']


class LunaTipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = LunaTipo
        fields = ['lunTipCod', 'lunTipNombre', 'lunTipDescripcion']


class LunaCaracteristicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = LunaCaracteristica
        fields = ['lunCarCod', 'lunCarNombre', 'lunCarDescripcion', 'lunCarPrecioAdicional']


class LunaConfiguracionSerializer(serializers.ModelSerializer):
    material = LunaMaterialSerializer(source='lunMatCod', read_only=True)
    tipo = LunaTipoSerializer(source='lunTipCod', read_only=True)
    
    class Meta:
        model = LunaConfiguracion
        fields = [
            'lunConfCod',
            'lunMatCod',
            'lunTipCod',
            'material',
            'tipo',
            'lunConfPrecioBase'
        ]