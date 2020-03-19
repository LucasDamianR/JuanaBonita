
# coding: utf-8

# In[1]:

import json
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
import asyncio
from selenium.webdriver.common.action_chains import ActionChains
import numpy as np
import pdb
from ipywidgets import IntProgress
from IPython.display import display
import os
from selenium.webdriver.support import expected_conditions
from IPython.display import clear_output
import itertools

def test()
    return json.loads()

def createDriver():
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument(f'user-agent={user_agent}')
    chrome_options.add_argument("--window-size=1325x1744")
    # options.headless = True
    return webdriver.Chrome('/usr/bin/chromedriver', options = chrome_options)

def agregarLinks(url_aux,driver,lista,tipologia_aux,url_concat):
    
    driver.get(url_aux)
    
    #busco la barra lateral
    aside_bar = driver.execute_script('''
    var x = document.getElementsByClassName('list-line-decorate j-attr-filter');
    return x;''')
    #busco de la barra lateral, el que tenga como header "COLOR"
    for i ,valor in enumerate(aside_bar):
        if valor.find_element_by_tag_name('li').text.upper() == 'COLOR':
            #guardo la posicion del item que se llama "color"
            elemento = i
    #Busco la cantidad de elementos del item en la posicion "elemento". que contiene la posicion
    #del item "COLOR", para sacar la cantidad de colores que tiene la tabla
    cantidad = driver.execute_script(f'''
    var x = document.getElementsByClassName('list-line-decorate j-attr-filter')[{elemento}].getElementsByClassName('j-auto-attrlink').length;
    return x''')
    #loop para sacar el href y el nombre de cada color, y se agrega a la lista, y luego se devuelve
    for c in range(cantidad):

        href_aux = driver.execute_script(f'''
        var x = document.getElementsByClassName('list-line-decorate j-attr-filter')[{elemento}].getElementsByClassName('j-auto-attrlink')[{c}].getAttribute('href');
        return x;
        ''')

        nombre_aux = driver.execute_script(f'''
        var x = document.getElementsByClassName('list-line-decorate j-attr-filter')[{elemento}].getElementsByClassName('j-auto-attrlink')[{c}].textContent;
        return x''')

        lista.append([tipologia_aux,
                     nombre_aux.strip(),
                     url_concat+href_aux])
    return lista
    

def scrape_url(url_aux,pos_aux,url_scraper,aux_tipologia,aux_color,aux_flag):
    
    
    lista_auxiliar = []
    url = url_aux
    while True:
        try:
            txt = re.findall(r'goodsInfo\s*:\s*({.*})', requests.get(url).text)[0]
            break
        except:
            pass

    data = json.loads(txt)

    #DESCRIPCION
    descripcion = (data['detail']['goods_name'])
    #PRECIO 

    precio = data['price']['info']['price'][aux_flag]['retailPrice']['amount']
    #PRECIO CON DTO
    precio_dto = data['price']['info']['price'][aux_flag]['salePrice']['amount']    
    #ID
    codigo = data['localSize']['skc']
    #JPG
    jpg = data['goods_imgs']['main_image']['origin_image']

    for item in data['attrSize']:

        lista_auxiliar.append([pos_aux,
                            aux_tipologia,
                            aux_color,
                            codigo,
                            descripcion,
                            item['attr_value_en'],
                            item['stock'],
                            precio,
                            precio_dto,
                            jpg,
                            url_aux,
                            url_scraper
                            ])
    return lista_auxiliar

def scrape_batch(url_chunk):
    chunk_resp = []
    for indices,fila in url_chunk.iterrows():
        chunk_resp.append(scrape_url(fila['href'],fila['pos'],fila['url_scraper'],fila['tipo'],fila['color'],fila['auxi']))
                     
    return chunk_resp


def aplanar_lista(lista):
    if type(lista[0][0]) != list:
        return lista
    else:
        lista = list(itertools.chain(*lista))
        return aplanar_lista(lista)
