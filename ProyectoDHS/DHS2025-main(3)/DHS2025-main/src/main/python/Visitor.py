from compiladorVisitor import compiladorVisitor
from compiladorParser import compiladorParser
from TablaSimbolos import TablaSimbolos

class Visitor(compiladorVisitor):
    def __init__(self):
        self.ts = TablaSimbolos()
        self.errores = []

    def visitBloque(self, ctx):
        self.ts.addContexto()
        self.visitChildren(ctx)
        self.ts.delContexto()

    def visitDeclAsig(self, ctx):
        tipo = ctx.declaracion().getChild(0).getText()
        # Buscamos el ID en la regla declaracion
        for i in range(ctx.declaracion().getChildCount()):
            hijo = ctx.declaracion().getChild(i)
            if hasattr(hijo, 'getSymbol') and hijo.getSymbol().type == compiladoresParser.ID:
                nombre = hijo.getText()
                if self.ts.buscarLocal(nombre):
                    self.errores.append(f"Error: Variable '{nombre}' ya declarada.")
                else:
                    self.ts.addIdentificador(nombre, tipo)
        return self.visitChildren(ctx)

    def visitAsignacion(self, ctx):
        nombre = ctx.getChild(0).getText()
        if not self.ts.buscarGlobal(nombre):
            self.errores.append(f"Error: Variable '{nombre}' no declarada.")
        return self.visitChildren(ctx)