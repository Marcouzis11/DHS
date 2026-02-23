class Contexto:
    def __init__(self):
        self.simbolos = {}  # diccionario de símbolos

    def addSimbolo(self, id_obj):
        # Usamos duck typing para obtener el nombre independientemente de la implementación de la clase ID
        nombre = id_obj.getNombre() if hasattr(id_obj, "getNombre") else getattr(id_obj, "nombre", None)
        if nombre in self.simbolos:
            raise Exception(f"Error: El símbolo '{nombre}' ya existe en este contexto")
        self.simbolos[nombre] = id_obj

    def buscarSimbolo(self, nombre):
        return self.simbolos.get(nombre)


class TS:
    _instancia = None

    def __init__(self):
        if TS._instancia is not None:
            raise Exception("TS es singleton, usa getTablaSimbolo()")
        self.contexto = [Contexto()]  # lista de Contextos (el primero es GLOBAL)
        self.historial = []           # Almacena contextos cerrados para el reporte final

    @classmethod
    def getTablaSimbolo(cls):
        if cls._instancia is None:
            cls._instancia = TS()
        return cls._instancia

    def addContexto(self):
        self.contexto.append(Contexto())

    def delContexto(self):
        if len(self.contexto) > 1:
            eliminado = self.contexto.pop()
            self.historial.append(eliminado)
        else:
            print("[TS] Intento de eliminar el contexto GLOBAL ignorado.")

    def addSimbolo(self, id_obj):
        if not self.contexto:
            raise Exception("No hay contexto actual")
        self.contexto[-1].addSimbolo(id_obj)

    def buscarSimbolo(self, nombre):
        # Busca desde el contexto más interno hacia afuera (Regla de Scope)
        for ctx in reversed(self.contexto):
            simbolo = ctx.buscarSimbolo(nombre)
            if simbolo:
                return simbolo
        return None

    def buscarSimboloContexto(self, nombre):
        if not self.contexto:
            return None
        return self.contexto[-1].buscarSimbolo(nombre)

    # --- NUEVA FUNCIÓN PARA EXPORTAR ARCHIVO REQUERIDO POR CONSIGNA ---
    def generarReporteTabla(self):
        """Genera el archivo output/tabla_de_simbolos.txt correctamente"""

        import os

        # Obtener directorio donde está este archivo .py
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Construir ruta absoluta segura
        carpeta_output = os.path.join(base_dir, "output")
        ruta_archivo = os.path.join(carpeta_output, "tabla_de_simbolos.txt")

        # Crear carpeta si no existe
        os.makedirs(carpeta_output, exist_ok=True)

        with open(ruta_archivo, "w", encoding="utf-8") as f:
            f.write("=== REPORTE DE TABLA DE SÍMBOLOS ===\n\n")

            todos_los_contextos = self.contexto + self.historial

            for i, ctx in enumerate(todos_los_contextos):
                nombre_ctx = "GLOBAL" if i == 0 else f"LOCAL {i}"
                f.write(f"-- Contexto {nombre_ctx} --\n")

                if ctx.simbolos:
                    f.write(f"{'Nombre':<15} | {'Tipo':<10} | {'Init':<6} | {'Usado':<6}\n")
                    f.write("-" * 50 + "\n")

                    for nombre, simbolo in ctx.simbolos.items():
                        tipo = getattr(simbolo, "tipo", "—")
                        if hasattr(simbolo, "getTipoDato"):
                            tipo = simbolo.getTipoDato()

                        ini = "Sí" if getattr(simbolo, "inicializado", False) else "No"
                        use = "Sí" if getattr(simbolo, "usado", False) else "No"

                        f.write(f"{nombre:<15} | {str(tipo):<10} | {ini:<6} | {use:<6}\n")
                else:
                    f.write("   (vacío)\n")

                f.write("\n")

        print(f"Reporte generado en: {ruta_archivo}")

    def obtenerTodosLosSimbolos(self):
        todos = []
        if hasattr(self, 'contexto') and self.contexto:
            for ctx in self.contexto:
                if hasattr(ctx, 'simbolos'):
                    todos.extend(ctx.simbolos.values())
        if hasattr(self, 'historial') and self.historial:
            for ctx in self.historial:
                if hasattr(ctx, 'simbolos'):
                    todos.extend(ctx.simbolos.values())
        return todos

    def mostrarTablaCompleta(self):
        # Mantiene tu función de consola original intacta
        print("\n=== TABLA DE SÍMBOLOS COMPLETA ===")
        todos_los_contextos = []
        if self.contexto: todos_los_contextos.extend(self.contexto)
        if self.historial: todos_los_contextos.extend(self.historial)

        if not todos_los_contextos:
            print("(No hay contextos registrados)")
            return

        for i, ctx in enumerate(todos_los_contextos):
            print("\n-- Contexto GLOBAL --" if i == 0 else f"\n-- Contexto LOCAL {i} --")
            if ctx.simbolos:
                for nombre, simbolo in ctx.simbolos.items():
                    tipo = simbolo.getTipoDato() if hasattr(simbolo, "getTipoDato") else "—"
                    ini = "Sí" if getattr(simbolo, "inicializado", False) else "No"
                    use = "Sí" if getattr(simbolo, "usado", False) else "No"
                    print(f"  {nombre}: {tipo} (init={ini}, usado={use})")
            else:
                print("  (vacío)")
        print("\n=========================\n")
