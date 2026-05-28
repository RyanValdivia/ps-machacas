from django.db import migrations
import sys

# Crea los roles en la BD por defecto
def create_roles(apps, schema_editor): 
    print("[INFO] Creando roles por defecto...", flush=True)
    sys.stdout.flush()
    
    Role = apps.get_model('users', 'Role')
    roles = [
        ('GERENTE', 'Gerente', 0),
        ('CAJERO', 'Cajero', 2),
        ('VENDEDOR', 'Vendedor', 2),
        ('OPTOMETRA', 'Optometra', 4),
        ('LOGISTICA', 'Logística', 3),
    ]
    
    created_count = 0
    for cod, nombre, nivel in roles:
        role, created = Role.objects.update_or_create(
            rolNom=cod,
            defaults={
                'rolDes': nombre,
                'rolEstado': 'ACTIVO',
                'rolNivel': nivel
            }
        )
        if created:
            created_count += 1
        print("✓ Rol {}: {}".format("creado" if created else "actualizado", cod), flush=True)
        sys.stdout.flush()
    
    print("[OK] Roles creados/actualizados: {}/{}".format(created_count, len(roles)), flush=True)
    sys.stdout.flush()



class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_roles),
    ]