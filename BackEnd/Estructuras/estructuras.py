class Cliente:
    def __init__(self, nit, nombre):
        self.nit = nit
        self.nombre = nombre

    def __str__(self):
        return f'NIT: {self.nit}, Nombre: {self.nombre}'

class Banco:
    def __init__(self, codigo, nombre):
        self.codigo = codigo
        self.nombre = nombre

    def __str__(self):
        return f'Codigo: {self.codigo}, Nombre: {self.nombre}'

class Factura:
    def __init__(self, numero_factura, nit_cliente, fecha, valor):
        self.numero_factura = numero_factura
        self.nit_cliente = nit_cliente
        self.fecha = fecha
        self.valor = valor

    def __str__(self):
        return f'Numero Factura: {self.numero_factura}, NIT Cliente: {self.nit_cliente}, Fecha: {self.fecha}, Valor: {self.valor}'

class Pago:
    def __init__(self, codigo_banco, fecha, nit_cliente, valor):
        self.codigo_banco = codigo_banco
        self.fecha = fecha
        self.nit_cliente = nit_cliente
        self.valor = valor

    def __str__(self):
        return f'Codigo Banco: {self.codigo_banco}, Fecha: {self.fecha}, NIT Cliente: {self.nit_cliente}, Valor: {self.valor}'