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


# In[3]:


def scrape_url(pos_aux,tipo_aux,url_aux,precio_aux,precio_dto_aux,pagina_aux):    
    
    lista_auxiliar = []
    soup = BeautifulSoup(requests.get(url_aux).text,'html.parser')
    try:
        color = soup.find(class_='_colorName').text
    except:
        return []
    
    id_producto = soup.find('html').get('id')
    lista_auxiliar.append([pos_aux,
                           id_producto, #ID PRODUCTO
                           tipo_aux,
                           color, #COLOR
                           soup.find('title').text.split('|')[0].strip(), #DESC
                           precio_aux,
                           precio_dto_aux,
                           soup.find(class_='_seoImg main-image').get('href'), #IMG
                           url_aux,#URL
                           pagina_aux,
    ])
    
    return lista_auxiliar    

#PAGINA_SCRAPER

def scrape_batch(url_chunk):
    chunk_resp = []
    for url in url_chunk:
        chunk_resp.append(scrape_url(url[0],url[1],url[4],url[3],url[2],url[5]))
                                    
    return chunk_resp


# In[4]:


url_links = [['https://www.zara.com/mx/es/mujer-prendas-exterior-l1184.html?v1=1445646','ABRIGO'],
             ['https://www.zara.com/mx/es/mujer-chaquetas-l1114.html?v1=1445720','CHAQUETA'],
             ['https://www.zara.com/mx/es/mujer-blazers-l1055.html?v1=1445747','BLAZER'],
             ['https://www.zara.com/mx/es/mujer-vestidos-l1066.html?v1=1445722','VESTIDO'],
             ['https://www.zara.com/mx/es/mujer-camisas-l1217.html?v1=1445723','CAMISA'],
             ['https://www.zara.com/mx/es/mujer-camisetas-l1362.html?v1=1445717','CAMISETA'],
             ['https://www.zara.com/mx/es/mujer-punto-l1152.html?v1=1445718','TEJIDO'],
             ['https://www.zara.com/mx/es/mujer-pantalones-l1335.html?v1=1445724','PANTALON'],
             ['https://www.zara.com/mx/es/mujer-jeans-l1119.html?v1=1445721','JEAN'],
             ['https://www.zara.com/mx/es/mujer-faldas-l1299.html?v1=1445719','FALDA'],
             ['https://www.zara.com/mx/es/mujer-sudaderas-l1320.html?v1=1445645','BUZO']
           ]
fecha = datetime.date.today()

urls = pd.DataFrame(url_links)



urls.rename(columns={0:'url',
                    1:'tipo'},
           inplace=True)


browser = createDriver()
hrefs_list = []
for index,row in urls.iterrows():
    try:
        browser.get(row['url'])
    except:
        browser.quit()
        time.sleep(1)
        browser = createDriver()
        continue
    
    ELEMENTS_A = browser.find_elements_by_css_selector('a.item._item')
                                                         
    soup = BeautifulSoup(browser.page_source,'html.parser')
    
    for indices, element in enumerate(ELEMENTS_A):
        
        for i in soup.find_all(class_='price _product-price'):
                try:
                    precio = i.find(class_='main-price').get('data-price')
                    precio_dto = precio
                except:
                    precio = i.find(class_='line-through').get('data-price')
                    precio_dto = i.find(class_='sale').get('data-price')

        hrefs_list.append([indices,row['tipo'],precio_dto,precio,element.get_attribute('href'),row['url']            
        ])
        



batch_size = 5
url_chunks = [hrefs_list[x:x+batch_size] for x in range(0, len(hrefs_list), batch_size)]
items = []


for url_chunk in url_chunks:
    items.append(scrape_batch(url_chunk))

new_list = aplanar_lista(items)





df = pd.DataFrame(new_list)

df.rename(columns={0:'pos',
                  1:'id_producto',
                  2:'tipo',
                  3:'color',
                  4:'descripcion',
                  5:'precio',
                  6:'precio_dto',
                  7:'img',
                  8:'url',
                  9:'pagina_scraper'},
          inplace=True
         )

df['marca'] ='ZARA'
df['tipo_es'] = df['tipo']
df['color_es'] = df['color']
df['sexo'] = 'Mujer'
df['moneda'] = 'PESO MXN'
df['origen'] = 'ZARA'


df['id_producto'] = df['id_producto'].apply(lambda x:x.split('-')[1])


df['precio'] = (df['precio']
                .str.extract(r"([\d,\.]+)", expand=False)
                .str.replace(".", "")
                .str.replace(",", ".")
                .astype(float))



df['precio_dto'] = (df['precio_dto']
                    .str.extract(r"([\d,\.]+)", expand=False)
                    .str.replace(".", "")
                    .str.replace(",", ".")
                    .astype(float))


#df.to_excel(f'zara{fecha}.xlsx')
df.to_excel(f'/home/aa/cloudJ/JB/PRD/scrapper/Scripts/Mexico/Salida/zara{fecha}.xlsx')
print(f'GUARDO EL EXCEL zara{fecha}.xlsx')

browser.quit()