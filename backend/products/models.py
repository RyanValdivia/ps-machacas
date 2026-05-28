from django.db import models
from decimal import Decimal
from suppliers.models import Supplier
from categories.models import ProductCategory
from django.core.exceptions import ValidationError
from sequences.models import ProductSequence

class Product(models.Model):
    
  STATUS_CHOICES = [
    ('Active', 'Activo'),
    ('Inactive', 'Inactivo'),
  ]

  MATERIAL_CHOICES = [
    ('A', 'Acetato'),
    ('M', 'Metal'),
    ('TR', 'TR'),
    ('C', 'Carey'),
    ('N', 'No aplica'),
  ]
    
  prodCod = models.AutoField(primary_key=True)
  
  prodCode = models.CharField(
    max_length=20,
    unique=True,
    verbose_name="Codigo del Producto",
    blank=True,
    null=True,
    editable=False  
  )

  catproCod = models.ForeignKey(
    ProductCategory,
    on_delete=models.PROTECT,
    verbose_name="Categoria"
  )

  provCod = models.ForeignKey(
    Supplier,
    on_delete=models.PROTECT,
    verbose_name="Proveedor"
  )

  prodDescr = models.TextField(
    verbose_name="Descripcion",
    editable=False
  )
    
  prodMarca = models.CharField(
    max_length=50,
    verbose_name="Marca",
    blank=True,
    help_text="Obligatorio para monturas, opcional para accesorios"
  )
    
  prodMate = models.CharField(
    max_length=2,
    choices=MATERIAL_CHOICES,
    default='N',
    verbose_name="Material",
    help_text="Solo para monturas"
  )

  prodColor = models.CharField(
    max_length=30,
    verbose_name="Color",
    blank=True
  )

  prodTalla = models.CharField(
    max_length=20,
    verbose_name="Talla",
    blank=True,
    help_text="Ej: 54-18-140"
  )

  prodGenero = models.CharField(
    max_length=10,
    choices=[
      ('Hombre', 'Hombre'),
      ('Mujer', 'Mujer'),
      ('Unisex', 'Unisex'),
      ('Nino', 'Nino'),
    ],
    default='Unisex',
    verbose_name="Genero",
    blank=True
  )

  prodTieneSobrelente = models.BooleanField(
    default=False,
    verbose_name="Tiene Sobrelente",
    help_text="Indica si la montura incluye sobrelente"
  )

  prodForma = models.CharField(
    max_length=30,
    verbose_name="Forma",
    blank=True,
    help_text="Ej: Redondo, Cuadrado, Aviador"
  )

  prodDescripcionAdicional = models.TextField(
    verbose_name="Descripcion Adicional",
    blank=True,
    help_text="Informacion adicional del producto"
  )

  prodCostoInv = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    verbose_name="Costo",
    default=0
  )
    
  prodPrecioVenta = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    verbose_name="Precio Venta",
    default=0
  )

  prodStock = models.IntegerField(
    default=1,
    verbose_name="Stock",
  )

  prodStockMin = models.IntegerField(
    default=0,
    verbose_name="Stock Minimo"
  )

  prodEstado = models.CharField(
    max_length=10,
    choices=STATUS_CHOICES,
    default='Active',
    verbose_name="Estado"
  )

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True) 

  class Meta:
    db_table = 'product'
    verbose_name = 'Producto'
    verbose_name_plural = 'Productos'
    ordering = ['-created_at']

  def __str__(self):
    return self.prodDescr if self.prodDescr else f"Producto {self.prodCod}"

  def es_montura(self):
    """Verifica si es montura"""
    return self.catproCod.catproCode == 'MO'
  
  def es_accesorio(self):
    """Verifica si es accesorio"""
    return self.catproCod.catproCode == 'AC'

  def clean(self):
    super().clean()
    
    # Validaciones basicas
    if self.prodCostoInv < 0:
      raise ValidationError({'prodCostoInv': 'No puede ser negativo'})
    
    if self.prodPrecioVenta < 0:
      raise ValidationError({'prodPrecioVenta': 'No puede ser negativo'})
    
    if self.prodStock < 0:
      raise ValidationError({'prodStock': 'No puede ser negativo'})
    
    # Validaciones para MONTURAS
    if self.es_montura():
      if not self.prodMarca or len(self.prodMarca.strip()) < 2:
        raise ValidationError({'prodMarca': 'Marca obligatoria para monturas (minimo 2 caracteres)'})
      
      if self.prodMate == 'N':
        raise ValidationError({'prodMate': 'Debes seleccionar un material para monturas (A, M, TR o C)'})
      
      if not self.prodTalla:
        raise ValidationError({'prodTalla': 'Talla obligatoria para monturas'})
    
    # Validaciones para ACCESORIOS
    if self.es_accesorio():
      if self.prodMate != 'N':
        raise ValidationError({'prodMate': 'Los accesorios deben tener material "No aplica"'})

  def generate_product_code(self):
    """Genera codigo segun tipo de producto"""
    if self.es_montura():
      material = self.prodMate if self.prodMate != 'N' else 'X'
      sequence_type = material
      next_number = ProductSequence.get_next_value(sequence_type)
      return f"{material}{next_number}"  # Sin guion y sin ceros de relleno
    else:
      # Para accesorios
      sequence_type = 'GENERAL'
      next_number = ProductSequence.get_next_value(sequence_type)
      return str(next_number)  # Sin ceros de relleno

  def generate_description(self):
    """Genera descripcion automatica"""
    partes = []

    if self.es_montura():
      # Para monturas: Marca Talla Color Forma [Sobrelente] - Descripcion adicional
      if self.prodMarca:
        partes.append(self.prodMarca)
      if self.prodTalla:
        partes.append(self.prodTalla)
      if self.prodColor:
        partes.append(self.prodColor)
      if self.prodForma:
        partes.append(self.prodForma)
      
      descripcion = " | ".join(partes[:2]) if len(partes) >= 2 else " ".join(partes)
      if len(partes) > 2:
        descripcion += " " + " ".join(partes[2:])
      if self.prodTieneSobrelente:
        descripcion += " [Con Sobrelente]"
      if self.prodDescripcionAdicional:
        descripcion += f" - {self.prodDescripcionAdicional}"
    else:
      # Para accesorios: Marca (si tiene) - Descripcion adicional
      if self.prodMarca:
        partes.append(self.prodMarca)
      descripcion = " | ".join(partes) if partes else ""
      if self.prodDescripcionAdicional:
        if descripcion:
          descripcion += f" - {self.prodDescripcionAdicional}"
        else:
          descripcion = self.prodDescripcionAdicional

    return descripcion.strip()

  def save(self, *args, **kwargs):
    is_new = self.pk is None

    # Convertir marca a mayúsculas si existe
    if self.prodMarca:
      self.prodMarca = self.prodMarca.upper()
    
    # Para accesorios, forzar material a 'N'
    if self.es_accesorio():
      self.prodMate = 'N'

    # Validar
    self.full_clean()

    if is_new:
      # Producto nuevo
      self.prodCode = self.generate_product_code()
      self.prodDescr = self.generate_description()
      super().save(*args, **kwargs)
    else:
      # Actualizacion
      super().save(*args, **kwargs)
      
      new_description = self.generate_description()
      if self.prodDescr != new_description:
        self.prodDescr = new_description
        super().save(update_fields=['prodDescr'])

  @property
  def margen_ganancia(self):
    if self.prodCostoInv > 0:
      margen = ((self.prodPrecioVenta - self.prodCostoInv) / self.prodCostoInv) * 100
      return round(margen, 2)
    return 0
  
  @property
  def ganancia_unitaria(self):
    return round(self.prodPrecioVenta - self.prodCostoInv, 2)
  
  @property
  def valor_total_stock(self):
    return round(self.prodStock * self.prodCostoInv, 2)


################################################################################### LUNAS PERSONALIZADAS

class LunaMaterial(models.Model):
    """Catálogo de materiales de lunas"""
    lunMatCod = models.AutoField(primary_key=True)
    lunMatNombre = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Material"
    )
    lunMatDescripcion = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    lunMatActivo = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )

    class Meta:
        db_table = 'luna_material'
        verbose_name = 'Material de Luna'
        verbose_name_plural = 'Materiales de Luna'
        ordering = ['lunMatNombre']

    def __str__(self):
        return self.lunMatNombre


class LunaTipo(models.Model):
    """Catálogo de tipos de lunas"""
    lunTipCod = models.AutoField(primary_key=True)
    lunTipNombre = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Tipo"
    )
    lunTipDescripcion = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    lunTipActivo = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )

    class Meta:
        db_table = 'luna_tipo'
        verbose_name = 'Tipo de Luna'
        verbose_name_plural = 'Tipos de Luna'
        ordering = ['lunTipNombre']

    def __str__(self):
        return self.lunTipNombre


class LunaCaracteristica(models.Model):
    """Características adicionales para lunas (Blue Block, Fotocromático, etc.)"""
    lunCarCod = models.AutoField(primary_key=True)
    lunCarNombre = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Característica"
    )
    lunCarDescripcion = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    lunCarPrecioAdicional = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Precio Adicional"
    )
    lunCarActivo = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )

    class Meta:
        db_table = 'luna_caracteristica'
        verbose_name = 'Característica de Luna'
        verbose_name_plural = 'Características de Luna'
        ordering = ['lunCarNombre']

    def __str__(self):
        return f"{self.lunCarNombre} (+S/{self.lunCarPrecioAdicional})"


class LunaConfiguracion(models.Model):
    """Configuración base: Material + Tipo con precio base"""
    lunConfCod = models.AutoField(primary_key=True)
    
    lunMatCod = models.ForeignKey(
        LunaMaterial,
        on_delete=models.PROTECT,
        verbose_name="Material"
    )
    lunTipCod = models.ForeignKey(
        LunaTipo,
        on_delete=models.PROTECT,
        verbose_name="Tipo"
    )
    
    lunConfPrecioBase = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio Base"
    )
    lunConfActivo = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )

    class Meta:
        db_table = 'luna_configuracion'
        verbose_name = 'Configuración de Luna'
        verbose_name_plural = 'Configuraciones de Luna'
        unique_together = ['lunMatCod', 'lunTipCod']
        ordering = ['lunMatCod', 'lunTipCod']

    def __str__(self):
        return f"{self.lunMatCod.lunMatNombre} - {self.lunTipCod.lunTipNombre} (S/{self.lunConfPrecioBase})"

    def clean(self):
        super().clean()
        if self.lunConfPrecioBase < 0:
            raise ValidationError({'lunConfPrecioBase': 'El precio no puede ser negativo'})