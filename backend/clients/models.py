from django.db import models

class Client(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ('DNI', 'DNI'),
        ('RUC', 'RUC'),
        ('CE', 'Carnet de extranjeria'),
    ]
    
    cliCod = models.AutoField(primary_key=True)
    cliTipoDoc = models.CharField(max_length=10, choices=TIPO_DOCUMENTO_CHOICES, default='DNI', blank=True, null=True)
    cliNumDoc = models.CharField(max_length=20, unique=True, blank=True, null=True)
    cliNomCompleto = models.CharField(max_length=100)  # Este es obligatorio
    cliTelef = models.CharField(max_length=9, blank=True, null=True)  # Opcional
    cliFechaNac = models.DateField(null=True, blank=True)  # Opcional
    
    def save(self, *args, **kwargs):
        """Convertir nombre a mayúsculas antes de guardar"""
        if self.cliNomCompleto:
            self.cliNomCompleto = self.cliNomCompleto.upper().strip()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.cliNomCompleto} ({self.cliNumDoc})"


class Optometrist(models.Model):
    optCod = models.AutoField(primary_key=True)
    optNombre = models.CharField(max_length=100)
    optApellido = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.optNombre} {self.optApellido}"   

class Recipe(models.Model):
    recCod = models.AutoField(primary_key=True)
    # Datos generales
    recFech = models.DateField(auto_now_add=True)
    recEstado = models.CharField(max_length=50, default='Activo', blank=True, null=True)
    recObservaciones = models.TextField(blank=True, null=True)
    recInfoExtra = models.TextField(blank=True, null=True)

    # Distancia interpupilar
    receDIP = models.IntegerField(null=True, blank=True) #corregir quitar max_digits
    receDIPCerca = models.IntegerField(null=True, blank=True)
    
    # Adición Opcional para presbicia
    receAdd = models.DecimalField(max_digits=4  , decimal_places=2, null=True, blank=True)
    
    # Ojo derecho
    receEsfeOD = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    receCilinOD = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    receEjeOD = models.IntegerField(null=True, blank=True)
    receAvccOD = models.IntegerField(null=True, blank=True)
    
    # Ojo Izquierdo
    receEsfeOI = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    receCilinOI = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    receEjeOI = models.IntegerField(null=True, blank=True)
    receAvccOI = models.IntegerField(null=True, blank=True)
    receEsExterna = models.BooleanField(default=False)
    
    # Otros campos
    diagnostico = models.JSONField(default=list, blank=True)

    # Relaciones
    cliCod = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    optCod = models.ForeignKey(
        Optometrist,
        on_delete=models.PROTECT,
        related_name='recipes_realizadas'
    )

    def __str__(self):
        return f"Recipe {self.recCod}"
