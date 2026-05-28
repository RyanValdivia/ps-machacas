from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
import sys
from products.views import (
    LunaMaterialViewSet,
    LunaTipoViewSet,
    LunaCaracteristicaViewSet,
    LunaConfiguracionViewSet
)

# Router exclusivo para lunas
lunas_router = DefaultRouter()
lunas_router.register(r'materiales', LunaMaterialViewSet, basename='luna-material')
lunas_router.register(r'tipos', LunaTipoViewSet, basename='luna-tipo')
lunas_router.register(r'caracteristicas', LunaCaracteristicaViewSet, basename='luna-caracteristica')
lunas_router.register(r'configuracion', LunaConfiguracionViewSet, basename='luna-configuracion')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/categories/', include('categories.urls')),
    path('api/products/', include('products.urls')),
    path('api/clients/', include('clients.urls')),
    path('api/user/', include('users.urls')),
    path('api/sales/', include('sales.urls')),
    path('api/suppliers/', include('suppliers.urls')),
    path('api/cash/', include('cash.urls')),
    path('api/proxy/', include('external_services.urls')),
    path('api/opticalcenter/', include('opticalCenter.urls')),
    
    # Sistema de lunas personalizadas
    path('api/lunas/', include(lunas_router.urls)),
]

# Servir archivos media (SIEMPRE, incluso en producción con PyInstaller)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG or getattr(sys, 'frozen', False):  # ← AGREGAR ESTA CONDICIÓN
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    print(f"📂 Sirviendo archivos media desde: {settings.MEDIA_ROOT}")  # ← AGREGAR LOG