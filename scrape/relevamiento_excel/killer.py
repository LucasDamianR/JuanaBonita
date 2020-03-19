#!/usr/bin/env python
# coding: utf-8

import datetime
import subprocess
import os
import signal 
import pickle
start = datetime.datetime.today()
#Este booleano sirve para inicializar el While.
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

#Comando de consola que busca procesos en primer plano, devolviendo su descripción y el id.

#    print(ESCOPETAZO)
    cmd = 'powershell "gps | where {$_.MainWindowTitle } | select Description, id'
#abrimos la consola y ejecutamos CMD    
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    #Iteramos el resultado de la consola.
    for line in proc.stdout:
        #Como devuelve Bytes, lo codificamos a str. y buscamos el proceso 'Excel'.
        if line.decode(errors='ignore').find('Excel') != -1: # <-------------------- Linea (errors='ignore) agregada por jose 11/03/2020
            #Si lo encuentra significa que es el candidato a morir,
            #Entonces tomamos la linea y hacemos un split() para obtener el ultimo registro.
            #Lo hacemos porque un ejemplo de output puede ser:
            #'Microsoft Office Excel                                                3512'
            #Entonces nos aseguramos que [-1] Siempre va a ser el id si lo cortamos por espacios en blanco.
            candidato = line.decode().split()[-1]
            #Ejecuta la función kill de sistema operativo, con el id del candidato a matar, con la signal.SIGTERM.
            os.kill(int(candidato), signal.SIGTERM)
            
# Lienas agregadas por Jose el 12/03/2020 ↓↓↓
#Creo un .txt en la raiz del .py para corroborar el tiempo final de su ejecución 
end = datetime.datetime.today()
tiempo_final = end-start
file1 = open("end_killer","w")#write mode 
file1.write(f"Tiempo de ejecucion: {tiempo_final} \n") 
file1.close()

