
# coding: utf-8

# In[1]:


from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import requests
from time import strftime
import datetime
import time
from pandas import ExcelWriter
import re
import pyodbc
from selenium.webdriver.common.action_chains import ActionChains
import numpy as np
import os
import json
from selenium.webdriver.support import expected_conditions
from sc_header import enviarMail,createDriver


# In[2]:


start_ = datetime.datetime.now()
fecha = datetime.date.today()
hoy = fecha.strftime('%Y/%m/%d')


# In[4]:


browser = createDriver()
browser.get("https://www.zaful.com/")            


# In[5]:


browser.execute_script('''
$('#js-changeCountry').mouseover();
document.getElementsByClassName('header-country-wrapper')[0].getElementsByTagName('a')[0].click();
document.getElementsByClassName('header-country-wrapper')[0].click();
document.querySelector("#js-changeCountry > div > div.header-country-wrapper > div > ul.hot-country-list > li:nth-child(1) > a").click();

document.getElementsByClassName('link-update-preferences logsss_event_cl')[0].click();

''')


# In[6]:


#LINKS 
links_aux = browser.execute_script('''
            var arr=[];
            var arn=[];
            var cant = document.getElementsByClassName('nav-item').length;

            for (i=0;i<cant;i++){

                arr.push(document.getElementsByClassName('nav-item')[i].getElementsByTagName('a')[0].getAttribute('href'));

                arn.push(document.getElementsByClassName('nav-item')[i].getElementsByTagName('a')[0].textContent);
            }

            function zip(a, b) {
                  var arr = [];
                  for (var key in a) arr.push([a[key], b[key]]);
                  return arr;
                }

            return zip(arr,arn);
            ''')


# In[8]:


LINKS = [i for i in links_aux if i[1] in ["Women","Men"]]


# In[9]:


paginacion = []
paginacion_total = []
for LINK in LINKS:
    
    browser.get(LINK[0])
    
    elementos_paginacion = browser.execute_script('''
                return document.getElementsByClassName('listspan')[0].getElementsByTagName('a');
                ''')
    paginacion_aux = []
    for page in elementos_paginacion:
        if page.text != "":
            try:
                pagina = int(page.get_attribute('data-page'))
                paginacion_aux.append(page)
            except:
                pass   
    # max page
    flag_pag = 0
    for i in paginacion_aux:
        if int(i.text) > flag_pag:
            flag_pag = int(i.text)
    
    for x in range(1,flag_pag):
        paginacion_total.append([LINK[0]+f'g_{x}.html' , LINK[1]])    


# In[10]:


browser.quit()


# In[11]:


dfLinks = pd.DataFrame(data=paginacion_total,columns=['url','tipo'])


# In[12]:


dfLinks[dfLinks['tipo'] == 'Women'].to_excel(f'Links_{fecha}.xlsx')


# In[ ]:


#ACA SCRIPT QUE LLAME A TODOS LOS SCRIPTS


# In[22]:


lista_proc = [['zaful-1','zaful_1',''],
     ['zaful-2','zaful_2',''],
     ['zaful-3','zaful_3',''],
     ['zaful-4','zaful_4',''],
     ['zaful-5','zaful_5',''],
     ['zaful-6','zaful_6','']
     ]




import subprocess
start_time = datetime.datetime.today()
                                                                  
procesos = [subprocess.Popen(("/home/aa/miniconda3/bin/python", f"/home/aa/cloudJ/JB/PRD/scrapper/Scripts/Usa/Zaful/{proc[0]}.py")) for proc in lista_proc]


for proc, proceso in zip(lista_proc, procesos):
    proc[2] = "OK" if proceso.wait() == 0 else "ERROR"
end_time = datetime.datetime.today()

FINAL = '{}'.format(end_time - start_time)[:-4]


dir_list = os.listdir()
versiones = 0
#iterar todos los elementos
for item_list in dir_list:
    #split nombre y extension
    nombre_base, extension = os.path.splitext(item_list)
    #Preguntar si el .txt es resumen_zaful
    if extension == '.txt' and nombre_base.split('_')[0] == 'resumen':
        versiones+=1

version = versiones+1



hora ='  {}'.format(datetime.datetime.now())[13:-7]
file = open(f"/home/aa/cloudJ/JB/PRD/scrapper/Scripts/Usa/Zaful/resumen_{fecha}.txt", "w")
file.write("----------------------------"+ os.linesep)
for item in lista_proc:
    file.write(str(item[1])+"...."+str(item[2]) + os.linesep)
file.write(f'Version: {version}' + os.linesep)
file.write(f'Tiempo: {FINAL} '+ os.linesep)
file.close()


enviarMail()


