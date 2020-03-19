#!/usr/bin/env python
# coding: utf-8

import odbc
import win32com.client
import pandas as pd
import pyodbc
import pickle
import datetime

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

