from rest_framework import serializers
from .models import Venta, VentaDetalle, Comprobante, ComprobanteDetalle
from products.models import Product
from clients.models import Client
from users.models import User
from suppliers.models import Supplier
from decimal import Decimal


class ClienteSimpleSerializer(serializers.ModelSerializer):
    """Serializer simple para mostrar datos del cliente"""
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Client
        fields = ['cliCod', 'cliNomCompleto', 'cliNumDoc', 'cliTipoDoc', 'nombre_completo']
    
    def get_nombre_completo(self, obj):
        return f"{obj.cliNomCompleto}"


class ProductoSimpleSerializer(serializers.ModelSerializer):
    """Serializer simple para productos en ventas"""
    categoria = serializers.CharField(source='catproCod.catproNom', read_only=True)
    
    class Meta:
        model = Product
        fields = ['prodCod', 'prodCode', 'prodDescr', 'prodMarca', 'prodPrecioVenta', 'prodStock', 'categoria']


class VentaDetalleSerializer(serializers.ModelSerializer):
    """Serializer para detalle de venta (lectura)"""
    producto = ProductoSimpleSerializer(source='prodCod', read_only=True)
    lunaLaboratorio_nombre = serializers.CharField(source='lunaLaboratorio.provRazSocial', read_only=True)
    lunaLaboratorio_id = serializers.IntegerField(source='lunaLaboratorio.provCod', read_only=True)
    
    class Meta:
        model = VentaDetalle
        fields = [
            'ventDetCod',
            'prodCod',
            'producto',
            'ventDetCantidad',
            'ventDetPrecioUni',
            'ventDetSubtotal',
            'ventDetDescuento',
            'ventDetTotal',
            'ventDetDescripcion',
            'ventDetMarca',
            'ventDetAnulado',
            # Campos de luna personalizada
            'esLunaPersonalizada',
            'lunaMaterial',
            'lunaTipo',
            'lunaCaracteristicas',
            'lunaLaboratorio',
            'lunaLaboratorio_nombre',
            'lunaLaboratorio_id',
            'lunaCostoLaboratorio'
        ]
        read_only_fields = ['ventDetCod', 'ventDetSubtotal', 'ventDetTotal', 'ventDetDescripcion', 'ventDetMarca']


class LunaCaracteristicasField(serializers.Field):
    """Campo personalizado que acepta array de IDs o string"""
    
    def to_internal_value(self, data):
        """Convertir de frontend (array o string) a string para el modelo"""
        if isinstance(data, list):
            # Array de IDs -> convertir a nombres separados por coma
            if data:
                from products.models import LunaCaracteristica
                caracteristicas = LunaCaracteristica.objects.filter(lunCarCod__in=data)
                nombres = [c.lunCarNombre for c in caracteristicas]
                return ', '.join(nombres)
            return ''
        elif isinstance(data, str):
            return data
        return ''
    
    def to_representation(self, value):
        """Convertir de modelo (string) a frontend (string)"""
        return value if value else ''


class VentaDetalleCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar detalle de venta"""
    lunaCaracteristicas = LunaCaracteristicasField(required=False, allow_null=True)
    lunConfCod = serializers.IntegerField(required=False, allow_null=True, write_only=True)  # Campo auxiliar, no se guarda en DB
    
    class Meta:
        model = VentaDetalle
        fields = [
            'prodCod',
            'ventDetCantidad',
            'ventDetPrecioUni',
            'ventDetDescuento',
            'esLunaPersonalizada',
            'lunConfCod',  # Campo auxiliar para procesar configuración
            'lunaMaterial',
            'lunaTipo',
            'lunaCaracteristicas',
            'lunaLaboratorio',
            'lunaCostoLaboratorio']
        extra_kwargs = {
            'lunaMaterial': {'required': False, 'allow_blank': True},
            'lunaTipo': {'required': False, 'allow_blank': True},
        }
    
    def validate_ventDetCantidad(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor a 0")
        return value
    
    def validate(self, data):
        """Convertir lunConfCod a material/tipo si viene en initial_data"""
        # Acceder a los datos crudos del request
        if hasattr(self, 'initial_data'):
            raw_data = self.initial_data
            
            # Si viene lunConfCod, convertir a material y tipo
            if raw_data.get('lunConfCod'):
                from products.models import LunaConfiguracion, LunaCaracteristica
                try:
                    config = LunaConfiguracion.objects.select_related(
                        'lunMatCod', 'lunTipCod'
                    ).get(pk=raw_data['lunConfCod'])
                    data['lunaMaterial'] = config.lunMatCod.lunMatNombre
                    data['lunaTipo'] = config.lunTipCod.lunTipNombre
                    
                    # Convertir IDs de características a nombres
                    if raw_data.get('lunaCaracteristicas'):
                        caracteristicas_ids = raw_data['lunaCaracteristicas']
                        if caracteristicas_ids:
                            caracteristicas = LunaCaracteristica.objects.filter(
                                lunCarCod__in=caracteristicas_ids
                            )
                            nombres = [c.lunCarNombre for c in caracteristicas]
                            data['lunaCaracteristicas'] = ', '.join(nombres) if nombres else ''
                except LunaConfiguracion.DoesNotExist:
                    pass
        
        # Validar según tipo
        es_luna = data.get('esLunaPersonalizada', False)
        
        if es_luna:
            if not data.get('ventDetPrecioUni'):
                raise serializers.ValidationError({
                    'ventDetPrecioUni': 'El precio es obligatorio para lunas'
                })
        else:
            # Validar stock solo para productos normales
            producto = data.get('prodCod')
            cantidad = data.get('ventDetCantidad', 1)
            
            if producto and cantidad > producto.prodStock:
                raise serializers.ValidationError({
                    'ventDetCantidad': f'Stock insuficiente. Disponible: {producto.prodStock}'
                })
        
        return data


class VentaSerializer(serializers.ModelSerializer):
    """Serializer para venta (lectura)"""
    cliente = ClienteSimpleSerializer(source='cliCod', read_only=True)
    usuario = serializers.CharField(source='usuCod.username', read_only=True)
    detalles = VentaDetalleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Venta
        fields = [
            'ventCod',
            'cliCod',
            'cliente',
            'usuCod',
            'usuario',
            'ventFecha',
            'ventSubTotal',
            'ventDescuento',
            'ventTotal',
            'ventObservaciones',
            'ventFormaPago',
            'ventReferenciaPago',
            'ventTarjetaTipo',
            'ventAdelanto',
            'ventSaldo',
            'ventEstado',
            'ventEstadoRecoj',
            'ventFechaEntrega',
            'detalles']


class VentaListSerializer(serializers.ModelSerializer):
    """Serializer para listado de ventas"""
    cliente = ClienteSimpleSerializer(source='cliCod', read_only=True)
    vendedor = serializers.CharField(source='usuCod.username', read_only=True)
    estado_pago_display = serializers.CharField(source='get_ventEstado_display', read_only=True)
    estado_pedido_display = serializers.CharField(source='get_ventEstadoRecoj_display', read_only=True)
    nombre_cliente = serializers.ReadOnlyField()
    
    class Meta:
        model = Venta
        fields = [
            'ventCod',
            'ventFecha',
            'cliente',
            'nombre_cliente',
            'vendedor',
            'ventTotal',
            'ventAdelanto',
            'ventSaldo',
            'ventEstado',
            'estado_pago_display',
            'ventEstadoRecoj',
            'estado_pedido_display',
            'ventAnulada'
        ]


class VentaDetailSerializer(serializers.ModelSerializer):
    """Serializer para detalle completo de venta"""
    cliente = ClienteSimpleSerializer(source='cliCod', read_only=True)
    vendedor = serializers.CharField(source='usuCod.username', read_only=True)
    detalles = VentaDetalleSerializer(source='ventadetalle_set', many=True, read_only=True)
    estado_pago_display = serializers.CharField(source='get_ventEstado_display', read_only=True)
    estado_pedido_display = serializers.CharField(source='get_ventEstadoRecoj_display', read_only=True)
    forma_pago_display = serializers.CharField(source='get_ventFormaPago_display', read_only=True)
    nombre_cliente = serializers.ReadOnlyField()
    
    class Meta:
        model = Venta
        fields = [
            'ventCod',
            'ventFecha',
            'ventFechaEntrega',
            'usuCod',
            'vendedor',
            'cliCod',
            'cliente',
            'nombre_cliente',
            'cajaAperCod',
            'ventSubTotal',
            'ventDescuento',
            'ventTotal',
            'ventAdelanto',
            'ventSaldo',
            'ventEstado',
            'estado_pago_display',
            'ventEstadoRecoj',
            'estado_pedido_display',
            'ventFormaPago',
            'forma_pago_display',
            'ventReferenciaPago',
            'ventTarjetaTipo',
            'ventObservaciones',
            'ventAnulada',
            'ventMotivoAnulacion',
            'detalles'
        ]
        read_only_fields = [
            'ventCod', 'ventFecha', 'ventSubTotal', 'ventTotal', 
            'ventSaldo', 'ventEstado', 'ventAnulada'
        ]


class VentaCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear venta"""
    detalles = VentaDetalleCreateSerializer(many=True, write_only=True)
    
    class Meta:
        model = Venta
        fields = [
            'cliCod',
            'ventObservaciones',
            'ventFormaPago',
            'ventReferenciaPago',
            'ventTarjetaTipo',
            'detalles'
        ]
    
    def validate_detalles(self, value):
        if not value:
            raise serializers.ValidationError("Debe agregar al menos un producto")
        return value
    
    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')
        
        # Obtener usuario del contexto
        usuario = self.context['request'].user
        
        # Crear venta
        venta = Venta.objects.create(
            usuCod=usuario,
            **validated_data
        )
        
        # Crear detalles
        for detalle_data in detalles_data:
            # Procesar lunas personalizadas: convertir lunConfCod a material/tipo
            if detalle_data.get('esLunaPersonalizada') and detalle_data.get('lunConfCod'):
                from products.models import LunaConfiguracion, LunaCaracteristica
                try:
                    config = LunaConfiguracion.objects.select_related(
                        'lunMatCod', 'lunTipCod'
                    ).get(pk=detalle_data['lunConfCod'])
                    
                    # Asignar material y tipo
                    detalle_data['lunaMaterial'] = config.lunMatCod.lunMatNombre
                    detalle_data['lunaTipo'] = config.lunTipCod.lunTipNombre
                    
                    # Convertir IDs de características a nombres
                    if detalle_data.get('lunaCaracteristicas'):
                        caracteristicas_ids = detalle_data['lunaCaracteristicas']
                        if caracteristicas_ids and isinstance(caracteristicas_ids, list):
                            caracteristicas = LunaCaracteristica.objects.filter(
                                lunCarCod__in=caracteristicas_ids
                            )
                            nombres = [c.lunCarNombre for c in caracteristicas]
                            detalle_data['lunaCaracteristicas'] = ', '.join(nombres) if nombres else ''
                        elif isinstance(caracteristicas_ids, str):
                            # Ya es string, mantenerlo
                            pass
                    
                    # Eliminar lunConfCod antes de crear el objeto (no existe en el modelo)
                    detalle_data.pop('lunConfCod', None)
                            
                except LunaConfiguracion.DoesNotExist:
                    detalle_data.pop('lunConfCod', None)
                except Exception as e:
                    detalle_data.pop('lunConfCod', None)
            
            VentaDetalle.objects.create(
                ventCod=venta,
                **detalle_data
            )
        
        # Calcular totales
        venta.calcular_totales()
        venta.save()
        
        return venta


class VentaUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar venta"""
    
    class Meta:
        model = Venta
        fields = [
            'cliCod',
            'ventObservaciones',
            'ventEstadoRecoj',
            'ventFechaEntrega'
        ]


class PagoSerializer(serializers.Serializer):
    """Serializer para registrar pagos"""
    monto = serializers.DecimalField(max_digits=10, decimal_places=2)
    forma_pago = serializers.ChoiceField(choices=Venta.FORMA_PAGO)
    referencia_pago = serializers.CharField(max_length=50, required=False, allow_blank=True)
    tarjeta_tipo = serializers.ChoiceField(choices=Venta.TIPO_TARJETA, required=False, allow_blank=True)
    
    def validate_monto(self, value):
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a 0")
        return value


class ComprobanteDetalleSerializer(serializers.ModelSerializer):
    """Serializer para detalle de comprobante"""
    
    class Meta:
        model = ComprobanteDetalle
        fields = [
            'comdetCod',
            'comdetDescripcion',
            'comdetCantidad',
            'comdetPrecioUni',
            'comdetTotal'
        ]


class ComprobanteSerializer(serializers.ModelSerializer):
    """Serializer para comprobante"""
    venta = VentaSerializer(source='ventCod', read_only=True)
    detalles = ComprobanteDetalleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Comprobante
        fields = [
            'comprCod',
            'ventCod',
            'venta',
            'comprSerie',
            'comprNumero',
            'comprFecha',
            'comprSubtotal',
            'comprIgv',
            'comprTotal',
            'detalles']
