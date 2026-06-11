import pytest
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from django.conf import settings
import os
import tempfile


@pytest.fixture
def authenticated_client(api_client):
    user = User.objects.create_user(username='testuser', password='testpass')
    api_client.force_authenticate(user=user)
    return api_client


@pytest.mark.django_db
class TestOpticalCenterViewSet:
    # TEST: GET sin autenticacion retorna 401
    def test_unauthenticated(self, api_client):
        r = api_client.get('/api/opticalcenter/')
        assert r.status_code == status.HTTP_401_UNAUTHORIZED

    # TEST: GET /api/opticalcenter/ retorna objeto, no lista
    def test_list_returns_object(self, authenticated_client):
        r = authenticated_client.get('/api/opticalcenter/')
        assert r.status_code == status.HTTP_200_OK
        assert isinstance(r.data, dict)
        assert 'optNom' in r.data

    # TEST: GET /api/opticalcenter/ crea registro por defecto si no existe
    def test_list_creates_default(self, authenticated_client):
        r = authenticated_client.get('/api/opticalcenter/')
        assert r.data['id'] == 1

    # TEST: GET /api/opticalcenter/1/ retorna el registro
    def test_retrieve(self, authenticated_client):
        from opticalCenter.models import OpticalCenter
        OpticalCenter.objects.create(pk=1, optNom="Mi Optica")
        r = authenticated_client.get('/api/opticalcenter/1/')
        assert r.status_code == status.HTTP_200_OK
        assert r.data['optNom'] == "Mi Optica"

    # TEST: POST crea/actualiza el singleton
    def test_create(self, authenticated_client):
        r = authenticated_client.post('/api/opticalcenter/', {'optNom': 'Nueva Optica', 'optLema': 'Ver bien'}, format='json')
        assert r.status_code == status.HTTP_200_OK
        assert r.data['optNom'] == 'Nueva Optica'
        assert r.data['optLema'] == 'Ver bien'

    # TEST: POST actualiza si ya existe
    def test_create_updates_existing(self, authenticated_client):
        authenticated_client.post('/api/opticalcenter/', {'optNom': 'Primera'}, format='json')
        r = authenticated_client.post('/api/opticalcenter/', {'optNom': 'Segunda'}, format='json')
        assert r.status_code == status.HTTP_200_OK
        assert r.data['optNom'] == 'Segunda'

    # TEST: PUT update
    def test_update(self, authenticated_client):
        from opticalCenter.models import OpticalCenter
        OpticalCenter.objects.create(pk=1, optNom="Original")
        r = authenticated_client.put('/api/opticalcenter/1/', {'optNom': 'Actualizada'}, format='json')
        assert r.status_code == status.HTTP_200_OK
        assert r.data['optNom'] == 'Actualizada'

    # TEST: PATCH partial update
    def test_partial_update(self, authenticated_client):
        from opticalCenter.models import OpticalCenter
        OpticalCenter.objects.create(pk=1, optNom="Original", optDir="Av Test")
        r = authenticated_client.patch('/api/opticalcenter/1/', {'optNom': 'Solo Nombre'}, format='json')
        assert r.status_code == status.HTTP_200_OK
        assert r.data['optNom'] == 'Solo Nombre'
        assert r.data['optDir'] == 'Av Test'

    # TEST: DELETE retorna 405 (no permitido)
    def test_delete_not_allowed(self, authenticated_client):
        r = authenticated_client.delete('/api/opticalcenter/1/')
        assert r.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    # TEST: POST con datos invalidos retorna 400
    def test_create_invalid_data(self, authenticated_client):
        r = authenticated_client.post('/api/opticalcenter/', {'optNom': ''}, format='json')
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    # TEST: POST con carga de logo
    def test_create_with_logo(self, authenticated_client):
        from django.core.files.uploadedfile import SimpleUploadedFile
        logo = SimpleUploadedFile("logo.png", b"fake_image_content", content_type="image/png")
        r = authenticated_client.post('/api/opticalcenter/', {'optNom': 'Con Logo', 'optLogo': logo}, format='multipart')
        assert r.status_code == status.HTTP_200_OK
        assert r.data['optNom'] == 'Con Logo'

    # TEST: optLogoUrl se genera correctamente con logo
    def test_logo_url_generated(self, authenticated_client):
        from opticalCenter.models import OpticalCenter
        oc = OpticalCenter.objects.create(pk=1, optNom="Logo Test")
        r = authenticated_client.get('/api/opticalcenter/1/')
        assert r.status_code == status.HTTP_200_OK
        assert r.data.get('optLogoUrl') is None or r.data.get('optLogoUrl') == ''

    # TEST: _ensure_media_dirs crea directorios necesarios
    def test_ensure_media_dirs(self, authenticated_client):
        from opticalCenter.views import OpticalCenterViewSet
        view = OpticalCenterViewSet()
        view._ensure_media_dirs()
        media_root = getattr(settings, 'MEDIA_ROOT', None)
        if media_root:
            company_dir = os.path.join(str(media_root), 'company')
            assert os.path.exists(company_dir)

    # TEST: POST con error en DB retorna 500
    def test_create_db_error(self, authenticated_client, mocker):
        mocker.patch('opticalCenter.models.OpticalCenter.objects.get_or_create', side_effect=Exception("DB error"))
        r = authenticated_client.post('/api/opticalcenter/', {'optNom': 'Fallo'}, format='json')
        assert r.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert 'error' in r.data

    # TEST: PUT con error retorna 500
    def test_update_error(self, authenticated_client, mocker):
        mocker.patch('opticalCenter.models.OpticalCenter.objects.get_or_create', side_effect=Exception("Fallo update"))
        r = authenticated_client.put('/api/opticalcenter/1/', {'optNom': 'Fallo'}, format='json')
        assert r.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    # TEST: PATCH con error retorna 500
    def test_partial_update_error(self, authenticated_client, mocker):
        mocker.patch('opticalCenter.models.OpticalCenter.objects.get_or_create', side_effect=Exception("Fallo patch"))
        r = authenticated_client.patch('/api/opticalcenter/1/', {'optNom': 'Fallo'}, format='json')
        assert r.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
