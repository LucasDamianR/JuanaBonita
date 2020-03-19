
# coding: utf-8

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


# In[2]:


url_base = 'https://www.foleys.com.mx/mujer/ver-todo/'
fecha = datetime.date.today()


# In[3]:


browser = createDriver()
browser.get(url_base)


# In[4]:


TIMEOUT = 3
last_height = browser.execute_script("return document.body.scrollHeight;")
while True:

    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(TIMEOUT)
    new_height = browser.execute_script("return document.body.scrollHeight;")
    if new_height == last_height:
        break
    last_height = new_height
try:
    browser.find_element_by_class_name('mc-closeModal').click()
except:
    pass


# In[5]:


productos = browser.find_elements_by_class_name('prolabel-wrapper')


# In[259]:


urllist = [[indice+1, producto.find_element_by_tag_name('a').get_attribute('href')] for indice, producto in enumerate(productos)]


# In[ ]:


browser.execute_script('window.scrollTo(0,200)')


# In[257]:


def scrape_url(pos_aux,url_aux):
    
    lista_auxiliar = []
    soup = BeautifulSoup(requests.get(url_aux).text,'html.parser')
    scripts = soup.find_all('script',type='text/javascript')

    for item in extract_json_objects(scripts[73].text):
        pass

    descripcion = soup.find('h1',class_='texto-centrado').text
    id_producto = soup.find('p',class_='text-center-414 text-center-414-landscape').text.split(':')[1].strip() #ID_PRODUCTO
    marca = soup.find('h4').text.strip() #MARCA
    color_auxiliar = soup.find(class_='product-description').text #COLOR (BUSCARLO)
    soup.find(class_='cloud-zoom').img.get('src') #IMG
    lista_auxiliar.append([pos_aux,
                           id_producto, #ID_PRODUCTO
                           item['productPrice'],
                           item['productOldPrice'],
                           descripcion, #DESCRIPCION
                           marca, #MARCA
                           color_auxiliar, #COLOR (BUSCARLO)
                           soup.find(class_='cloud-zoom').img.get('src'), #IMG
                           url_aux, #href
                          ])
    return lista_auxiliar

#PAGINA_SCRAPER
def scrape_batch(url_chunk):
    chunk_resp = []
    for url in url_chunk:
        chunk_resp.append(scrape_url(url[0],url[1]))
    return chunk_resp


# In[260]:


batch_size = 5

url_chunks = [urllist[x:x+batch_size] for x in range(0, len(urllist), batch_size)]
items = []
for url_chunk in url_chunks:
    try:
        items.append(scrape_batch(url_chunk))
    except:
        pass



new_list = aplanar_lista(items)


# In[263]:


df = pd.DataFrame(new_list)


# In[271]:


df.rename(columns={0:'pos',
                   1:'id_producto',
                   2:'precio_dto',
                   3:'precio',
                   4:'descripcion',
                   5:'marca',
                   6:'TIPOCOLOR',
                   7:'img',
                   8:'url'
                   
                   
                  },
         inplace = True)


# In[324]:


df['tipo'] = df['descripcion'].apply(lambda x:x.split()[0])
df.loc[df['tipo']=='Skinny','tipo'] = 'JEAN'


# In[272]:


df['pagina_scraper'] = url_base
df['origen'] = 'FOLEYS'
df['moneda'] = 'PESOS MXN'
df['sexo'] = 'Mujer'

# In[274]:


browser.quit()


# In[474]:


def find_color(serie):
    
    if serie.find(' color ') != -1:
        return serie.split(' color ')[1].split()[0].replace(',','').replace('.','')
    else:
        return serie.split()[1].replace(',','').replace('.','')

    


# In[475]:


df['COL_AUX'] = df['TIPOCOLOR'].apply(find_color)


# In[488]:


for index,row in df.iterrows():
    
    if row['COL_AUX'] =='con':
        if row['TIPOCOLOR'].upper().find('ESTAMPADO') != -1:
            df.loc[index,'COL_AUX'] ='ESTAMPADO'
        elif row['TIPOCOLOR'].upper().find('LÍNEAS') !=-1:
            df.loc[index,'COL_AUX'] ='RAYADO'
        elif row['descripcion'].upper().find('NEGROS') !=-1:
            df.loc[index,'COL_AUX'] ='NEGRO'
            
    
    if row['COL_AUX'] == 'colo':
        if row['TIPOCOLOR'].upper().find('PLATA') != -1:
            df.loc[index,'COL_AUX'] ='PLATA'
            
    if row['COL_AUX'] == 'off':
        if row['TIPOCOLOR'].upper().find('FLOREADA') != -1:
            df.loc[index,'COL_AUX'] ='EST. FLORES'
    
    if row['COL_AUX'] =='corte':
        if row['TIPOCOLOR'].upper().find('ESTAMPADO') != -1:
            df.loc[index,'COL_AUX'] ='ESTAMPADO'
        elif row['TIPOCOLOR'].upper().find('MULTICOLOR') != -1:
            df.loc[index,'COL_AUX'] ='MULTICOLOR'
        elif row['descripcion'].upper().find('NEGROS') != -1 or row['descripcion'].upper().find('NEGRA') != -1  :
            df.loc[index,'COL_AUX'] ='NEGRO'
        elif row['descripcion'].upper().find('AZULES') != -1:
            df.loc[index,'COL_AUX'] ='AZUL'
        elif row['descripcion'].upper().find('MULTICOLOR') != -1:
            df.loc[index,'COL_AUX'] ='MULTICOLOR'
            
    if row['COL_AUX'] =='larga':
        df.loc[index,'COL_AUX'] = 'multicolor'
    
    if row['COL_AUX'] == 'recto':
        if row['TIPOCOLOR'].upper().find('ESTAMPADO') != -1:
            df.loc[index,'COL_AUX'] ='ESTAMPADO'
        elif row['TIPOCOLOR'].upper().find('AZUL') != -1:
            df.loc[index,'COL_AUX'] ='AZUL'
        
    if row['COL_AUX'] == 'camisero':
        if row['descripcion'].upper().find('ESTAMPADO DE FLORES') != -1:
            df.loc[index,'COL_AUX'] ='EST. FLORES'
            
    if row['COL_AUX'] =='corto':
        if row['descripcion'].upper().find('ESTAMPADO FLORAL') != -1 or row['descripcion'].upper().find('ESTAMPADO DE FLORES') != -1:
            df.loc[index,'COL_AUX'] ='EST. FLORES'
        elif row['descripcion'].upper().find('MULTICOLOR') != -1 or row['descripcion'].upper().find('MULTICULOR') != -1:
            df.loc[index,'COL_AUX'] ='MULTICOLOR'
        elif row['descripcion'].upper().find('GRIS') != -1:
            df.loc[index,'COL_AUX'] ='GRIS'
    
    if row['COL_AUX'] =='tipo':
        if row['descripcion'].upper().find('ESTAMPADA') != -1:
            df.loc[index,'COL_AUX'] ='ESTAMPADO'
    
    if row['COL_AUX'] == 'tipo':
        if row['TIPOCOLOR'].upper().find('ESTAMPADO') != -1 or row['TIPOCOLOR'].upper().find('ESTAMPADO') != -1:
            df.loc[index,'COL_AUX'] ='ESTAMPADO'
            
    if row['COL_AUX'] =='chanel':
        if row['descripcion'].upper().find('MULTICOLOR') != -1:
            df.loc[index,'COL_AUX'] ='MULTICOLOR'        
    
    if row['COL_AUX'].upper() == 'MULTI':
        df.loc[index,'COL_AUX'] ='MULTICOLOR'
    
    if row['COL_AUX'] =='a':
        df.loc[index,'COL_AUX'] = 'MULTICOLOR'


# In[494]:


df['COL_AUX'] = df['COL_AUX'].str.upper()


# In[497]:


df.loc[df['COL_AUX']=='BLANCA','COL_AUX'] ='BLANCO'
df.loc[df['COL_AUX']=='AMARILLA','COL_AUX'] ='AMARILLO'
df.loc[df['COL_AUX']=='DORADA','COL_AUX'] ='DORADO'
df.loc[df['COL_AUX']=='NEGRA','COL_AUX'] ='NEGRO'
df.loc[df['COL_AUX']=='NEGROS','COL_AUX'] ='NEGRO'
df.loc[df['COL_AUX']=='AZÚL','COL_AUX'] ='AZUL'
df.loc[df['COL_AUX']=='AZULES','COL_AUX'] ='AZUL'
df.loc[df['COL_AUX']=='ROJA','COL_AUX'] ='ROJO'


# In[519]:


df = df[['pos', 'id_producto', 'descripcion', 'COL_AUX', 'marca','sexo', 'tipo', 'moneda',
         'precio_dto', 'precio', 'img', 'url', 'pagina_scraper', 'origen']]
df.rename(columns={'COL_AUX':'color'},inplace=True)

df['precio'] = df['precio'].astype('float')
df['precio_dto'] = df['precio_dto'].astype('float')
df.to_excel(f'/home/aa/cloudJ/JB/PRD/scrapper/Scripts/Mexico/Salida/foleys{fecha}.xlsx')


print(f'GUARDO EL EXCEL foleys{fecha}.xlsx')

browser.quit()

