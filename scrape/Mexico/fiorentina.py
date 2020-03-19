
# coding: utf-8

# In[69]:


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
import time
import itertools
from sc_header import createDriver,aplanar_lista,extract_json_objects


# In[ ]:


fecha = datetime.date.today()


# In[95]:


urls = ['https://www.fiorentina.com.mx/pijamas-leisure.html',
        'https://www.fiorentina.com.mx/lenceria.html',
        'https://www.fiorentina.com.mx/ropa-deportiva.html']


# In[96]:


browser = createDriver()


# In[97]:


ex=[]
hrefs_list = []

for url in urls:
    try:
        browser.get(url)
    except:
        browser.quit()
        browser = createDriver()
        time.sleep(1)
        browser.get(url)
        ex.append(url)
    while True:
        for indice, item in enumerate(browser.find_elements_by_class_name('item')):
            
            hrefs_list.append([
                indice,
                item.find_element_by_tag_name('a').get_attribute('href'),
                browser.current_url
                ])
        try:
            browser.find_element_by_css_selector('.next.i-next').click()
        except:
            break
    


# In[107]:


df_urls  = pd.DataFrame(hrefs_list)


# In[109]:


df_urls.rename(columns = {0:'pos',
                          1:'href',
                          2:'pagina_scraper'},
              inplace = True)


# In[251]:


def scrape_url(pos_aux,url_aux,pagina_aux):    
    
    lista_auxiliar = []
    soup = BeautifulSoup(requests.get(url_aux).text,'html.parser')
    scripts = soup.find_all(type="text/javascript")
    
    for json_data in extract_json_objects(scripts[14].text):
        pass
    
    for aux_price in extract_json_objects(scripts[13].text):
        pass
    for categorie in extract_json_objects(scripts[5].text):
        pass

    for key, value in json_data['option_labels'].items():

        if value['configurable_product']['base_image'] != None:

            lista_auxiliar.append([pos_aux, #pos
                                   aux_price['productId'], #ID PRODUCTO
                                   categorie['ecommerce']['detail']['products']['category'], #CATEGORIA
                                   key,#COLOR
                                   categorie['ecommerce']['detail']['products']['name'].strip(), #DESCRIPCION
                                   aux_price['productOldPrice'], #PRECIO
                                   aux_price['productPrice'],#PRECIO_DTO
                                   value['configurable_product']['base_image'], #IMG
                                   url_aux, #HREF
                                   pagina_aux, #PAGINA_SCRAPER
                                  ])
    return lista_auxiliar 
#    except:
#        return [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
    
def scrape_batch(url_chunk):
    chunk_resp = []
    for url in url_chunk:
                                     
        chunk_resp.append(scrape_url(url[0],url[1],url[2]))
                                    
    return chunk_resp


# In[252]:


batch_size = 5
url_chunks = [hrefs_list[x:x+batch_size] for x in range(0, len(hrefs_list), batch_size)]
items = []

for url_chunk in url_chunks:
    items.append(scrape_batch(url_chunk))


# In[254]:


new_list = aplanar_lista(items)


# In[258]:


df = pd.DataFrame(new_list)


# In[265]:


df.rename(columns={0:'pos',
                   1:'id_producto',
                   2:'tipo',
                   3:'color',
                   4:'descripcion',
                   5:'precio',
                   6:'precio_dto',
                   7:'img',
                   8:'url',
                   9:'pagina_scraper'
                   },
         inplace=True)


# In[277]:


df['tipo'] = df['tipo'].apply(lambda x:x.replace('REBAJAS: ÚLTIMOS DÍAS|','').replace('NUEVAS COLECCIONES|','').replace('ÚLTIMOS DÍAS DE REBAJAS|',''))
                        

# In[292]:


df = df[~df['tipo'].str.contains('Accesorios')]


# In[295]:


df.reset_index(drop=True,inplace=True)


# In[ ]:


df['marca'] ='FIORENTINA'
df['tipo_es'] = df['tipo']
df['color_es'] = df['color']
df['sexo'] = 'Mujer'
df['moneda'] = 'PESO MXN'
df['origen'] = 'FIORENTINA'


# In[311]:


df['precio'] = df['precio'].astype(float)


# In[312]:


df['precio_dto'] = df['precio_dto'].astype(float)


# In[313]:


#df.to_excel(f'fiorentina{fecha}.xlsx')
df.to_excel(f'/home/aa/cloudJ/JB/PRD/scrapper/Scripts/Mexico/Salida/fiorentina{fecha}.xlsx')
print(f'GUARDO EL EXCEL fiorentina{fecha}.xlsx')
