
# coding: utf-8

# In[2]:


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
import pyodbc
from selenium.webdriver.common.action_chains import ActionChains
import numpy as np
import os
import json
from selenium.webdriver.support import expected_conditions
from sc_header import scrape_batch, scrape_url, aplanar_lista,createDriver, return_chunk, aplanar


# In[3]:


fecha = datetime.date.today()
hoy = fecha.strftime('%Y/%m/%d')


# In[4]:


browser = createDriver()


# In[5]:


browser.get("https://www.zaful.com/")    


# In[6]:


browser.execute_script('''
$('#js-changeCountry').mouseover();
document.getElementsByClassName('header-country-wrapper')[0].getElementsByTagName('a')[0].click();
document.getElementsByClassName('header-country-wrapper')[0].click();
document.querySelector("#js-changeCountry > div > div.header-country-wrapper > div > ul.hot-country-list > li:nth-child(1) > a").click();

document.getElementsByClassName('link-update-preferences logsss_event_cl')[0].click();

''')


# In[7]:


dfLinks = pd.read_excel(f'Links_{fecha}.xlsx')


# In[8]:


dfLinks = return_chunk(dfLinks,1)


# In[9]:


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
        df_save.to_excel('zaful1.xlsx')
        
        file = open("zaful_chunk1.txt", "w")
        file.write( str(url_chunk) + os.linesep)
        file.close()
    except:
        print("Error al guardar")

browser.quit()
end_ = datetime.datetime.now()


# In[13]:



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


# In[ ]:


file = open("zaful-1.txt", "w")
file.write(  os.linesep +f'ZAFUL_1 - {len(df)}' ) 
file.write(  os.linesep +f'CANTIDAD DE ITEMS - {len(df)}' ) 
file.write(  os.linesep +f'DURACION - {format(end_ - start_)[:-4]}' ) 
file.close()


# In[15]:


df.to_excel(f'./Salida/zaful1-{fecha}.xlsx')


# In[32]:


browser.quit()

