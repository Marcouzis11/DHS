from antlr4 import TerminalNode
from antlr4 import ErrorNode
from TablaSimbolos import TS
from Funciones import Funcion
from Variables import Variables
from compiladorParser import compiladorParser
from compiladorListener import compiladorListener

class Escucha (compiladorListener) :
    declaracion = 0
    indent = 1
    profundidad = 0
    numNodos = 0
    
    def __init__(self):
        self.ts = TS.getTablaSimbolo()
    
    def enterPrograma(self, ctx:compiladorParser.ProgramaContext):
        print("Comienza el parsing")
        
    def exitPrograma(self, ctx:compiladorParser.ProgramaContext):
        print("Fin del parsing")
        self.ts.mostrarTabla() 
        
    #DECLARACIONES
        
    def enterDeclaracion(self, ctx:compiladorParser.DeclaracionContext):
        self.declaracion += 1
        print("Declaracion ENTER -> |" + ctx.getText() + "|")
        
    def exitDeclaracion(self, ctx:compiladorParser.DeclaracionContext):
        tipo = ctx.tipo().getText()
        # listavar puede ser recursiva, aquí simplificamos suponiendo que es una lista separada por comas
        texto = ctx.getText()
        # Extraer variables y asignaciones
        # Ejemplo: int a=1, b, c=2;
        declaracion = texto.replace(tipo, '').replace(';', '').strip()
        partes = [p.strip() for p in declaracion.split(',')]
        for parte in partes:
            if '=' in parte:
                nombre, valor = [x.strip() for x in parte.split('=')]
            else:
                nombre = parte
            # Verifica si ya existe en este contexto
            if self.ts.buscarSimboloContexto(nombre):
                print(f"Error: variable '{nombre}' ya declarada en este contexto.")
            else:
                var = Variables(nombre, tipo)
                var.setInicializado()
                self.ts.addSimbolo(var)
                print(f"Declarada variable '{nombre}' tipo {tipo}, inicializada: {var.inicializado}")
    
    #EXIT ASIGNACION
    def exitAsignacion(self, ctx:compiladorParser.AsignacionContext):
        nombre = ctx.ID().getText()
        simbolo = self.ts.buscarSimbolo(nombre)
        if simbolo is None:
            print(f"Error: variable '{nombre}' no declarada.")
        elif not isinstance(simbolo, Variables):
            print(f"Error: '{nombre}' no es una variable.")
        else:
            simbolo.setInicializado()
            simbolo.setUsado()
            print(f"Variable '{nombre}' asignada y ahora inicializada y usada.")
    
    #EXIT PROTOTIPADO FUNCION
    def exitPrototipoFunc(self, ctx:compiladorParser.PrototipoFuncContext):
        tipo = ctx.tipo().getText()
        nombre = ctx.ID().getText()
        if self.ts.buscarSimboloContexto(nombre):
            print(f"Error: función '{nombre}' ya declarada en este contexto.")
        else:
            func = Funcion(nombre, tipo)
            self.ts.addSimbolo(func)
            print(f"Prototipo de función '{nombre}' tipo {tipo} declarado.")
    
    #EXIT DECLARACIONES FUNCION
    def exitDeclaracionFunc(self, ctx:compiladorParser.DeclaracionFuncContext):
        tipo = ctx.tipo().getText()
        nombre = ctx.ID().getText()
        if self.ts.buscarSimboloContexto(nombre):
            print(f"Error: función '{nombre}' ya declarada en este contexto.")
        else:
            func = Funcion(nombre, tipo)
            self.ts.addSimbolo(func)
            print(f"Declarada función '{nombre}' tipo {tipo}")
            
    #EXIT LLAMADA FUNCION
    def exitLlamadaFunc(self, ctx:compiladorParser.LlamadaFuncContext):
        nombre = ctx.ID().getText()
        simbolo = self.ts.buscarSimbolo(nombre)
        if simbolo is None:
            print(f"Error: función '{nombre}' no declarada.")
        elif not isinstance(simbolo, Funcion):
            print(f"Error: '{nombre}' no es una función.")
        else:
            simbolo.setUsado()
            print(f"Llamada a función '{nombre}' registrada y marcada como usada.")
        
    #WHILES
    
    def enterIwhile(self, ctx:compiladorParser.IwhileContext):
        print("  "*self.indent + "Comienza while")
        self.indent += 1
    
    def exitIwhile(self, ctx:compiladorParser.IwhileContext):
        self.indent -= 1
        print("  "*self.indent + "Fin while")
    
    
    
    #BLOQUES
    
    def enterBloque(self, ctx:compiladorParser.BloqueContext):
        print("  "*self.indent + "Comienza bloque {")
        self.indent += 1
        self.ts.addContexto()
        
        
    def exitBloque(self, ctx:compiladorParser.BloqueContext):
        self.indent -= 1
        print("  "*self.indent + "} Fin bloque")
        self.ts.mostrarTabla()
        self.ts.delContexto()
    
    
    def visitErrorNode(self, node: ErrorNode):
        print(" ---> ERROR")
        
    def enterEveryRule(self, ctx):
        self.numNodos += 1
    
    def __str__(self):
        return "Se hicieron " + str(self.declaracion) + " declaraciones\n" #+ \
                #"Se visitaron " + str(self.numNodos) + " nodos"