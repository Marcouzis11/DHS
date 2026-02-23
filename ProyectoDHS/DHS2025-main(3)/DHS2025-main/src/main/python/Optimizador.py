import os
import re

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
            
    #OPTIMIZACIÓN DE CADA BLOQUE (Propagación de constantes y simplificación de expresiones)
    def optimizar_bloque(self, lineas, inicio, fin):
        constantes = {}

        for i in range(inicio, fin + 1):
            linea = lineas[i].strip()
            partes = linea.split()

            if not partes:
                continue

            if len(partes) >= 3 and partes[1] == "=":
                izquierda = partes[0]

                if izquierda in constantes:
                    del constantes[izquierda]

                # a = 3
                if len(partes) == 3 and partes[2].lstrip('-').isdigit():
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

                    if op1.lstrip('-').isdigit() and op2.lstrip('-').isdigit():
                        try:
                            if operador == '==':
                                resultado = int(op1) == int(op2)
                            elif operador == '!=':
                                resultado = int(op1) != int(op2)
                            elif operador == '>':
                                resultado = int(op1) > int(op2)
                            elif operador == '<':
                                resultado = int(op1) < int(op2)
                            elif operador == '>=':
                                resultado = int(op1) >= int(op2)
                            elif operador == '<=':
                                resultado = int(op1) <= int(op2)
                            else:
                                resultado = eval(f"{op1} {operador} {op2}")
                            constantes[izquierda] = resultado
                            lineas[i] = f"{izquierda} = {resultado}\n"
                        except:
                            lineas[i] = f"{izquierda} = {op1} {operador} {op2}\n"
                    else:
                        lineas[i] = f"{izquierda} = {op1} {operador} {op2}\n"

            elif partes[0] == "if":
                condicion = partes[1]
                label_true = partes[3]

                valor = constantes.get(condicion, condicion)

                if valor is False or valor == 0 or valor == "False":
                    # Nunca entra: convertir en jmp al label falso (la línea siguiente)
                    lineas[i] = ""
                elif valor is True or (str(valor).lstrip('-').isdigit() and int(valor) != 0) or valor == "True":
                    # Siempre entra: convertir en jmp directo
                    lineas[i] = f"jmp {label_true}\n"
                    
    #ELIMINAR BLOQUES MUERTOS (Bloques que nunca se ejecutan porque no hay saltos a ellos, o porque su condición es siempre falsa)
    def eliminar_bloques_muertos(self, lineas):
        resultado = []
        i = 0
        while i < len(lineas):
            linea = lineas[i].strip()
            partes = linea.split()

            if partes and partes[0] == "jmp":
                resultado.append(lineas[i])
                i += 1
                bloque_muerto = []
                while i < len(lineas):
                    sig = lineas[i].strip()
                    sig_partes = sig.split()
                    if not sig_partes or sig_partes[0].endswith(":"):
                        break
                    bloque_muerto.append(lineas[i])
                    i += 1

                # Solo eliminar si todas las líneas son asignaciones a temporales
                solo_temporales = all(
                    re.match(r'^t\d+\s*=', b.strip()) or not b.strip()
                    for b in bloque_muerto
                )

                if not solo_temporales:
                    resultado.extend(bloque_muerto)
            else:
                resultado.append(lineas[i])
                i += 1
        return resultado
    

    #ELIMINAR CODIGO MUERTO (Se hace de atras para adelante)
    def eliminar_codigo_muerto(self, lineas, inicio, fin):
        # Primero recolectar TODAS las variables que se usan en cualquier lado
        usadas = set()
        for i in range(inicio, fin + 1):
            linea = lineas[i].strip()
            partes = linea.split()
            if not partes:
                continue
            if len(partes) >= 3 and partes[1] == "=":
                for token in partes[2:]:
                    if token.isidentifier():
                        usadas.add(token)
            elif partes[0] in ("push", "if", "jmp", "pop"):
                for token in partes[1:]:
                    if token.isidentifier():
                        usadas.add(token)

        # Luego eliminar solo temporales que nunca se usan
        for i in range(inicio, fin + 1):
            linea = lineas[i].strip()
            partes = linea.split()
            if not partes:
                continue
            if len(partes) >= 3 and partes[1] == "=":
                var = partes[0]
                if re.match(r'^t\d+$', var) and var not in usadas:
                    lineas[i] = ""
                    
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

            # Etiqueta usada en jmp
            if partes[0] == "jmp":
                if len(partes) > 1:
                    etiquetas_usadas.add(partes[1])

            # Etiqueta usada en if
            if partes[0] == "if":
                etiquetas_usadas.add(partes[3])

            # ← CAMBIO: Etiqueta usada en push (dirección de retorno)
            if partes[0] == "push":
                if len(partes) > 1 and re.match(r'^L\d+$', partes[1]):
                    etiquetas_usadas.add(partes[1])

        # Eliminar etiquetas no usadas
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

        # Optimizar cada bloque, primera pasada:
        for inicio, fin in self.bloques:
            self.optimizar_bloque(lineas, inicio, fin)
        lineas = self.limpiar_codigo(lineas)
        # Segunda pasada: regenerar bloques sobre código ya optimizado y eliminar muertos
        while True:
            antes = list(lineas)
            self.generar_bloques(lineas)
            for inicio, fin in self.bloques:
                self.optimizar_bloque(lineas, inicio, fin)
            self.eliminar_codigo_muerto(lineas, 0, len(lineas) - 1)
            lineas = self.limpiar_codigo(lineas)
            if lineas == antes:
                break
        lineas = self.eliminar_etiquetas_inutiles(lineas)

        with open(self.archivo_salida, "w", encoding="utf-8") as f:
            f.writelines(lineas)

        print("Optimización terminada.")
        print("Bloques:", self.bloques)
