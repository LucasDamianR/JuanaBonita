
# coding: utf-8


import pandas as pd
import pyodbc
import numpy as np
from pandas import ExcelWriter
import datetime
start_ = datetime.datetime.today()
scraper='SISI'


# In[2]:


fecha = str(datetime.date.today())
ipath = f'./Salida/sisi{fecha}.xlsx'
df_sisi = pd.read_excel(ipath)


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


maxCorrida = "select max(id_sc3_corrida)+1 from sc3_detalle where origen ='SISI UY' "
maxCorrida = pd.read_sql(maxCorrida,cnxn) 


# In[5]:


maxCorrida = int(maxCorrida[""][0])


# In[6]:


df_sisi["Precio Nuevo"] = [precio.split('$')[2].strip() if len(precio.split('$'))==3 else precio.split('$')[1] for precio in df_sisi["precio"]]
df_sisi["Precio Anterior"] = [precio.split('$')[1].strip() for precio in df_sisi["precio"]]


# In[7]:


df_sisi['Precio Nuevo'] = (df_sisi["Precio Nuevo"]
                            .str.extract(r"([\d,\.]+)", expand=False)
                            .str.replace(".", "")
                            .astype(float))


# In[8]:


df_sisi['Precio Anterior'] = (df_sisi["Precio Anterior"]
                               .str.extract(r"([\d,\.]+)", expand=False)
                               .str.replace(".", "")
                               .astype(float))


# In[9]:


df_sisi['TIPO_AUX'] = df_sisi['tipo']
df_sisi['COLOR_AUX'] = df_sisi['color']


# In[10]:


df_sisi['moneda'] = 'PESOS UY'


df_sisi = df_sisi.drop_duplicates()
df_sisi = df_sisi.dropna()

cursor = cnxn.cursor()
for index,row in df_sisi.iterrows():                                                            
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


# In[ ]:


end_ = datetime.datetime.today()

print(f'Inserts {scraper} en : {end_-start_}')

