from django.shortcuts import render
import requests

# Create your views here.
def index(request):
    return render(request, 'index.html')

def Cargar(request):
    return render(request, 'Carga.html')

def ayuda(request):
    return render(request, 'ayuda.html')

def CargarT(request):
    return render(request, 'CargaTransac.html')

def ConsultEst(request):
    return render(request, 'ConsultEst.html')

def ConsultIng(request):
    return render(request, 'ConsultIng.html')