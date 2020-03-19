#!/usr/bin/env python
# coding: utf-8

import os.path, time
import pandas as pd

def last_modified(file):
    hora_creacion = time.ctime(os.path.getmtime(file))
    hora =  hora_creacion.split(" ")[3].split(":")[0]
    hora_actual =  int(time.localtime().tm_hour)
    corriendo =int(hora_actual) - int(hora)
    return corriendo


ESCOPETAZO = True
while ESCOPETAZO == True:
    #Intento abrir el txt, si no lo encuentra, no hace nada(porque puede ser que no exista hasta que termine "RELEVAMIENTO_EXCEL.PY",
    #Entonces obviamos esa Exception. Pero si encuentra OTRA Exception, vamos a frenar la ejecución y mostraremos cual es.
    try:
        #Vamos a leer el pkl ESCOPETAZO, para obtener el valor que contiene
        ESCOPETAZO = pickle.load(open("ESCOPETAZO.pkl", "rb"))
  #      print(type(ESCOPETAZO))
    except FileNotFoundError as FNF:
        pass

    except Exception as e:
        #Si el archivo no existe, y arroja otra excepción, de esta manera lo podemos manipular.
        print(e)
        raise
    
    if last_modified("temp_output.xlsx") >= 1:
        
        df_output = pd.read_excel("temp_output.xlsx")
        ultimo_output = df_output.iloc[-1][10]
        df_errores = pd.read_excel("temp_errores.xlsx")
        ultimo_errores = df_errores.iloc[-1][3]
        
        if ultimo_output > ultimo_errores:
            print("indice output es mayor")
            nuevo_indice = ultimo_output
            
        else:
            print("indice errores es mayor")
            nuevo_indice = ultimo_errores
            
        f = open("revivir.txt","wb")
        REVIVIR = f.read()
        REVIVIR = int(nuevo_indice)
        f.close()    
        
print("FINALIZO LA EJECUCIÓN DE reinicio.py")


