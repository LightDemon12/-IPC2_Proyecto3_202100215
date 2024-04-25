from django.shortcuts import render
import requests
from .forms import FileForm
from xml.dom.minidom import parseString 
import re



API = 'http://localhost:5000'



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



def cargarXML(request):
    context = {
        'content': None
    }

    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data['file']
            txt = uploaded_file.read() # Lee el contenido del archivo
            response = requests.post('http://localhost:5000/grabarConfiguracion', data=txt)  # Cambia API+'/results' a 'http://localhost:5000/upload'
            if response.status_code == 200:
                xml_response = response.text  # Lee la respuesta como texto
                dom = parseString(xml_response)  # Parsea el XML
                pretty_xml = dom.toprettyxml()  # Serializa el XML con indentación
                pretty_xml_without_blank_lines = re.sub(r'\n\s*\n', '\n', pretty_xml)  # Elimina las líneas en blanco
                context['content'] = pretty_xml_without_blank_lines  # Guarda la respuesta XML en el contexto
                return render(request, 'Carga.html', context)
        return render(request, 'Carga.html')
    else:
        return render(request, 'Carga.html')
    

def cargarXML2(request):
    context = {
        'content': None
    }

    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data['file']
            txt = uploaded_file.read() # Lee el contenido del archivo
            response = requests.post('http://localhost:5000/grabarTransaccion', data=txt)  # Cambia API+'/results' a 'http://localhost:5000/upload'
            if response.status_code == 200:
                xml_response = response.text  # Lee la respuesta como texto
                dom = parseString(xml_response)  # Parsea el XML
                pretty_xml = dom.toprettyxml()  # Serializa el XML con indentación
                pretty_xml_without_blank_lines = re.sub(r'\n\s*\n', '\n', pretty_xml)  # Elimina las líneas en blanco
                context['content'] = pretty_xml_without_blank_lines  # Guarda la respuesta XML en el contexto
                return render(request, 'CargaTransac.html', context)
        return render(request, 'CargaTransac.html')
    else:
        return render(request, 'CargaTransac.html')