import sys
from antlr4 import *
from compiladorLexer  import compiladorLexer

from Escucha import Escucha
from MyErrorListener import MyErrorListener

from compiladorParser import compiladorParser


def main(argv):
    archivo = "c:\\Users\\marti\\OneDrive\\Documentos\\GitHub\\DHS12\\ProyectoDHS\\DHS2025-main(3)\\DHS2025-main\\input\\programa.txt"
    if len(argv) > 1 :
        archivo = argv[1]
    input = FileStream(archivo)
    lexer = compiladorLexer(input)
    stream = CommonTokenStream(lexer)
    parser = compiladorParser(stream)
    
    error_listener = MyErrorListener()
    parser.removeErrorListeners()  # Elimina los listeners por defecto
    parser.addErrorListener(error_listener)  # Agrega el listener personalizado
    
    
    escucha = Escucha()
    parser.addParseListener(escucha)
    tree = parser.programa()
    
    if error_listener.errores:
        print("\n=== ERRORES SINTÁCTICOS DETECTADOS ===")
        for e in error_listener.errores:
            print(e)
        #print("\n Análisis semántico cancelado por errores sintácticos.\n")
        #return  #No sigue al análisis semántico
        
    #visitante = Caminante()
    #visitante.visitPrograma()
    
    print(escucha)
    #print(tree.toStringTree(recog=parser))

if __name__ == '__main__':
    main(sys.argv)