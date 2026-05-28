from django.shortcuts import render
from .models import OpticalCenter
from .serializers import OpticalCenterSerializer
from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import decorators
from django.conf import settings
import os
import sys


class OpticalCenterViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = OpticalCenter.objects.all()
    serializer_class = OpticalCenterSerializer
    http_method_names = ['get', 'patch', 'put', 'post']

    def get_object(self):
        obj, created = OpticalCenter.objects.get_or_create(pk=1)
        return obj 

    def list(self, request, *args, **kwargs):
        """Devuelve el único registro de OpticalCenter como objeto, no como lista"""
        print("📥 [VIEW] GET /opticalcenter/ - Solicitando datos")
        obj, created = OpticalCenter.objects.get_or_create(pk=1)
        serializer = self.get_serializer(obj, context={'request': request})
        print(f"✅ [VIEW] Datos enviados: {serializer.data.keys()}")
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        print(f"📥 [VIEW] GET /opticalcenter/{kwargs.get('pk')}/ - Solicitando datos")
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        print("📝 [VIEW] POST /opticalcenter/ - Creando/Actualizando")
        print(f"📦 [VIEW] Datos recibidos: {request.data.keys()}")
        print(f"📦 [VIEW] Content-Type: {request.content_type}")
        
        # Verificar si viene archivo
        if 'optLogo' in request.FILES:
            logo = request.FILES['optLogo']
            print(f"📸 [VIEW] Logo recibido: {logo.name}, tamaño: {logo.size} bytes, tipo: {logo.content_type}")
        else:
            print("ℹ️ [VIEW] No se recibió archivo de logo")
        
        # Asegurar que existe el directorio de medios
        self._ensure_media_dirs()
        
        try:
            obj, created = OpticalCenter.objects.get_or_create(pk=1)
            serializer = self.get_serializer(obj, data=request.data, partial=True, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            print(f"✅ [VIEW] OpticalCenter {'creado' if created else 'actualizado'} exitosamente")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"❌ [VIEW] Error al crear/actualizar: {e}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, *args, **kwargs):
        print(f"📝 [VIEW] PUT /opticalcenter/{kwargs.get('pk')}/ - Actualizando")
        print(f"📦 [VIEW] Datos recibidos: {request.data.keys()}")
        print(f"📦 [VIEW] Content-Type: {request.content_type}")
        
        # Verificar si viene archivo
        if 'optLogo' in request.FILES:
            logo = request.FILES['optLogo']
            print(f"📸 [VIEW] Logo recibido: {logo.name}, tamaño: {logo.size} bytes, tipo: {logo.content_type}")
        else:
            print("ℹ️ [VIEW] No se recibió archivo de logo en esta actualización")
        
        # Asegurar que existe el directorio de medios
        self._ensure_media_dirs()
        
        try:
            response = super().update(request, *args, **kwargs)
            print(f"✅ [VIEW] OpticalCenter actualizado exitosamente")
            return response
        except Exception as e:
            print(f"❌ [VIEW] Error al actualizar: {e}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def partial_update(self, request, *args, **kwargs):
        print(f"📝 [VIEW] PATCH /opticalcenter/{kwargs.get('pk')}/ - Actualización parcial")
        print(f"📦 [VIEW] Datos recibidos: {request.data.keys()}")
        
        # Verificar si viene archivo
        if 'optLogo' in request.FILES:
            logo = request.FILES['optLogo']
            print(f"📸 [VIEW] Logo recibido: {logo.name}, tamaño: {logo.size} bytes")
        
        # Asegurar que existe el directorio de medios
        self._ensure_media_dirs()
        
        try:
            response = super().partial_update(request, *args, **kwargs)
            print(f"✅ [VIEW] OpticalCenter actualizado parcialmente")
            return response
        except Exception as e:
            print(f"❌ [VIEW] Error en actualización parcial: {e}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def _ensure_media_dirs(self):
        """Asegura que existan los directorios de medios necesarios"""
        try:
            # Obtener MEDIA_ROOT
            if hasattr(settings, 'MEDIA_ROOT'):
                if isinstance(settings.MEDIA_ROOT, str):
                    media_root = settings.MEDIA_ROOT
                else:
                    media_root = str(settings.MEDIA_ROOT)
            else:
                # Fallback si no está configurado
                if getattr(sys, 'frozen', False):
                    appdata = os.environ.get('APPDATA', '')
                    media_root = os.path.join(appdata, 'RegistraMe', 'media')
                else:
                    media_root = os.path.join(settings.BASE_DIR, 'media')
            
            company_dir = os.path.join(media_root, 'company')
            
            print(f"📁 [VIEW] MEDIA_ROOT: {media_root}")
            print(f"📁 [VIEW] Company dir: {company_dir}")
            
            # Crear directorios si no existen
            os.makedirs(media_root, exist_ok=True)
            os.makedirs(company_dir, exist_ok=True)
            
            # Verificar permisos de escritura
            test_file = os.path.join(media_root, '.test_write')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                print(f"✅ [VIEW] Permisos de escritura OK en: {media_root}")
            except Exception as e:
                print(f"❌ [VIEW] NO HAY PERMISOS DE ESCRITURA en {media_root}: {e}")
                raise
            
            print(f"✅ [VIEW] Directorios de medios verificados correctamente")
            
        except Exception as e:
            print(f"❌ [VIEW] Error crítico al configurar directorios de medios: {e}")
            import traceback
            traceback.print_exc()
            raise