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
        self._params_pendientes = []
    
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
    
    def exitDeclaracion(self, ctx: compiladorParser.DeclaracionContext):
        tipo = ctx.tipo().getText()
        texto = ctx.getText()
        declaracion = texto.replace(tipo, '', 1).replace(';', '').strip()
        partes = [p.strip() for p in declaracion.split(',')]
        
        for parte in partes:
            if '=' in parte:
                nombre, valor = [x.strip() for x in parte.split('=', 1)]
                var = Variables(nombre, tipo)
                var.setInicializado()
                
                # Marcar variables usadas en el lado derecho
                ids_derecha = re.findall(r'\b[a-zA-Z_]\w*\b', valor)
                for id_ in ids_derecha:
                    simbolo_val = self.ts.buscarSimbolo(id_)
                    if simbolo_val is None:
                        print(f"[SEMÁNTICO] Error: variable '{id_}' usada sin declarar.")
                    elif isinstance(simbolo_val, Variables):
                        simbolo_val.setUsado()
            else:
                nombre = parte
                var = Variables(nombre, tipo)
            
            if self.ts.buscarSimboloContexto(nombre):
                print(f"[SEMÁNTICO] Error: variable '{nombre}' ya declarada en este contexto.")
            else:
                self.ts.addSimbolo(var)
                print(f"Declarada variable '{nombre}' tipo {tipo}, inicializada: {var.inicializado}")
        
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
        lado_derecho = texto.split('=', 1)[1].strip().rstrip(';')

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

            # Verificar compatibilidad de tipos
            tipo_izq = simbolo.getTipoDato() if hasattr(simbolo, "getTipoDato") else None
            tipo_der = simbolo_valor.getTipoDato() if hasattr(simbolo_valor, "getTipoDato") else None

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
            
    #ENTER DECLARACIONES FUNCION
    def enterDeclaracionFunc(self, ctx: compiladorParser.DeclaracionFuncContext):
        pass
    
    #EXIT DECLARACIONES FUNCION
    def exitDeclaracionFunc(self, ctx: compiladorParser.DeclaracionFuncContext):
        tipo = ctx.tipo().getText()
        nombre = ctx.ID().getText()
        existente = self.ts.buscarSimboloContexto(nombre)
        if existente:
            if isinstance(existente, Funcion):
                # Ya existía como prototipo, solo lo marcamos como implementado
                print(f"Función '{nombre}' tipo {tipo} implementada (tenía prototipo).")
            else:
                print(f"[SEMÁNTICO] Error: '{nombre}' ya declarada en este contexto.")
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
        
    #FORS
            
    def exitIfor(self, ctx: compiladorParser.IforContext):
        pass
    
    
    
    #BLOQUES
    
    def enterBloque(self, ctx: compiladorParser.BloqueContext):
        print("  "*self.indent + "Comienza bloque {")
        self.indent += 1
        self.ts.addContexto()
        
        padre = ctx.parentCtx

        # Detectar si el bloque pertenece a un for (directo o a través de instruccion)
        if isinstance(padre, compiladorParser.IforContext):
            for_ctx = padre
        elif isinstance(padre, compiladorParser.InstruccionContext) and isinstance(padre.parentCtx, compiladorParser.IforContext):
            for_ctx = padre.parentCtx
        else:
            for_ctx = None

        if for_ctx is not None:
            if for_ctx.tipo() is not None:
                tipo = for_ctx.tipo().getText()
                nombre = for_ctx.asignacionSimple(0).ID().getText()
                if not self.ts.buscarSimboloContexto(nombre):
                    var = Variables(nombre, tipo)
                    var.setInicializado()
                    self.ts.addSimbolo(var)
                    print(f"Declarada variable '{nombre}' tipo {tipo} (for), inicializada: {var.inicializado}")

        # Si el padre es una declaración de función, registrar parámetros
        elif isinstance(padre, compiladorParser.DeclaracionFuncContext):
            params_ctx = padre.parametros()
            if params_ctx is not None:
                self._registrar_parametros(params_ctx)
                
    def _registrar_parametros(self, params_ctx):
        # Buscar primer parámetro directamente por regla
        if params_ctx.parametro() is not None:
            p = params_ctx.parametro()
            nombre = p.ID().getText()
            tipo = p.tipo().getText()
            var = Variables(nombre, tipo)
            var.setInicializado()
            self.ts.addSimbolo(var)
            print(f"Declarado parámetro '{nombre}' tipo {tipo}")
            
            # Buscar el resto en listapar
            lista = params_ctx.listapar()
            while lista is not None and lista.parametro() is not None:
                p = lista.parametro()
                nombre = p.ID().getText()
                tipo = p.tipo().getText()
                var = Variables(nombre, tipo)
                var.setInicializado()
                self.ts.addSimbolo(var)
                print(f"Declarado parámetro '{nombre}' tipo {tipo}")
                lista = lista.listapar()

        
    def exitBloque(self, ctx:compiladorParser.BloqueContext):
        self.indent -= 1
        print("  "*self.indent + "} Fin bloque")
        self.ts.delContexto()
    
    
    def visitErrorNode(self, node: ErrorNode):
        print(" ---> ERROR")
        
    def enterEveryRule(self, ctx):
        self.numNodos += 1
    
    def __str__(self):
        return "Se hicieron " + str(self.declaracion) + " declaraciones\n" #+ \
                #"Se visitaron " + str(self.numNodos) + " nodos"