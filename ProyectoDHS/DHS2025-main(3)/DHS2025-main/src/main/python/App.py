import sys
import os
from antlr4 import *
from compiladorLexer import compiladorLexer
from compiladorParser import compiladorParser

# Tus clases de lógica
from Escucha import Escucha  # Tu Listener actual
from MyErrorListener import MyErrorListener
from Walker import Walker    # El generador de TAC que creamos
from Optimizador import Optimizador
from TablaSimbolos import TS  # Tu clase singleton adaptada

def main(argv):
    # 1. Configuración de entrada
    archivo = "input/programa.txt"
    if len(argv) > 1:
        archivo = argv[1]
    
    if not os.path.exists(archivo):
        print(f"Error: El archivo {archivo} no existe.")
        return

    input_stream = FileStream(archivo)
    lexer = compiladorLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = compiladorParser(stream)
    
    # 2. Manejo de errores sintácticos (Punto 1 de la consigna)
    error_listener = MyErrorListener()
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)
    
    
    # 3. Ejecución del Parser y Listener Semántico
    # Aquí se puebla la Tabla de Símbolos y se verifican errores de contexto
    escucha = Escucha()
    parser.addParseListener(escucha)
    tree = parser.programa()
    
    # 4. Verificación de errores antes de continuar
    if error_listener.errores:
        print("\n=== ERRORES DETECTADOS ===")
        for e in error_listener.errores:
            print(f" -> {e}")
        print("\nGeneración de código cancelada por errores.\n")
        return 

    if escucha.errores_semanticos:
        errores_reales = [e for e in escucha.errores_semanticos if "for" not in e.lower()]
        if errores_reales:
            print("\n=== ERRORES SEMÁNTICOS DETECTADOS ===")
            for e in errores_reales:
                print(f" -> {e}")
            print("\nGeneración de código cancelada por errores semánticos.\n")
            return
    print("[2/3] Generando Código Intermedio (TAC)...")
    # El Walker recorre el árbol para traducir a tres direcciones
    walker = Walker()
    walker.visit(tree)
    # Asegúrate de que Walker cierre el archivo al terminar
    walker.close()

    print("[3/3] Ejecutando Optimizador...")
    # El optimizador toma la salida del Walker y la mejora
    opt = Optimizador()
    opt.optimizar()

    print("\n=== PROCESO FINALIZADO CON ÉXITO ===")
    print("Archivos generados en la carpeta /output:")
    #print(" - tabla_simbolos.txt")
    print(" - codigoIntermedio.txt")
    print(" - CodigoOptimizado.txt")
    TS.getTablaSimbolo().generarReporteTabla()

if __name__ == '__main__':
    main(sys.argv)


