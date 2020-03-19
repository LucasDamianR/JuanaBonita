
# coding: utf-8

# In[8]:


import pandas as pd
import pyodbc
import numpy as np
from pandas import ExcelWriter
import datetime
start_ = datetime.datetime.today()
scraper='COCOT'


# In[2]:


fecha = str(datetime.date.today())
ipath = f'./Salida/cocot{fecha}.xlsx'
df_cocot = pd.read_excel(ipath)


# In[26]:


server = 'tcp:192.168.1.6'
database ="planeamiento"
username = 'sa'
password = 'sa'
cnxn = pyodbc.connect('DRIVER={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.2.so.0.1};SERVER='+server+
                      ';DATABASE='+database+
                      ';UID='+username+
                      ';PWD='+ password) 


# In[5]:


maxCorrida = "select max(id_sc3_corrida)+1 from sc3_detalle where origen ='COCOT UY' "
maxCorrida = pd.read_sql(maxCorrida,cnxn) 


# In[6]:


maxCorrida = int(maxCorrida[""][0])


# In[8]:


df_cocot["Precio Nuevo"] = [precio.split('$')[2].strip() if len(precio.split('$'))==3 else precio.split('$')[1] for precio in df_cocot["precio"]]
df_cocot["Precio Anterior"] = [precio.split('$')[1].strip() for precio in df_cocot["precio"]]


# In[9]:


df_cocot['Precio Nuevo'] = (df_cocot["Precio Nuevo"]
                            .str.extract(r"([\d,\.]+)", expand=False)
                            .str.replace(".", "")
                            .astype(float))


# In[10]:


df_cocot['Precio Anterior'] = (df_cocot["Precio Anterior"]
                               .str.extract(r"([\d,\.]+)", expand=False)
                               .str.replace(".", "")
                               .astype(float))


# In[11]:


df_cocot['TIPO_AUX'] = df_cocot['tipo']
df_cocot['COLOR_AUX'] = df_cocot['color']


# In[12]:


df_cocot['moneda'] = 'PESOS UY'


# In[13]:


df_cocot['marca'] = 'COCOT'


df_cocot= df_cocot.dropna()
df_cocot= df_cocot.drop_duplicates()


cursor = cnxn.cursor()
for index,row in df_cocot.iterrows():                                                            
    cursor.execute("INSERT INTO sc3_detalle([id_sc3_producto],[id_sc3_corrida],[marca],[tipo],[tipo_es],[color],[color_es],[sexo],[descripcion],[moneda],[precio],[precio_original],[fecha_alta],[url_imagen],[url_producto],[origen]) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", 
                   row['codigo'], 
                   maxCorrida,
                   row['marca'],
                   row['tipo'],
                   row['TIPO_AUX'],
                   row['color'],
                   row['COLOR_AUX'],
                   row['sexo'],
                   row['DESC'], 
                   row['moneda'],
                   row['Precio Nuevo'], 
                   row['Precio Anterior'], 
                   row['fecha'],
                   row['img_producto'], 
                   row['url_producto'],
                   row['origen']) 
    cnxn.commit()
cursor.close()
cnxn.close()


# In[9]:


end_ = datetime.datetime.today()


# In[16]:


print(f'Inserts {scraper} en : {end_-start_}')


# In[ ]:


#!jupyter nbconvert --to script 'Cocot_insert.ipynb'

