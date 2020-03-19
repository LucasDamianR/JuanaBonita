
# coding: utf-8

# In[227]:


from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import numpy as np
import requests
import datetime
from bs4 import BeautifulSoup
import pandas as pd
from pandas import ExcelWriter
import time
import unicodedata
import pyodbc
import os
from json import JSONDecoder
from sc_header import createDriver,extract_json_objects


# In[228]:


def scrape_url(url_aux,sexo_aux):
    
    global output

    response = requests.get(url_aux)
    soup = BeautifulSoup(response.content, "html.parser")
    scripts = soup.find_all('script')
    #EL NUMERO DE SCRIPT TENER CUIDADO, A VECES CAMBIA.
    #OLD = 14
    for data in extract_json_objects(scripts[15].text):
        if data != {}:

            x = soup.find(class_='mx')
            color_aux = data['color']['name']
            if color_aux == '':
                color_aux = soup.find(class_='o-list-swatches__a js-swatch-link-product has-mouse-click-focus-disabled').get('title')
            try:
                output.append([soup.find('h1').text,
                               x.span.text.strip(),
                               color_aux,
                               sexo_aux,
                               data['images'][0]['medium'],
                               soup.find(class_='breadcrumb-item active').text.strip(),
                               x.find(class_='newprice').text.strip(),
                               x.find(class_='mx-price').text.strip(),
                               url_aux
                              ])
            except Exception as e:
                pass
                

def scrape_batch(url_chunk):
    chunk_resp = []
    for a,b in url_chunk.iterrows():
        scrape_url(b['url'],b['sexo'])
    


# In[229]:


browser = createDriver()
browser.get('https://www.cuidadoconelperro.com.mx/')


# In[230]:


#INTENTO CERRAR EL MODAL
try:
    inputs = browser.find_elements_by_tag_name('input')
    for input_ in inputs:
        if input_.get_attribute('type') =='submit':
            input_.click()
except:
    pass


# In[231]:


urls_principales = []
for item in browser.find_element_by_class_name('department-selector').find_elements_by_tag_name('a'):
    if item.text != 'KIDS':
        urls_principales.append([item.get_attribute('href'),item.text])
        


# In[232]:


cat_aux = []
for url in urls_principales:
    browser.get(url[0])
    WebDriverWait(browser,50).until(EC.presence_of_element_located((By.CSS_SELECTOR,'.fas.fa-bars'))).click()
    WebDriverWait(browser,50).until(EC.presence_of_element_located((By.LINK_TEXT,url[1]))).click()
    for cat in browser.find_element_by_css_selector('.list-unstyled.components').find_elements_by_tag_name('a'):
        cat_aux.append([cat.get_attribute('href'),
                       url[1]])


# In[245]:


df_cat = pd.DataFrame(cat_aux)


# In[246]:


df_cat = df_cat[(~df_cat[0].str.contains('accesorios'))&
                (~df_cat[0].str.contains('calcetines'))&
                (~df_cat[0].str.contains('zapatos'))&
                (~df_cat[0].str.contains('tiendas'))]


# In[247]:


df_cat = df_cat[df_cat[0] != 'https://www.cuidadoconelperro.com.mx/mx/lenceria-y-pijamas/panties/bikini-cintura-alta/13556']
df_cat = df_cat.reset_index(drop=True).rename(columns={0:'url',1:'sexo'})


# In[248]:


href_list = []
for index,row in df_cat.iterrows():
    
    try:
        browser.get(row['url'])
    except:
        pass
    TIMEOUT = 2
        
    #WHILE PARA PODER PASAR DE PAGINA
    while True:
        
        #WHILE PARA HACER SCROLL
        last_height = browser.execute_script("return document.body.scrollHeight;")
        while True:

            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(TIMEOUT)
            new_height = browser.execute_script("return document.body.scrollHeight;")
            if new_height == last_height:
                break
            last_height = new_height
        #TOMO TODOS LOS PRODUCTOS
        for item in browser.find_elements_by_class_name('title'):
            
            href_list.append([item.find_element_by_tag_name('a').get_attribute('href'),
                              row['sexo']])
        #DESPUES DE TOMAR TODOS LOS PRODUCTOS, CLICKEO EN NEXTPAGE, SI ES QUE TIENE            
        try:
            browser.find_element_by_css_selector('.next.js-search-link').click()
        except:
            break
    


# In[249]:


df_href = pd.DataFrame(href_list)


# In[250]:


df_href = df_href.rename(columns={0:'url',1:'sexo'})


# In[251]:


df_href.drop_duplicates(inplace=True)
df_href.reset_index(drop=True,inplace=True)


# In[ ]:


batch_size = 5
url_chunks = [df_href[x:x+batch_size] for x in range(0, len(df_href), batch_size)]


# In[253]:


browser.quit()


# In[254]:


start_ = datetime.datetime.now()
output = []
for url_chunk in url_chunks:
    scrape_batch(url_chunk)
        
end_ = datetime.datetime.now()


# In[263]:


df = pd.DataFrame(output)

df = df.rename(columns={0:'descripcion',
                       1:'id_producto',
                       2:'color',
                       3:'sexo',
                       4:'img',
                       5:'tipo',
                       6:'precio',
                       7:'precio_dto',
                       8:'url'
                      })


# In[267]:


df['precio'] = (df['precio']
                .str.extract(r"([\d,\.]+)", expand=False)
                .str.replace(",", "")
                .astype(float))



df['precio_dto'] = (df['precio_dto']
                    .str.extract(r"([\d,\.]+)", expand=False)
                    .str.replace(",", "")
                    .astype(float))


# In[273]:



df['marca'] = 'CUIDADO CON EL PERRO'
df['tipo_es'] = df['tipo']
df['color_es'] = df['color']
df['moneda'] = 'PESO MXN'
df['origen'] = 'CUIDADO CON EL PERRO'


# In[276]:


df = df.drop_duplicates()
df = df.dropna()


# In[ ]:


fecha = datetime.date.today()


# In[ ]:


df.to_excel(f'/home/aa/cloudJ/JB/PRD/scrapper/Scripts/Mexico/Salida/ccep{fecha}.xlsx')
print(f'GUARDO EL EXCEL ccep{fecha}.xlsx')

