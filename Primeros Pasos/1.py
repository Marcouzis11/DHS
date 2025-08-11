for nro in list(range(0,10)):
    if nro == 5 :
        break
    print(nro)
    
print("Fin")

try :
    x = int(input("Ingrese entero: "))
    print(x)
except KeyboardInterrupt :
    print("Detenido")
except ValueError :
    print("No se puede convertir")
finally :
    print("Fin")