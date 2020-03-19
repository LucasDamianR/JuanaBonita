
# coding: utf-8

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
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
from sc_header import createDriver


fecha = datetime.date.today()

browser = createDriver()
browser.get('https://mx.zaful.com/')


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



LINKS = [i for i in links_aux if i[1] in ["Mujer","Hombre"]]


# In[46]:


LINKS[1][0] = LINKS[1][0].replace('?odr=hot','')


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
    
    for x in range(0,flag_pag):
        paginacion_total.append([LINK[0]+f'g_{x+1}.html' , LINK[1]])    




dfLinks = pd.DataFrame(data=paginacion_total,columns=['url','tipo'])



dfLinks.to_excel(f'/home/aa/cloudJ/JB/PRD/scrapper/Scripts/Mexico/Links_{fecha}.xlsx')




lista_proc = [['zaful-1','zaful',''],
     ['zaful-2','zaful',''],
     ['zaful-3','zaful',''],
     ['zaful-4','zaful',''],
     ['zaful-5','zaful','']
     ]


browser.quit()

import subprocess
start_time = datetime.datetime.today()
                                                                  
procesos = [subprocess.Popen(("/home/aa/miniconda3/bin/python", f"/home/aa/cloudJ/JB/PRD/scrapper/Scripts/Mexico/{proc[0]}.py")) for proc in lista_proc]

for proc, proceso in zip(lista_proc, procesos):
    proc[2] = "OK" if proceso.wait() == 0 else "ERROR"
    
end_time = datetime.datetime.today()

FINAL = '{}'.format(end_time - start_time)[:-4]
print(f'Tiempo Zaful_Mexico: {FINAL}')


