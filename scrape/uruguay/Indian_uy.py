
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
scraper ='INDIAN'


# In[96]:


URLS = [['Mujer','https://www.indian.com.uy/vestimenta'],
       ['Mujer','https://www.indian.com.uy/ropa-interior'],
       ['Hombre','https://www.indian.com.uy/maximo-for-men']]


# In[3]:


start_ = datetime.datetime.now()
fecha = datetime.date.today()

user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'    

chrome_options = Options()  
chrome_options.add_argument("--headless")  
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--window-size=1825x1244")


browser = webdriver.Chrome('/usr/bin/chromedriver', options = chrome_options)


# In[107]:


LISTA_PRODUCTOS = []
for url in URLS:
    sexo = url[0]
    #request de la url , vestimenta, ropa int, hombres.
    browser.get(url[1])
    if url[1] == 'https://www.indian.com.uy/vestimenta':
        #OBTENER LAS CATEGORIAS DE LA PÁGINA
        #SUBCATEGORIAS = [[i.text,i.find_element_by_tag_name('a').get_attribute('href')] for i in browser.find_element_by_xpath('//*[@id="collapseColection"]/ul/ul/li/ul').find_elements_by_tag_name('li')]
        SUBCATEGORIAS = browser.execute_script('''
                        var cant = document.getElementsByClassName('blk blkCategorias')[0].getElementsByClassName('lst lstStd')[0].getElementsByTagName('label').length;

                        var arn = []
                        var arl = []
                        for (i=0;i<cant;i++){

                            var nombre = document.getElementsByClassName('blk blkCategorias')[0].getElementsByClassName('lst lstStd')[0].getElementsByTagName('label')[i].getAttribute('title');
                            var link = document.getElementsByClassName('blk blkCategorias')[0].getElementsByClassName('lst lstStd')[0].getElementsByTagName('label')[i].getAttribute('data-val');

                            arn[i] = nombre
                            arl[i] = link
                        }

                        function zip(a, b) {
                          var arr = [];
                          for (var key in a) arr.push([a[key], b[key]]);
                          return arr;
                        }

                        return zip(arn,arl );

                        ''')
    if url[1] != 'https://www.indian.com.uy/vestimenta': SUBCATEGORIAS = [1]
        

    for SUB in SUBCATEGORIAS:
        #print(SUB[0])
        if url[1] == 'https://www.indian.com.uy/vestimenta':
            browser.get(SUB[1])
        
        last_height = browser.execute_script("return document.body.scrollHeight")
        while True:

            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
            try:
                browser.execute_script('''document.getElementsByClassName('btnMas btn btn01')[0].click();''')
            except:
                pass
            new_height = browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        #A SCRAPEAR
        PRODUCTOS = browser.execute_script('''
            var x = document.getElementsByClassName('articleList aListProductos ')[0];
            return x;''').find_elements_by_class_name('it')
        for PRODUCTO in PRODUCTOS:
            if url[1] != 'https://www.indian.com.uy/vestimenta':
                cat='NONE'
            else:
                cat = SUB[0]
            LISTA_PRODUCTOS.append([#PRODUCTO.find_element_by_tag_name('a').get_attribute('href').split('/')[-1],
                                    #COLOR[0],
                                    #sexo,
                                    #cat,
                                    #PRODUCTO.find_element_by_tag_name('a').get_attribute('href'),
                                    #PRODUCTO.find_element_by_tag_name('a').find_element_by_tag_name('img').get_attribute('data-original'),
                                    #PRODUCTO.find_element_by_class_name('hover-container').find_element_by_tag_name('h3').get_attribute('title'),

                                    #SKU
                                    PRODUCTO.get_attribute('data-codprod'),
                                    sexo,
                                    cat,
                                    #HREF
                                    PRODUCTO.find_element_by_tag_name('a').get_attribute('href'),
                                    #IMG
                                    PRODUCTO.find_element_by_tag_name('a').find_element_by_tag_name('img').get_attribute('src'),
                                    #DESCRIPCION
                                    PRODUCTO.find_element_by_class_name('cnt').find_element_by_tag_name('a').get_attribute('title'),
                                    #PRECIOS
                                    PRODUCTO.find_element_by_class_name('precios').text
                                   ])


# In[110]:


df_indian = pd.DataFrame(LISTA_PRODUCTOS)


# In[112]:


df_indian.rename(columns={0:'codigo'},inplace=True)
df_indian.rename(columns={1:'sexo'},inplace=True)
df_indian.rename(columns={2:'tipo'},inplace=True)
df_indian.rename(columns={3:'url_producto'},inplace=True)
df_indian.rename(columns={4:'img_producto'},inplace=True)
df_indian.rename(columns={5:'descripcion'},inplace=True)
df_indian.rename(columns={6:'precio'},inplace=True)


# In[113]:


df_indian['precio_dto'] = df_indian['precio'].apply(lambda x : x.split('$')[2] if len(x.split('$')) == 3 else x.split('$')[1])

df_indian['precio_original'] = df_indian['precio'].apply(lambda x : x.split('$')[1] if len(x.split('$')) == 3 else x.split('$')[1])


# In[115]:


df_indian['fecha'] = fecha


# In[116]:


df_indian['origen'] = 'INDIAN UY'
df_indian['marca'] = 'INDIAN'


# In[117]:


browser.quit()
if len(df_indian.drop_duplicates()) == len(df_indian.dropna()) == len(df_indian) == True:
    print(f'CIUDADO DUPLICADOS EN {scraper}')


# In[118]:


writer = ExcelWriter('/home/aa/cloudJ/JB/PRD/scrapper/Scripts/Uruguay/Salida/indian'+str(fecha)+'.xlsx')
df_indian.to_excel(writer,'Hoja1')
writer.save()


# In[ ]:


end_ = datetime.datetime.now()
print(f'Tiempo de ejecución {scraper}: {str(end_ - start_)[:-7]}')


# In[ ]:


#!jupyter nbconvert --to script 'Indian_uy.ipynb'

