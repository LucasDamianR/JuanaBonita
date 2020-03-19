
# coding: utf-8

# In[66]:


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


# In[301]:


fecha = datetime.date.today()


# In[ ]:


url_base = 'https://cklass.shop/collections/ropa-dama'


# In[4]:


browser = createDriver()


# In[41]:


browser.get(url_base)


# In[43]:


urllist = []
max_page = int((WebDriverWait(browser,40).until(EC.presence_of_all_elements_located((By.CLASS_NAME,'page')))[-1]).text)
for i in range(max_page):
    pos = 0
    time.sleep(1)
    product_card = browser.find_elements_by_class_name('spf-product-card__image-wrapper')
    for item in product_card:
        pos+=1
        urllist.append([pos,
                         item.get_attribute('href'),
                         browser.current_url])
    try:
        WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CLASS_NAME,"next"))).click()
    except:
        print('NO SE PUDO CLICKEAR')


# In[177]:


def scrape_url(pos_aux,url_aux,pagina_aux):
    
    lista_auxiliar = []
    soup = BeautifulSoup(requests.get(url_aux).text,'html.parser')
    
    metadatos = soup.find_all('script',type='application/json')[1]
    metadatos = json.loads(metadatos.text)
    
    for data in metadatos['variants']:
        lista_auxiliar.append([pos_aux,
                               metadatos['id'],#ID
                               metadatos['title'], #DESCRIPCION
                               metadatos['published_at'], #FECHA DE LANZAMIENTO
                               metadatos['vendor'], #MARCA
#                               [i for i in metadatos['tags'] if i != 'oferta'], #DESPUES DE SCRAPEAR, VERIFICAR QUE SOLO TRAIGA UN ELEMENTO
                               data['title'], #talle)
                               data['sku'], #SKU
                               data['available'], #DISPO
                               [i.text.strip() for i in soup.find_all(class_='product-single__prices product-single__prices--policy-enabled')], #PRECIOS
                               soup.find_all('noscript')[-1].img['src'], #TEST
                               #[i.get('src') for i in soup.find_all('img') if i.get('src').find('1024x1024') != -1][0], #IMG
                               url_aux, #URL
                               pagina_aux, #PAGINA_SCRAPER
                              ])
    
    return lista_auxiliar    


#PAGINA_SCRAPER

def scrape_batch(url_chunk):
    chunk_resp = []
    for url in url_chunk:
        chunk_resp.append(scrape_url(url[0],url[1],url[2]))
    return chunk_resp



batch_size = 5

url_chunks = [urllist[x:x+batch_size] for x in range(0, len(urllist), batch_size)]
items = []
for url_chunk in url_chunks:
    items.append(scrape_batch(url_chunk))


# In[180]:


new_list = aplanar_lista(items)


# In[254]:


df = pd.DataFrame(new_list)


# In[255]:


df.rename(columns={0:'pos',
                  1:'id_producto',
                  2:'descripcion',
                  3:'publicacion',
                  4:'marca',
                  5:'talle',
                  6:'sku',
                  7:'disponible',
                  8:'precio_flag',
                  9:'img',
                  10:'url',
                  11:'pagina_scraper'},
         inplace=True)


# In[257]:


df['precio_flag'] = df['precio_flag'].apply(lambda x:x[0])


# In[275]:


#ESTA INVERTIDO EN LA PÁGINA, ENTONCES PRECIO_DTO > PRECIO (REAL)
df['precio'] = df['precio_flag'].apply(lambda x: x.split('\n            \n')[1])
df['precio_dto'] = df['precio_flag'].apply(lambda x: x.split('\n            \n')[0])


# In[276]:


df['precio'] = (df['precio']
                .str.extract(r"([\d,\.]+)", expand=False)
                .str.replace(",", "")
                .astype(float))


# In[277]:


df['precio_dto'] = (df['precio_dto']
                    .str.extract(r"([\d,\.]+)", expand=False)
                    .str.replace(",", "")
                    .astype(float))


# In[280]:


df['precio'] = np.where(df['precio_dto']>df['precio'],
                        df['precio_dto'],
                        df['precio'])


# In[286]:


df['tipo'] = df['descripcion'].apply(lambda x:x.split()[0])


# In[291]:


df.loc[df['talle']=='CHI','talle'] = 'S'
df.loc[df['talle']=='MED','talle'] = 'M'
df.loc[df['talle']=='GDE','talle'] = 'L'
df.loc[df['talle']=='EXG','talle'] = 'XL'


# In[294]:


df['moneda'] = 'PESO MXN'
df['origen'] = 'CKLASS'
df['sexo'] = 'Mujer'

# In[370]:


df['marca'] = df['marca'].str.upper()


# In[311]:


df['color'] = df['url'].apply(lambda x:x.split('/')[-1])


# In[352]:


df['color'] = df['color'].apply(lambda x:" ".join(re.findall(r"([^\d-]+)",x)))


# In[371]:


#df.to_excel(f'cklass{fecha}.xlsx')
df.to_excel(f'/home/aa/cloudJ/JB/PRD/scrapper/Scripts/Mexico/Salida/cklass{fecha}.xlsx')
print(f'GUARDO EL EXCEL cklass{fecha}.xlsx')
