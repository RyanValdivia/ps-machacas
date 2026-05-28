from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VentaViewSet, VentaDetalleViewSet, imprimir_ticket, test_impresora

router = DefaultRouter()
router.register(r'ventas', VentaViewSet, basename='venta')
router.register(r'ventas-detalle', VentaDetalleViewSet, basename='venta-detalle')

urlpatterns = [
    path('', include(router.urls)),
    # Endpoints de impresión
    path('imprimir/', imprimir_ticket, name='imprimir_ticket'),
    path('imprimir/test/', test_impresora, name='test_impresora'),
]