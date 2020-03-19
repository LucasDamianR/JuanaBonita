
# coding: utf-8

# In[11]:


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
from sc_header import createDriver,aplanar_lista,extract_json_objects


# In[12]:


fecha = datetime.date.today()


# In[13]:


def scrape_url(pos_aux,url_aux):
    
    
    lista_auxiliar = []
    response = requests.get(url_aux)
    soup = BeautifulSoup(response.content, "html.parser")
    scripts = soup.find_all('script')
    try:
        tipologia = soup.find(class_='last').text
    except:
        tipologia = ''
    #verificar que siempre sea 38 de alguna forma.
    try:
        for result in extract_json_objects(scripts[38].text):
            pass
        try:
            color = soup.find(class_='value-field Color').text
        except:
            color ='SIN COLOR'
        
        for json_item in result['skus']:
            lista_auxiliar.append([pos_aux,
                                   result['productId'], #ID
                                   result['name'], # DESC
                                   json_item['sku'], #SKU
                                   json_item['dimensions']['Talla'], #TALLE
                                   color, #COLOR:
                                   json_item['image'], #IMG
                                   url_aux,
                                   tipologia,
                                   json_item['seller'], #seller
                                   json_item['availablequantity'], #cantidad
                                   json_item['bestPriceFormated'] if json_item['availablequantity'] > 0 else np.nan,
                                   json_item['listPriceFormated'] if json_item['availablequantity'] > 0 else np.nan
                                  ])

        return lista_auxiliar
    except:
        return [-1]
#PAGINA_SCRAPER

def scrape_batch(url_chunk):
    chunk_resp = []
    for url in url_chunk:
        chunk_resp.append(scrape_url(url[0],url[1]))
    return chunk_resp

def createDriver():
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument(f'user-agent={user_agent}')
    chrome_options.add_argument("--window-size=1625x2444")
    # options.headless = True
    return webdriver.Chrome(options = chrome_options)

def aplanar_lista(lista):
    if type(lista[0][0]) != list:
        return lista
    else:
        lista = list(itertools.chain(*lista))
        return aplanar_lista(lista)            


# In[14]:


url_mujer_ropa = 'https://mx.andrea.com/mujer/ropa'


# In[16]:


browser = createDriver()
browser.get('https://mx.andrea.com/mujer/ropa')


# In[17]:


TIMEOUT = 3
last_height = browser.execute_script("return document.body.scrollHeight;")
while True:

    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    try:
        #Click button
        WebDriverWait(browser, 50).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.load-more-category.button-lineal.secundario'))).click()
        
    except:
        pass
    time.sleep(TIMEOUT)
    new_height = browser.execute_script("return document.body.scrollHeight;")
    if new_height == last_height:
        break
    last_height = new_height


# In[18]:


urllist = []
aux_pos = 0
for img in browser.find_elements_by_class_name('contenedor-img'):
    try:
        aux_pos+=1
        urllist.append([aux_pos,img.find_element_by_tag_name('a').get_attribute('href')])
    except:
        pass


# In[19]:


batch_size = 5

url_chunks = [urllist[x:x+batch_size] for x in range(0, len(urllist), batch_size)]
items = []
for url_chunk in url_chunks:
    items.append(scrape_batch(url_chunk))


# In[20]:


new_list = aplanar_lista(items)


# In[ ]:


df = pd.DataFrame(new_list)


# In[21]:


#CUANDO NO ESTA DISPONIBLE, NO APARECE EL PRECIO, POR ESO HAY VALORES EN NAN DONDE DEBERÍA IR EL PRECIO.


# In[27]:


df.rename(columns={0:'pos',
                  1:'id_producto',
                  2:'descripcion',
                  3:'sku',
                  4:'talle',
                  5:'color',
                  6:'img',
                  7:'url',
                  8:'tipo',
                  9:'marca',
                  10:'stock',
                  11:'precio_dto',
                  12:'precio'
                  },inplace=True)


# In[28]:


#QUEREMOS EL DF CON LOS PRODUCTOS ESTAN DISPONIBLES
df = df[df['stock']!= 0]


# In[29]:


df["precio_dto"] = (df["precio_dto"]
                    .str.extract(r"([\d,\.]+)", expand=False)
                    .str.replace(",", "")
                    .astype(float))


# In[30]:


df["precio"] = (df["precio"]
                .str.extract(r"([\d,\.]+)", expand=False)
                .str.replace(",", "")
                .astype(float))


# In[72]:


#df['precio'] = df['precio'].fillna(0)
#df['precio_dto'] = df['precio_dto'].fillna(0)


# In[31]:


for index,row in df.iterrows():
    
    if row['precio'] == 0:
        
        df.loc[index,'precio'] = row['precio_dto']
        


# In[32]:


df['fecha_alta'] = datetime.date.today()


# In[33]:


df['origen'] = 'ANDREA'
df['marca'] = df['marca'].str.upper()
df['pagina_scraper'] = url_mujer_ropa
df['moneda'] = 'PESO MXN'
df['sexo'] = 'Mujer'

# In[ ]:


#USAMOS SIN STOCK


# In[45]:


df.loc[df['talle'] == 'ECH','talle'] = 'XS'
df.loc[df['talle'] == 'CH','talle'] = 'S'
df.loc[df['talle'] == 'G','talle'] = 'L'
df.loc[df['talle'] == 'EG','talle'] = 'XL'
df.loc[df['talle'] == 'EEG','talle'] = 'XXL'
df.loc[df['talle'] == 'EEEG','talle'] = 'XXXL'
df.loc[df['talle'] == '4EG','talle'] = 'XXXXL'
df.loc[df['talle'] == 'CH/M','talle'] = 'S/M'


# In[60]:


#df.to_excel(f'Andrea{fecha}.xlsx')
df.to_excel(f'/home/aa/cloudJ/JB/PRD/scrapper/Scripts/Mexico/Salida/andrea{fecha}.xlsx')
print(f'GUARDO EL EXCEL: Andrea{fecha}.xlsx')

# In[50]:


browser.quit()

