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
    


def downloadC(request):
    context = {
        'content': None
    }

    response = requests.get('http://localhost:5000/downloadC')
    if response.status_code == 200:
        xml_response = response.text  # Lee la respuesta como texto
        dom = parseString(xml_response)  # Parsea el XML
        pretty_xml = dom.toprettyxml()  # Serializa el XML con indentación
        pretty_xml = re.sub(r'\n\s*\n', '\n', pretty_xml)  # Elimina espacios en blanco adicionales
        context['content'] = pretty_xml  # Guarda la respuesta XML en el contexto
        return render(request, 'Carga.html', context)
    else:
        return render(request, 'Carga.html')

def downloadT(request):
    context = {
        'content': None
    }

    response = requests.get('http://localhost:5000/downloadT')
    if response.status_code == 200:
        xml_response = response.text  # Lee la respuesta como texto
        dom = parseString(xml_response)  # Parsea el XML
        pretty_xml = dom.toprettyxml()  # Serializa el XML con indentación
        pretty_xml = re.sub(r'\n\s*\n', '\n', pretty_xml)  # Elimina espacios en blanco adicionales
        context['content'] = pretty_xml  # Guarda la respuesta XML en el contexto
        return render(request, 'CargaTransac.html', context)
    else:
        return render(request, 'CargaTransac.html')
    

def posts(request, nit_cliente=None):
    context = {'posts': None}

    # Construye la URL de la API
    url = 'http://localhost:5000/results'
    if nit_cliente is not None:
        url += '/' + nit_cliente

    # Realiza la solicitud a la API
    response = requests.get(url)

    # Si la respuesta es exitosa, actualiza 'posts' en el contexto con la respuesta JSON
    if response.status_code == 200:
        context['posts'] = response.json()

    # Renderiza la plantilla 'ConsultEst.html' con el contexto
    return render(request, 'ConsultEst.html', context)