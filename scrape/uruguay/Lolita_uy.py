
# coding: utf-8

# In[2]:


from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support import expected_conditions
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
from ipywidgets import IntProgress
from IPython.display import display
from IPython.display import clear_output
import os
scraper = 'LOLITA'


# In[3]:


url = 'https://lolita.com.uy/vestimenta'


# In[4]:


start_ = datetime.datetime.now()
fecha = datetime.date.today()

user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'    

chrome_options = Options()  
chrome_options.add_argument("--headless")  
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--window-size=1825x1244")


browser = webdriver.Chrome('/usr/bin/chromedriver', options = chrome_options)


# In[5]:


browser.get(url)


# In[6]:


BLK = browser.find_element_by_class_name('blk')
if BLK.get_attribute('data-codigo') != 'categoria':
    raise "ERROR EN CATEGORÍA"


# In[7]:


LABELS = BLK.find_element_by_class_name('lst').find_elements_by_tag_name('label')


# In[8]:


CATEGORIAS = [[str(i.get_attribute('title')).upper(),i.get_attribute('data-val')] for i in LABELS]
                       
#ITERAR CATEGORIAS


# In[9]:


#browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")


# In[10]:


LISTA_PRODUCTOS = []

for CATEGORIA in CATEGORIAS:
    
    browser.get(CATEGORIA[1])
    last_height = browser.execute_script("return document.body.scrollHeight")
    while True:

        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            browser.execute_script('var elmnt = document.getElementById("catalogoPaginado");elmnt.scrollIntoView();')
            browser.find_element_by_id('catalogoPaginado').click()
        except:
            
            pass
        time.sleep(10.5)
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    ELEMENTO_PRODUCTOS = browser.find_element_by_xpath('//*[@id="catalogoProductos"]')

    PRODUCTOS = ELEMENTO_PRODUCTOS.find_elements_by_class_name('it')


    for item in PRODUCTOS:

        AUX_JPG = item.find_element_by_tag_name('a').find_elements_by_tag_name('img')[0].get_attribute('src')
        if AUX_JPG.find('.jpg') == -1:
            AUX_JPG = item.find_element_by_tag_name('a').find_elements_by_tag_name('img')[1].get_attribute('src')
        if AUX_JPG.find('.jpg') == -1:
            AUX_JPG = item.find_element_by_tag_name('a').find_elements_by_tag_name('img')[2].get_attribute('src')

        if AUX_JPG.find('.jpg') != -1:
            IMG = AUX_JPG

        ID = item.get_attribute('data-codprod')
        DESCRIPCION = item.text.split('\n')[0].split(' - ')[0]
        COLOR = item.text.split('\n')[0].split(' - ')[1]
        PRECIO = item.text.split('\n')[1]
        #PRECIO_DTO = item.find_element_by_class_name('descuentosMDP').text
        HREF = item.find_element_by_tag_name('a').get_attribute('href')
        browser.find_element_by_class_name('descuentosMDP').text

        LISTA_PRODUCTOS.append([ID,
                                DESCRIPCION,
                                COLOR,
                                PRECIO,
                                #PRECIO_DTO,
                                HREF,
                                IMG])


# In[11]:


end_ = datetime.datetime.now()


# In[20]:


df_lolita = pd.DataFrame(LISTA_PRODUCTOS)


# In[22]:


df_lolita.rename(columns={0:'codigo'},inplace=True)
df_lolita.rename(columns={1:'descripcion'},inplace=True)
df_lolita.rename(columns={2:'color'},inplace=True)
df_lolita.rename(columns={3:'precio'},inplace=True)
df_lolita.rename(columns={4:'url_producto'},inplace=True)
df_lolita.rename(columns={5:'img_producto'},inplace=True)


# In[23]:


df_lolita['fecha'] = fecha


# In[24]:


df_lolita['origen'] = 'LOLITA UY'
df_lolita['marca'] = 'LOLITA'


# In[25]:


browser.quit()

if len(df_lolita.drop_duplicates()) == len(df_lolita.dropna()) == len(df_lolita) == True:
    print(f'CIUDADO DUPLICADOS EN {scraper}')


# In[26]:


writer = ExcelWriter('/home/aa/cloudJ/JB/PRD/scrapper/Scripts/Uruguay/Salida/lolita'+str(fecha)+'.xlsx')
df_lolita.to_excel(writer,'Hoja1')
writer.save()


end_ = datetime.datetime.now()
print(f'Tiempo de ejecución {scraper}: {str(end_ - start_)[:-7]}')


#jupyter nbconvert --to script 'Lolita_uy.ipynb'

