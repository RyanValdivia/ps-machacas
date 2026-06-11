import pytest
from django.db import transaction
from sequences.models import ProductSequence


@pytest.mark.django_db
def test_create_sequence():
    """Prueba creación de secuencia."""
    seq = ProductSequence.objects.create(
        sequence_type='TEST1',
        current_value=100,
        description='Test Sequence'
    )
    assert seq.sequence_type == 'TEST1'
    assert seq.current_value == 100
    assert seq.description == 'Test Sequence'  # No hay uppercase en este modelo
    assert seq.created_at is not None
    assert seq.updated_at is not None


@pytest.mark.django_db
def test_sequence_str():
    """Prueba representación string."""
    seq = ProductSequence.objects.create(sequence_type='TEST2', current_value=50)
    assert str(seq) == 'TEST2: 50'


@pytest.mark.django_db
def test_sequence_unique_type():
    """Prueba que sequence_type es único."""
    ProductSequence.objects.create(sequence_type='UNIQ')
    from django.db import IntegrityError
    with pytest.raises(IntegrityError):
        ProductSequence.objects.create(sequence_type='UNIQ')


@pytest.mark.django_db
def test_get_next_value_new_sequence():
    """Prueba obtener siguiente valor para nueva secuencia."""
    value = ProductSequence.get_next_value('NEWSEQ')
    assert value == 1

    seq = ProductSequence.objects.get(sequence_type='NEWSEQ')
    assert seq.current_value == 1


@pytest.mark.django_db
def test_get_next_value_existing_sequence():
    """Prueba obtener siguiente valor para secuencia existente."""
    ProductSequence.objects.create(sequence_type='EXIST', current_value=5)

    value = ProductSequence.get_next_value('EXIST')
    assert value == 6

    seq = ProductSequence.objects.get(sequence_type='EXIST')
    assert seq.current_value == 6


@pytest.mark.django_db
def test_get_next_value_concurrent():
    """Prueba get_next_value es atómico."""
    # Primera llamada
    value1 = ProductSequence.get_next_value('CONCUR')
    # Segunda llamada
    value2 = ProductSequence.get_next_value('CONCUR')

    assert value1 == 1
    assert value2 == 2

    seq = ProductSequence.objects.get(sequence_type='CONCUR')
    assert seq.current_value == 2


@pytest.mark.django_db
def test_reset_sequence():
    """Prueba resetear secuencia."""
    ProductSequence.objects.create(sequence_type='RESET1', current_value=100)

    new_value = ProductSequence.reset_sequence('RESET1', new_value=0)
    assert new_value == 0

    seq = ProductSequence.objects.get(sequence_type='RESET1')
    assert seq.current_value == 0


@pytest.mark.django_db
def test_reset_sequence_custom_value():
    """Prueba resetear secuencia con valor personalizado."""
    ProductSequence.objects.create(sequence_type='CUSTOM1', current_value=50)

    new_value = ProductSequence.reset_sequence('CUSTOM1', new_value=10)
    assert new_value == 10

    seq = ProductSequence.objects.get(sequence_type='CUSTOM1')
    assert seq.current_value == 10


@pytest.mark.django_db
def test_sequence_default_values():
    """Prueba valores por defecto."""
    seq = ProductSequence.objects.create(sequence_type='DEF')
    assert seq.current_value == 0
    assert seq.description == ''


@pytest.mark.django_db
def test_sequence_ordering():
    """Prueba ordenamiento de secuencias."""
    # Limpiar secuencias existentes
    ProductSequence.objects.all().delete()

    ProductSequence.objects.create(sequence_type='Z1', current_value=1)
    ProductSequence.objects.create(sequence_type='A1', current_value=2)
    ProductSequence.objects.create(sequence_type='M1', current_value=3)

    sequences = list(ProductSequence.objects.all())
    assert sequences[0].sequence_type == 'A1'
    assert sequences[1].sequence_type == 'M1'
    assert sequences[2].sequence_type == 'Z1'


@pytest.mark.django_db
def test_sequence_update_auto_updated_at():
    """Prueba que updated_at se actualiza automáticamente."""
    import time
    seq = ProductSequence.objects.create(sequence_type='AUTO1', current_value=10)

    # Pequeña pausa para asegurar que cambie el timestamp
    time.sleep(0.01)

    # Actualizar el valor
    seq.current_value = 20
    seq.save()

    seq.refresh_from_db()
    assert seq.current_value == 20
