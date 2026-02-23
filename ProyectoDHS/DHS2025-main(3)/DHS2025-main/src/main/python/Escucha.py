from antlr4 import TerminalNode
import re
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
        self.ts.mostrarTablaCompleta() 
        
        print("\n[Chequeo Semántico Final]")
        for simbolo in self.ts.obtenerTodosLosSimbolos():
            if isinstance(simbolo, Variables):
                if not simbolo.usado:
                    print(f"[SEMÁNTICO] WARNING: Variable '{simbolo.nombre}' declarada pero nunca usada.")
        
    #DECLARACIONES
        
    def enterDeclaracion(self, ctx:compiladorParser.DeclaracionContext):
        self.declaracion += 1
        #print("Declaracion ENTER -> |" + ctx.getText() + "|")
        
    # def exitDeclaracion(self, ctx:compiladorParser.DeclaracionContext):
    #     tipo = ctx.tipo().getText()
    #     # listavar puede ser recursiva, aquí simplificamos suponiendo que es una lista separada por comas
    #     texto = ctx.getText()
    #     # Extraer variables y asignaciones
    #     # Ejemplo: int a=1, b, c=2;
    #     declaracion = texto.replace(tipo, '').replace(';', '').strip()
    #     partes = [p.strip() for p in declaracion.split(',')]
    #     for parte in partes:
    #         if '=' in parte:
    #             nombre, valor = [x.strip() for x in parte.split('=')]
    #         else:
    #             nombre = parte
    #         # Verifica si ya existe en este contexto
    #         if self.ts.buscarSimboloContexto(nombre):
    #             print(f"Error: variable '{nombre}' ya declarada en este contexto.")
    #         else:
    #             var = Variables(nombre, tipo)
    #             var.setInicializado()
    #             self.ts.addSimbolo(var)
    #             print(f"Declarada variable '{nombre}' tipo {tipo}, inicializada: {var.inicializado}")
    
    def exitDeclaracion(self, ctx:compiladorParser.DeclaracionContext):
        tipo = ctx.tipo().getText()
        texto = ctx.getText()
        # Extraer variables y asignaciones
        # Ejemplo: int a=1, b, c=2;
        declaracion = texto.replace(tipo, '').replace(';', '').strip()
        partes = [p.strip() for p in declaracion.split(',')]
        for parte in partes:
            if '=' in parte:
                nombre, valor = [x.strip() for x in parte.split('=',1)]
                var = Variables(nombre, tipo)
                var.setInicializado()
            else:
                nombre = parte
                var = Variables(nombre, tipo)
                
            if self.ts.buscarSimboloContexto(nombre):
                print(f"[SEMÁNTICO] Error: variable '{nombre}' ya declarada en este contexto.")
            else:
                self.ts.addSimbolo(var)
                print(f"Declarada variable '{nombre}' tipo {tipo}, inicializada: {var.inicializado}")
    
    # def exitAsignacion(self, ctx:compiladorParser.AsignacionContext):
    #     # Lado izquierdo
    #     nombre = ctx.ID().getText()
    #     simbolo = self.ts.buscarSimbolo(nombre)
    #     if simbolo is None:
    #         print(f"[SEMÁNTICO] Error: variable '{nombre}' no declarada.")
    #     elif not isinstance(simbolo, Variables):
    #         print(f"[SEMÁNTICO] Error: '{nombre}' no es una variable.")
    #     else:
    #         simbolo.setInicializado()
            
    #     texto = ctx.getText()       # Ejemplo: "a=b"
    #     lado_derecho = texto.split('=')[1].strip().rstrip(';')

        # posibles_ids = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', lado_derecho)

        # for id_ in posibles_ids:
        #     # Ignorar si es un número o palabra reservada tipo 'int', 'float', etc. (opcional)
        #     if id_.isdigit():
        #         continue  # ignora números tipo "123"

        #     simbolo_valor = self.ts.buscarSimbolo(id_)
        #     if simbolo_valor is None:
        #         print(f"[SEMÁNTICO] Error: variable '{id_}' usada sin declarar.")
        #     elif isinstance(simbolo_valor, Variables):
        #         simbolo_valor.setUsado()
        #         if not simbolo_valor.inicializado:
        #             print(f"[SEMÁNTICO] Error: variable '{id_}' usada sin inicializar.")
        #         else:
        #             print(f"Variable '{id_}' usada correctamente en asignación.")
        
    def exitAsignacion(self, ctx:compiladorParser.AsignacionContext):
        # Lado izquierdo
        nombre = ctx.ID().getText()
        simbolo = self.ts.buscarSimbolo(nombre)
        if simbolo is None:
            print(f"[SEMÁNTICO] Error: variable '{nombre}' no declarada.")
            return
        elif not isinstance(simbolo, Variables):
            print(f"[SEMÁNTICO] Error: '{nombre}' no es una variable.")
            return
        else:
            simbolo.setInicializado()

        # Lado derecho
        texto = ctx.getText()       # Ejemplo: "a = b + c"
        lado_derecho = texto.split('=')[1].strip().rstrip(';')

        # Buscar todos los identificadores en el lado derecho
        ids_derecha = re.findall(r'\b[a-zA-Z_]\w*\b', lado_derecho)

        for nombre_valor in ids_derecha:
            # Ignorar números
            if nombre_valor.isdigit():
                continue

            simbolo_valor = self.ts.buscarSimbolo(nombre_valor)
            if simbolo_valor is None:
                print(f"[SEMÁNTICO] Error: variable '{nombre_valor}' usada sin declarar.")
                continue

            # Verificar inicialización
            if not getattr(simbolo_valor, "inicializado", False):
                print(f"[SEMÁNTICO] Error: variable '{nombre_valor}' usada sin inicializar.")

            # 🔍 Verificar compatibilidad de tipos
            tipo_izq = getattr(simbolo, "tipo", None)
            if tipo_izq is None and hasattr(simbolo, "getTipo"):
                tipo_izq = simbolo.getTipo()
            elif tipo_izq is None and hasattr(simbolo, "getTipoDato"):
                tipo_izq = simbolo.getTipoDato()

            tipo_der = getattr(simbolo_valor, "tipo", None)
            if tipo_der is None and hasattr(simbolo_valor, "getTipo"):
                tipo_der = simbolo_valor.getTipo()
            elif tipo_der is None and hasattr(simbolo_valor, "getTipoDato"):
                tipo_der = simbolo_valor.getTipoDato()

            if tipo_izq is not None and tipo_der is not None and tipo_izq != tipo_der:
                print(f"[SEMÁNTICO] Error: tipos incompatibles en asignación '{nombre} = {nombre_valor}' "
                    f"({tipo_izq} ← {tipo_der})")
            else:
                simbolo_valor.setUsado()
                print(f"Variable '{nombre_valor}' usada correctamente en asignación.")



    
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
        #self.ts.mostrarTabla()
        self.ts.delContexto()
    
    
    def visitErrorNode(self, node: ErrorNode):
        print(" ---> ERROR")
        
    def enterEveryRule(self, ctx):
        self.numNodos += 1
    
    def __str__(self):
        return "Se hicieron " + str(self.declaracion) + " declaraciones\n" #+ \
                #"Se visitaron " + str(self.numNodos) + " nodos"