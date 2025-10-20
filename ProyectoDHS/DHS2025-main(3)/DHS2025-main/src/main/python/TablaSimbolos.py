class Contexto:
    def __init__(self):
        self.simbolos = {}  # diccionario de símbolos

    def addSimbolo(self, id_obj):
        nombre = id_obj.getNombre()
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
        self.contexto = [Contexto()]  # lista de Contextos
        self.historial = []

    @classmethod
    def getTablaSimbolo(cls):
        if cls._instancia is None:
            cls._instancia = TS()
        return cls._instancia

    def addContexto(self):
        self.contexto.append(Contexto())

    def delContexto(self):
        if self.contexto:
            self.contexto.pop()

    def addSimbolo(self, id_obj):
        if not self.contexto:
            raise Exception("No hay contexto actual")
        self.contexto[-1].addSimbolo(id_obj)

    def buscarSimbolo(self, nombre):
        # Busca desde el contexto más interno hacia afuera
        for ctx in reversed(self.contexto):
            simbolo = ctx.buscarSimbolo(nombre)
            if simbolo:
                return simbolo
        return None

    def buscarSimboloContexto(self, nombre):
        if not self.contexto:
            return None
        return self.contexto[-1].buscarSimbolo(nombre)

    # def mostrarTabla(self):
    #     print("\n======= 🧠 TABLA DE SÍMBOLOS =======")

    #     if not self.contexto:
    #         print("⚠️  No hay contextos registrados.")
    #         return

    #     for i, ctx in enumerate(self.contexto):
    #         print(f"\n--- Contexto {i} ---")
    #         if ctx.simbolos:
    #             for nombre, simbolo in ctx.simbolos.items():
    #                 print(f"  {nombre:<15} -> {simbolo}")
    #         else:
    #             print("  (vacío)")

    #     print("====================================\n")
    
    def mostrarTabla(self):
        print("\n=== TABLA DE SÍMBOLOS ===")
        
        if not self.contexto:
            print("No hay contextos.")
            return

        for i, ctx in enumerate(self.contexto):
            nombre_ctx = "GLOBAL" if i == 0 else f"LOCAL {i}"
            print(f"\n-- Contexto {nombre_ctx} --")
            
            if not ctx.simbolos:
                print("  (vacío)")
                continue
                
            for nombre, simbolo in ctx.simbolos.items():
                tipo = simbolo.getTipoDato()
                inicializado = "Sí" if simbolo.inicializado else "No"
                usado = "Sí" if simbolo.usado else "No"
                
                # Si es función, mostrar argumentos
                args_str = ""
                if simbolo.__class__.__name__ == "Funcion":
                    args = simbolo.getListaArgs()
                    if args:
                        args_str = f", args=[{', '.join(arg.getNombre() for arg in args)}]"
                
                print(f"  {nombre}: {tipo} (init={inicializado}, usado={usado}{args_str})")
        
        print("\n=========================")