from products.models import Product
from cash.models import CashOpening
from users.models import User
from clients.models import Client
from suppliers.models import Supplier
from decimal import Decimal
from django.db import models, transaction
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

class Venta(models.Model):
    ESTADO_VENTA = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADO', 'Pagado'),
        ('PARCIAL', 'Pago Parcial'),
        ('ANULADO', 'Anulado'),
    ]

    ESTADO_PEDIDO = [
        ('PENDIENTE', 'Pendiente'),
        ('LISTO', 'Listo para recoger'),
        ('ENTREGADO', 'Entregado'),
        ('ANULADO', 'Anulado'),
    ]

    FORMA_PAGO = [
        ('EFECTIVO', 'Efectivo'),
        ('YAPE', 'Yape'),
        ('VISA', 'Visa'),
    ]

    TIPO_TARJETA = [
        ('VISA', 'Visa'),
        ('', 'No Aplica'),
    ]

    # Campos principales
    ventCod = models.AutoField(primary_key=True, verbose_name="Codigo Venta")
    
    usuCod = models.ForeignKey(
        User, 
        on_delete=models.PROTECT,
        verbose_name="Vendedor"
    )

    cajaAperCod = models.ForeignKey(
        CashOpening,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Caja asociada"
    )

    # Cliente
    cliCod = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name='ventas',
        verbose_name="Cliente",
        null=True,
        blank=True,
        help_text="Dejar vacio para cliente generico"
    )

    # Datos de la venta
    ventFecha = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha Venta"
    )
    ventFechaEntrega = models.DateField(
        null=True, 
        blank=True,
        verbose_name="Fecha Entrega Estimada"
    )
    ventEstado = models.CharField(
        max_length=20, 
        choices=ESTADO_VENTA, 
        default='PENDIENTE',
        verbose_name="Estado Pago"
    )
    ventEstadoRecoj = models.CharField(
        max_length=20, 
        choices=ESTADO_PEDIDO, 
        default='PENDIENTE',
        verbose_name="Estado Pedido"
    )
    
    # Totales
    ventSubTotal = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name="Subtotal"
    )
    ventDescuento = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name="Descuento Total"
    )
    ventTotal = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name="Total"
    )
    ventAdelanto = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name="Adelanto"
    )
    ventSaldo = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name="Saldo"
    )
    
    ventObservaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones"
    )
    ventAnulada = models.BooleanField(
        default=False,
        verbose_name="Anulada"
    )
    ventMotivoAnulacion = models.TextField(
        blank=True,
        verbose_name="Motivo Anulacion"
    )

    # Pago
    ventFormaPago = models.CharField(
        max_length=15,
        choices=FORMA_PAGO,
        default='',
        blank=True,
        verbose_name="Forma de Pago"
    )
    ventReferenciaPago = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Referencia de Pago"
    )
    ventTarjetaTipo = models.CharField(
        max_length=10,
        choices=TIPO_TARJETA,
        blank=True,
        verbose_name="Tipo de Tarjeta"
    )

    class Meta:
        db_table = 'venta'
        ordering = ['-ventFecha']
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        indexes = [
            models.Index(fields=['-ventFecha']),
            models.Index(fields=['ventEstado']),
        ]

    def __str__(self):
        cliente_nombre = self.cliCod.cliNombre if self.cliCod else "Cliente Generico"
        return f"Venta #{self.ventCod} - {cliente_nombre} - S/{self.ventTotal}"

    @property
    def nombre_cliente(self):
        if self.cliCod:
            return self.cliCod.cliNomCompleto
        return "Cliente Generico"

    @transaction.atomic
    def anular_venta(self, motivo):
        if self.ventAnulada:
            raise ValidationError("La venta ya esta anulada")

        if self.ventEstadoRecoj == "ENTREGADO":
            raise ValidationError("No se puede anular una venta ya entregada")
        
        # Anular comprobante si existe
        if hasattr(self, 'comprobante'):
            self.comprobante.comprAnulado = True
            self.comprobante.save()

        # Devolver stock de todos los detalles
        detalles = self.ventadetalle_set.select_for_update().all()
        for detalle in detalles:
            if not detalle.ventDetAnulado:
                detalle.devolver_stock()
                # Usar update directo para evitar validaciones
                VentaDetalle.objects.filter(pk=detalle.pk).update(ventDetAnulado=True)

        # Usar update directo para evitar validaciones de caja
        Venta.objects.filter(pk=self.pk).update(
            ventAnulada=True,
            ventEstado="ANULADO",
            ventEstadoRecoj="ANULADO",
            ventMotivoAnulacion=motivo,
            ventAdelanto=Decimal("0"),
            ventSubTotal=Decimal("0"),
            ventDescuento=Decimal("0"),
            ventTotal=Decimal("0"),
            ventSaldo=Decimal("0")
        )
        
        # Refrescar el objeto actual con los cambios
        self.refresh_from_db()

    def establecer_estado_pedido_automatico(self):
        """
        Establece el estado del pedido automáticamente según la lógica:
        - Si tiene lunas personalizadas → PENDIENTE
        - Si NO tiene lunas Y saldo = 0 → ENTREGADO
        - Si NO tiene lunas Y saldo > 0 → LISTO
        """
        if self.ventAnulada:
            return  # No cambiar estado de ventas anuladas
        
        # Verificar si hay lunas personalizadas
        tiene_lunas = self.ventadetalle_set.filter(
            ventDetAnulado=False,
            esLunaPersonalizada=True
        ).exists()
        
        if tiene_lunas:
            # Si tiene lunas, siempre PENDIENTE (esperando fabricación)
            self.ventEstadoRecoj = "PENDIENTE"
        else:
            # Si NO tiene lunas, decidir por saldo
            if self.ventSaldo <= 0:
                # Pagado completo → ENTREGADO
                self.ventEstadoRecoj = "ENTREGADO"
                self.ventFechaEntrega = timezone.now().date()
            else:
                # Saldo pendiente → LISTO (esperando pago)
                self.ventEstadoRecoj = "LISTO"

    def marcar_listo_para_recoger(self):
        if self.ventAnulada:
            raise ValidationError("No puedes marcar como listo una venta anulada")
        self.ventEstadoRecoj = "LISTO"
        self.save()

    def marcar_entregado(self):
        if self.ventAnulada:
            raise ValidationError("Una venta anulada no puede ser entregada")
        if self.ventSaldo > 0:
            raise ValidationError("No puedes entregar una venta con saldo pendiente")
        self.ventEstadoRecoj = "ENTREGADO"
        self.ventFechaEntrega = timezone.now().date()
        self.save()

    @transaction.atomic
    def calcular_totales(self, actualizar_estado_pedido=True):
        """
        Calcula totales de la venta
        
        Args:
            actualizar_estado_pedido: Si es True, actualiza el estado del pedido automáticamente.
                                     Si es False, respeta el estado actual del pedido.
        """
        detalles = self.ventadetalle_set.filter(ventDetAnulado=False)
        
        if not detalles.exists():
            self._reset_totales()
            return

        # Calcular subtotal y descuento
        subtotal = sum(detalle.ventDetSubtotal for detalle in detalles)
        descuento_total = sum(detalle.ventDetDescuento for detalle in detalles)

        # Actualizar campos
        self.ventSubTotal = subtotal
        self.ventDescuento = descuento_total
        self.ventTotal = subtotal - descuento_total
        self.ventSaldo = max(self.ventTotal - self.ventAdelanto, Decimal("0"))

        # Actualizar estado de pago
        self._actualizar_estado()
        
        # Establecer estado de pedido automáticamente solo si se solicita
        if actualizar_estado_pedido:
            self.establecer_estado_pedido_automatico()

    def _reset_totales(self):
        self.ventSubTotal = Decimal("0")
        self.ventDescuento = Decimal("0")
        self.ventTotal = Decimal("0")
        self.ventSaldo = Decimal("0")
        self.ventEstado = "PENDIENTE"

    def _actualizar_estado(self):
        if self.ventAnulada:
            self.ventEstado = "ANULADO"
        elif self.ventSaldo == Decimal("0") and self.ventTotal > Decimal("0"):
            self.ventEstado = "PAGADO"
        elif self.ventAdelanto > Decimal("0") and self.ventSaldo > Decimal("0"):
            self.ventEstado = "PARCIAL"
        else:
            self.ventEstado = "PENDIENTE"

    @transaction.atomic
    def registrar_pago(self, monto, forma_pago, referencia_pago='', tarjeta_tipo=''):
        
        if self.ventAnulada:
            raise ValidationError("No se puede registrar pago en una venta anulada")
        
        monto = Decimal(str(monto))
        
        if monto <= 0:
            raise ValidationError("El monto del pago debe ser mayor a cero")
        
        if monto > self.ventSaldo:
            raise ValidationError(f"El monto (S/{monto}) excede el saldo pendiente (S/{self.ventSaldo})")

        # Buscar sesion de caja abierta
        sesion_caja_actual = CashOpening.objects.filter(
            usuCod=self.usuCod,
            cajaAperEstado='ABIERTA'
        ).first()
        
        if not sesion_caja_actual:
            raise ValidationError("No hay una sesion de caja abierta para registrar el pago")
        
        # Actualizar la caja de la venta
        if self.cajaAperCod != sesion_caja_actual:
            self.cajaAperCod = sesion_caja_actual
        
        # Actualizar campos de pago
        self.ventAdelanto += monto
        self.ventFormaPago = forma_pago
        self.ventReferenciaPago = referencia_pago
        self.ventTarjetaTipo = tarjeta_tipo if forma_pago == 'TARJETA' else ''
        
        # Recalcular totales SIN actualizar el estado del pedido
        # Esto respeta el estado manual que pudo haber puesto el usuario
        self.calcular_totales(actualizar_estado_pedido=False)
        self.save()
        
        # Generar comprobante si esta totalmente pagado
        if self.ventSaldo == Decimal("0") and self.ventTotal > Decimal("0"):
            comprobante = self._generar_comprobante()
            return {
                "mensaje": f"Pago registrado: S/{monto}",
                "saldo_actual": float(self.ventSaldo),
                "estado": self.ventEstado,
                "comprobante": comprobante.comprobante_completo
            }
        
        return {
            "mensaje": f"Pago registrado: S/{monto}",
            "saldo_actual": float(self.ventSaldo),
            "estado": self.ventEstado
        }

    def _generar_comprobante(self):
        """Genera comprobante simple (nota de venta)"""
        if hasattr(self, 'comprobante'):
            return self.comprobante

        comprobante = Comprobante.objects.create(ventCod=self)
        return comprobante

    def save(self, *args, **kwargs):
        """Guarda la venta y asigna sesion de caja si es necesario"""
        
        # Asignar sesion si es venta nueva o no tiene sesion
        if not self.cajaAperCod and self.usuCod:
            # ✅ CORREGIDO: Buscar CUALQUIER caja abierta, no solo la del usuario
            sesion_caja_abierta = CashOpening.objects.filter(
                cajaAperEstado='ABIERTA'
            ).order_by('cajaApertuFechHora').first()
            
            if sesion_caja_abierta:
                self.cajaAperCod = sesion_caja_abierta
                print(f"✓ Venta asignada a apertura #{sesion_caja_abierta.cajaAperCod}")
            else:
                if self.ventAdelanto > 0:
                    raise ValidationError(
                        "Debe abrir caja antes de registrar ventas con pago"
                    )

        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        """Validaciones de la venta"""
        super().clean()

        # Validar caja si hay adelanto
        if self.ventAdelanto > 0 and not self.cajaAperCod:
            raise ValidationError({
                'cajaAperCod': 'Se requiere una sesion de caja abierta para registrar pagos'
            })
        
        if self.cajaAperCod:
            if self.cajaAperCod.cajaAperEstado != 'ABIERTA':
                raise ValidationError({
                    'cajaAperCod': 'La sesion de caja no esta abierta'
                })
            
            # ✅ REMOVIDO: Ya no validamos que la caja sea del mismo usuario
            # Cualquier vendedor puede usar cualquier caja abierta

################################################################################### VENTA_DETALLE

class VentaDetalle(models.Model):

    ventDetCod = models.AutoField(primary_key=True, verbose_name="Codigo Detalle")
    
    ventCod = models.ForeignKey(
        Venta, 
        on_delete=models.CASCADE,
        verbose_name="Venta"
    )
    prodCod = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name="Producto"
    )
    
    # Cantidades y precios
    ventDetCantidad = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Cantidad",
        default=1
    )
    
    ventDetPrecioUni = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Precio Unitario",
        null=True,  # ← AGREGADO: permite null temporalmente
        blank=True  # ← AGREGADO: permite blank
    )
    
    ventDetSubtotal = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Subtotal",
        default=0  # ← AGREGADO: valor por defecto
    )
    
    ventDetDescuento = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Descuento"
    )
    
    ventDetTotal = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Total",
        default=0  # ← AGREGADO: valor por defecto
    )
    
    ventDetAnulado = models.BooleanField(
        default=False,
        verbose_name="Anulado"
    )

    # Datos del producto al momento de la venta
    ventDetDescripcion = models.CharField(
        max_length=500,
        verbose_name="Descripcion",
        blank=True  # ← AGREGADO: permite blank
    )
    ventDetMarca = models.CharField(
        max_length=100,
        verbose_name="Marca",
        blank=True
    )
    
    # ==================== CAMPOS PARA LUNAS PERSONALIZADAS ====================
    esLunaPersonalizada = models.BooleanField(
        default=False,
        verbose_name="Es Luna Personalizada"
    )
    
    # Configuración de la luna
    lunaMaterial = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Material de Luna",
        help_text="Ej: Orgánico, Policarbonato, Cristal"
    )
    lunaTipo = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Tipo de Luna",
        help_text="Ej: Monofocal, Bifocal, Multifocal, Progresivo"
    )
    lunaCaracteristicas = models.TextField(
        blank=True,
        verbose_name="Características Adicionales",
        help_text="Ej: Blue Block, Fotocromático, Anti-reflejo (separadas por comas)"
    )
    
    # Información del laboratorio (se completa después)
    lunaLaboratorio = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='lunas_suministradas',
        verbose_name="Laboratorio Proveedor",
        help_text="Laboratorio que fabricó la luna"
    )
    lunaCostoLaboratorio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Costo del Laboratorio",
        help_text="Costo que cobró el laboratorio"
    )
    
    class Meta:
        db_table = "venta_detalle"
        ordering = ["ventDetCod"]
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalles de Venta"

    def __str__(self):
        marca = self.ventDetMarca if self.ventDetMarca else "Sin marca"
        return f"Det #{self.ventDetCod} - {marca} x{self.ventDetCantidad}"
    
    def clean(self):
        """Validaciones antes de guardar"""
        super().clean()
        
        # No validar si está anulado o no tiene datos completos
        if self.ventDetAnulado or not self.prodCod_id:
            return
        
        # Las lunas personalizadas NO validan stock
        if self.esLunaPersonalizada:
            return

        # Validar stock disponible
        cantidad_requerida = self.ventDetCantidad
        
        # Si es actualización, considerar el stock que se va a liberar
        if self.pk:
            try:
                detalle_original = VentaDetalle.objects.get(pk=self.pk)
                stock_disponible = self.prodCod.prodStock + detalle_original.ventDetCantidad
            except VentaDetalle.DoesNotExist:
                stock_disponible = self.prodCod.prodStock
        else:
            stock_disponible = self.prodCod.prodStock

        if cantidad_requerida > stock_disponible:
            raise ValidationError(
                f"Stock insuficiente para {self.prodCod.prodDescr}. "
                f"Disponible: {stock_disponible}, Solicitado: {cantidad_requerida}"
            )
    
    @transaction.atomic
    def save(self, *args, **kwargs):
        # CORREGIDO: Manejo simplificado de stock
        is_new = self.pk is None
        cantidad_anterior = 0
        
        # Si es edición, obtener cantidad anterior
        if not is_new:
            try:
                detalle_original = VentaDetalle.objects.select_for_update().get(pk=self.pk)
                cantidad_anterior = detalle_original.ventDetCantidad
            except VentaDetalle.DoesNotExist:
                is_new = True
        
        # Copiar datos del producto si es necesario
        if not self.ventDetPrecioUni or not self.ventDetDescripcion:
            self._copiar_datos_producto()
        
        # Calcular totales
        self._calcular_totales()
        
        # Validar
        self.full_clean()
        
        # Guardar
        super().save(*args, **kwargs)
        
        # CORREGIDO: Actualizar stock SOLO si NO es luna personalizada Y NO está anulado
        if not self.ventDetAnulado and not self.esLunaPersonalizada:
            producto = Product.objects.select_for_update().get(pk=self.prodCod_id)
            
            if is_new:
                # Creación: restar cantidad
                producto.prodStock -= self.ventDetCantidad
            else:
                # Edición: ajustar diferencia
                diferencia = cantidad_anterior - self.ventDetCantidad
                producto.prodStock += diferencia
            
            producto.save(update_fields=['prodStock'])
        
        # Actualizar totales de la venta
        if self.ventCod_id:
            self.ventCod.calcular_totales()
            self.ventCod.save()
    
    def _copiar_datos_producto(self):
        """Copia datos del producto o genera descripción de luna personalizada"""
        if self.prodCod:
            # Si NO es luna personalizada, copiar datos del producto normalmente
            if not self.esLunaPersonalizada:
                self.ventDetPrecioUni = Decimal(self.prodCod.prodPrecioVenta).quantize(Decimal("0.01"))
                self.ventDetDescripcion = self.prodCod.prodDescr
                self.ventDetMarca = self.prodCod.prodMarca if self.prodCod.prodMarca else ""
            else:
                # Es luna personalizada: generar descripción descriptiva
                if self.lunaMaterial and self.lunaTipo:
                    # Construir descripción base con los campos de texto
                    descripcion = f"LUNA {self.lunaMaterial.upper()} - {self.lunaTipo.upper()}"
                    
                    # Agregar características si existen (texto separado por comas)
                    if self.lunaCaracteristicas:
                        descripcion += f" ({self.lunaCaracteristicas})"
                    
                    self.ventDetDescripcion = descripcion
                    self.ventDetMarca = "PERSONALIZADO"
                else:
                    # Luna sin material/tipo completo
                    self.ventDetDescripcion = "LUNA PERSONALIZADA"
                    self.ventDetMarca = "PERSONALIZADO"

    def _calcular_totales(self):
        """Calcula subtotal y total"""
        if self.ventDetPrecioUni:
            subtotal = Decimal(self.ventDetPrecioUni) * self.ventDetCantidad
            self.ventDetSubtotal = subtotal.quantize(Decimal("0.01"))
            self.ventDetTotal = (self.ventDetSubtotal - self.ventDetDescuento).quantize(Decimal("0.01"))

    @transaction.atomic
    def devolver_stock(self):
        """Devuelve stock al producto"""
        if not self.ventDetAnulado and self.prodCod_id:
            producto = Product.objects.select_for_update().get(pk=self.prodCod_id)
            producto.prodStock += self.ventDetCantidad
            producto.save(update_fields=["prodStock"])

################################################################################### COMPROBANTE

class Comprobante(models.Model):
    """Comprobante simple - Nota de Venta"""
    
    comprCod = models.AutoField(primary_key=True, verbose_name="Codigo Comprobante")
    
    ventCod = models.OneToOneField(
        Venta,
        on_delete=models.PROTECT,
        related_name='comprobante',
        verbose_name="Venta asociada"
    )

    # Serie y correlativo
    comprSerie = models.CharField(
        max_length=4, 
        verbose_name="Serie",
        default="NV01"
    )
    comprCorrelativo = models.IntegerField(verbose_name="Correlativo")
    
    comprFechaEmision = models.DateTimeField(
        default=timezone.now, 
        verbose_name="Fecha de Emision"
    )

    # Cliente
    comprNombreCliente = models.CharField(
        max_length=200, 
        verbose_name="Nombre Cliente"
    )
    comprDocumentoCliente = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Documento Cliente"
    )

    # Totales
    comprSubtotal = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        verbose_name="Subtotal"
    )
    comprDescuento = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        verbose_name="Descuento"
    )
    comprTotal = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        verbose_name="Total"
    )

    comprAnulado = models.BooleanField(
        default=False,
        verbose_name="Anulado"
    )

    class Meta:
        db_table = 'comprobante'
        ordering = ['-comprFechaEmision']
        verbose_name = 'Comprobante'
        verbose_name_plural = 'Comprobantes'
        indexes = [
            models.Index(fields=['comprSerie', 'comprCorrelativo']),
        ]

    def __str__(self):
        return f"Nota de Venta {self.comprobante_completo}"

    @property
    def comprobante_completo(self):
        """Retorna el numero completo"""
        return f"{self.comprSerie}-{str(self.comprCorrelativo).zfill(8)}"

    def save(self, *args, **kwargs):
        """Guarda y genera datos automaticamente"""
        if not self.pk:
            self._asignar_correlativo()
            self._copiar_datos_venta()
        
        super().save(*args, **kwargs)
        
        # Generar detalles
        if not self.detalles.exists():
            self.generar_detalles_desde_venta()

    def _asignar_correlativo(self):
        """Asigna el siguiente correlativo"""
        ultimo = Comprobante.objects.filter(
            comprSerie=self.comprSerie
        ).order_by('-comprCorrelativo').first()
        
        self.comprCorrelativo = (ultimo.comprCorrelativo + 1) if ultimo else 1

    def _copiar_datos_venta(self):
        """Copia datos de la venta"""
        venta = self.ventCod
        
        # Datos del cliente
        if venta.cliCod:
            self.comprNombreCliente = venta.cliCod.cliNomCompleto
            self.comprDocumentoCliente = f"{venta.cliCod.cliTipoDoc}: {venta.cliCod.cliNumDoc}"
        else:
            self.comprNombreCliente = "Cliente Generico"
            self.comprDocumentoCliente = ""
        
        # Totales
        self.comprSubtotal = venta.ventSubTotal
        self.comprDescuento = venta.ventDescuento
        self.comprTotal = venta.ventTotal

    def generar_detalles_desde_venta(self):
        """Genera los detalles del comprobante"""
        venta_detalles = self.ventCod.ventadetalle_set.filter(ventDetAnulado=False)
        
        for detalle_venta in venta_detalles:
            ComprobanteDetalle.objects.create(
                comprCod=self,
                prodCod=detalle_venta.prodCod,
                comprDetDescripcion=detalle_venta.ventDetDescripcion,
                comprDetCantidad=detalle_venta.ventDetCantidad,
                comprDetPrecioUni=detalle_venta.ventDetPrecioUni,
                comprDetSubtotal=detalle_venta.ventDetSubtotal,
                comprDetDescuento=detalle_venta.ventDetDescuento,
                comprDetTotal=detalle_venta.ventDetTotal
            )

################################################################################### COMPROBANTE_DETALLE

class ComprobanteDetalle(models.Model):
    """Detalles del comprobante"""
    
    comprDetCod = models.AutoField(
        primary_key=True, 
        verbose_name="Codigo Detalle"
    )
    
    comprCod = models.ForeignKey(
        Comprobante,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name="Comprobante"
    )
    
    prodCod = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name="Producto"
    )

    comprDetDescripcion = models.CharField(
        max_length=500, 
        verbose_name="Descripcion"
    )
    
    comprDetCantidad = models.IntegerField(verbose_name="Cantidad")
    comprDetPrecioUni = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Precio Unitario"
    )
    
    comprDetSubtotal = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Subtotal"
    )
    comprDetDescuento = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name="Descuento"
    )
    comprDetTotal = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Total"
    )

    class Meta:
        db_table = 'comprobante_detalle'
        ordering = ['comprDetCod']
        verbose_name = 'Detalle de Comprobante'
        verbose_name_plural = 'Detalles de Comprobante'

    def __str__(self):
        return f"Det {self.comprDetCod} - {self.comprDetDescripcion[:50]}"