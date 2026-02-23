import os

class Optimizador:

    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.output_path = os.path.join(self.base_path, "output")

        self.archivo_entrada = os.path.join(self.output_path, "codigoIntermedio.txt")
        self.archivo_salida = os.path.join(self.output_path, "CodigoOptimizado.txt")

        self.bloques = []

    #GENERADOR DE BLOQUES
    def generar_bloques(self, lineas):
        self.bloques = []
        inicio = 0

        for i, linea in enumerate(lineas):
            partes = linea.split()

            if partes and (partes[0] == "jmp" or partes[0] == "if"):
                self.bloques.append((inicio, i))
                inicio = i + 1

            elif partes and partes[0].endswith(":") and i != 0:
                self.bloques.append((inicio, i - 1))
                inicio = i

        if inicio < len(lineas):
            self.bloques.append((inicio, len(lineas) - 1))

    #PROPAGACIÓN DE CONSTANTES Y FOLDING
    def optimizar_bloque(self, lineas, inicio, fin):
        constantes = {}

        for i in range(inicio, fin + 1):
            linea = lineas[i].strip()
            partes = linea.split()

            if not partes:
                continue

            #OPTIMIZACIÓN EN ASIGNACIONES
            if len(partes) >= 3 and partes[1] == "=":
                izquierda = partes[0]

                if izquierda in constantes:
                    del constantes[izquierda]

                # a = 3
                if len(partes) == 3 and partes[2].isdigit():
                    constantes[izquierda] = int(partes[2])
                    lineas[i] = f"{izquierda} = {partes[2]}\n"
                    continue

                # a = b
                if len(partes) == 3:
                    op = partes[2]
                    if op in constantes:
                        valor = constantes[op]
                        constantes[izquierda] = valor
                        lineas[i] = f"{izquierda} = {valor}\n"
                    continue

                # a = b op c
                if len(partes) == 5:
                    op1, operador, op2 = partes[2], partes[3], partes[4]

                    if op1 in constantes:
                        op1 = str(constantes[op1])
                    if op2 in constantes:
                        op2 = str(constantes[op2])

                    if op1.isdigit() and op2.isdigit():
                        resultado = eval(f"{op1} {operador} {op2}")
                        constantes[izquierda] = resultado
                        lineas[i] = f"{izquierda} = {resultado}\n"
                    else:
                        lineas[i] = f"{izquierda} = {op1} {operador} {op2}\n"

            #OPTIMIZACIÓN IF
            elif partes[0] == "if":
                condicion = partes[1]

                if condicion in constantes:
                    valor = constantes[condicion]

                    if valor == 0:
                        # nunca entra entonces elimina el codigo
                        lineas[i] = ""
                    else:
                        # siempre entra lo convertir en jmp directo
                        lineas[i] = f"jmp {partes[3]}\n"

                elif condicion == "false":
                    lineas[i] = ""

                elif condicion == "true":
                    lineas[i] = f"jmp {partes[3]}\n"

    #ELIMINAR CODIGO MUERTO (Se hace de atras para adelante)
    def eliminar_codigo_muerto(self, lineas, inicio, fin):

        vivas = set()

        for i in range(fin, inicio - 1, -1):
            linea = lineas[i].strip()
            partes = linea.split()

            if not partes:
                continue

            # Asignaciones
            if len(partes) >= 3 and partes[1] == "=":
                var = partes[0]

                if var not in vivas:
                    lineas[i] = ""
                else:
                    vivas.remove(var)

                    for token in partes[2:]:
                        if token.isidentifier():
                            vivas.add(token)

            # push usa variable
            elif partes[0] == "push":
                if partes[1].isidentifier():
                    vivas.add(partes[1])

            # if usa variable
            elif partes[0] == "if":
                if partes[1].isidentifier():
                    vivas.add(partes[1])

            # jmp t0 (usa variable)
            elif partes[0] == "jmp":
                if len(partes) > 1 and partes[1].isidentifier():
                    vivas.add(partes[1])
                    
    def eliminar_etiquetas_inutiles(self, lineas):

        etiquetas_definidas = set()
        etiquetas_usadas = set()

        # Buscar etiquetas definidas y usadas
        for linea in lineas:
            partes = linea.strip().split()

            if not partes:
                continue

            # Etiqueta definida
            if partes[0].endswith(":"):
                nombre = partes[0][:-1]
                etiquetas_definidas.add(nombre)

            # Etiqueta usada
            if partes[0] == "jmp":
                if len(partes) > 1 and not partes[1].isidentifier():
                    etiquetas_usadas.add(partes[1])

                elif len(partes) > 1:
                    etiquetas_usadas.add(partes[1])

            if partes[0] == "if":
                etiquetas_usadas.add(partes[3])

        # Eliminar etiquetas no usadas
        nuevas_lineas = []

        nuevas_lineas = []
        primera_etiqueta = None

        for linea in lineas:
            partes = linea.strip().split()

            if partes and partes[0].endswith(":"):
                nombre = partes[0][:-1]

                if primera_etiqueta is None:
                    primera_etiqueta = nombre
                    nuevas_lineas.append(linea)
                    continue

                if nombre not in etiquetas_usadas:
                    continue

            nuevas_lineas.append(linea)

        return nuevas_lineas

    # LIMPIA LINEAS QUE ESTÁN VACÍAS
    def limpiar_codigo(self, lineas):
        return [l for l in lineas if l.strip() != ""]

    #TODA LA OPTIMIZACIÓN JUNTA EN UNA FUNCION (Se usa en el App.py)
    def optimizar(self):

        if not os.path.exists(self.archivo_entrada):
            print("No se encontró codigoIntermedio.txt")
            return

        with open(self.archivo_entrada, "r", encoding="utf-8") as f:
            lineas = f.readlines()

        self.generar_bloques(lineas)

        # Optimizar cada bloque
        for inicio, fin in self.bloques:
            self.optimizar_bloque(lineas, inicio, fin)
        self.eliminar_codigo_muerto(lineas, 0, len(lineas) - 1)
        lineas = self.limpiar_codigo(lineas)
        lineas = self.eliminar_etiquetas_inutiles(lineas)

        with open(self.archivo_salida, "w", encoding="utf-8") as f:
            f.writelines(lineas)

        print("Optimización terminada.")
        print("Bloques:", self.bloques)
