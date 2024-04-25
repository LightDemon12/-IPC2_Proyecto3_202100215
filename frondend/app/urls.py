from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('Carga', views.Cargar, name='Carga'),
    path('ayuda', views.ayuda, name='ayuda'),
    path('CargaTransac', views.CargarT, name='CargaTransac'),
    path('ConsultEst', views.ConsultEst, name='ConsultEst'),
    path('ConsultIng', views.ConsultIng, name='ConsultIng'),
    path('cargarXML2/', views.cargarXML2, name='cargarXML2'),
]