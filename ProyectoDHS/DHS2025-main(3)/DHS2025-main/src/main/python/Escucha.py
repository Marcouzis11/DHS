from compiladorParser import compiladorParser
from compiladorListener import compiladorListener

class Escucha (compiladorListener) :
    declaracion = 0
    indent = 1
    
    def enterPrograma(self, ctx:compiladorParser.ProgramaContext):
        print("Comienza el parsing")
        
    def exitPrograma(self, ctx:compiladorParser.ProgramaContext):
        print("Fin del parsing")
        
    def enterDeclaracion(self, ctx:compiladorParser.DeclaracionContext):
        self.declaracion += 1

    def enterIwhile(self, ctx:compiladorParser.IwhileContext):
        print("Comienza while")
    
    def exitIwhile(self, ctx:compiladorParser.IwhileContext):
        print("Fin de while")
    
    def __str__(self):
        return "Se hicieron " + str(self.declaracion) + "declaraciones"