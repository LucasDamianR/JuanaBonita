
# coding: utf-8

# In[1]:
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import smtplib
import datetime
import itertools
from bs4 import BeautifulSoup
import requests
import math

def createDriver():
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument(f'user-agent={user_agent}')
    chrome_options.add_argument("--window-size=1825x1844")
    return webdriver.Chrome( options = chrome_options)


def scrape_url(url_aux,pos_aux,url_scraper):
    
    
    lista_auxiliar = []
    response = requests.get(url_aux)
    soup = BeautifulSoup(response.content, "html.parser")
    talles = [[i.text.strip(),i['data-sku']] for i in soup.find_all(class_='js-sizeItem')]
    
    try:
        aux_tipo = [i.span for i in soup.find_all(class_='path mt20 w')]
        aux_tipo = [i.text for i in aux_tipo[0].a.findNextSiblings()]
    except:
        lista_auxiliar.append([-1,
                               -1,
                               -1,
                               -1,
                               -1,
                               -1,
                               -1,
                               -1,
                               -1,
                               -1,
                               -1,
                               -1,
                               -1
                               ])
    
    for i in soup.find_all(class_='normal-price none pr'):
        aux = i
        prices = [x.text for x in aux.find_all('span')[-2:]]
    for talle in talles:

        for i in soup.find_all(class_='big-color'):
            try:
                lista_auxiliar.append([pos_aux,
                                       talle[1],
                                       talle[0],
                                       i.a['title'],
                                       aux_tipo[0],
                                       aux_tipo[1],
                                       aux_tipo[-1].split('/')[0].strip(),
                                       aux_tipo[-1].split('/')[1].strip(),
                                       prices[0],
                                       prices[1],
                                       i.a['href'],
                                       i.img['src'],
                                       url_scraper
                                      ])
            except:
                return url_aux
    return lista_auxiliar


def scrape_batch(url_chunk,url_scrape):
    chunk_resp = []
    for url in url_chunk:
        chunk_resp.append(scrape_url(url[0],url[1],url_scrape))
    return chunk_resp


def aplanar_lista(lista):
    if type(lista[0][0]) != list:
        return lista
    else:
        lista = list(itertools.chain(*lista))
        return aplanar_lista(lista)
    
    
    
def return_chunk(df,num):
    
    num = num-1
    BLOQUES = 6
    BLOQUE = math.ceil(len(df)/BLOQUES)
    split_df = lambda items, chunksize: [items[i:i+chunksize] for i in range(0, len(items), chunksize)]
    L = split_df(df,BLOQUE)
    
    return L[num]
    
    
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



def enviarMail():

    

    # login
    user = 'lucasprueba2019@gmail.com'
    password = 'lucaslucas1'
    aux_destinatarios = 'lrojas@juanabonita.com', 'jhernandez@juanabonita.com'
    # Mensaje
    msg = MIMEMultipart()
    fecha = datetime.date.today()
    msg['From'] = " Reportes Juana                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      ."
    msg['Subject'] = f'** ZAFUL SCRAPER **'

    txt =f"/home/aa/cloudJ/JB/PRD/scrapper/Scripts/Usa/Zaful/resumen_{fecha}.txt"
    f = open (txt,'r')
    mensaje = f.read()
    f.close()

    part = MIMEText(mensaje)
    msg.attach(part)
    part = MIMEApplication(open(txt ,"rb").read())
    part.add_header('Content-Disposition', 'attachment', filename = f"resumen_{fecha}.txt")
    msg.attach(part)
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    server.login(user,password)
    server.sendmail(user, aux_destinatarios, msg.as_string())
    server.quit()


    
def restore_items(restore):
    total_items = []
    for index,row in restore.iterrows():

        for fila in row:

            fila_aux = fila.replace('"','').replace("'",'').strip('[]').split('], [')
            for row_aux in fila_aux:

                final_append = row_aux.split(',')
                total_items.append(list(map(str.strip,final_append)))

    return total_items




def zscrape_url(url_aux,pos_aux,url_scraper):
    
    
    lista_auxiliar = []
    response = requests.get(url_aux)
    soup = BeautifulSoup(response.content, "html.parser")
    talles = [[i.text.strip(),i['data-sku']] for i in soup.find_all(class_='js-sizeItem')]
    
    try:
        aux_tipo = [i.span for i in soup.find_all(class_='path mt20 w')]
        aux_tipo = [i.text for i in aux_tipo[0].a.findNextSiblings()]
    except:
        lista_auxiliar.append([-1,
                               -1,
                               -1,
                               -1,
                               -1,
                               -1,
                               -1,
                               -1,
                               -1,
                               -1,
                               -1,
                               -1,
                               -1
                               ])
    
    for i in soup.find_all(class_='normal-price none pr'):
        aux = i
        prices = [x.text for x in aux.find_all('span')[-2:]]
    for talle in talles:

        for i in soup.find_all(class_='big-color'):
            try:
                lista_auxiliar.append([pos_aux,
                                       talle[1],
                                       talle[0],
                                       i.a['title'],
                                       aux_tipo[0],
                                       aux_tipo[1],
                                       aux_tipo[-1].split('/')[0].strip(),
                                       aux_tipo[-1].split('/')[1].strip(),
                                       prices[0],
                                       prices[1],
                                       i.a['href'],
                                       i.img['src'],
                                       url_scraper
                                      ])
            except:
                return url_aux
    return lista_auxiliar


def zscrape_batch(url_chunk,url_scrape):
    chunk_resp = []
    for url in url_chunk:
        chunk_resp.append(scrape_url(url[0],url[1],url_scrape))
    return chunk_resp

