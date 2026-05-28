from django.db import migrations

def create_default_supplier(apps, schema_editor):
    Supplier = apps.get_model('suppliers', 'Supplier')

    Supplier.objects.get_or_create(
        provRuc='00000000000',
        defaults={
            'provRazSocial': 'Proveedor Genérico',
            'provDirec': 'No especificado',
            'provTele': '999999999',
            'provEmail': 'generico@proveedor.com',
            'provCiu': 'N/A',
            'provEstado': 'Active',
        }
    )

class Migration(migrations.Migration):

    dependencies = [
        ('suppliers', '0001_initial'),  # ajusta si tu número es distinto
    ]

    operations = [
        migrations.RunPython(create_default_supplier),
    ]
