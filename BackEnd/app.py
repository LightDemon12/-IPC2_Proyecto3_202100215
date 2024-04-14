from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/grabarTransaccion', methods=['POST'])
def grabar_transaccion():
    # Aquí va la lógica para grabar la transacción
    # Puedes acceder a los datos enviados con la solicitud a través de request.json
    datos = request.json
    return jsonify({'status': 'Transacción grabada'}), 200

@app.route('/grabarConfiguracion', methods=['POST'])
def grabar_configuracion():
    # Aquí va la lógica para grabar la configuración
    datos = request.json
    return jsonify({'status': 'Configuración grabada'}), 200

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
    app.run(debug=True)