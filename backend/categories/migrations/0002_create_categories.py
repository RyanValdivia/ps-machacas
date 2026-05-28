from django.db import migrations

def create_categories(apps, schema_editor):
    ProductCategory = apps.get_model('categories', 'ProductCategory')

    categorias = [
        ('AC', 'Accesorios'),
        ('MO', 'Monturas'),
    ]

    for code, nombre in categorias:
        ProductCategory.objects.get_or_create(
            catproCode=code,
            defaults={'catproNom': nombre}
        )

class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_categories),
    ]
