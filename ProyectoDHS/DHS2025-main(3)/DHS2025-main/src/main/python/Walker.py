
import os

from compiladorVisitor import compiladorVisitor
from compiladorParser import compiladorParser

class Walker(compiladorVisitor):
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))

        output_dir = os.path.join(base_dir, "output")
        os.makedirs(output_dir, exist_ok=True)

        ruta = os.path.join(output_dir, "codigoIntermedio.txt")

        print("Generando archivo en:", ruta)

        self.archivo = open(ruta, "w")
        self.t_cont = 0
        self.l_cont = 0
        
        self.pila_retornos = []
        self.tabla_funciones = {}
        
    def visitPrograma(self, ctx):
        print("Entré a programa")
        return self.visitChildren(ctx)
    
    def visitTerminal(self, node):
        return node.getText()

    #Devuelve el label con su numero (L1, L2, etc)
    def get_label(self):
        self.l_cont += 1
        return f"L{self.l_cont}"
    
    #Ingresa y ve los hijos de instrucción o si hay más instrucciones
    def visitInstrucciones(self, ctx):
        if ctx.instruccion():
            self.visit(ctx.instruccion())
        if ctx.instrucciones():
            self.visit(ctx.instrucciones())
        return None

    def visitInstruccion(self, ctx):
        return self.visitChildren(ctx)
    
    def visitBloque(self, ctx):
        return self.visit(ctx.instrucciones())
    
    def visitDeclaracion(self, ctx):
        # Primera variable
        id_name = ctx.ID().getText()

        if ctx.inic():
            valor = self.visit(ctx.inic().opal())
            self.archivo.write(f"{id_name} = {valor}\n")

        # Variables adicionales (si existen)
        if ctx.listavar():
            self.visit(ctx.listavar())
            
    def visitListavar(self, ctx):
        if ctx.ID():
            id_name = ctx.ID().getText()

            if ctx.inic():
                valor = self.visit(ctx.inic().opal())
                self.archivo.write(f"{id_name} = {valor}\n")

            if ctx.listavar():
                self.visit(ctx.listavar())

    #Escribe la asignación en el codigoIntermedio.txt
    def visitAsignacion(self, ctx):
        id_name = ctx.ID().getText()
        valor = self.visit(ctx.opal())
        self.archivo.write(f"{id_name} = {valor}\n")
    
    #Lo mismo que la de arriba (pero por un problema de punto y coma con el for)
    def visitAsignacionSimple(self, ctx):
        id_name = ctx.ID().getText()
        valor = self.visit(ctx.opal())
        self.archivo.write(f"{id_name} = {valor}\n")
        
    #Ingresa a las opal y sigue toda la precedencia de operadores
    def visitOpal(self, ctx):
        return self.visit(ctx.expOR())
    
    def visitExpOR(self, ctx):
        izquierda = self.visit(ctx.expAND())
        return self.visitExpORp(ctx.expORp(), izquierda)

    def visitExpORp(self, ctx, izquierda):
        if ctx.getChildCount() == 0:
            return izquierda

        operador = ctx.getChild(0).getText()
        derecha = self.visit(ctx.expAND())

        temp = self.nuevoTemp()
        self.archivo.write(f"{temp} = {izquierda} {operador} {derecha}\n")

        return self.visitExpORp(ctx.expORp(), temp)
    
    def visitExpAND(self, ctx):
        izquierda = self.visit(ctx.expIGUAL())
        return self.visitExpANDp(ctx.expANDp(), izquierda)

    def visitExpANDp(self, ctx, izquierda):
        if ctx.getChildCount() == 0:
            return izquierda

        operador = ctx.getChild(0).getText()
        derecha = self.visit(ctx.expIGUAL())

        temp = self.nuevoTemp()
        self.archivo.write(f"{temp} = {izquierda} {operador} {derecha}\n")

        return self.visitExpANDp(ctx.expANDp(), temp)
    
    def visitExpIGUAL(self, ctx):
        izquierda = self.visit(ctx.expCOMP())
        return self.visitExpIGUALp(ctx.expIGUALp(), izquierda)

    def visitExpIGUALp(self, ctx, izquierda):
        if ctx.getChildCount() == 0:
            return izquierda

        operador = ctx.getChild(0).getText()
        derecha = self.visit(ctx.expCOMP())

        temp = self.nuevoTemp()
        self.archivo.write(f"{temp} = {izquierda} {operador} {derecha}\n")

        return self.visitExpIGUALp(ctx.expIGUALp(), temp)
    
    def visitExpCOMP(self, ctx):
        izquierda = self.visit(ctx.expSUMA())
        return self.visitExpCOMPp(ctx.expCOMPp(), izquierda)

    def visitExpCOMPp(self, ctx, izquierda):
        if ctx.getChildCount() == 0:
            return izquierda

        operador = ctx.getChild(0).getText()
        derecha = self.visit(ctx.expSUMA())

        temp = self.nuevoTemp()
        self.archivo.write(f"{temp} = {izquierda} {operador} {derecha}\n")

        return self.visitExpCOMPp(ctx.expCOMPp(), temp)

        
    def visitExpSUMA(self, ctx):
        izquierda = self.visit(ctx.term())
        return self.visitExpSUMAp(ctx.expSUMAp(), izquierda)
    
    def visitExpSUMAp(self, ctx, izquierda):
        if ctx.getChildCount() == 0:
            return izquierda

        operador = ctx.getChild(0).getText()
        derecha = self.visit(ctx.term())

        temp = self.nuevoTemp()
        self.archivo.write(f"{temp} = {izquierda} {operador} {derecha}\n")

        return self.visitExpSUMAp(ctx.expSUMAp(), temp)
    
    def visitTerm(self, ctx):
        izquierda = self.visit(ctx.factor())
        return self.visitTermp(ctx.termp(), izquierda)
    
    def visitTermp(self, ctx, izquierda):
        if ctx.getChildCount() == 0:
            return izquierda

        operador = ctx.getChild(0).getText()
        derecha = self.visit(ctx.factor())

        temp = self.nuevoTemp()
        self.archivo.write(f"{temp} = {izquierda} {operador} {derecha}\n")

        return self.visitTermp(ctx.termp(), temp)

    def visitFactor(self, ctx):
        if ctx.NUMERO():
            return ctx.NUMERO().getText()

        if ctx.ID():
            return ctx.ID().getText()

        if ctx.llamadaFunc():
            return self.visit(ctx.llamadaFunc())

        if ctx.opal():
            return self.visit(ctx.opal())
        
    #Visita el if y lo coloca así: if condicion jmp LX
    def visitIif(self, ctx):
        cond = self.visit(ctx.opal())

        Ltrue = self.get_label()
        Lfalse = self.get_label()
        Lend = self.get_label()

        self.archivo.write(f"if {cond} jmp {Ltrue}\n")
        self.archivo.write(f"jmp {Lfalse}\n")

        # Escribe el label de TRUE y el contenido
        self.archivo.write(f"{Ltrue}:\n")
        self.visit(ctx.instruccion())  # cuerpo del if

        # ¿Existe else?
        if ctx.ielse() and ctx.ielse().instruccion():
            self.archivo.write(f"jmp {Lend}\n")

        # Escribe el label de FALSE y el contenido
        self.archivo.write(f"{Lfalse}:\n")

        if ctx.ielse() and ctx.ielse().instruccion():
            self.visit(ctx.ielse().instruccion())
            self.archivo.write(f"{Lend}:\n")

    #Escribe el while con los labels correspondientes (utiliza if para la condición)
    def visitIwhile(self, ctx):
        Linicio = self.get_label()
        Lbody = self.get_label()
        Lfin = self.get_label()

        self.archivo.write(f"{Linicio}:\n")

        cond = self.visit(ctx.opal())

        self.archivo.write(f"if {cond} jmp {Lbody}\n")
        self.archivo.write(f"jmp {Lfin}\n")

        self.archivo.write(f"{Lbody}:\n")
        self.visit(ctx.instruccion())   

        self.archivo.write(f"jmp {Linicio}\n")
        self.archivo.write(f"{Lfin}:\n")
        
        #Escribe el for con los labels correspondientes (utiliza if para la condición)
    def visitIfor(self, ctx):
        
        if ctx.tipo() is None:
            self.visit(ctx.asignacion())
            asigs = ctx.asignacionSimple()
            incremento_ctx = asigs[0]
        else:
            asigs = ctx.asignacionSimple()
            self.visit(asigs[0])
            incremento_ctx = asigs[1]

        start = self.get_label()
        body = self.get_label()
        end = self.get_label()

        self.archivo.write(start + ":\n")

        #IF del for
        cond = self.visit(ctx.opal())
        self.archivo.write(f"if {cond} jmp {body}\n")
        self.archivo.write(f"jmp {end}\n")

        self.archivo.write(body + ":\n")
        self.visit(ctx.instruccion())

        self.visit(incremento_ctx)

        self.archivo.write(f"jmp {start}\n")
        self.archivo.write(end + ":\n")
        
    #Prototipado de la función (se guarda el nombre y la cantidad para verificar en la llamada)
    def visitPrototipoFunc(self, ctx):
        nombre = ctx.ID().getText()

        cantidad = 0

        params_ctx = ctx.parametros()

        if params_ctx and params_ctx.parametro():
            cantidad = 1  # primer parámetro

            lista = params_ctx.listapar()
            while lista and lista.parametro():
                cantidad += 1
                lista = lista.listapar()

        self.tabla_funciones[nombre] = cantidad
        return None
    
    #Declaración de la función (se escribe el código de la función con su cuerpo)
    def visitDeclaracionFunc(self, ctx):
        
        self.hay_return = False
        nombre = ctx.ID().getText()
        self.archivo.write(f"{nombre}:\n")

        tRet = self.nuevoTemp()
        self.pila_retornos.append(tRet)

        # pop dirección de retorno
        self.archivo.write(f"pop {tRet}\n")

        # obtener parámetros
        params_ctx = ctx.parametros()

        if params_ctx and params_ctx.parametro():

            params = []

            # primer parámetro
            primer = params_ctx.parametro()
            params.append(primer.ID().getText())

            # resto de parámetros
            lista = params_ctx.listapar()
            while lista and lista.parametro():
                params.append(lista.parametro().ID().getText())
                lista = lista.listapar()

            # invertir por LIFO
            params.reverse()

            for p in params:
                self.archivo.write(f"pop {p}\n")

        # cuerpo
        self.visit(ctx.bloque())

        # retorno por defecto
        if not self.hay_return:
            self.archivo.write(f"push 0\n")
            self.archivo.write(f"jmp {tRet}\n")

        self.pila_retornos.pop()


    #El return se traduce a push del valor a retornar y un jmp al label de retorno de la función (que se guarda en una pila para soportar recursión)
    def visitIreturn(self, ctx):

        valor = self.visit(ctx.opal())

        tRet = self.pila_retornos[-1]

        self.archivo.write(f"push {valor}\n")
        self.archivo.write(f"jmp {tRet}\n")
        self.hay_return = True
    
    #Llamada de la función
    def visitLlamadaFunc(self, ctx):

        nombre = ctx.ID().getText()

        args = []

        if ctx.argumentos() and ctx.argumentos().argumento():
            arg_ctx = ctx.argumentos()

            args.append(self.visit(arg_ctx.argumento()))

            lista = arg_ctx.listaargumentos()
            while lista and lista.argumento():
                args.append(self.visit(lista.argumento()))
                lista = lista.listaargumentos()

        # push argumentos
        for arg in args:
            self.archivo.write(f"push {arg}\n")

        label_ret = self.get_label()

        # push dirección de retorno
        self.archivo.write(f"push {label_ret}\n")

        # salto a función
        self.archivo.write(f"jmp {nombre}\n")

        # label retorno
        self.archivo.write(f"{label_ret}:\n")

        temp = self.nuevoTemp()
        self.archivo.write(f"pop {temp}\n")

        return temp

    #Función para generar un temporal
    def nuevoTemp(self):
        temp = f"t{self.t_cont}"
        self.t_cont += 1
        return temp

    def close(self):
        self.archivo.close()