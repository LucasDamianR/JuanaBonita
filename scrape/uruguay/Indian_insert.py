
# coding: utf-8

# In[1]:


import pandas as pd
import pyodbc
import numpy as np
from pandas import ExcelWriter
import datetime
start_ = datetime.datetime.today()
scraper = 'INDIAN'


# In[2]:


fecha = str(datetime.date.today())
ipath = f'./Salida/indian{fecha}.xlsx'
df_indian = pd.read_excel(ipath)


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


maxCorrida = "select max(id_sc3_corrida)+1 from sc3_detalle where origen ='INDIAN UY' "
maxCorrida = pd.read_sql(maxCorrida,cnxn) 


# In[5]:


maxCorrida = int(maxCorrida[""][0])


# In[6]:


for index,row in df_indian.iterrows():
    if row['tipo'] =='NONE':
        df_indian.loc[index,'tipo'] = row['descripcion'].split()[0].upper()
        


# In[69]:


df_indian['color'] = df_indian['descripcion'].apply(lambda x : x.split('-')[-1])    


# In[70]:


for index,row in df_indian.iterrows():
    split_desc = row['color'].split()[-1]
    
    if len(split_desc) <= 2:
        
        df_indian.loc[index,'color'] = row['color'][:row['color'].find(row['color'].split()[-1])].strip()


# In[72]:


df_indian['TIPO_AUX'] = df_indian['tipo']
df_indian['COLOR_AUX'] = df_indian['color']


# In[75]:


df_indian['moneda'] = 'PESOS UY'

df_indian.drop('precio_original',axis=1,inplace=True)
df_indian.drop('precio_dto',axis=1,inplace=True)

df_indian['precio_original'] = 0
df_indian['precio_dto'] = 0

for index,row in df_indian.iterrows():
    
    SPLIT = row['precio'].split('$')
    if len(SPLIT) == 2:
        df_indian.loc[index,'precio_original'] = SPLIT[1]
        df_indian.loc[index,'precio_dto'] = SPLIT[1]
        
    if len(SPLIT) == 3:
        df_indian.loc[index,'precio_original'] = SPLIT[1]
        df_indian.loc[index,'precio_dto'] = SPLIT[2]
        
    

df_indian['precio_original'] = df_indian['precio_original'].apply(lambda x:x.replace('.',''))
df_indian['precio_dto'] = df_indian['precio_dto'].apply(lambda x:x.replace('.',''))

df_indian['precio_dto'] = (df_indian["precio_dto"]
                            .str.extract(r"([\d,\.]+)", expand=False)
                            .str.replace(".", "")
                            .astype(float))

df_indian['precio_original'] = (df_indian["precio_original"]
                               .str.extract(r"([\d,\.]+)", expand=False)
                               .str.replace(".", "")
                               .astype(float))


df_indian= df_indian.drop_duplicates()

df_indian = df_indian.dropna()

cursor = cnxn.cursor()
for index,row in df_indian.iterrows():                                                            
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


# In[1]:


#!jupyter nbconvert --to script 'Indian_insert.ipynb'

