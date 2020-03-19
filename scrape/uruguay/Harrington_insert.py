
# coding: utf-8

# In[1]:


import pandas as pd
import pyodbc
import numpy as np
from pandas import ExcelWriter
import datetime
start_ = datetime.datetime.today()
scraper='HARRINGTON'


# In[2]:


fecha = str(datetime.date.today())
ipath = f'./Salida/Harrington{fecha}.xlsx'
df_harrington = pd.read_excel(ipath)


# In[3]:


server = 'tcp:192.168.1.6'
database ="planeamiento"
username = 'sa'
password = 'sa'
cnxn = pyodbc.connect('DRIVER={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.2.so.0.1};SERVER='+server+
                      ';DATABASE='+database+
                      ';UID='+username+
                      ';PWD='+ password) 


# In[4]:


maxCorrida = "select max(id_sc3_corrida)+1 from sc3_detalle where origen ='HARRINGTON UY' "
maxCorrida = pd.read_sql(maxCorrida,cnxn) 


# In[23]:


maxCorrida = int(maxCorrida[""][0])


# In[5]:


TIPOLOGIA = ['Remera','Camisa','Pantalón','Pantalon','Bermuda','Campera','Jean','Short','T-shirt','Sweater','Chaleco','Cardigan',
             'Sobretodo','Saco','Traje','Montgomery']

TIPOLOGIA = list(map(lambda x: x.upper(),TIPOLOGIA))


# In[6]:


df_harrington['Tipo'] = 0


# In[13]:


df_harrington.loc[df_harrington['Descripcion']=='T','Descripcion'] = "T-Shirt A Rayas Harrington Label"
df_harrington.loc[df_harrington['Descripcion']=='T-Shirt A Rayas Harrington Label','Color'] = "Gris/blanco"
#'T-Shirt A Rayas Harrington Label'
#https://www.harrington.com.uy/catalogo/t-shirt-a-rayas-harrington-label-gris-blanco_520709_000217


# In[14]:


for index, row in df_harrington.iterrows():
    for TIPO in TIPOLOGIA:
        if row['Descripcion'].upper().find(TIPO) != -1 :
            df_harrington.loc[index,'Tipo'] = TIPO


# In[15]:


for index, row in df_harrington.iterrows():
    
    if row['Descripcion'].find('Panatlon') != -1:
        df_harrington.loc[index,'Tipo'] = 'PANTALON'
    if row['Tipo'] =='PANTALÓN':
        df_harrington.loc[index,'Tipo'] = 'PANTALON'


# In[16]:


df_harrington["Precio Nuevo"] = [precio.split('$U')[2].strip() if len(precio.split('$U'))==3 else precio.split('$U')[1] for precio in df_harrington["Precio"]]
df_harrington["Precio Anterior"] = [precio.split('$U')[1].strip() for precio in df_harrington["Precio"]]


# In[17]:


df_harrington['Precio Nuevo'] = (df_harrington["Precio Nuevo"]
                         .str.extract(r"([\d,\.]+)", expand=False)
                         .str.replace(".", "")
                         .astype(float))


# In[18]:


df_harrington['Precio Anterior'] = (df_harrington["Precio Anterior"]
                         .str.extract(r"([\d,\.]+)", expand=False)
                         .str.replace(".", "")
                         .astype(float))


# In[19]:


df_harrington['TIPO_AUX'] = df_harrington['Tipo']
df_harrington['COLOR_AUX'] = df_harrington['Color']


# In[20]:


if len(df_harrington[df_harrington['Tipo']==0]) !=0:
    print(f"REVISAR {scraper} condicion >> (Tipo == 0 > 0) ")
    raise 


# In[21]:


df_harrington['Origen'] ='HARRINGTON UY'

df_harrington = df_harrington.drop_duplicates()
df_harrington = df_harrington.dropna()
# In[26]:


cursor = cnxn.cursor()
for index,row in df_harrington.iterrows():                                                            
    cursor.execute("INSERT INTO sc3_detalle([id_sc3_producto],[id_sc3_corrida],[marca],[tipo],[tipo_es],[color],[color_es],[sexo],[descripcion],[moneda],[precio],[precio_original],[fecha_alta],[url_imagen],[url_producto],[origen]) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", 
                   row['id Producto'], 
                   maxCorrida,
                   row['Marca'],
                   row['Tipo'],
                   row['TIPO_AUX'],
                   row['Color'],
                   row['COLOR_AUX'],
                   row['Sexo'],
                   row['Descripcion'], 
                   row['Moneda'],
                   row['Precio Nuevo'], 
                   row['Precio Anterior'], 
                   row['Fecha'],
                   row['Url Imagen'], 
                   row['Url Producto'],
                   row['Origen']) 
    cnxn.commit()
cursor.close()
cnxn.close()



end_ = datetime.datetime.today()

print(f'Inserts {scraper} en : {end_-start_}')



#!jupyter nbconvert --to script 'Cocot_insert.ipynb'

