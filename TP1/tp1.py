
diccionario_estaciones = {}

with open("/home/marc/Documentos/GitHub/DHS/TP1/Datos/registro_temperatura365d_smn.txt", encoding="latin-1") as file :
    for linea in file :
        partes = linea.strip()
        print(partes)
        
        if linea.startswith("-----") or linea.startswith("FECHA") or linea.strip() == "":
            continue
        
        fecha_str = linea[0:8].strip()
        tmax_str = linea[8:15].strip()
        tmin_str = linea[15:21].strip()
        nombre = linea[21:].strip()
            
        tmax = float(tmax_str) if tmax_str != "" else None
        tmin = float(tmin_str) if tmin_str != "" else None

        fecha = int(fecha_str)
        
        if nombre not in diccionario_estaciones:
            diccionario_estaciones[nombre] = {"tmax": [], "tmin": [], "fecha": []}
        
        diccionario_estaciones[nombre]["tmax"].append(tmax)
        diccionario_estaciones[nombre]["tmin"].append(tmin)
        diccionario_estaciones[nombre]["fecha"].append(fecha)
        
    for nombre, datos in diccionario_estaciones.items():
        print(f"Estación: {nombre}")
        print("Fechas:", datos["fecha"])
        print("Tmax:", datos["tmax"])
        print("Tmin:", datos["tmin"])
        print("-" * 40)  # separador
        
    print("DICCIONARIO CREADO CORRECTAMENTE \n")
    print("GENERANDO ARCHIVO CON CALCULOS \n")
    
    print(diccionario_estaciones["AEROPARQUE AERO"]["tmax"][-1])
    