from django.urls import path, include
from rest_framework import routers
from .views import ClientViewSet, OptometristViewSet, RecipeViewSet 
from . import views

router = routers.DefaultRouter()
router.register(r'client', ClientViewSet, basename='Client') #Ya en front y testeado
router.register(r'optometrist', OptometristViewSet, basename='Optometrist') #testeado post get y put
router.register(r'prescription', RecipeViewSet, basename='Prescription') #

urlpatterns = [
    path('', include(router.urls)),
    path('buscar/', views.buscar_cliente_por_documento, name='buscar-cliente'),
]
