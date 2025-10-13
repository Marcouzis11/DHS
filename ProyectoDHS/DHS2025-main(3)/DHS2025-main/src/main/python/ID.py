from abc import ABC, abstractmethod

class ID(ABC):
    def __init__ (self, nombre, tipoDato):
        self.nombre = nombre
        self.tipoDato = tipoDato
        self.inicializado = False
        self.usado = False
    
    def getNombre(self):
        return self.nombre
    
    def getTipoDato(self):
        return self.tipoDato
    
    def setInicializado(self):
        self.inicializado = True
        
    def setUsado(self):
        self.usado = True
        
    def getUsado(self):
        return self.usado