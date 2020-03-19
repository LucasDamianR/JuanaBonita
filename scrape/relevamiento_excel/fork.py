import datetime
import subprocess
import os


fecha = datetime.date.today()
                
lista_proc = [['relevamiento_excel','Relevamiento excel',''],
              ['killer','Killer','']
             ]

start_ = datetime.datetime.today()


procesos = [subprocess.Popen(("C:/ProgramData/Anaconda3/python.exe", f"C:/Users/jhernandez/Practica_python/scriptRelevamiento/{proc[0]}.py")) for proc in lista_proc]
#procesos = [subprocess.Popen(("/home/aa/miniconda3/bin/python", f"/home/aa/cloudJ/JB/PRD/scrapper/Scripts/Mexico/{proc[0]}.py")) for proc in lista_proc]



for proc, proceso in zip(lista_proc, procesos):
    proc[2] = "OK" if proceso.wait() == 0 else "ERROR"
end_time = datetime.datetime.today()

FINAL = '{}'.format(end_time - start_)[:-4]

hora ='  {}'.format(datetime.datetime.now())[13:-7]
file = open(f"C:/Users/jhernandez/Practica_python/scriptRelevamiento/resumen_{fecha}.txt", "w")

print('TERMINE')

file.write("----------------------------"+ os.linesep)
for item in lista_proc:
    file.write(str(item[1])+"...."+str(item[2]) + os.linesep)
file.write(f'Tiempo: {FINAL} '+ os.linesep)
file.close()
