from django.shortcuts import render
import requests
from .forms import FileForm
from xml.dom.minidom import parseString 
import re
from django.http import JsonResponse
import json
from itertools import chain

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

def searchNIT(request):
    if request.method == 'GET':
        nit_cliente = request.GET['search']
        print(nit_cliente)
        try:
            response = requests.get(API+f'/resultsnit/{nit_cliente}')
            if response.status_code == 200:
                resumen_clientes = response.json()
                context = {
                    'posts': resumen_clientes
                }
                return render(request, 'ConsultEstSingle.html', context)
            else:
                return render(request, 'ConsultEstSingle.html')
        except Exception as e:
            print(e)

        return render(request, 'ConsultEstSingle.html')
    
def clear_animals(request):
    response = requests.delete('http://localhost:5000/clear')
    if response.status_code == 200:
        return render(request, 'clear_success.html', {'alert_message': '¡Bien hecho! Los registros se han borrado con éxito.'})
    else:
        return render(request, 'clear_error.html', {'alert_message': '¡Error! Hubo un problema al intentar borrar los registros.'})
    

import requests
from django.http import JsonResponse

def sumar_meses(request, mes):
    # Realiza una solicitud al backend para obtener los datos
    response = requests.get(f'http://localhost:5000/sumarMeses/{mes}')

    # Imprime la respuesta recibida
    print(f"Response received: {response.text}")

    # Comprueba si la solicitud fue exitosa
    if response.status_code == 200:
        # Intenta parsear los datos como JSON y captura cualquier error
        try:
            data = response.json()
        except json.JSONDecodeError:
            print("Error decoding JSON")
            return JsonResponse({'error': 'Hubo un problema al decodificar los datos del backend.'})

        # Transforma los datos
        labels = sorted(data['total_facturas_por_mes'].keys())
        total_facturas = [data['total_facturas_por_mes'][label] for label in labels]

        # Obtiene la lista de bancos de los datos de pagos
        bancos = set(banco for pagos_mes in data['total_pagos_por_mes'].values() for banco in pagos_mes.keys())

        total_pagos_por_banco = {banco: [data['total_pagos_por_mes'].get(label, {}).get(banco, 0) for label in labels] for banco in bancos}

        # Imprime los datos que se están enviando a la plantilla
        print(f"Data sent to template: labels={labels}, total_facturas={total_facturas}, total_pagos_por_banco={total_pagos_por_banco}")

        # Si la solicitud fue exitosa, renderiza la plantilla con los datos transformados
        return render(request, 'ConsultIng.html', {'data': json.dumps({'labels': labels, 'total_facturas': total_facturas, 'total_pagos_por_banco': total_pagos_por_banco})})
    else:
        # Si hubo un error, devuelve un mensaje de error
        return JsonResponse({'error': 'Hubo un problema al obtener los datos del backend.'})