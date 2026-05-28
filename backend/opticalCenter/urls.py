from rest_framework import routers
from .views import OpticalCenterViewSet
from django.urls import path, include
router = routers.DefaultRouter()
router.register(r'', OpticalCenterViewSet, basename='opticalcenter')

urlpatterns = [
    path('', include(router.urls))
]