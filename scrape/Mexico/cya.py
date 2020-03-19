
# coding: utf-8

# In[130]:


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
import time
import pyodbc
import os
import itertools
import json
import re
from json import JSONDecoder
from sc_header import createDriver,aplanar_lista,extract_json_objects


# In[131]:


fecha = datetime.date.today()


# In[132]:


def scrape_url(pos_aux,url_aux,tipo_aux,pagina_aux):
    
    soup = BeautifulSoup(requests.get(url_aux).text,'html.parser')
    
    lista_auxiliar = []
    lista_auxiliar.append([pos_aux,
                           soup.find(class_='editable').get('content'), #ID_PRODUCTO
                           soup.find('h1').text,#DESC
                           soup.find(class_='color_pick selected').get('title'), #COLOR
                           tipo_aux,
                           soup.find(class_='content_prices clearfix').text, #PRECIO TODO
                           soup.find('img',{'id':'bigpic'}).get('src'), #IMG
                           url_aux,
                           pagina_aux,
    ])
    
    return lista_auxiliar

#PAGINA_SCRAPER
def scrape_batch(url_chunk):
    chunk_resp = []
    for url in url_chunk:
        chunk_resp.append(scrape_url(url[0],url[1],url[2],url[3]))
                                    
    return chunk_resp


# In[133]:


url_base = 'https://www.cyamoda.com/dama'


# In[134]:


browser = createDriver()
for _ in range(10):
    try:
        browser.get(url_base)
        break
    except:
        browser.quit()
        time.sleep(1)
        browser = createDriver()
        


url_base = 'https://www.cyamoda.com/dama'


# In[134]:


browser = createDriver()
for _ in range(10):
    try:
        browser.get(url_base)
        break
    except:
        browser.quit()
        time.sleep(1)
        browser = createDriver()
        

all_hrefs = [i.get_attribute('href') for i in browser.find_elements_by_tag_name('a')]


all_hrefs = [hrefs for hrefs in all_hrefs if hrefs.find('dama-') != -1 and hrefs.find('caballero') == -1]
    
        

links = [hrefs for hrefs in all_hrefs if hrefs.find('accesorios') == -1 and hrefs.find('bolso') == -1 and hrefs.find('zapatos') == -1 and hrefs.find('manga-corta') == -1]

all_links = []
for LINK in links:
    browser.get(LINK)
    
    TIMEOUT = 3
    last_height = browser.execute_script("return document.body.scrollHeight;")
    while True:

        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(TIMEOUT)
        new_height = browser.execute_script("return document.body.scrollHeight;")
        if new_height == last_height:
            break
        last_height = new_height
    
    for indices, href in enumerate(browser.find_elements_by_css_selector('a.product_img_link')):
        all_links.append([indices+1,
                          href.get_attribute('href'),
                          LINK,
                          LINK.split('dama-')[1]
                         ])
        
browser.quit()


# In[141]:


batch_size = 5
url_chunks = [all_links[x:x+batch_size] for x in range(0, len(all_links), batch_size)]


# In[142]:


items = []
for url_chunk in url_chunks:
    items.append(scrape_batch(url_chunk))


# In[143]:


new_list = aplanar_lista(items)


# In[144]:


df = pd.DataFrame(new_list)


# In[146]:


df.rename(columns={0:'pos',
                  1:'id_producto',
                  2:'descripcion',
                  3:'color',
                  4:'tipo',
                  5:'PRECIO',
                  6:'img',
                  7:'url',
                  8:'pagina_scraper'},inplace=True)


# In[147]:


df['origen'] ='C&A'
df['moneda'] = 'PESO MXN'
df['marca'] = 'C&A'
df['fecha'] = fecha
df['sexo'] = 'Mujer'

# In[ ]:


df['PRECIO'].apply(lambda x:x.split('$'))


# In[149]:


df['precio'] = 0
df['precio_dto'] = 0
for index,row in df.iterrows():
    precio = row['PRECIO']
    if len(precio.split('$')) == 2:
        df.loc[index,'precio'] = precio.split('$')[1]
        df.loc[index,'precio_dto'] = precio.split('$')[1]
        
    elif len(precio.split('$')) == 3:
        df.loc[index,'precio'] = precio.split('$')[1]
        df.loc[index,'precio_dto'] = precio.split('$')[2]
        
        

df['tipo'] = df['tipo'].apply(lambda x:x.split('dama-')[1].replace('-',' '))



df = df.drop('PRECIO',axis=1)


df['precio'] = (df['precio']
                .str.extract(r"([\d,\.]+)", expand=False)
                .str.replace(",", "")
                .astype(float))


df['precio_dto'] = (df['precio_dto']
                    .str.extract(r"([\d,\.]+)", expand=False)
                    .str.replace(",", "")
                    .astype(float))



#df.to_excel(f'cya{fecha}.xlsx')
df.to_excel(f'/home/aa/cloudJ/JB/PRD/scrapper/Scripts/Mexico/Salida/cya{fecha}.xlsx')
print(f'GUARDO EL EXCEL cya{fecha}.xlsx')

