from Contexto import Contexto



class TS:
    _instancia = None

    def __init__(self):
        if TS._instancia is not None:
            raise Exception("TS es singleton, usa getTablaSimbolo()")
        self.contexto = [Contexto()]  # lista de Contextos

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

    def mostrarTabla(self):
        print("\n======= 🧠 TABLA DE SÍMBOLOS =======")

        if not self.contexto:
            print("⚠️  No hay contextos registrados.")
            return

        for i, ctx in enumerate(self.contexto):
            print(f"\n--- Contexto {i} ---")
            if ctx.simbolos:
                for nombre, simbolo in ctx.simbolos.items():
                    print(f"  {nombre:<15} -> {simbolo}")
            else:
                print("  (vacío)")

        print("====================================\n")