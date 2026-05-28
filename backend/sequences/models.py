from django.db import models
from django.db import transaction

class ProductSequence(models.Model):
    
  sequence_type = models.CharField(
    max_length=10,
    unique=True,
    verbose_name="Tipo de Secuencia",
    help_text="Material (A, M, TR, C) o GENERAL para no monturas"
  )
  
  current_value = models.IntegerField(
    default=0,
    verbose_name="Valor Actual",
    help_text="Ultimo numero asignado"
  )
  
  description = models.CharField(
    max_length=50,
    blank=True,
    verbose_name="Descripcion",
    help_text="Descripcion del tipo de secuencia"
  )
  
  created_at = models.DateTimeField(
    auto_now_add=True,
    verbose_name="Fecha de Creacion"
  )
  
  updated_at = models.DateTimeField(
    auto_now=True,
    verbose_name="Ultima Actualizacion"
  )
  
  class Meta:
    db_table = 'product_sequence'
    verbose_name = 'Secuencia de Producto'
    verbose_name_plural = 'Secuencias de Productos'
    ordering = ['sequence_type']
  
  def __str__(self):
    return f"{self.sequence_type}: {self.current_value}"
  
  @classmethod
  def get_next_value(cls, sequence_type):
    with transaction.atomic():
      sequence, created = cls.objects.select_for_update().get_or_create(
          sequence_type=sequence_type,
          defaults={'current_value': 0}
      )
      sequence.current_value += 1
      sequence.save(update_fields=['current_value'])
      return sequence.current_value
  
  @classmethod
  def reset_sequence(cls, sequence_type, new_value=0):
    with transaction.atomic():
      sequence = cls.objects.select_for_update().get(sequence_type=sequence_type)
      sequence.current_value = new_value
      sequence.save(update_fields=['current_value'])
      return sequence.current_value