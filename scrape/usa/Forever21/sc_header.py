
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
import asyncio
from selenium.webdriver.common.action_chains import ActionChains
import numpy as np
import pdb
#pdb.set_trace()
from ipywidgets import IntProgress
from IPython.display import display
import os
from selenium.webdriver.support import expected_conditions
from IPython.display import clear_output



def createDriver():
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument(f'user-agent={user_agent}')
    chrome_options.add_argument("--window-size=1825x1444")
    # options.headless = True
    return webdriver.Chrome(options = chrome_options)

def config_moneda(driver):
    #CERRAR EL MODAL

    try:
        botones_close = driver.find_elements_by_class_name('glClose')
    except:
        botones_close = []

    for close in botones_close:
        try:
            print('Cerrando modal')
            close.click()
        except:
            pass
    
    
    #CLICK EN LA PARTE SUPERIOR DERECHA, DONDE HAY UN MODAL DE CONFIGURACIÓN DE PAÍS / MONEDA
    driver.execute_script("document.getElementsByClassName('t_small pl_5 pb_5 pr_5 vm')[0].click();")
    #ASIGNAR DOLAR 
    driver.execute_script("document.getElementsByTagName('select')[1].value ='USD'")
    time.sleep(2)
    driver.find_element_by_class_name('glControls').find_element_by_tag_name('input').click()


#   #CLICK EN LA PARTE SUPERIOR DERECHA, DONDE HAY UN MODAL DE CONFIGURACIÓN DE PAÍS / MONEDA
#   driver.execute_script("document.getElementsByClassName('table sameline fr')[0].getElementsByTagName('span')[0].click();")
#   #ASIGNAR DOLAR 
#   driver.execute_script("document.getElementsByTagName('select')[1].value ='USD'")
#   time.sleep(2)
#   #CLICK EN EL BOTON DE GUARDAR 
#   driver.find_element_by_xpath('//*[@id="globale_csc_popup"]/div/div/div/div/div[3]/input').click()








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










