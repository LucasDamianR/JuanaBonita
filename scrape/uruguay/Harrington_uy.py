
# coding: utf-8

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

scraper='Harrington'
# In[2]:


start_ = datetime.datetime.now()
fecha = datetime.date.today()


user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'    

chrome_options = Options()  
chrome_options.add_argument("--headless")  
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--window-size=1325x744")
browser = webdriver.Chrome('/usr/bin/chromedriver', options = chrome_options)
url_base = 'https://www.harrington.com.uy/vestimenta'
browser.get(url_base)


# In[3]:


total = browser.find_element_by_xpath('//*[@id="central"]/div[3]/div/div[1]').text


# In[4]:


last_height = browser.execute_script("return document.body.scrollHeight")
while True:

    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(8)
    new_height = browser.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

page = BeautifulSoup(browser.page_source,"html.parser")


# In[5]:


ELEMENTO_PRODUCTOS = browser.find_element_by_xpath('//*[@id="catalogoProductos"]')


# In[6]:


PRODUCTOS = ELEMENTO_PRODUCTOS.find_elements_by_class_name('it')


# In[7]:


LISTA_PRODUCTOS = []
for item in PRODUCTOS:
    
    AUX_JPG = item.find_element_by_tag_name('a').find_elements_by_tag_name('img')[0].get_attribute('src')
    if AUX_JPG.find('.jpg') == -1:
        AUX_JPG = item.find_element_by_tag_name('a').find_elements_by_tag_name('img')[1].get_attribute('src')
    elif AUX_JPG.find('.jpg') == -1:
        AUX_JPG = item.find_element_by_tag_name('a').find_elements_by_tag_name('img')[2].get_attribute('src')
    
    if AUX_JPG.find('.jpg') != -1:
        IMG = AUX_JPG
            
    ID = item.get_attribute('data-codprod')
    DESCRIPCION = item.text.split('\n')[0].split(' - ')[0]
    COLOR = item.text.split('\n')[0].split(' - ')[1]
    PRECIO = item.text.split('\n')[1]
    HREF = item.find_element_by_tag_name('a').get_attribute('href')
    
    LISTA_PRODUCTOS.append([ID,
                            DESCRIPCION,
                            COLOR,
                            PRECIO,
                            HREF,
                            IMG])

df_harrington = pd.DataFrame(LISTA_PRODUCTOS)


# In[178]:


LISTA_PRODUCTOS[0]


# In[10]:


df_harrington = df_harrington.rename(columns={0: 'id Producto'})
df_harrington = df_harrington.rename(columns={1: 'Descripcion'})
df_harrington = df_harrington.rename(columns={2: 'Color'})
df_harrington = df_harrington.rename(columns={3: 'Precio'})
df_harrington = df_harrington.rename(columns={4: 'Url Producto'})
df_harrington = df_harrington.rename(columns={5: 'Url Imagen'})


# In[11]:


df_harrington["Fecha"] = str(fecha)
df_harrington["Marca"] = "Harrington"
df_harrington["Moneda"] = "PESO UY"
df_harrington['Sexo'] = 'Hombre'
df_harrington['Origen'] = "HARRINGTON UY"


# In[12]:


browser.quit()

if len(df_harrington.drop_duplicates()) == len(df_harrington.dropna()) == len(df_harrington) == True:
    print(f'CIUDADO DUPLICADOS EN {scraper}')


writer = ExcelWriter('/home/aa/cloudJ/JB/PRD/scrapper/Scripts/Uruguay/Salida/Harrington'+str(fecha)+'.xlsx')
df_harrington.to_excel(writer,'Hoja1')
writer.save()

end_ = datetime.datetime.now()

print(f'Tiempo de ejecución {scraper}: {str(end_ - start_)[:-7]}')
