
# coding: utf-8

# In[1]:


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
import pyodbc
import asyncio
from selenium.webdriver.common.action_chains import ActionChains
import numpy as np
import itertools
import pdb
from ipywidgets import IntProgress
from IPython.display import display
import os
from IPython.display import clear_output
import json
from selenium.webdriver.support import expected_conditions

from sc_header import scrape_batch, scrape_url, aplanar_lista,createDriver,return_chunk, aplanar


# In[2]:


start_ = datetime.datetime.now()
fecha = datetime.date.today()
hoy = fecha.strftime('%Y/%m/%d')


# In[3]:


browser = createDriver()


# In[4]:


browser.get("https://www.zaful.com/")            


# In[5]:


browser.execute_script('''
$('#js-changeCountry').mouseover();
document.getElementsByClassName('header-country-wrapper')[0].getElementsByTagName('a')[0].click();
document.getElementsByClassName('header-country-wrapper')[0].click();
document.querySelector("#js-changeCountry > div > div.header-country-wrapper > div > ul.hot-country-list > li:nth-child(1) > a").click();

document.getElementsByClassName('link-update-preferences logsss_event_cl')[0].click();

''')


# In[6]:



dfLinks = pd.read_excel(f'Links_{str(fecha)}.xlsx')

dfLinks = return_chunk(dfLinks,6)


# In[8]:


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
        urllist.append([product.find_element_by_css_selector('.pr.imgWrap').find_element_by_tag_name('a').get_attribute('href'),inx])
    batch_size = 5
    
    url_chunks = [urllist[x:x+batch_size] for x in range(0, len(urllist), batch_size)]
    
    for url_chunk in url_chunks:
        items.append(scrape_batch(url_chunk,row['url']))
    
    try:
        df_save = pd.DataFrame(items)
        df_save.to_excel('zaful6.xlsx')
        
        file = open("zaful_chunk6.txt", "w")
        file.write( str(url_chunk) + os.linesep)
        file.close()
    except:
        print("Error al guardar")
        
end_ = datetime.datetime.now()
browser.quit()


# In[9]:




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


file = open("zaful-6.txt", "w")
file.write(  os.linesep +f'ZAFUL_6 - {len(df)}' )
file.write(  os.linesep +f'CANTIDAD DE ITEMS - {len(df)}' )
file.write(  os.linesep +f'DURACION - {format(end_ - start_)[:-4]}' )
file.close()


df.to_excel(f'./Salida/zaful6-{fecha}.xlsx')

