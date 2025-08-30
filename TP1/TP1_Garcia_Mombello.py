from datetime import datetime, timedelta #Importo para poder poner las fechas que son INT en formato Fecha, es mas comodo para buscar un año hacia atras.


diccionario_estaciones = {}

with open("/home/marc/Documentos/GitHub/DHS/TP1/Datos/registro_temperatura365d_smn.txt", encoding="latin-1") as file :
    for linea in file :
        #partes = linea.strip()
        #print(partes)
        
        if linea.startswith("-----") or linea.startswith("FECHA") or linea.strip() == "":
            continue
        
        fecha_str = linea[0:8].strip()
        tmax_str = linea[8:15].strip()
        tmin_str = linea[15:21].strip()
        nombre = linea[21:].strip()
        fecha_dt = datetime.strptime(fecha_str, "%d%m%Y")
        
        tmax = float(tmax_str) if tmax_str != "" else None
        tmin = float(tmin_str) if tmin_str != "" else None

        fecha = fecha_dt
        
        if nombre not in diccionario_estaciones:
            diccionario_estaciones[nombre] = {"tmax": [], "tmin": [], "fecha": []}
        
        diccionario_estaciones[nombre]["tmax"].append(tmax)
        diccionario_estaciones[nombre]["tmin"].append(tmin)
        diccionario_estaciones[nombre]["fecha"].append(fecha)
    
    #En caso de que quiera ver el diccionario como se guardó descomentar
    """for nombre, datos in diccionario_estaciones.items():
        print(f"Estación: {nombre}")
        print("Fechas:", datos["fecha"])
        print("Tmax:", datos["tmax"])
        print("Tmin:", datos["tmin"])
        print("-" * 40)"""
        
    print("DICCIONARIO CREADO CORRECTAMENTE \n")
    print("GENERANDO ARCHIVO CON CALCULOS, ESPERE PORFAVOR, PUEDE TARDAR UNOS SEGUNDOS \n")
    
    
    #Calculo de la fecha más reciente un año atrás
    fecha_límite = diccionario_estaciones[nombre]["fecha"][0] - timedelta(days=365) #Cuenta exactamente 365 días atras, algunos meses tienen más días que otros.
    
    with open("reporteTemps.txt","w") as reporte :
        
        # MAX Y MINS POR ESTACION DE HASTA 1 AÑO ATRÁS
        reporte.write("### ESTACION ####### TMAX ####### TMIN ####### FECHA ### \n")
        for estacion in diccionario_estaciones :
            for i in range(len(diccionario_estaciones[estacion]["fecha"])) :
                fecha_actual = diccionario_estaciones[estacion]["fecha"][i]
                if(fecha_actual >= fecha_límite) :    
                    reporte.write(estacion + "\t\t" + 
                        str(diccionario_estaciones[estacion]["tmax"][i]) + "\t\t" +
                        str(diccionario_estaciones[estacion]["tmin"][i]) + "\t\t" +
                        str(diccionario_estaciones[estacion]["fecha"][i]) + "\n" 
                        )
        

        reporte.write("\n ESTACION CON MÁS AMPLITUD TÉRMICA POR CADA FECHA \n### FECHA ###### ESTACION ###### AMPLITUD ### TMAX ### TMIN \n")
        total_fechas = diccionario_estaciones[next(iter(diccionario_estaciones))]["fecha"]
        
        for fecha_actual in total_fechas:
            amp_max = 0
            for estacion, datos in diccionario_estaciones.items():
                if fecha_actual in datos["fecha"]:
                    j = datos["fecha"].index(fecha_actual)
                    if(datos["tmax"][j] is None or datos["tmin"][j] is None):
                        continue
                    tmax_calculo = datos["tmax"][j]
                    tmin_calculo = datos["tmin"][j]
                    amp_max_actual = tmax_calculo-tmin_calculo
                    if(amp_max_actual >= amp_max):
                        amp_max = amp_max_actual
                        estacion_max_amp = estacion
                        tmax_max_amp = tmax_calculo
                        tmin_max_amp = tmin_calculo
            reporte.write(
                "F: " + str(fecha_actual) + "\t" +
                "E: " + estacion_max_amp + "\t" +
                "AMP_MAX: " + str(amp_max) + "\t" +
                "T+: " + str(tmax_max_amp) + "\t" +
                "T-: " + str(tmin_max_amp) + "\t\n" 
            )
            
        reporte.write("\n ESTACION CON MENOS AMPLITUD TÉRMICA POR CADA FECHA \n### FECHA ###### ESTACION ###### AMPLITUD ### TMAX ### TMIN \n")
        
        for fecha_actual in total_fechas:
            amp_min = 1000000000
            for estacion, datos in diccionario_estaciones.items():
                if fecha_actual in datos["fecha"]:
                    j = datos["fecha"].index(fecha_actual)
                    if(datos["tmax"][j] is None or datos["tmin"][j] is None):
                        continue
                    tmax_calculo = datos["tmax"][j]
                    tmin_calculo = datos["tmin"][j]
                    amp_min_actual = tmax_calculo-tmin_calculo
                    if(amp_min_actual <= amp_min):
                        amp_min = amp_min_actual
                        estacion_min_amp = estacion
                        tmax_min_amp = tmax_calculo
                        tmin_min_amp = tmin_calculo
            reporte.write(
                "F: " + str(fecha_actual) + "\t" +
                "E: " + estacion_min_amp + "\t" +
                "AMP_MIN: " + str(amp_min) + "\t" +
                "T+: " + str(tmax_min_amp) + "\t" +
                "T-: " + str(tmin_min_amp) + "\t\n" 
            )
            
            
        reporte.write("\n MAYOR DIFERENCIA DE AMPLITUD TERMICA ENTRE 2 ESTACIONES POR CADA FECHA \n### FECHA ###### ESTACION-MAX ###### TMAX ###### ESTACION-MIN ###### TMIN ###### AMP_MAX \n")

        for fecha_actual in total_fechas:
            amp_max = 0
            temp_temp_max = 0
            temp_temp_min = 1000000
            for estacion, datos in diccionario_estaciones.items():
                if fecha_actual in datos["fecha"]:
                    j = datos["fecha"].index(fecha_actual)
                    if(datos["tmax"][j] is None or datos["tmin"][j] is None):
                        continue
                    if(datos["tmax"][j] >= temp_temp_max):
                        temp_temp_max = datos["tmax"][j]
                        estacion_temp_max = estacion
                    if(datos["tmin"][j] <= temp_temp_min):
                        temp_temp_min = datos["tmin"][j]
                        estacion_temp_min = estacion
                    amp_max_actual = temp_temp_max-temp_temp_min
                    if(amp_max_actual >= amp_max):
                        amp_max = amp_max_actual
            reporte.write(
                "F: " + str(fecha_actual) + "\t" +
                "ET+ : " + estacion_temp_max + "\t" +
                "T+ :" + str(temp_temp_max) + "\t" +
                "ET- :" + estacion_temp_min + "\t" +
                "T- :" + str(temp_temp_min) + "\t" +
                "AMP_MAX: " + str(amp_max) + "\t\n" 
            )
            
            
        reporte.write("\n MENOR DIFERENCIA DE AMPLITUD TERMICA ENTRE 2 ESTACIONES POR CADA FECHA \n### FECHA ###### ESTACION-MAX ###### TMAX ###### ESTACION-MIN ###### TMIN ###### AMP_MAX \n")

        for fecha_actual in total_fechas:
            amp_min = 1000000
            for estacion, datos in diccionario_estaciones.items():
                for estacion2, datos2 in diccionario_estaciones.items():
                    if estacion == estacion2:
                        continue
                    if fecha_actual in datos["fecha"] and fecha_actual in datos2["fecha"]:
                        j = datos["fecha"].index(fecha_actual)
                        k = datos2["fecha"].index(fecha_actual)
                        if(datos["tmax"][j] is None or datos["tmin"][j] is None or datos2["tmax"][k] is None or datos2["tmin"][k] is None):
                            continue
                        if (datos["tmax"][j] != datos2["tmin"][k] and datos["tmax"][j] > datos2["tmin"][k]):
                            amp_min_actual = datos["tmax"][j] - datos2["tmin"][k]
                        
                        if(amp_min_actual <= amp_min):
                            amp_min = amp_min_actual
                            estacion_temp_max = estacion
                            estacion_temp_min = estacion2
                            temp_temp_max = datos["tmax"][j]
                            temp_temp_min = datos2["tmin"][k]
            reporte.write(
                "F: " + str(fecha_actual) + "\t" +
                "ET+ : " + estacion_temp_max + "\t" +
                "T+ :" + str(temp_temp_max) + "\t" +
                "ET- :" + estacion_temp_min + "\t" +
                "T- :" + str(temp_temp_min) + "\t" +
                "AMP_MIN: " + str(amp_min) + "\t\n" 
            )
                    
