from django.urls import path
from . import views

urlpatterns = [
    path('dni', views.consultar_dni, name='consultar_dni'),
    path('ruc', views.consultar_ruc, name='consultar_ruc'),
]
