
# coding: utf-8

# In[2]:


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


# In[3]:


scraper='COCOT'


# In[4]:


URLS = [['Mujer','https://cocot.com.uy/damas'],
        ['Hombre','https://cocot.com.uy/hombres']]


# In[5]:


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


# In[6]:


#browser.get()


# In[7]:


#page = BeautifulSoup(browser.page_source,"html.parser")


# In[8]:


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
    for i in LABELS:
        #CREAR UN STR DE MAYÚSCULAS 
        CAT = str(i.get_attribute('title')).upper()
        if  CAT == 'MEDIAS':
            continue
        elif CAT == 'ACCESORIOS':
            continue
        else:
            CATEGORIAS.append([CAT.capitalize(),i.get_attribute('data-val')])
    #ITERAR CATEGORIAS
    for CATEGORIA in CATEGORIAS:
        
        browser.get(CATEGORIA[1])
        
        SUB_CATEGORIAS = []
        
        #GUARDO LA PÁGINA PARA HACER UNA REQUEST AL FINALIZAR TODOS LOS COLORES
        CURRENT_URL = browser.current_url
        #LABELS CATEGORIA DONDE SE GUARDAN TODAS LAS CATEGORÍAS
        try:
            LABELS_CATEGORIA = browser.find_element_by_class_name('blk').find_element_by_class_name('lst').find_elements_by_tag_name('label')
            NO_HAY = 0
        except:
            NO_HAY = 1
        #SI NO_HAY ES 1 . (SIGNIFICA QUE NO TIENE SUB_CATEGORIA)
        if NO_HAY == 1 or CATEGORIA[0] == 'Ropa deportiva':
            
            try:                
                AUX_PALETA = browser.find_element_by_xpath('//*[@id="catalogoFiltros"]').find_element_by_class_name('cnt').find_elements_by_class_name('blk')[-1]
            except:
                continue
            #Si contiene 'Color' hicimos bien el trabajo, sino.. tendremos que revisar (si cambio el HTML)
            if 'Color' == AUX_PALETA.text:
                
                #LOOP de AUX_PALETA, cada elemento tiene el color. 
                PALETA = AUX_PALETA.find_elements_by_class_name('it')
                PALETA_COLORES = [[i,i.get_attribute('data-val')] for i in PALETA]
                #for COLOR_AUX in PALETA_COLORES:
                for i in range(1,len(PALETA_COLORES)+1):
                    #ESTOY POR ACA DPS SEGUIR VIENDO
                    for X in [9,8,4,5,6]:
                        try:
                            #Clickear color
                            #Cada nombre en Capitalize() porque es minúscula
                            NOMBRE_COLOR = browser.find_element_by_css_selector(f'#catalogoFiltros > div > div:nth-child({X}) > div.cnt > div > label:nth-child({i})').get_attribute('data-val')    
                            #NOMBRE_COLOR = COLOR_AUX[1]
                            browser.find_element_by_css_selector(f'#catalogoFiltros > div > div:nth-child(9) > div.cnt > div > label:nth-child({i})').click()
                            break
                        except:
                            pass
                    time.sleep(1.5)
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
                        COLOR = NOMBRE_COLOR
                        PRECIO = PRODUCTO.text.split('\n')[1]
                        HREF = PRODUCTO.find_element_by_tag_name('a').get_attribute('href')
                        LISTA_PRODUCTOS.append([ID,
                                                DESCRIPCION,
                                                CATEGORIA[0],
                                                COLOR,
                                                url[0],
                                                PRECIO,
                                                HREF,
                                                IMG])
            
        else:

            for label_categoria in LABELS_CATEGORIA:
                #Lista con sub categorias
                SUB_CATEGORIAS.append([label_categoria.get_attribute('title').capitalize(),label_categoria.get_attribute('data-val')])
            #loop de sub_categorias
            for SUB in SUB_CATEGORIAS:
                #request de una sub_categoria : ejemplo (soutien)

                browser.get(SUB[1])
                #AUX_PALETA intenta ser el ultimo conjunto de la barra lateral izquierda (o sea "Color")
                try:                
                    AUX_PALETA = browser.find_element_by_xpath('//*[@id="catalogoFiltros"]').find_element_by_class_name('cnt').find_elements_by_class_name('blk')[-1]
                except:
                    continue
                #Si contiene 'Color' hicimos bien el trabajo, sino.. tendremos que revisar (si cambio el HTML)
                if 'Color' == AUX_PALETA.text:

                    #LOOP de AUX_PALETA, cada elemento tiene el color. 
                    PALETA = AUX_PALETA.find_elements_by_class_name('it')

                    PALETA_COLORES = [[i,i.get_attribute('data-val')] for i in PALETA]

                    #for COLOR_AUX in PALETA_COLORES:
                    for i in range(1,len(PALETA_COLORES)+1):
                        #ESTOY POR ACA DPS SEGUIR VIENDO
                        for X in [9,8,4,5,6]:
                            try:
                                #Clickear color
                                #Cada nombre en Capitalize() porque es minúscula
                                NOMBRE_COLOR = browser.find_element_by_css_selector(f'#catalogoFiltros > div > div:nth-child({X}) > div.cnt > div > label:nth-child({i})').get_attribute('data-val')    
                                #NOMBRE_COLOR = COLOR_AUX[1]
                                browser.find_element_by_css_selector(f'#catalogoFiltros > div > div:nth-child(9) > div.cnt > div > label:nth-child({i})').click()
                                break
                            except:
                                pass


                        time.sleep(1.5)


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
                            COLOR = NOMBRE_COLOR
                            PRECIO = PRODUCTO.text.split('\n')[1]
                            HREF = PRODUCTO.find_element_by_tag_name('a').get_attribute('href')
                            LISTA_PRODUCTOS.append([ID,
                                                    DESCRIPCION,
                                                    SUB[0],
                                                    COLOR,
                                                    url[0],
                                                    PRECIO,
                                                    HREF,
                                                    IMG])
                        browser.get(SUB[1])


# In[11]:


dfCocot = pd.DataFrame(LISTA_PRODUCTOS)


# In[12]:


dfCocot.rename(columns={0:'codigo'},inplace=True)
dfCocot.rename(columns={1:'descripcion'},inplace=True)
dfCocot.rename(columns={2:'tipo'},inplace=True)
dfCocot.rename(columns={3:'color'},inplace=True)
dfCocot.rename(columns={4:'sexo'},inplace=True)
dfCocot.rename(columns={5:'precio'},inplace=True)
dfCocot.rename(columns={6:'url_producto'},inplace=True)
dfCocot.rename(columns={7:'img_producto'},inplace=True)


# In[14]:


dfCocot['DESC'] = dfCocot['descripcion'].str.capitalize().apply(lambda x : x.split('\n')[0].split(' - ')[0])


# In[15]:


dfCocot['color'] = dfCocot['color'].str.capitalize()


# In[16]:


dfCocot['fecha'] = fecha


# In[17]:


dfCocot['origen'] = 'COCOT UY'
dfCocot['marca'] = 'Cocot'

browser.quit()
if len(dfCocot.drop_duplicates()) == len(dfCocot.dropna()) == len(dfCocot) == True:
    print(f'CIUDADO DUPLICADOS EN {scraper}')


# In[18]:


writer = ExcelWriter('/home/aa/cloudJ/JB/PRD/scrapper/Scripts/Uruguay/Salida/cocot'+str(fecha)+'.xlsx')
dfCocot.to_excel(writer,'Hoja1')
writer.save()


# In[20]:


end_ = datetime.datetime.now()


# In[21]:


print('Tiempo de ejecución '+scraper+': '+str(end_ - start_)[:-7])

