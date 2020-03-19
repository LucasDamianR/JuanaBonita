
# coding: utf-8

# In[70]:


import pandas as pd
import pyodbc
import numpy as np
from pandas import ExcelWriter
import datetime
start_ = datetime.datetime.today()
scraper='LOLITA'


# In[71]:


fecha = str(datetime.date.today())
ipath = f'./Salida/lolita{fecha}.xlsx'
df_lolita = pd.read_excel(ipath)


# In[72]:


server = 'tcp:192.168.1.6'
database ="planeamiento"
username = 'sa'
password = 'sa'
cnxn = pyodbc.connect('DRIVER={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.2.so.0.1};SERVER='+server+
                      ';DATABASE='+database+
                      ';UID='+username+
                      ';PWD='+ password) 


# In[73]:


maxCorrida = "select max(id_sc3_corrida)+1 from sc3_detalle where origen ='LOLITA UY' "
maxCorrida = pd.read_sql(maxCorrida,cnxn) 


# In[74]:


maxCorrida = int(maxCorrida[""][0])


# In[75]:


df_lolita['precio'] = df_lolita['precio'].apply(lambda x : x.replace('.',''))


# In[76]:


df_lolita["precio_dto"] = [precio.split('UYU')[2].strip() if len(precio.split('UYU'))==3 else precio.split('UYU')[1] for precio in df_lolita["precio"]]
df_lolita["precio_original"] = [precio.split('UYU')[1].strip() for precio in df_lolita["precio"]]


# In[77]:


df_lolita['tipo'] = df_lolita['descripcion'].apply(lambda x: x.split()[1] if x.split()[0] == 'Maxi' else x.split()[0])    


# In[78]:


df_lolita['TIPO_AUX'] = df_lolita['tipo']
df_lolita['COLOR_AUX'] = df_lolita['color']
df_lolita['moneda'] = 'PESOS UY'
df_lolita['sexo'] = 'Mujer'


# In[79]:


df_lolita = df_lolita.dropna()


# In[80]:


df_lolita = df_lolita.drop_duplicates()


# In[81]:


df_lolita['precio_dto'] = (df_lolita['precio_dto'].str.extract(r"([\d,\.]+)", expand=False)
                               .str.replace(".", "")
                               .astype(float))


df_lolita['precio_original'] = (df_lolita['precio_original'].str.extract(r"([\d,\.]+)", expand=False)
                               .str.replace(".", "")
                               .astype(float))


# In[ ]:


cursor = cnxn.cursor()
for index,row in df_lolita.iterrows():                                                            
    cursor.execute("INSERT INTO sc3_detalle([id_sc3_producto],[id_sc3_corrida],[marca],[tipo],[tipo_es],[color],[color_es],[sexo],[descripcion],[moneda],[precio],[precio_original],[fecha_alta],[url_imagen],[url_producto],[origen]) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", 
                   row['codigo'], 
                   maxCorrida,
                   row['marca'],
                   row['tipo'],
                   row['TIPO_AUX'],
                   row['color'],
                   row['COLOR_AUX'],
                   row['sexo'],
                   row['descripcion'], 
                   row['moneda'],
                   row['precio_dto'], 
                   row['precio_original'], 
                   row['fecha'],
                   row['img_producto'], 
                   row['url_producto'],
                   row['origen']) 
    cnxn.commit()
cursor.close()
cnxn.close()


# In[ ]:


end_ = datetime.datetime.today()

print(f'Inserts {scraper} en : {end_-start_}')


# In[102]:


#!jupyter nbconvert --to script 'Lolita_insert.ipynb'

