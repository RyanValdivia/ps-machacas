from django.db import migrations

def create_initial_sequences(apps, schema_editor):
    ProductSequence = apps.get_model('sequences', 'ProductSequence')
    
    sequences_data = [
        {'sequence_type': 'A', 'description': 'Monturas de Acetato', 'current_value': 0},
        {'sequence_type': 'M', 'description': 'Monturas de Metal', 'current_value': 0},
        {'sequence_type': 'TR', 'description': 'Monturas TR', 'current_value': 0},
        {'sequence_type': 'C', 'description': 'Monturas de Carey', 'current_value': 0},
        {'sequence_type': 'GENERAL', 'description': 'Productos no monturas', 'current_value': 0},
    ]
    
    for seq_data in sequences_data:
        ProductSequence.objects.get_or_create(
            sequence_type=seq_data['sequence_type'],
            defaults={
                'description': seq_data['description'],
                'current_value': seq_data['current_value']
            }
        )

def reverse_sequences(apps, schema_editor):
    ProductSequence = apps.get_model('sequences', 'ProductSequence')
    ProductSequence.objects.all().delete()

class Migration(migrations.Migration):
    
    dependencies = [
        ('sequences', '0001_initial'),
    ]
    
    operations = [
        migrations.RunPython(create_initial_sequences, reverse_sequences),
    ]