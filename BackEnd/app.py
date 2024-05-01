from flask import Flask, request, jsonify, render_template, send_file , Response
from flask_cors import CORS
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import re
from collections import defaultdict
from Estructuras.estructuras import Cliente, Banco, Factura, Pago
from datetime import datetime



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

def normalizar_NIT(NIT):
    return re.sub(r'\W', '-', NIT)  # Reemplaza todos los signos no alfanuméricos por un guion

def normalizar_fecha(fecha):
    return re.sub(r'[-/\.]', '/', fecha)  # Reemplaza todos los guiones, puntos y barras por barras

def procesar_elementoT(elemento):
    tipo_elemento = elemento.tag
    if tipo_elemento == 'factura':
        numeroFactura = elemento.find('numeroFactura').text
        NITcliente = normalizar_NIT(elemento.find('NITcliente').text)  # Normaliza el NIT del cliente
        fecha_str = re.findall(r'\b\d{1,2}[-/\.]\d{1,2}[-/\.]\d{4}\b', normalizar_fecha(elemento.find('fecha').text))[0]  # Normaliza y extrae la fecha
        valor = re.findall(r'\d+', elemento.find('valor').text)[0]  # Extrae solo los números
        if NITcliente not in clientes:
            contadores[tipo_elemento]['facturasConError'] += 1
        elif numeroFactura in facturas:
            contadores[tipo_elemento]['facturasDuplicadas'] += 1
        else:
            facturas[numeroFactura] = Factura(numeroFactura, NITcliente, fecha_str, valor)
            contadores[tipo_elemento]['nuevasFacturas'] += 1
            configuracion.append(facturas[numeroFactura])
    elif tipo_elemento == 'pago':
        codigoBanco = elemento.find('codigoBanco').text
        fecha_str = normalizar_fecha(elemento.find('fecha').text)  # Normaliza la fecha
        fecha_str = re.findall(r'\b\d{1,2}[-/\.]\d{1,2}[-/\.]\d{4}\b', fecha_str)[0]  # Extrae la fecha
        for fmt in ('%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y'):
            try:
                fecha = datetime.strptime(fecha_str, fmt)
                break
            except ValueError:
                pass
        NITcliente = normalizar_NIT(elemento.find('NITcliente').text)  # Normaliza el NIT del cliente
        valor = re.findall(r'\d+', elemento.find('valor').text)[0]  # Extrae solo los números
        if NITcliente not in clientes:
            contadores[tipo_elemento]['pagosConError'] += 1
        elif codigoBanco not in bancos:
            contadores[tipo_elemento]['pagosConError'] += 1
        elif (NITcliente, fecha.date()) in [(pago.nit_cliente, datetime.strptime(pago.fecha, '%d/%m/%Y').date()) for lista_pagos in pagos.values() for pago in lista_pagos]:
            contadores[tipo_elemento]['pagosDuplicados'] += 1
        else:
            nuevo_pago = Pago(codigoBanco, fecha_str, NITcliente, valor)
            if codigoBanco not in pagos:
                pagos[codigoBanco] = [nuevo_pago]
            else:
                pagos[codigoBanco].append(nuevo_pago)
            contadores[tipo_elemento]['nuevosPagos'] += 1
            configuracion.append(nuevo_pago)


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


@app.route('/clear', methods=['DELETE'])
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
@app.route('/devolverEstadoCuenta/<nit_cliente>', methods=['GET'])
def devolver_estado_cuenta(nit_cliente=None):
    # Crea una lista para almacenar los estados de las cuentas
    estados_cuenta = []

    # Recorre la lista de clientes
    for nit, cliente in clientes.items():
        # Solo procesa los clientes que coincidan con el NIT proporcionado, si se proporcionó
        if nit_cliente is None or nit == nit_cliente:
            # Crea un diccionario para almacenar el estado de la cuenta del cliente
            estado_cuenta_cliente = {
                'NIT': nit,
                'nombre': cliente.nombre,
            }
            # Añade el estado de la cuenta a la lista
            estados_cuenta.append(estado_cuenta_cliente)

    # Ordena la lista de estados de cuenta de los clientes por el campo 'NIT'
    estados_cuenta.sort(key=lambda x: x['NIT'])

    # Recorre la lista de bancos
    for codigo, banco in bancos.items():
        # Crea un diccionario para almacenar los datos del banco
        estado_cuenta_banco = {
            'codigo': codigo,
            'nombre': banco.nombre,
        }
        # Añade los datos del banco a la lista
        estados_cuenta.append(estado_cuenta_banco)

    # Ordena la lista de estados de cuenta de los bancos por el campo 'codigo'
    estados_cuenta.sort(key=lambda x: x.get('codigo', ''))

    # Devuelve la lista de estados de las cuentas
    return jsonify(estados_cuenta), 200

@app.route('/devolverResumenPagos', methods=['GET'])
@app.route('/devolverResumenPagos/<nit_cliente>', methods=['GET'])
def devolver_resumen_pagos(nit_cliente=None):
    # Crea listas para almacenar los detalles de las facturas y pagos
    detalles_facturas = []
    detalles_pagos = []

    # Recorre la lista de facturas
    for numeroFactura, factura in facturas.items():
        # Solo procesa las facturas que coincidan con el NIT proporcionado, si se proporcionó
        if nit_cliente is None or factura.nit_cliente == nit_cliente:
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
    for codigoBanco, lista_pagos in pagos.items():
        for pago in lista_pagos:
            # Solo procesa los pagos que coincidan con el NIT proporcionado, si se proporcionó
            if nit_cliente is None or pago.nit_cliente == nit_cliente:
                # Crea un diccionario para almacenar los detalles del pago
                detalles_pago = {
                    'codigoBanco': codigoBanco,
                    'fecha': pago.fecha,
                    'nit_cliente': pago.nit_cliente,
                    'valor': pago.valor
                }
                # Añade los detalles del pago a la lista
                detalles_pagos.append(detalles_pago)

    # Ordena las listas por el campo 'nit_cliente'
    detalles_facturas.sort(key=lambda x: x['nit_cliente'])
    detalles_pagos.sort(key=lambda x: x['nit_cliente'])

    # Crea un diccionario para almacenar el resumen de pagos
    resumen_pagos = {
        'detalles_facturas': detalles_facturas,
        'detalles_pagos': detalles_pagos
    }

    # Devuelve el resumen de pagos
    return jsonify(resumen_pagos), 200



@app.route('/downloadC', methods=['GET'])
def download_fileC():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, '../ArchivosPrueba/resultados.xml')
    response = send_file(file_path, as_attachment=True)
    response.headers["Content-Disposition"] = "attachment; filename=resultados.xml"
    return response

@app.route('/downloadT', methods=['GET'])
def download_fileT():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, '../ArchivosPrueba/resultadosT.xml')
    response = send_file(file_path, as_attachment=True)
    response.headers["Content-Disposition"] = "attachment; filename=resultadosT.xml"
    return response

@app.route('/results', methods=['GET'])
def get_all_results():
    resumen_clientes = {}

    # Recorre la lista de facturas
    for numeroFactura, factura in facturas.items():
        nit = factura.nit_cliente  # Usa una variable diferente para el NIT del cliente
        if nit not in resumen_clientes:
            resumen_clientes[nit] = {
                'facturas': [],
                'pagos': [],
                'total_facturas': 0,
                'total_pagos': 0
            }
        factura_dict = {
            'numeroFactura': factura.numero_factura,
            'nit_cliente': factura.nit_cliente,
            'fecha': factura.fecha,
            'valor': factura.valor
        }
        resumen_clientes[nit]['facturas'].append(factura_dict)
        resumen_clientes[nit]['total_facturas'] += int(factura.valor)

    # Recorre la lista de pagos
    for codigoBanco, lista_pagos in pagos.items():
        for pago in lista_pagos:
            nit = pago.nit_cliente  # Usa una variable diferente para el NIT del cliente
            if nit not in resumen_clientes:
                resumen_clientes[nit] = {
                    'facturas': [],
                    'pagos': [],
                    'total_facturas': 0,
                    'total_pagos': 0
                }
            pago_dict = {
                'codigoBanco': pago.codigo_banco,
                'fecha': pago.fecha,
                'nit_cliente': pago.nit_cliente,
                'valor': pago.valor
            }
            resumen_clientes[nit]['pagos'].append(pago_dict)
            resumen_clientes[nit]['total_pagos'] += int(pago.valor)

    # Ordena las facturas y calcula el saldo para cada cliente
    for nit, resumen in resumen_clientes.items():
        resumen['facturas'] = sorted(resumen['facturas'], key=lambda x: x['fecha'], reverse=True)
        saldo = resumen['total_facturas'] - resumen['total_pagos']
        resumen['saldo'] = 'Saldo a pagar: ' + str(saldo) if saldo > 0 else 'Saldo a favor: ' + str(-saldo)
        resumen['nit_cliente'] = nit  # Agrega el NIT del cliente al resumen

    # Convierte el diccionario en una lista de tuplas y la ordena por la clave (NIT del cliente)
    resumen_clientes = sorted(resumen_clientes.items(), key=lambda x: x[0])

    # Extrae solo los valores (resúmenes de los clientes) de la lista de tuplas
    resumen_clientes = [cliente_resumen for nit, cliente_resumen in resumen_clientes]

    return jsonify(resumen_clientes)


    

@app.route('/resultsnit/<nit_cliente>', methods=['GET'])
def get_single_result(nit_cliente):
    resumen_clientes = {}

    # Recorre la lista de facturas
    for numeroFactura, factura in facturas.items():
        nit = factura.nit_cliente  # Usa una variable diferente para el NIT del cliente
        if nit not in resumen_clientes:
            resumen_clientes[nit] = {
                'facturas': [],
                'pagos': [],
                'total_facturas': 0,
                'total_pagos': 0
            }
        factura_dict = {
            'numeroFactura': factura.numero_factura,
            'nit_cliente': factura.nit_cliente,
            'fecha': factura.fecha,
            'valor': factura.valor
        }
        resumen_clientes[nit]['facturas'].append(factura_dict)
        resumen_clientes[nit]['total_facturas'] += int(factura.valor)

    # Recorre la lista de pagos
    for codigoBanco, lista_pagos in pagos.items():
        for pago in lista_pagos:
            nit = pago.nit_cliente  # Usa una variable diferente para el NIT del cliente
            if nit not in resumen_clientes:
                resumen_clientes[nit] = {
                    'facturas': [],
                    'pagos': [],
                    'total_facturas': 0,
                    'total_pagos': 0
                }
            pago_dict = {
                'codigoBanco': pago.codigo_banco,
                'fecha': pago.fecha,
                'nit_cliente': pago.nit_cliente,
                'valor': pago.valor
            }
            resumen_clientes[nit]['pagos'].append(pago_dict)
            resumen_clientes[nit]['total_pagos'] += int(pago.valor)

    # Ordena las facturas y calcula el saldo para cada cliente
    for nit, resumen in resumen_clientes.items():
        resumen['facturas'] = sorted(resumen['facturas'], key=lambda x: x['fecha'], reverse=True)
        saldo = resumen['total_facturas'] - resumen['total_pagos']
        resumen['saldo'] = 'Saldo a pagar: ' + str(saldo) if saldo > 0 else 'Saldo a favor: ' + str(-saldo)
        resumen['nit_cliente'] = nit  # Agrega el NIT del cliente al resumen

    # Si se proporcionó un NIT de cliente, devuelve solo el resumen de ese cliente
    cliente_resumen = resumen_clientes.get(nit_cliente)
    if cliente_resumen is None:
        return jsonify({'error': 'Cliente no encontrado'}), 404
    return jsonify(cliente_resumen)

@app.route('/sumarMeses/<int:mes>', methods=['GET'])
def sumar_meses(mes):
    # Asegúrate de que el mes es válido
    if mes < 1 or mes > 12:
        return jsonify({'error': 'Mes inválido'}), 400

    # Calcula los meses y años anteriores
    año_actual = datetime.now().year
    mes_anterior1 = mes - 1 if mes > 1 else 12
    año_anterior1 = año_actual if mes > 1 else año_actual - 1
    mes_anterior2 = mes_anterior1 - 1 if mes_anterior1 > 1 else 12
    año_anterior2 = año_anterior1 if mes_anterior1 > 1 else año_anterior1 - 1

    # Crea un diccionario para almacenar las sumas de facturas y pagos por mes
    total_facturas_por_mes = {mes: 0, mes_anterior1: 0, mes_anterior2: 0}
    total_pagos_por_mes = {mes: {}, mes_anterior1: {}, mes_anterior2: {}}

    # Filtra y suma las facturas y pagos de los meses relevantes
    for factura in facturas.values():
        mes_factura = datetime.strptime(factura.fecha, '%d/%m/%Y').month
        if mes_factura in total_facturas_por_mes:
            total_facturas_por_mes[mes_factura] += int(factura.valor)

    for codigo_banco, lista_pagos in pagos.items():
        for pago in lista_pagos:
            mes_pago = datetime.strptime(pago.fecha, '%d/%m/%Y').month
            if mes_pago in total_pagos_por_mes:
                if codigo_banco not in total_pagos_por_mes[mes_pago]:
                    total_pagos_por_mes[mes_pago][codigo_banco] = 0
                total_pagos_por_mes[mes_pago][codigo_banco] += int(pago.valor)

    # Prepara la respuesta
    response = {'total_facturas_por_mes': total_facturas_por_mes, 'total_pagos_por_mes': total_pagos_por_mes}

    # Imprime la respuesta
    print(response)

    # Devuelve la respuesta
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='localhost', port='5000',debug=True)

