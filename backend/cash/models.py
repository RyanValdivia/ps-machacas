from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from users.models import User
from decimal import Decimal

class Cash(models.Model):
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('DESACTIVADO', 'Desactivado'),
        ('SUSPENDIDO', 'Suspendido'),
    ]
    
    cajCod = models.AutoField(primary_key=True)
    
    usuCod = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Usuario Responsable"
    )
    
    cajNom = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nombre de Caja"
    )
    
    cajDes = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Descripcion"
    )
    
    cajEstado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default='ACTIVO',
        verbose_name="Estado"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cash'
        verbose_name = 'Caja'
        verbose_name_plural = 'Cajas'
        ordering = ['cajNom']

    def __str__(self):
        return self.cajNom
    
    def clean(self):
        super().clean()
        if not self.cajNom or len(self.cajNom.strip()) < 3:
            raise ValidationError({'cajNom': 'El nombre debe tener al menos 3 caracteres'})
    
    @property
    def tiene_apertura_activa(self):
        return self.aperturas.filter(cajaAperEstado='ABIERTA').exists()
    
    @property
    def apertura_actual(self):
        return self.aperturas.filter(cajaAperEstado='ABIERTA').first()


class CashOpening(models.Model):
    ESTADO_CHOICES = [
        ('ABIERTA', 'Abierta'),
        ('CERRADA', 'Cerrada'),
        ('ANULADA', 'Anulada'),
    ]

    cajaAperCod = models.AutoField(primary_key=True)
    
    cajCod = models.ForeignKey(
        Cash,
        on_delete=models.PROTECT,
        related_name="aperturas",
        verbose_name="Caja"
    )
    
    usuCod = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Cajero"
    )

    cajaApertuFechHora = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha Apertura"
    )
    
    cajaAperMontInicial = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Monto Inicial"
    )

    cajaAperFechaHorCierre = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha Cierre"
    )
    
    cajaAperMontCierre = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Monto Cierre"
    )
    
    cajaAperMontEsperado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Monto Esperado"
    )
    
    cajaAperDiferencia = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Diferencia"
    )

    cajaAperEstado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default='ABIERTA',
        verbose_name="Estado"
    )
    
    cajaAperObservacio = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones"
    )

    class Meta:
        db_table = 'cash_opening'
        verbose_name = "Apertura de Caja"
        verbose_name_plural = "Aperturas de Caja"
        ordering = ['-cajaApertuFechHora']

    def __str__(self):
        return f"Apertura #{self.cajaAperCod} - {self.cajCod.cajNom} ({self.cajaAperEstado})"
    
    def clean(self):
        super().clean()
        
        if self.cajaAperMontInicial < 0:
            raise ValidationError({'cajaAperMontInicial': 'No puede ser negativo'})
        
        if self.cajaAperEstado == 'ABIERTA' and not self.pk:
            if CashOpening.objects.filter(cajCod=self.cajCod, cajaAperEstado='ABIERTA').exists():
                raise ValidationError({'cajCod': 'Esta caja ya tiene una apertura activa'})
            
            if CashOpening.objects.filter(usuCod=self.usuCod, cajaAperEstado='ABIERTA').exists():
                raise ValidationError({'usuCod': 'Ya tienes una caja abierta'})
    
    def cerrar_caja(self, monto_cierre, observaciones=''):
        if self.cajaAperEstado != 'ABIERTA':
            raise ValidationError('Solo se pueden cerrar cajas abiertas')
        
        from sales.models import Venta
        ventas_total = Venta.objects.filter(
            cajaAperCod=self,
            ventAnulada=False
        ).aggregate(total=models.Sum('ventTotal'))['total'] or Decimal('0')
        
        self.cajaAperMontEsperado = self.cajaAperMontInicial + ventas_total
        self.cajaAperMontCierre = Decimal(str(monto_cierre))
        self.cajaAperDiferencia = self.cajaAperMontCierre - self.cajaAperMontEsperado
        self.cajaAperFechaHorCierre = timezone.now()
        self.cajaAperEstado = 'CERRADA'
        
        if observaciones:
            self.cajaAperObservacio = observaciones
        
        self.save()
    
    def anular(self, motivo):
        if self.cajaAperEstado == 'CERRADA':
            raise ValidationError('No se puede anular una caja cerrada')
        
        self.cajaAperEstado = 'ANULADA'
        self.cajaAperObservacio = f"ANULADA: {motivo}"
        self.save()
    
    @property
    def total_ventas(self):
        from sales.models import Venta
        total = Venta.objects.filter(
            cajaAperCod=self,
            ventAnulada=False
        ).aggregate(total=models.Sum('ventTotal'))['total']
        return total or Decimal('0')
    
    @property
    def cantidad_ventas(self):
        from sales.models import Venta
        return Venta.objects.filter(cajaAperCod=self, ventAnulada=False).count()