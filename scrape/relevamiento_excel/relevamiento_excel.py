#!/usr/bin/env python
# coding: utf-8

import odbc
import win32com.client
import pandas as pd
import pyodbc
import pickle
import datetime

try:
    f = open("revivir.txt","rb")
    REVIVIR = f.read()
    REVIVIR = int(REVIVIR)
    f.close()
except:
    REVIVIR=0


def connection():
    server = 'tcp:192.168.1.6'
    database = 'planeamiento'
    username = 'sa'
    password = 'sa'

    return pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)


def check_excel(file,excel_id,index,start_processing_date):
    global output
    #xl = win32com.client.gencache.EnsureDispatch('Excel.Application')
    #file = r'C:\Users\lrojas\Desktop\Copia de archivo de ejemplo.xlsx'
#    file = f'r{path}'
    try:
        xl = win32com.client.Dispatch('Excel.Application')
        xl.DisplayAlerts = False
        xl.EnableEvents = False
        try:
            #wb = xl.Workbooks.Open(file, None,True)
            #wb = xl.Workbooks.Open(Filename=file,CorruptLoad=True,Editable=False,ReadOnly=True)
            #wb = xl.Workbooks.Open(Filename=file,IgnoreReadOnlyRecommended=True,CorruptLoad=True,Editable=False,ReadOnly=True)
            #wb = xl.Workbooks.Open(Filename=file,IgnoreReadOnlyRecommended=True,CorruptLoad=True,ReadOnly=True)
            wb = xl.Workbooks.Open(file, None, True)

        except Exception as e:
            #print(e)
            #xl.Application.Quit()
            return e , []

        datos = []
        try:
            for x in wb.Connections:
                for i in x.Ranges:
                    try:
                        #PRIMER DATO QUE TRAE LA PRIMER CELDA
                        celda = i.Cells(1,1)
                        #LA COORDENADA DE LA PRIMER CELDA
                        coordenada = i.Cells(1,1).Address
                    except Exception as p:
                        print(p)
                    try:
                        for o in x.Ranges(1).QueryTable.Parameters:

                            end_processing_date = datetime.datetime.today()
                            datos.append([x,
                                          x.ODBCConnection.CommandText,
                                          x.ODBCConnection.Connection,
                                          i.Parent.Name,
                                          celda,
                                          coordenada,
                                          o.SourceRange.Address,
                                          o.SourceRange.Parent.Name,
                                          o.SourceRange.Value,
                                          excel_id,
                                          index,
                                          start_processing_date,
                                          end_processing_date
                                         ])
                        flag = 1
                    except:
                        flag = 0
                    if flag == 0:

                        try:
                            if len(i.ListObject.QueryTable.Parameters) != 0:

                                for p in i.ListObject.QueryTable.Parameters:
                                    
                                    end_processing_date = datetime.datetime.today()
                                    datos.append([x,
                                                  x.ODBCConnection.CommandText,
                                                  x.ODBCConnection.Connection,
                                                  i.Parent.Name,
                                                  celda,
                                                  coordenada,
                                                  p.SourceRange.Address,
                                                  p.SourceRange.Parent.Name,
                                                  p.SourceRange.Value,
                                                  excel_id,
                                                  index,
                                                  start_processing_date,
                                                  end_processing_date
                                                 ])
                            else:
                                end_processing_date = datetime.datetime.today()
                                datos.append([x,
                                              x.ODBCConnection.CommandText,
                                              x.ODBCConnection.Connection,
                                              i.Parent.Name, #EDIT None
                                              celda,
                                              coordenada,
                                              None,
                                              None,
                                              None,
                                              excel_id,
                                              index,
                                              start_processing_date,
                                              end_processing_date
                                             ])

                        except Exception as e:
                            try:
                                end_processing_date = datetime.datetime.today()
                                datos.append([x,
                                              x.ODBCConnection.CommandText,
                                              x.ODBCConnection.Connection,
                                              i.Parent.Name,
                                              celda,
                                              coordenada,
                                              None,
                                              None,
                                              None,
                                              excel_id,
                                              index,
                                              start_processing_date,
                                              end_processing_date
                                             ])
                            except:
                                try:
                                    if len(i.ListObject.QueryTable.Parameters) != 0:

                                        for p in i.ListObject.QueryTable.Parameters:
                                            end_processing_date = datetime.datetime.today()
                                            datos.append([x,
                                                          x.OLEDBConnection.CommandText,
                                                          x.OLEDBConnection.Connection,
                                                          i.Parent.Name,
                                                          celda,
                                                          coordenada,
                                                          p.SourceRange.Address,
                                                          p.SourceRange.Parent.Name,
                                                          p.SourceRange.Value,
                                                          excel_id,
                                                          index,
                                                          start_processing_date,
                                                          end_processing_date
                                                         ])
                                    else:
                                        end_processing_date = datetime.datetime.today()
                                        datos.append([x,
                                                      x.ODBCConnection.CommandText,
                                                      x.ODBCConnection.Connection,
                                                      i.Parent.Name, #EDIT None
                                                      celda,
                                                      coordenada,
                                                      None,
                                                      None,
                                                      None,
                                                      excel_id,
                                                      index,
                                                      start_processing_date,
                                                      end_processing_date
                                                     ])

                                except:
                                    try:
                                        end_processing_date = datetime.datetime.today()
                                        datos.append([x,
                                                      x.OLEDBConnection.CommandText,
                                                      x.OLEDBConnection.Connection,
                                                      i.Parent.Name,
                                                      celda,
                                                      coordenada,
                                                      None,
                                                      None,
                                                      None,
                                                      excel_id,
                                                      index,
                                                      start_processing_date,
                                                      end_processing_date
                                                     ])
                                    except:      
                                        end_processing_date = datetime.datetime.today()
                                        datos.append([x,
                                                  None,
                                                  None,
                                                  i.Parent.Name,
                                                  celda,
                                                  coordenada,
                                                  None,
                                                  None,
                                                  None,
                                                  excel_id,
                                                  index,
                                                  start_processing_date,
                                                  end_processing_date
                                                     ])

            

        except Exception as c:
            return c , []

        end_processing_date = datetime.datetime.today()
        #df = pd.DataFrame(datos)
        #df = df.applymap(str)
        #datos = map(str,datos)
        if datos == []:
            datos.append(['None',
                          'None',
                          'None',
                          'None',
                          'None',
                          'None',
                          'None',
                          'None',
                          'None',
                           excel_id,
                           index,
                           start_processing_date,
                           end_processing_date])
        elif type(datos[0]) == list:
            datos = [list(map(str,i))for i in datos]

        else:
            datos = list(map(str,datos))
    #    xl.DisplayAlerts = False
    
        if type(datos[0]) == str:
            
            output +=[datos]
        else:
            output += datos

        
        try:
            #wb.Close(0)
            #wb.Close(False)
            #wb.Close(SaveChanges=0)
            xl.ActiveWorkbook.Saved = True
            xl.ActiveWorkbook.Close
            #wb.Close(SaveChanges=0,Filename=file)
        except:
            wb.Close(SaveChanges = False)
            #wb.Close(SaveChanges = False,Filename=file)
        xl.Application.Quit()

        #return df
        return 0
    except Exception as G:
        return G,[]


    
cnxn = connection()
query = 'select * from planeamiento..ctrl_excel with(nolock) where end_processing_date is null'

df = pd.read_sql(query,cnxn)
cnxn.close()

#Vamos a levantar los errores anteriores y vamos a relevar los excels_id que no estan en la lista de errores.

errores = pd.read_excel('full_errores.xlsx')

#Buscamos los excel_id que no se encuentran en errores
df = df[~df['excel_id'].isin(errores[0])].reset_index(drop=True)


ESCOPETAZO = True

output = []
errores = []
#Definimos el tiempo de inicio del proceso completo.
start = datetime.datetime.today()
#df.loc[REVIVIR:]
for index,row in df.loc[REVIVIR:].iterrows(): 
    #archivo es por ej: z:/.../planeamiento/rotulos.xlsx
    archivo = row['path']+row['filename']
    
    #definimos el tiempo que va a inicializar el procesamiento de un archivo excel.
    start_processing_date = datetime.datetime.today()
    
    #llamamos a la función y le pasamos los parametros necesarios.
    result = check_excel(archivo,row['excel_id'],index,start_processing_date)
    
    #Si la función result devuelve != 0, significa que hubo un error, entonces tenemos que identificarlo.
    if result != 0:
        
        errores.append([row['excel_id'],archivo,result,index])
            
    else:
        pass
    #Cada 50 vueltas del iterrows(), va a guardar un archivo .xlsx
    if int(index/50) == index/50:
        
        # guardo un xlsx temporal con los datos obtenidos hasta el momento.
        pd.DataFrame(output).to_excel('temp_output.xlsx')
        
        #Si existen errores, vamos a identificarlos y guardalos en un .xlsx llamado "temp_errores", para luego
        #investigar el motivo del mismo.
        if len(errores) > 0:
            pd.DataFrame(errores).to_excel('temp_errores.xlsx')
            
#End es el tiempo final que ejecuto todo el script.        
end = datetime.datetime.today()
print(end-start)
        
#Este booleano es para  avisarle al script Killer.py que ya tiene que salir del While y terminar su ejecución.
ESCOPETAZO = False
#Guardamos en un pkl el booleano que va a recibir el script Killer.py
pickle.dump(ESCOPETAZO , open("ESCOPETAZO.pkl","wb"))

hoy = datetime.date.today()
pd.DataFrame(output).to_excel(f'relevamiento_excel-{hoy}.xlsx')


