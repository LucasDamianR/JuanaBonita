
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
from pandas import ExcelWriter
import re
from selenium.webdriver.common.action_chains import ActionChains
import numpy as np
from ipywidgets import IntProgress
from IPython.display import display
import os
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
from sc_header import createDriver, return_chunk, zscrape_url, zscrape_batch, aplanar



fecha = datetime.date.today()


dfLinks = pd.read_excel(f'/home/aa/cloudJ/JB/PRD/scrapper/Scripts/Mexico/Links_{fecha}.xlsx')

dfLinks = return_chunk(dfLinks,3)

browser = createDriver()


start_ = datetime.datetime.now()
items = []

for index,row in dfLinks.iterrows():
    try:
        browser.get(row['url'])
    except:
        browser.quit()
        time.sleep(1)
        browser = createDriver()
        continue
    
    productos = browser.find_elements_by_class_name('js_proList_item')
    urllist = []
    
    for inx,product in enumerate(productos):    
        precio = browser.find_elements_by_css_selector('.my_shop_price.js_market_wrap')[inx].get_attribute('data-bz')
        try:
            precio_dto = browser.find_elements_by_css_selector('.my_shop_price.js_list_shopprice')[inx].get_attribute('data-bz')
        except Exception as e:
            print(e)
            precio_dto = precio
            
        urllist.append([product.find_element_by_css_selector('.pr.imgWrap').find_element_by_tag_name('a').get_attribute('href'),
                            precio_dto,
                            precio,
                            inx])
     
    batch_size = 5
    
    url_chunks = [urllist[x:x+batch_size] for x in range(0, len(urllist), batch_size)]
    
    for url_chunk in url_chunks:
        items.append(zscrape_batch(url_chunk,row['url']))
            
    try:
        df_save = pd.DataFrame(items)
        df_save.to_excel('zaful3.xlsx')
        
        file = open("zaful_chunk3.txt", "w")
        file.write( str(url_chunk) + os.linesep)
        file.close()
    except:
        print("Error al guardar")
        
end_ = datetime.datetime.now()
browser.quit()



new_list = aplanar(items)
new_list = [item for item in new_list if len(item) == 13]        
df = pd.DataFrame(new_list)

df.rename(columns={0:'pos',
                  1:'id_producto',
                  2:'talle',
                  3:'color',
                  4:'sexo',
                  5:'tipo',
                  6:'sub_categoria',
                  7:'descripcion',
                  8:'precio_dto',
                  9:'precio_original',
                  10:'url',
                  11:'img',
                  12:'pagina_scraper'
                  },inplace=True)



file = open("/home/aa/cloudJ/JB/PRD/scrapper/Scripts/Mexico/zaful-3.txt", "w")
file.write(  os.linesep +f'ZAFUL_3 - {len(df)}' ) 
file.write(  os.linesep +f'CANTIDAD DE ITEMS - {len(df)}' ) 
file.write(  os.linesep +f'DURACION - {format(end_ - start_)[:-4]}' ) 
file.close()


df.to_excel(f'/home/aa/cloudJ/JB/PRD/scrapper/Scripts/Mexico/Salida/zaful-3{fecha}.xlsx')

print('TERMINO ZAFUL-3.py')