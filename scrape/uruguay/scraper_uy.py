# coding: utf-8

import datetime
import os
import smtplib
import pyodbc
import pandas as pd
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

hoy = datetime.datetime.today().strftime("%Y/%m/%d")


def enviarResumen(file):
    
    # login
    user = 'lucasprueba2019@gmail.com'
    password = 'lucaslucas1'
    destinatario = 'lrojas@juanabonita.com'#,'pfstearns@juanabonita.com','adorronsoro@juanabonita.com','pcontreras@juanabonita.com'
    # Mensaje
    msg = MIMEMultipart()
    msg['Subject'] = '** RESUMEN SCRAPER URUGUAY**'
    part = MIMEText(" ")
    try:
                                    
        part = MIMEApplication(open(file ,"rb").read())
        part.add_header('Content-Disposition', 'attachment', filename= "Scraper_Corrida_"+str(fecha)+".txt")
    except:
        part = MIMEText("No se encontraron logs")
        
    msg.attach(part)
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    
    server.login(user,password)
    server.sendmail(user, destinatario, msg.as_string())
    server.quit()


fecha = datetime.datetime.today().strftime("_%d-%m-%Y")



lista_proc = [['Harrington_uy','Harrington',''],
     ['Sisi_uy','Sisi',''],
     ['Lolita_uy','Lolita',''],
     ['Indian_uy','Indian',''],
     ['Cocot_uy','Cocot','']
     ]



import subprocess
start_ = datetime.datetime.today()
                                                                                        
procesos = [subprocess.Popen(("/home/aa/miniconda3/bin/python", f"/home/aa/cloudJ/JB/PRD/scrapper/Scripts/Uruguay/{proc[0]}.py")) for proc in lista_proc]


for proc, proceso in zip(lista_proc, procesos):
    proc[2] = "OK" if proceso.wait() == 0 else "ERROR"
end_time = datetime.datetime.today()
FINAL = '{}'.format(end_time - start_)[:-4]



lista_inserts = [['Harrington_insert','Harrington',''],
                 ['Sisi_insert','Sisi',''],
                 ['Lolita_insert','Lolita',''],
                 ['Indian_insert','Indian',''],
                 ['Cocot_insert','Cocot',''],
                ]

start_ = datetime.datetime.today()
                                                                                        
procesos_inserts = [subprocess.Popen(("/home/aa/miniconda3/bin/python", f"/home/aa/cloudJ/JB/PRD/scrapper/Scripts/Uruguay/{proc[0]}.py")) for proc in lista_inserts]


for proc, proceso in zip(lista_inserts, procesos_inserts):
    proc[2] = "OK" if proceso.wait() == 0 else "ERROR"
end_time = datetime.datetime.today()
FINAL_INSERT = '{}'.format(end_time - start_)[:-4]



hora ='  {}'.format(datetime.datetime.now())[13:-7]
log=f"/home/aa/cloudJ/JB/PRD/scrapper/Scripts/Uruguay/Scraper_Corrida{fecha}.txt"
file = open(log, "w")
file.write("SCRAPER  | ESTADO" + os.linesep)
file.write("---------------------"+ os.linesep)
for item in lista_proc:
    file.write(str(item[1])+"...."+str(item[2]) + os.linesep)
file.write('Tarea programada web scrappers : '+FINAL + os.linesep)
file.write('Tarea programada inserts : '+FINAL_INSERT + os.linesep)

file.close()



enviarResumen(log)

