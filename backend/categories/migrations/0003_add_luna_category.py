from django.db import migrations

def create_luna_category(apps, schema_editor):
    """Crea la categoría LUNA para productos personalizados"""
    ProductCategory = apps.get_model('categories', 'ProductCategory')
    
    ProductCategory.objects.get_or_create(
        catproCode='LUNA',
        defaults={'catproNom': 'Lunas'}
    )

def reverse_luna_category(apps, schema_editor):
    """Elimina la categoría LUNA"""
    ProductCategory = apps.get_model('categories', 'ProductCategory')
    ProductCategory.objects.filter(catproCode='LUNA').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0002_create_categories'),
    ]

    operations = [
        migrations.RunPython(create_luna_category, reverse_luna_category),
    ]
