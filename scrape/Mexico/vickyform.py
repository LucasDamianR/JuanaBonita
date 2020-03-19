
# coding: utf-8

# In[325]:


from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import numpy as np
import requests
import datetime
from bs4 import BeautifulSoup
import pandas as pd
import pyodbc
import os
import re
import time
import itertools
from sc_header import createDriver,aplanar_lista,extract_json_objects
HOMBRE = 'BOXER N17'
fecha = datetime.date.today()


# In[2]:


urls = ['https://www.vickyform.com/bras',
        'https://www.vickyform.com/panties',
        'https://www.vickyform.com/trajes-de-bano/traje-de-bano',
        'https://www.vickyform.com/baby-dolls',
        'https://www.vickyform.com/shapers',
        'https://www.vickyform.com/pijamas']


# In[3]:


browser = createDriver()


# In[5]:


browser.get(urls[0])


# In[4]:


hrefs_list = []
for url in urls:
    try:
        browser.get(url)
    except:
        browser.quit()
        time.sleep(1)
        browser = createDriver()
        browser.get(url)
        
    last_height = browser.execute_script("return document.body.scrollHeight")
    while True:

        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(7)
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    
    productImages = browser.find_elements_by_class_name('productImage')
    
    for indice, image in enumerate(productImages):
        hrefs_list.append([indice+1,
                           image.get_attribute('href'),
                           url,
                           image.get_attribute('title')
                          ])
browser.quit()


# In[5]:


def scrape_url(pos_aux,url_aux,pagina_aux,desc_aux):    
    
    lista_auxiliar = []
    soup = BeautifulSoup(requests.get(url_aux).text,'html.parser')

    #CATEGORIA
    for i in soup.find_all(class_='bread-crumb'):
        categoria = "|".join([m.a.text for m in i.find_all('li')])
    
    scripts = soup.find_all('script')
    
    for skuJson in extract_json_objects(scripts[41].text):
        pass

    aux = []
    try:
        for val in skuJson['skus']:

            col = val['dimensions']['Color']
            if col not in aux:

                lista_auxiliar.append([pos_aux,
                                       soup.find(class_='codigo-produto col-xs-12').text, #ID PRODUCTO
                                       categoria, #TIPO
                                       col,#COLOR
                                       desc_aux, #DESCRIPCION
                                       val['seller'], #MARCA
                                       [i.text for i in soup.find_all(class_='price-box')],
                                       #soup.find(class_='skuBestPrice').text,#PRECIO_DTO
                                       val['image'], #IMG
                                       url_aux, #HREF
                                       pagina_aux
                                       ])
                aux.append(col)

        return lista_auxiliar 
    except:
        return [-1]

    
def scrape_batch(url_chunk):
    chunk_resp = []
    for url in url_chunk:
                                     
        chunk_resp.append(scrape_url(url[0],url[1],url[2],url[3]))
                                    
    return chunk_resp


# In[6]:


batch_size = 5
url_chunks = [hrefs_list[x:x+batch_size] for x in range(0, len(hrefs_list), batch_size)]
items = []


# In[7]:



for url_chunk in url_chunks:
    items.append(scrape_batch(url_chunk))


# In[40]:


new_list = aplanar_lista(items)


# In[316]:


df = pd.DataFrame(new_list)


# In[317]:


df.rename(columns={0:'pos',
                  1:'id_producto',
                  2:'categoria',
                  3:'color',
                  4:'descripcion',
                  5:'marca',
                  6:'PRECIO_AUX',
                  7:'img',
                  8:'url',
                  9:'pagina_scraper'},
         inplace=True)


# In[318]:


df['PRECIO_AUX'] = df['PRECIO_AUX'].apply(lambda x:x[0])

df['FLAG'] = df['PRECIO_AUX'].apply(lambda x:x.split('ou')[0])

df = df[df['FLAG'] != '']
df.reset_index(drop=True,inplace=True)



df['precio'] = df['FLAG'].apply(lambda x:re.findall(r'(?:^.*?\()?(\d+(?:\.\d+)?)',x)[0])
df['precio_dto'] = df['FLAG'].apply(lambda x:re.findall(r'(?:^.*?\()?(\d+(?:\.\d+)?)',x)[1])

df['precio'] = df['precio'].astype(float)
df['precio_dto'] = df['precio_dto'].astype(float)

df['precio'] = np.where(df['precio']==0,
                        df['precio_dto'],
                        df['precio'])

df.drop(['FLAG','PRECIO_AUX'],axis=1,inplace=True)

df['categoria'] = df['categoria'].apply(lambda x:x.replace('vickymx|',''))
df['categoria'] = df['categoria'].apply(lambda x : x.split('|')[1])

df['sexo'] = np.where(df['descripcion'].str.upper().str.contains(HOMBRE.upper()),
                      'HOMBRE',
                      'MUJER')


# In[322]:


df['tipo_es'] = df['categoria']
df.rename(columns={'categoria':'tipo'},inplace=True)
df['color_es'] = df['color']
df['moneda'] = 'PESO MXN'
df['origen'] = 'VICKY FORM'


# In[ ]:


#df.to_excel(f'vickyform{fecha}.xlsx')
df.to_excel(f'/home/aa/cloudJ/JB/PRD/scrapper/Scripts/Mexico/Salida/vickyform{fecha}.xlsx')
print(f'GUARDO EL EXCEL vickyform{fecha}.xlsx')

