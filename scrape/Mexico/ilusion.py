
# coding: utf-8

# In[77]:



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
import os
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys

fecha = datetime.date.today()

# In[78]:


def createDriver():
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument(f'user-agent={user_agent}')
    chrome_options.add_argument("--window-size=1625x2444")
    # options.headless = True
    return webdriver.Chrome(options = chrome_options)


# In[79]:


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


# In[80]:


browser = createDriver()


# In[81]:


url_base = "https://www.ilusion.com/moda.html"


# In[82]:


browser.get(url_base)


# In[83]:


nav_categories = browser.find_element_by_class_name('toggle-nav-categories')
categorias = [[categories.text,categories.find_element_by_tag_name('a').get_attribute('href')] for categories in nav_categories.find_elements_by_tag_name('li') if categories.text not in ['Maternidad','Accesorios','Calzado']]
    
    


# In[84]:


new_categories = []
for categoria in categorias:
    try:
        browser.get(categoria[1])
    except:
        browser.quit()
        browser = createDriver()
        browser.get(categoria[1])
    
    try:
        nav_categories = browser.find_element_by_class_name('toggle-nav-categories')
        for categories in nav_categories.find_elements_by_tag_name('li'):
            if categories.text not in ['Maternidad','Accesorios','Calzado']:
                new_categories.append([categories.text,categories.find_element_by_tag_name('a').get_attribute('href')] )

    except:
        pass
    


# In[85]:



hrefs_list = []
for categoria in new_categories:
    
    try:
        browser.get(categoria[1])
    except:
        browser.quit()
        browser = createDriver()
        browser.get(categoria[1])
        
    
    while True:
        for hrefs in browser.find_elements_by_css_selector('.product.photo.product-item-photo.content-loader'):
            
            hrefs_list.append([categoria[0],
                              hrefs.get_attribute('href')])



        try:
            browser.find_element_by_css_selector('.item.pages-item-next').find_element_by_tag_name('a').click()
        except:
            break


browser.quit()


def x_scrape_url(aux_tipologia,url_aux):
    
    lista_auxiliar = []
        
    soup = BeautifulSoup(requests.get(url_aux).text,'html.parser')
    scripts = soup.find_all('script')[28]
    #Defino una lista porque esta pagina transforma dos jsons de uno solo, entonces me voy a quedar solo con el primero [0]
    json_data = []
    for i in extract_json_objects(scripts.text):
        json_data.append(i)
    json_data = json_data[0]
    try:
        for inx, m in enumerate(json_data['attributes']['90']['options']):
            try:
                img = json_data['images'][m['products'][0]][0]['img']
            except:
                try:
                    img = json_data['images'][list(json_data['images'].keys())[inx]][0]['img']
                except:
                    return [-1,-1,-1,-1,-1,-1,-1]
            try:
                lista_auxiliar.append([json_data['productId'], #ID PRODUCTO
                                       m['label'], #COLOR
                                       soup.find(class_='base').text, #DESC
                                       aux_tipologia,
                                       soup.find(class_='price-wrapper').text, #PRECIO AUX
                                       json_data['images'][list(json_data['images'].keys())[0]][0]['img'], #IMG)
                                       url_aux])
            except:
                return [-1,-1,-1,-1,-1,-1,-1]
    except:
        return [-1,-1,-1,-1,-1,-1,-1]
        
    return lista_auxiliar

def x_scrape_batch(url_chunk):
    chunk_resp = []
    for url in url_chunk:
        chunk_resp.append(x_scrape_url(url[0],url[1]))
                     
    return chunk_resp

def aplanar_lista(lista):
    if type(lista[0][0]) != list:
        return lista
    else:
        lista = list(itertools.chain(*lista))
        return aplanar_lista(lista)


# In[228]:


items = []

batch_size = 5
url_chunks = [hrefs_list[x:x+batch_size] for x in range(0, len(hrefs_list), batch_size)]


# In[229]:


start_ = datetime.datetime.now()
for url_chunk in url_chunks:
    items.append(x_scrape_batch(url_chunk))
end_ = datetime.datetime.now()


# In[ ]:


import itertools
new_list = aplanar_lista(items)


# In[233]:


new_list = [i for i in new_list if type(i) != int]


# In[235]:


df = pd.DataFrame(new_list)


# In[237]:


df.rename(columns={0:'id_producto',
                  1:'color',
                  2:'descripcion',
                  3:'tipo',
                  4:'precio',
                  5:'img',
                  6:'url'},
         inplace=True)


# In[238]:


df['precio'] = df['precio'].apply(lambda x: float(x.split('$')[1].strip()))


# In[239]:


df['precio_dto'] = df['precio']



df = df.drop_duplicates()
df.reset_index(drop=True,inplace=True)


# In[246]:


df['tipo_es'] = df['tipo']
df['color_es'] = df['color']
df['sexo'] = 'Mujer'
df['moneda'] = 'PESO MXN'
df['origen'] = 'ILUSION'
df['marca'] = 'ILUSION'

df.to_excel(f'/home/aa/cloudJ/JB/PRD/scrapper/Scripts/Mexico/Salida/ilusion{fecha}.xlsx')
print(f'GUARDO EL EXCEL ilusion{fecha}.xlsx')

