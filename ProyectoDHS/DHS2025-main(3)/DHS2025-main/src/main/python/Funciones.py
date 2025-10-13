from ID import ID

class Funcion(ID):
    def __init__(self, nombre, tipoDato, args=None):
        super().__init__(nombre, tipoDato)
        self.args = args if args else []

    def getListaArgs(self):
        return self.args