from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal

class ProductCategory(models.Model):
    catproCod = models.AutoField(primary_key=True)

    catproCode = models.CharField(
        max_length=5,
        unique=True,
        verbose_name="Código de Categoría"
    )

    catproNom = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Nombre de Categoría"
    )

    catproRequiereInventario = models.BooleanField(
        default=True,
        verbose_name="Requiere Inventario",
        help_text="Si False, los productos no consumen stock (ej: Lunas Personalizadas)"
    )

    def save(self, *args, **kwargs):
        self.catproNom = self.catproNom.strip().title()
        self.catproCode = self.catproCode.strip().upper()
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.catproCode} - {self.catproNom}"
