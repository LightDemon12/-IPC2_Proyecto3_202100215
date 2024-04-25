from flask import Flask, request, jsonify, render_template, send_file , Response
from flask_cors import CORS
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import re
from collections import defaultdict
from Estructuras.estructuras import Cliente, Banco, Factura, Pago


app = Flask(__name__)
CORS(app)

configuracion = []
contadores = defaultdict(lambda: defaultdict(int))

clientes = {}
bancos = {}

def procesar_elemento(elemento):
    tipo_elemento = elemento.tag
    if tipo_elemento == 'cliente':
        nit = elemento.find('NIT').text
        nombre = elemento.find('nombre').text
        if nit in clientes:
            # Si el cliente ya existe, actualiza los datos
            clientes[nit].nombre = nombre
            contadores[tipo_elemento]['actualizados'] += 1
        else:
            # Si el cliente es nuevo, crea una nueva entrada
            clientes[nit] = Cliente(nit, nombre)
            contadores[tipo_elemento]['creados'] += 1
            configuracion.append(clientes[nit])
    elif tipo_elemento == 'banco':
        codigo = elemento.find('codigo').text
        nombre = elemento.find('nombre').text
        if codigo in bancos:
            # Si el banco ya existe, actualiza los datos
            bancos[codigo].nombre = nombre
            contadores[tipo_elemento]['actualizados'] += 1
        else:
            # Si el banco es nuevo, crea una nueva entrada
            bancos[codigo] = Banco(codigo, nombre)
            contadores[tipo_elemento]['creados'] += 1
            configuracion.append(bancos[codigo])

facturas = {}
pagos = {}

def procesar_elementoT(elemento):
    tipo_elemento = elemento.tag
    if tipo_elemento == 'factura':
        numeroFactura = elemento.find('numeroFactura').text
        NITcliente = elemento.find('NITcliente').text
        fecha = re.findall(r'\d+/\d+/\d+', elemento.find('fecha').text)[0]  # Extrae solo los números y los signos /
        valor = re.findall(r'\d+', elemento.find('valor').text)[0]  # Extrae solo los números
        if NITcliente not in clientes:
            # Si el NITcliente no coincide con ningún cliente existente, incrementa el contador de errores
            contadores[tipo_elemento]['facturasConError'] += 1
        elif numeroFactura in facturas:
            # Si la factura ya existe, incrementa el contador de facturas duplicadas
            contadores[tipo_elemento]['facturasDuplicadas'] += 1
        else:
            # Si la factura es nueva y el NITcliente coincide con un cliente existente, crea una nueva entrada
            facturas[numeroFactura] = Factura(numeroFactura, NITcliente, fecha, valor)
            contadores[tipo_elemento]['nuevasFacturas'] += 1
            configuracion.append(facturas[numeroFactura])
    elif tipo_elemento == 'pago':
        codigoBanco = elemento.find('codigoBanco').text
        fecha = re.findall(r'\d+/\d+/\d+', elemento.find('fecha').text)[0]  # Extrae solo los números y los signos /
        NITcliente = elemento.find('NITcliente').text
        valor = re.findall(r'\d+', elemento.find('valor').text)[0]  # Extrae solo los números
        if NITcliente not in clientes:
            # Si el NITcliente no coincide con ningún cliente existente, incrementa el contador de errores
            contadores[tipo_elemento]['pagosConError'] += 1
        elif codigoBanco in pagos:
            # Si el pago ya existe, incrementa el contador de pagos duplicados
            contadores[tipo_elemento]['pagosDuplicados'] += 1
        else:
            # Si el pago es nuevo y el NITcliente coincide con un cliente existente, crea una nueva entrada
            pagos[codigoBanco] = Pago(codigoBanco, fecha, NITcliente, valor)
            contadores[tipo_elemento]['nuevosPagos'] += 1
            configuracion.append(pagos[codigoBanco])

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/grabarConfiguracion', methods=['POST'])
def grabar_configuracion():
    entradaXML = request.data
    decodificarXML= entradaXML.decode('utf-8')
    print(decodificarXML)
    xmlRecibido = ET.XML(decodificarXML)

    for grupo in xmlRecibido:
        for elemento in grupo:
            objeto = procesar_elemento(elemento)
            configuracion.append(objeto)

    root = ET.Element('respuesta')
    for tipo_elemento in ['cliente', 'banco']:
        counts = contadores[tipo_elemento]
        tipo_element = ET.SubElement(root, tipo_elemento)
        for tipo_count, count in counts.items():
            count_element = ET.SubElement(tipo_element, tipo_count)
            count_element.text = str(count)

    xml_string = ET.tostring(root, encoding='utf8', method='xml')
    dom = minidom.parseString(xml_string)
    xml_str = dom.toprettyxml(encoding='utf-8')  # Utiliza toprettyxml() para agregar tabulaciones

    # Elimina las líneas en blanco adicionales
    xml_pretty_str = re.sub(r'>\n\s+([^<>\s].*?)\n\s+</', r'>\1<', xml_str.decode())

    with open('../ArchivosPrueba/resultados.xml', 'wb') as f:
        f.write(xml_pretty_str.encode('utf-8'))

    return xml_pretty_str



@app.route('/grabarTransaccion', methods=['POST'])
def grabar_transaccion():
    entradaXML = request.data
    decodificarXML= entradaXML.decode('utf-8')
    xmlRecibido = ET.XML(decodificarXML)

    for grupo in xmlRecibido:
        for elemento in grupo:
            procesar_elementoT(elemento)

    root = ET.Element('transacciones')
    for tipo_elemento in ['factura', 'pago']:
        counts = contadores[tipo_elemento]
        tipo_element = ET.SubElement(root, tipo_elemento)
        for tipo_count, count in counts.items():
            count_element = ET.SubElement(tipo_element, tipo_count)
            count_element.text = str(count)

    xml_string = ET.tostring(root, encoding='utf8', method='xml')
    dom = minidom.parseString(xml_string)
    xml_str = dom.toprettyxml(encoding='utf-8')  # Utiliza toprettyxml() para agregar tabulaciones

    # Elimina las líneas en blanco adicionales
    xml_pretty_str = re.sub(r'>\n\s+([^<>\s].*?)\n\s+</', r'>\1<', xml_str.decode())

    with open('../ArchivosPrueba/resultadosT.xml', 'wb') as f:
        f.write(xml_pretty_str.encode('utf-8'))

    return xml_pretty_str


@app.route('/limpiarDatos', methods=['DELETE'])
def limpiar_datos():
    # Vacía los diccionarios y la lista
    clientes.clear()
    bancos.clear()
    configuracion.clear()
    contadores.clear()
    facturas.clear()
    pagos.clear()
    return jsonify({'status': 'Datos limpiados'}), 200


@app.route('/devolverEstadoCuenta', methods=['GET'])
def devolver_estado_cuenta():
    # Crea una lista para almacenar los estados de las cuentas
    estados_cuenta = []

    # Recorre la lista de clientes
    for nit, cliente in clientes.items():
        # Crea un diccionario para almacenar el estado de la cuenta del cliente
        estado_cuenta_cliente = {
            'NIT': nit,
            'nombre': cliente.nombre,
        }
        # Añade el estado de la cuenta a la lista
        estados_cuenta.append(estado_cuenta_cliente)

    # Recorre la lista de bancos
    for codigo, banco in bancos.items():
        # Crea un diccionario para almacenar los datos del banco
        estado_cuenta_banco = {
            'codigo': codigo,
            'nombre': banco.nombre,
        }
        # Añade los datos del banco a la lista
        estados_cuenta.append(estado_cuenta_banco)

    # Devuelve la lista de estados de las cuentas
    return jsonify(estados_cuenta), 200


@app.route('/devolverResumenPagos', methods=['GET'])
def devolver_resumen_pagos():
    # Crea listas para almacenar los detalles de las facturas y pagos
    detalles_facturas = []
    detalles_pagos = []

    # Recorre la lista de facturas
    for numeroFactura, factura in facturas.items():
        # Crea un diccionario para almacenar los detalles de la factura
        detalles_factura = {
            'numeroFactura': numeroFactura,
            'nit_cliente': factura.nit_cliente,
            'fecha': factura.fecha,
            'valor': factura.valor
        }
        # Añade los detalles de la factura a la lista
        detalles_facturas.append(detalles_factura)

    # Recorre la lista de pagos
    for codigoBanco, pago in pagos.items():
        # Crea un diccionario para almacenar los detalles del pago
        detalles_pago = {
            'codigoBanco': codigoBanco,
            'fecha': pago.fecha,
            'nit_cliente': pago.nit_cliente,
            'valor': pago.valor
        }
        # Añade los detalles del pago a la lista
        detalles_pagos.append(detalles_pago)

    # Crea un diccionario para almacenar el resumen de pagos
    resumen_pagos = {
        'detalles_facturas': detalles_facturas,
        'detalles_pagos': detalles_pagos
    }

    # Devuelve el resumen de pagos
    return jsonify(resumen_pagos), 200

if __name__ == '__main__':
    app.run(host='localhost', port='5000',debug=True)