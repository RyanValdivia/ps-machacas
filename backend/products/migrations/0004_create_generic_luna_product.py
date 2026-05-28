from django.db import migrations
from decimal import Decimal

def create_generic_luna_product(apps, schema_editor):
    """
    MIGRACIÓN OBSOLETA - Ya no se usa
    Ahora se usa la migración 0006_load_luna_initial_data.py que crea LUNA-PERS
    """
    pass  # No hacer nada

def reverse_generic_luna_product(apps, schema_editor):
    """MIGRACIÓN OBSOLETA - No hacer nada"""
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_product_proddescripcionadicional_product_prodforma_and_more'),
        ('categories', '0003_add_luna_category'),
        ('suppliers', '0005_create_internal_supplier'),
    ]

    operations = [
        migrations.RunPython(create_generic_luna_product, reverse_generic_luna_product),
    ]
