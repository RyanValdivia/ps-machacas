from django.db import migrations

def create_internal_supplier(apps, schema_editor):
    """Crea el proveedor interno para productos personalizados"""
    Supplier = apps.get_model('suppliers', 'Supplier')
    
    Supplier.objects.get_or_create(
        provRuc='00000000000',
        defaults={
            'provRazSocial': 'INTERNO - PRODUCTOS PERSONALIZADOS',
            'provDirec': 'ALMACEN INTERNO',
            'provCiu': 'LIMA',
            'provEstado': 'Active'
        }
    )

def reverse_internal_supplier(apps, schema_editor):
    """Elimina el proveedor interno"""
    Supplier = apps.get_model('suppliers', 'Supplier')
    Supplier.objects.filter(provRuc='00000000000').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('suppliers', '0004_alter_supplier_provciu_alter_supplier_provdirec_and_more'),
    ]

    operations = [
        migrations.RunPython(create_internal_supplier, reverse_internal_supplier),
    ]
