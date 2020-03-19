#!/usr/bin/env python
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
import re
from selenium.webdriver.common.action_chains import ActionChains
import os
from selenium.webdriver.support import expected_conditions
import json
import itertools
from json import JSONDecoder
def extract_json_objects(text, decoder=JSONDecoder()):
    
    """Find JSON objects in text, and yield the decoded JSON data

    Does not attempt to look for JSON arrays, text, or other JSON types outside
    of a parent JSON object. 

    """
    pos = 0
    while True:
        match = text.find('{', pos)
        if match == -1:
            break
        try:
            result, index = decoder.raw_decode(text[match:])
            yield result
            pos = match + index
        except ValueError:
            pos = match + 1
            


def createDriver():
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument(f'user-agent={user_agent}')
    chrome_options.add_argument("--window-size=1825x1844")
    # options.headless = True
    return webdriver.Chrome( options = chrome_options)


# In[ ]:


def agregar_links(url_aux,driver,lista,tipologia_aux,url_concat):
    
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
    


def scrape_url(errores,items,url_aux,pos_aux,url_scraper,aux_tipologia,aux_color):
    
    #lista_auxiliar = []
    url = url_aux
    for _ in range(5):
        try:
            txt = re.findall(r'productIntroData\s*:\s*({.*})', requests.get(url).text)
            txt = txt[0]
            break
        except:
            pass
    try:
        data = json.loads(txt)
    except:
        errores.append([url_aux,pos_aux,url_scraper,aux_tipologia,aux_color])
        return 

    #ID
    codigo = data['detail']['goods_sn']
    #DESCRIPCION
    descripcion = data['detail']['goods_url_name']
    #PRECIO 
    precio = data['detail']['retailPrice']['amount']
    #PRECIO CON DTO
    precio_dto = data['detail']['salePrice']['amount']
    #JPG
    jpg = data['detail']['original_img']

    for item in data['attrSizeList']:
        
        items.append([pos_aux,
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
                      url_scraper])
    #return lista_auxiliar

def scrape_batch(errores,items,url_chunk):
    #chunk_resp = []
    for indices,fila in url_chunk.iterrows():
        scrape_url(errores,items,fila['href'],fila['pos'],fila['url_scraper'],fila['tipo'],fila['color'])
                     
    #return chunk_resp

def aplanar_lista(lista):
    if type(lista[0][0]) != list:
        return lista
    else:
        lista = list(itertools.chain(*lista))
        return aplanar_lista(lista)

def check_length(serie):
    
    #if menor a 8 es porque hay un link donde el max es un numero que no es el id_producto
    ##caso especial : 'https://www.shein.com/skdress07191118781-p-929597-cat-2005.html?scici=homepage_164~~0_Banner_1_0_hotZone_w7bymbmsz~~3_2~~real_1991~~ccc_shein_pc_kids-homepage_default~~0~~50001'
    #
    return str(max([X for X in map(int,re.findall(r"([\d]+)",serie)) if len(str(X))<8]))
    
    
def aplanar(lista):
    try:
        if type(lista[0][0]) != list and lista[0][0] != []:
            return lista
        else:
            lista = list(itertools.chain(*lista))
            return aplanar_lista(lista)
    except:
        lista = [i for i in lista if i != []]
            
        return aplanar_lista(lista)
    