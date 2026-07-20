import pytest
import os
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock
from opticalCenter.models import OpticalCenter

User = get_user_model()

# Tests de OpticalCenter: configuración general de la empresa, modelada como un
# registro singleton (pk=1). Cubre el viewset: GET auto-crea el registro si no existe,
# POST funciona como upsert (crea o actualiza), PUT/PATCH actualizan datos y logo
# (con mock de FileSystemStorage), DELETE está bloqueado por http_method_names (405)
# y a nivel de modelo delete() no borra el registro (protección de la config única).
# Varios tests mockean fallos (save, update, os.makedirs, open) para cubrir los
# bloques except de cada acción y las ramas de _ensure_media_dirs (MEDIA_ROOT no
# string, modo "frozen"/Tauri exe, error de permisos, error crítico genérico).

@pytest.fixture
def auth_client(api_client, db):
    """Fixture para proporcionar un cliente de API autenticado para OpticalCenter"""
    user = User.objects.create_user(usuNom="admin_opt", usuContra="password123", usuEmail="opt@test.com")
    api_client.force_authenticate(user=user)
    return api_client

@pytest.mark.django_db
def test_get_optical_center_auto_create(auth_client):
    """Verifica que el GET cree el registro único si no existe y lo devuelva (Líneas 32-38)"""
    url = reverse('opticalcenter-list')
    resp = auth_client.get(url)
    assert resp.status_code == 200
    assert resp.data['optNom'] == "" # Creado por defecto
    assert OpticalCenter.objects.count() == 1

@pytest.mark.django_db
def test_retrieve_optical_center(auth_client):
    """Prueba el método retrieve (GET por ID) (Línea 42)"""
    obj = OpticalCenter.objects.create(pk=1, optNom="Optica Test")
    url = reverse('opticalcenter-detail', kwargs={'pk': 1})
    resp = auth_client.get(url)
    assert resp.status_code == 200
    assert resp.data['optNom'] == "Optica Test"

@pytest.mark.django_db
@patch('opticalCenter.views.OpticalCenterViewSet._ensure_media_dirs')
def test_create_or_update_optical_center(mock_ensure, auth_client):
    """Prueba el método POST que actúa como upsert (Líneas 46-61)"""
    url = reverse('opticalcenter-list')
    payload = {'optNom': 'Nueva Optica', 'optLema': 'Lema 1'}
    resp = auth_client.post(url, payload)
    assert resp.status_code == 200
    assert resp.data['optNom'] == "Nueva Optica"
    assert mock_ensure.called

@pytest.mark.django_db
def test_create_exception_handling(auth_client):
    """Cubre el bloque except en create simulando error en save (Líneas 62-63)"""
    url = reverse('opticalcenter-list')
    with patch('opticalCenter.models.OpticalCenter.save', side_effect=Exception("DB Error")):
        resp = auth_client.post(url, {'optNom': 'Error'})
        assert resp.status_code == 500
        assert 'DB Error' in resp.data['error']

@pytest.mark.django_db
def test_update_optical_center_with_logo(auth_client):
    """Prueba la actualización (PUT) incluyendo un archivo de logo (Líneas 73-85)"""
    OpticalCenter.objects.create(pk=1, optNom="Vieja")
    url = reverse('opticalcenter-detail', kwargs={'pk': 1})
    # Bitstream de un PNG de 1x1 píxel transparente para pasar la validación de imagen de Django
    valid_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n\x2d\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    logo = SimpleUploadedFile("logo.png", valid_png, content_type="image/png")
    
    # Mock para evitar errores de filesystem real al guardar el logo
    with patch('django.core.files.storage.FileSystemStorage.save', return_value="logo.png"):
        resp = auth_client.put(url, {'optNom': 'Nueva', 'optLogo': logo}, format='multipart')
        assert resp.status_code == 200
        assert resp.data['optNom'] == "Nueva"

@pytest.mark.django_db
def test_update_exception_handling(auth_client):
    """Cubre el bloque except en update (Líneas 86-87)"""
    OpticalCenter.objects.create(pk=1)
    url = reverse('opticalcenter-detail', kwargs={'pk': 1})
    with patch('opticalCenter.views.viewsets.ModelViewSet.update', side_effect=Exception("Update Fail")):
        resp = auth_client.put(url, {'optNom': 'Fail'})
        assert resp.status_code == 500

@pytest.mark.django_db
def test_partial_update_optical_center(auth_client):
    """Prueba PATCH (Líneas 98-129)"""
    OpticalCenter.objects.create(pk=1, optNom="Original")
    url = reverse('opticalcenter-detail', kwargs={'pk': 1})
    resp = auth_client.patch(url, {'optNom': 'Parcial'})
    assert resp.status_code == 200
    assert resp.data['optNom'] == "Parcial"

@pytest.mark.django_db
def test_partial_update_exception_handling(auth_client):
    """Cubre el bloque except en partial_update (Línea 130)"""
    OpticalCenter.objects.create(pk=1)
    url = reverse('opticalcenter-detail', kwargs={'pk': 1})
    with patch('opticalCenter.views.viewsets.ModelViewSet.partial_update', side_effect=Exception("Patch Fail")):
        resp = auth_client.patch(url, {'optNom': 'Fail'})
        assert resp.status_code == 500

@pytest.mark.django_db
def test_destroy_optical_center(auth_client):
    """Prueba el método destroy (Línea 137)"""
    OpticalCenter.objects.create(pk=1)
    url = reverse('opticalcenter-detail', kwargs={'pk': 1})
    resp = auth_client.delete(url)
    # El ViewSet actual restringe http_method_names y no incluye 'delete'
    assert resp.status_code == 405

@pytest.mark.django_db
def test_ensure_media_dirs_branches(auth_client):
    """Cubre las ramas de configuración de MEDIA_ROOT (Líneas 139-150)"""
    view = auth_client.get(reverse('opticalcenter-list')).renderer_context['view']
    
    # Test rama settings.MEDIA_ROOT no es string
    with patch('django.conf.settings.MEDIA_ROOT', 123):
        view._ensure_media_dirs()
        # El código hace str(123), no debería fallar

    # Test rama sin MEDIA_ROOT y sys.frozen (simulando Tauri exe)
    with patch('django.conf.settings', spec=[]), \
         patch('sys.frozen', True, create=True), \
         patch('os.environ.get', return_value='/tmp/appdata'):
        view._ensure_media_dirs()

@pytest.mark.django_db
def test_ensure_media_dirs_write_permission_error(auth_client):
    """Cubre error de permisos de escritura (Líneas 163-169)"""
    view = auth_client.get(reverse('opticalcenter-list')).renderer_context['view']
    
    # Mock para que open() lance una excepción al intentar escribir el archivo .test_write
    with patch('builtins.open', side_effect=PermissionError("Acceso denegado")):
        with pytest.raises(PermissionError):
            view._ensure_media_dirs()

@pytest.mark.django_db
def test_ensure_media_dirs_critical_error(auth_client):
    """Cubre error crítico genérico en configuración de directorios (Líneas 178-179)"""
    view = auth_client.get(reverse('opticalcenter-list')).renderer_context['view']
    
    with patch('os.makedirs', side_effect=Exception("Critical OS Fail")):
        with pytest.raises(Exception) as exc:
            view._ensure_media_dirs()
        assert "Critical OS Fail" in str(exc.value)

@pytest.mark.django_db
def test_optical_center_model_delete_prevention():
    """Verifica que el modelo ignore el borrado para proteger la configuración (Línea 17 en models.py)"""
    obj = OpticalCenter.objects.create(pk=1, optNom="No Borrar")
    obj.delete()
    assert OpticalCenter.objects.filter(pk=1).exists()

@pytest.mark.django_db
def test_optical_center_model_str():
    """Verifica el __str__ del modelo"""
    obj = OpticalCenter.objects.create(pk=1)
    assert str(obj) == "Configuración General de la Empresa"
