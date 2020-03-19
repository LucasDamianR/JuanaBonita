
# coding: utf-8

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
import os
from selenium.webdriver.support import expected_conditions
import itertools
from json import JSONDecoder
import math

def return_chunk(df,num):
    
    num = num-1
    BLOQUES = 5
    BLOQUE = math.ceil(len(df)/BLOQUES)
    split_df = lambda items, chunksize: [items[i:i+chunksize] for i in range(0, len(items), chunksize)]
    L = split_df(df,BLOQUE)
    
    return L[num]


def createDriver():
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument(f'user-agent={user_agent}')
    chrome_options.add_argument("--window-size=1325x1744")
    # options.headless = True
    return webdriver.Chrome('/usr/bin/chromedriver', options = chrome_options)


def aplanar_lista(lista):
    if type(lista[0][0]) != list:
        return lista
    else:
        lista = list(itertools.chain(*lista))
        return aplanar_lista(lista)

    
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
            

            
def zscrape_url(url_aux,precio_dto,precio,pos_aux,url_scraper):
    
    
    lista_auxiliar = []
    response = requests.get(url_aux)
    soup = BeautifulSoup(response.content, "html.parser")
    talles = [[i.text.strip(),i['data-sku']] for i in soup.find_all(class_='js-sizeItem')]
    
    try:
        aux_tipo = [i.span for i in soup.find_all(class_='path mt20 w')]
        aux_tipo = [i.text for i in aux_tipo[0].a.findNextSiblings()]
    except:
        lista_auxiliar.append([-1,
                               -1,
                               -1,
                               -1,
                               -1,
                               -1,
                               -1,
                               -1,
                               -1,
                               -1,
                               -1,
                               -1,
                               -1
                               ])
    
    
    for talle in talles:

        for i in soup.find_all(class_='big-color'):
            try:
                lista_auxiliar.append([pos_aux,
                                       talle[1],
                                       talle[0],
                                       i.a['title'],
                                       aux_tipo[0],
                                       aux_tipo[1],
                                       aux_tipo[-1].split('/')[0].strip(),
                                       aux_tipo[-1].split('/')[1].strip(),
                                       precio_dto,
                                       precio,
                                       i.a['href'],
                                       i.img['src'],
                                       url_scraper
                                      ])
            except:
                return url_aux
    return lista_auxiliar


def zscrape_batch(url_chunk,url_scrape):
    chunk_resp = []
    for url in url_chunk:
        chunk_resp.append(zscrape_url(url[0],url[1],url[2],url[3],url_scrape))
    return chunk_resp


############### para ilusion:

def iscrape_url(aux_tipologia,url_aux):
    
    lista_auxiliar = []
    try:
        
        soup = BeautifulSoup(requests.get(url_aux).text,'html.parser')
        scripts = soup.find_all('script')[28]
        #Defino una lista porque esta pagina transforma dos jsons de uno solo, entonces me voy a quedar solo con el primero [0]
        json_data = []
        for i in extract_json_objects(scripts.text):
            json_data.append(i)
        json_data = json_data[0]

        for m in json_data['attributes']['90']['options']:

            lista_auxiliar.append([json_data['productId'], #ID PRODUCTO
                                   m['label'], #COLOR
                                   soup.find(class_='base').text, #DESC
                                   aux_tipologia,
                                   soup.find(class_='price-wrapper ').text, #PRECIO AUX
                                   json_data['images'][m['products'][0]][0]['img'], #IMG)
                                   url_aux])
    
        return lista_auxiliar
    except:
        return [-1,-1,-1,-1,-1,-1,-1]

def iscrape_batch(url_chunk):
    chunk_resp = []
    for url in url_chunk:
        chunk_resp.append(iscrape_url(url[0],url[1]))
                     
    return chunk_resp

############fin ilusion

            