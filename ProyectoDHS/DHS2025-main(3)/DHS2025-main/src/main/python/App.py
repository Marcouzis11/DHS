import sys
from antlr4 import *
from compiladorLexer  import compiladorLexer

from Escucha import Escucha

from compiladorParser import compiladorParser


def main(argv):
    archivo = "input/programa.txt"
    if len(argv) > 1 :
        archivo = argv[1]
    input = FileStream(archivo)
    lexer = compiladorLexer(input)
    stream = CommonTokenStream(lexer)
    parser = compiladorParser(stream)
    escucha = Escucha()
    parser.addParseListener(escucha)
    tree = parser.programa()
    #visitante = Caminante()
    #visitante.visitPrograma()
    print(escucha)
    #print(tree.toStringTree(recog=parser))

if __name__ == '__main__':
    main(sys.argv)