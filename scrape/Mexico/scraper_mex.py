
# coding: utf-8

import datetime
import os
import smtplib
import pyodbc
import pandas as pd
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import subprocess

hoy = datetime.datetime.today().strftime("%Y/%m/%d")
fecha = datetime.date.today()


def enviarMail():


    # login
    user = 'lucasprueba2019@gmail.com'
    password = 'lucaslucas1'
    aux_destinatarios = 'lrojas@juanabonita.com', 'jhernandez@juanabonita.com'
    # Mensaje
    msg = MIMEMultipart()
    fecha = datetime.date.today()
    msg['From'] = " Reportes Juana                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      ."
    msg['Subject'] = f'** SCRAPER MEXICO **'

    txt =f"/home/aa/cloudJ/JB/PRD/scrapper/Scripts/Mexico/resumen_{fecha}.txt"
    
    f = open (txt,'r')
    mensaje = f.read()
    f.close()

    part = MIMEText(mensaje)
    msg.attach(part)
    part = MIMEApplication(open(txt ,"rb").read())
    part.add_header('Content-Disposition', 'attachment', filename = f"resumen_{fecha}.txt")
    msg.attach(part)
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    server.login(user,password)
    server.sendmail(user, aux_destinatarios, msg.as_string())
    server.quit()

lista_proc = [['cya','C&A',''],
              ['andrea','Andrea',''],
              ['cklass','Cklass',''],
              ['foleys','Foleys',''],
              ['zara','Zara',''],
              ['fiorentina','Fiorentina',''],
              ['vickyform','Vicky Form',''],
              ['ilusion','Ilusion',''],
              ['zaful-mex','Zaful',''],
              ['ccep','Cuidado con el perro','']
             ]


start_ = datetime.datetime.today()

procesos = [subprocess.Popen(("/home/aa/miniconda3/bin/python", f"/home/aa/cloudJ/JB/PRD/scrapper/Scripts/Mexico/{proc[0]}.py")) for proc in lista_proc]



for proc, proceso in zip(lista_proc, procesos):
    proc[2] = "OK" if proceso.wait() == 0 else "ERROR"
end_time = datetime.datetime.today()
FINAL = '{}'.format(end_time - start_)[:-4]





hora ='  {}'.format(datetime.datetime.now())[13:-7]
file = open(f"/home/aa/cloudJ/JB/PRD/scrapper/Scripts/Mexico/resumen_{fecha}.txt", "w")

file.write("----------------------------"+ os.linesep)
for item in lista_proc:
    file.write(str(item[1])+"...."+str(item[2]) + os.linesep)
file.write(f'Tiempo: {FINAL} '+ os.linesep)
file.close()
print('*'*100)
print('SCRAPER MEX HAS FINISHED')


enviarMail()


