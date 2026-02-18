from antlr4.error.ErrorListener import ErrorListener

class MyErrorListener(ErrorListener):
    def __init__(self):
        super(MyErrorListener, self).__init__()
        self.errores = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        mensaje = msg.lower()
        tipo = "Error sintáctico genérico"

        #s Clasificación personalizada
        if "expecting ';'" in mensaje or "missing ';'" in mensaje:
            tipo = "Falta de punto y coma"
        elif "expecting '('" in mensaje or "missing '('" in mensaje:
            tipo = "Falta de apertura de paréntesis"
        elif "expecting ')'" in mensaje or "missing ')'" in mensaje:
            tipo = "Falta de apertura de paréntesis"
        elif "mismatched input" in mensaje and "expecting id" in mensaje:
            tipo = "Formato incorrecto en lista de declaración de variables"
        elif "no viable alternative" in mensaje:
            tipo = "Declaración mal formada, sintaxis incorrecta"
            

        error = f"[Sintáctico] Línea {line}:{column} - {tipo} ({msg})"
        self.errores.append(error)
        print(error)
