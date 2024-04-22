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
    for tipo_elemento, counts in contadores.items():
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
    # Aquí va la lógica para grabar la transacción
    # Puedes acceder a los datos enviados con la solicitud a través de request.json
    datos = request.json
    return jsonify({'status': 'Transacción grabada'}), 200


@app.route('/limpiarDatos', methods=['POST'])
def limpiar_datos():
    # Aquí va la lógica para limpiar los datos
    return jsonify({'status': 'Datos limpiados'}), 200

@app.route('/devolverEstadoCuenta', methods=['GET'])
def devolver_estado_cuenta():
    # Aquí va la lógica para devolver el estado de la cuenta
    estado_cuenta = {'saldo': 1000}  # Ejemplo
    return jsonify(estado_cuenta), 200

@app.route('/devolverResumenPagos', methods=['GET'])
def devolver_resumen_pagos():
    # Aquí va la lógica para devolver el resumen de pagos
    resumen_pagos = {'total_pagado': 500}  # Ejemplo
    return jsonify(resumen_pagos), 200

if __name__ == '__main__':
    app.run(host='localhost', port='5000',debug=True)