class Contexto:
    def __init__(self):
        # diccionario: nombre → ID (Variable o Funcion)
        self.simbolos = {}

    def addSimbolo(self, id_obj):
        if id_obj.nombre in self.simbolos:
            raise Exception(f"Símbolo '{id_obj.nombre}' ya declarado en este contexto")
        self.simbolos[id_obj.nombre] = id_obj

    def buscarSimbolo(self, nombre):
        return self.simbolos.get(nombre, None)

