
# coding: utf-8


from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import requests
from time import strftime
import datetime
import time
import re
from selenium.webdriver.common.action_chains import ActionChains
import os
from selenium.webdriver.support import expected_conditions
import json
import itertools



def quitar_modales(driver):
    #modal de inicio
    try:
        driver.execute_script("document.getElementsByClassName('universal-modal__close-button')[0].click();")
    except:
        pass
    #promociones_click para ocultar
    try:
        driver.execute_script("document.getElementsByClassName('promoDrawer__handlebar__icon')[0].click();")
    except:
        pass
    
def createDriver():
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument(f'user-agent={user_agent}')
    chrome_options.add_argument("--window-size=1825x1844")
    # options.headless = True
    return webdriver.Chrome( options = chrome_options)


def get_categorias(driver):    
    categoria_aux = []
    for i in range(1,9):
        categoria_aux.append(driver.execute_script(f"var x = document.getElementsByClassName('topNavLink')[{i}].getElementsByClassName('divisionLink')[0].getAttribute('data-divisionname'); return x"))

    return categoria_aux



def scrape_url(url_aux,pos_aux,url_scraper,aux_tipologia,aux_sexo):

    
    lista_auxiliar = []
    response = requests.get(url_aux)
    soup = BeautifulSoup(response.content, "html.parser")
    try:
        time.sleep(.3)
        metadatos = json.loads(soup.find('script', type='application/ld+json').text)
    except:
        
        return [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
    
    _ = False
    timeout = time.time() + 30
    while True:
        
        try:
            id_producto = metadatos[0]['productID'] #--- ID PRODUCTO
            descripcion = metadatos[0]['name'] #--- DESCRIPCION
            break
            
        except:
            pass
        
        if time.time() > timeout:
            
            return [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]

    
    
    ## tipologia = soup.find(class_='catnav--item catnav--item-selected').text #--- TIPOLOGIA
    try:
        precio = soup.find(class_='product-price__strike').text #--- PRECIO
    except:
        _ = True
    try:
        for item in metadatos[0]['offers']:

            sku = item['itemOffered']['sku'] #SKU
            jpg = item['itemOffered']['image'] #JPG
            marca = item['seller']['name'] #MARCA
            color = item['itemOffered']['color'] #COLOR
            precio_dto = item['price'] #PRECIO
            if _ == True:
                precio = precio_dto
            condicion = item['itemCondition']#CONDICION : NEW/ Y NOSE
            disponibilidad = item['availability'] #DISPONIBILIDAD : INSTOCK/OUTSTOCK

            lista_auxiliar.append([pos_aux,
                                   id_producto,
                                   descripcion,
                                   aux_tipologia,
                                   precio,
                                   aux_sexo,
                                   sku,
                                   jpg,
                                   marca,
                                   color,
                                   precio_dto,
                                   condicion,
                                   disponibilidad,
                                   url_aux,
                                   url_scraper])


        return lista_auxiliar
    except:
        return [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]


def scrape_batch(url_chunk):
    chunk_resp = []
    for indices,fila in url_chunk.iterrows():
        chunk_resp.append(scrape_url(fila['href'],fila['pos'],fila['pagina_scraper'],fila['tipo'],fila['sexo']))
    return chunk_resp


def aplanar_lista(lista):
    if type(lista[0][0]) != list:
        return lista
    else:
        lista = list(itertools.chain(*lista))
        return aplanar_lista(lista)


def aplanar(lista):
    try:
        if type(lista[0][0]) != list and lista[0][0] != []:
            return lista
        else:
            lista = list(itertools.chain(*lista))
            return aplanar_lista(lista)
    except:
        lista = [i for i in lista if i != []]
            
        return aplanar_lista(lista)
    

def get_all_urls(categoria_aux,driver,url_base):
    urls_aux = []
    for index, val_categoria in enumerate(categoria_aux):

        cant = driver.execute_script(f''' 
        var cant = document.getElementsByClassName('topNavLink')[{index+1}].getElementsByClassName('meganav-column')[1].getElementsByClassName('catnav--item').length;
        return cant;

        ''')
        for i in range(cant):
            urls_aux.append([val_categoria,
                         driver.execute_script(f"var x = document.getElementsByClassName('topNavLink')[{index+1}].getElementsByClassName('meganav-column')[1].getElementsByClassName('catnav--item')[{i}].textContent;return x;"),
                         url_base + driver.execute_script(f"var x = document.getElementsByClassName('topNavLink')[{index+1}].getElementsByClassName('meganav-column')[1].getElementsByClassName('catnav--item')[{i}].getElementsByTagName('a')[0].getAttribute('href');return x;")
                        ])
    
    return pd.DataFrame(urls_aux,columns=['sexo',
                                          'tipo',
                                          'url'])

def get_hrefs(dfLinks_aux,driver):
    #TEST
    lista_productos = []
    excepts = []
    skip = 0
    lista_href = []
    EX = []

    for index,row in dfLinks_aux.iterrows():

        flag_checkbox = False
        try:

            driver.get(row['url'])
        except:
            driver.quit()
            time.sleep(1)
            driver = createDriver()
            driver.delete_all_cookies()
            continue

        #"cantidad categorias"
        if '0 Items in the product grid' == driver.find_element_by_class_name('category__item-count').text:

            continue

        #SI NO CARGA DE UNA MANERA, LO HAGO DE LA OTRA. PORQUE ESTA PAGINA CARGA COMO SE LE ANTOJA.
        try:
            WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.CLASS_NAME, "tabs--object")))
        except:
            flag_checkbox = True


        try:
            CATEGORY_BOTON = [i for i in driver.find_elements_by_css_selector('.tabs--trigger.no-focus-enabled') if i.get_attribute('aria-label').find('category') != -1][0]
        except:
            CATEGORY_BOTON = False
            excepts.append([row['url'],
                            row['tipo']])

        #FOR DE CANTIDAD DE CATEGORIAS
        if flag_checkbox and CATEGORY_BOTON != False:

            CATEGORY_BOTON.click()
            for i in driver.find_elements_by_class_name('checkbox__box'):
                time.sleep(1.5)
                i.click()
            CATEGORY_BOTON.click()

        elif CATEGORY_BOTON != False:

            CATEGORY_BOTON.click()
            CATEGORIAS = WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.CLASS_NAME, "accordion--content--inner"))).find_elements_by_tag_name('label')

            for m in CATEGORIAS:
                if m.is_displayed():
                    time.sleep(2)
                    m.click()
                else:
                    raise
            CATEGORY_BOTON.click()

        else:
            pass

        while True:

            #Scroll
            time.sleep(1)
            driver.execute_script('window.scrollTo(0,document.body.scrollHeight);')
            #href de productos
            hrefs = driver.find_elements_by_class_name('product-card__link')
            for pos, valor in enumerate(hrefs):
                try:
                    lista_href.append([pos+1,valor.get_attribute('href'),row['url'],row['tipo'],row['sexo']])
                except:
                    raise

            #footer
            try:
                driver.find_element_by_class_name('icon-chevron-right').click()
            except:
                break

    df = pd.DataFrame(lista_href)
    df = df.drop_duplicates()
    df.reset_index(drop = True,inplace = True)
    df.rename(columns = {0:'pos',
                         1:'href',
                         2:'pagina_scraper',
                         3:'tipo',
                         4:'sexo'},inplace = True)
    return df
