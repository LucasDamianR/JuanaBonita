
# coding: utf-8

# In[1]:


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
scraper ='SISI'


# In[2]:


URLS = [['Mujer','https://sisi.com.uy/mujer'],
        ['Hombre','https://sisi.com.uy/hombre']]


# In[3]:


start_ = datetime.datetime.now()
fecha = datetime.date.today()


user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'    

chrome_options = Options()  
chrome_options.add_argument("--headless")  
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--window-size=1325x744")
browser = webdriver.Chrome('/usr/bin/chromedriver', options = chrome_options)
browser.delete_all_cookies()


# In[4]:


browser.get(URLS[0][1])


# In[5]:


BLK = browser.find_element_by_class_name('blk')
if BLK.get_attribute('data-codigo') != 'categoria':
    raise "ERROR EN CATEGORÍA"


# In[6]:


LABELS = BLK.find_element_by_class_name('lst').find_elements_by_tag_name('label')


# In[7]:


CATEGORIAS = []
for i in LABELS:
    #CREAR UN STR DE MAYÚSCULAS 
    CAT = str(i.get_attribute('title')).upper()
    if  CAT == 'MEDIAS':
        continue
    elif CAT == 'ACCESORIOS':
        continue
    elif CAT == 'BELLEZA':
        continue
    elif CAT == 'CALZADO':
        continue
    else:
        CATEGORIAS.append([CAT.capitalize(),i.get_attribute('data-val')])
#ITERAR CATEGORIAS


# In[8]:


CATEGORIAS


# In[14]:


LISTA_PRODUCTOS = []
#browser.find_element_by_xpath('//*[@id="catalogoFiltros"]/div/div[1]/div[2]/div')
for url in URLS:
    browser.get(url[1])
    BLK = browser.find_element_by_class_name('blk')
    if BLK.get_attribute('data-codigo') != 'categoria':
        raise "ERROR EN CATEGORÍA"

    #NAVEGAR POR EL ELEMENTO BLK HASTA LLEGAR A LA LISTA DONDE ESTAN
    #LAS LABELS 
    LABELS = BLK.find_element_by_class_name('lst').find_elements_by_tag_name('label')

    CATEGORIAS = []
    #QUITAR ELEMENTOS NO DESEADOS
    CATEGORIAS = []
    for i in LABELS:
        #CREAR UN STR DE MAYÚSCULAS 
        CAT = str(i.get_attribute('title')).upper()
        if  CAT == 'MEDIAS':
            continue
        elif CAT == 'ACCESORIOS':
            continue
        elif CAT == 'BELLEZA':
            continue
        elif CAT == 'CALZADO':
            continue
        else:
            CATEGORIAS.append([CAT.capitalize(),i.get_attribute('data-val')])
    #ITERAR CATEGORIAS
    for CATEGORIA in CATEGORIAS:
        
        browser.get(CATEGORIA[1])
    
        #GUARDO LA PÁGINA PARA HACER UNA REQUEST AL FINALIZAR TODOS LOS COLORES
        CURRENT_URL = browser.current_url
        #requesst de la pagina actual
        page = BeautifulSoup(browser.page_source,"html.parser")

        #A VER SI FUNCIONA AHORA ESTA PORQUERIA
        browser.get(browser.current_url)
        ##scroll 
        last_height = browser.execute_script("return document.body.scrollHeight")
        while True:

            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5.5)
            try:
                browser.execute_script('window.scrollTo(0, 1100);')
                #browser.find_element_by_xpath('//*[@id="catalogoPaginado"]/button/span').click()
                browser.execute_script('window.scrollTo(0, 1500);')
                browser.find_element_by_id('catalogoPaginado').click()
            except:
                pass

            new_height = browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        page = BeautifulSoup(browser.page_source,"html.parser")
        #VER SI AL FINALIZAR EL SCROLL, SE PUDO MOSTRAR TODOS LOS PRODUCTOS
        try:
            if int(browser.find_element_by_id("catalogoPaginado").text.split()[1]) != int(browser.find_element_by_id("catalogoPaginado").text.split()[-1]):

                print(browser.find_element_by_id("catalogoPaginado").text)
                browser.find_element_by_xpath('//*[@id="catalogoPaginado"]/button').click()
        except:
            pass

        #TODOS LOS PRODUCTOS
        DIV_PRODUCTOS = browser.find_element_by_xpath('//*[@id="catalogoProductos"]').find_elements_by_class_name('it')

        for PRODUCTO in DIV_PRODUCTOS:
#            raise
            #EXCLUIR LAS IMAGENES PNG(NORMALMENTE SON ICONOS)
            AUX_JPG = PRODUCTO.find_element_by_tag_name('a').find_elements_by_tag_name('img')[0].get_attribute('src')
            if AUX_JPG.find('.jpg') == -1:
                AUX_JPG = PRODUCTO.find_element_by_tag_name('a').find_elements_by_tag_name('img')[1].get_attribute('src')
            elif AUX_JPG.find('.jpg') == -1:
                AUX_JPG = PRODUCTO.find_element_by_tag_name('a').find_elements_by_tag_name('img')[2].get_attribute('src')
            if AUX_JPG.find('.jpg') != -1:
                IMG = AUX_JPG

            ID = PRODUCTO.get_attribute('data-codprod')
            DESCRIPCION = PRODUCTO.text
            PRECIO = PRODUCTO.text.split('\n') #[1] yy
            HREF = PRODUCTO.find_element_by_tag_name('a').get_attribute('href')
            LISTA_PRODUCTOS.append([ID,
                                    DESCRIPCION,
                                    CATEGORIA[0],
                                    url[0],
                                    PRECIO,
                                    HREF,
                                    IMG])


# In[15]:





# In[11]:


browser.save_screenshot('asd.png')


# In[43]:


dfSisi = pd.DataFrame(LISTA_PRODUCTOS)


# In[44]:


dfSisi.rename(columns={0:'codigo'},inplace=True)
dfSisi.rename(columns={1:'descripcion'},inplace=True)
dfSisi.rename(columns={2:'tipo'},inplace=True)
dfSisi.rename(columns={3:'sexo'},inplace=True)
dfSisi.rename(columns={4:'precio'},inplace=True)
dfSisi.rename(columns={5:'url_producto'},inplace=True)
dfSisi.rename(columns={6:'img_producto'},inplace=True)


# In[45]:


dfSisi = dfSisi[dfSisi['descripcion'] != ""]


# In[46]:


dfSisi['DESC'] = dfSisi['descripcion'].str.capitalize().apply(lambda x : x.split('\n')[0].split(' - ')[0])


# In[47]:


dfSisi['color'] = dfSisi['descripcion'].str.capitalize().apply(lambda x : x.split('\n')[0].split(' - ')[1]).str.capitalize()


# In[55]:


dfSisi['precio'] = dfSisi['precio'].apply(lambda x:x[1])


# In[58]:


dfSisi['precio_dto'] = dfSisi['precio'].apply(lambda x : x.split('$')[2] if len(x.split('$')) == 3 else x.split('$')[1])

dfSisi['precio_original'] = dfSisi['precio'].apply(lambda x : x.split('$')[1] if len(x.split('$')) == 3 else x.split('$')[1])


# In[59]:


dfSisi['fecha'] = fecha
dfSisi['origen'] = 'SISI UY'
dfSisi['marca'] = 'SISI'


# In[60]:


if len(dfSisi.drop_duplicates()) == len(dfSisi.dropna()) == len(dfSisi) == True:
    print(f'CIUDADO DUPLICADOS EN {scraper}')


# In[63]:


writer = ExcelWriter('/home/aa/cloudJ/JB/PRD/scrapper/Scripts/Uruguay/Salida/sisi'+str(fecha)+'.xlsx')
dfSisi.to_excel(writer,'Hoja1')
writer.save()


# In[64]:


browser.quit()


# In[ ]:



end_ = datetime.datetime.now()
print(f'Tiempo de ejecución {scraper}: {str(end_ - start_)[:-7]}')


# In[66]:


#!jupyter nbconvert --to script 'Sisi_uy.ipynb'

