#!/usr/bin/python3

"""
********************************************************************
* Author : Jesus Parra
  Github = https://github.com/jhparra777                         *
* Date = '6-02-2023'                                              *
* Description = Streamlit App - Oil Stations  - Funtions           *
********************************************************************
"""

import pandas as pd
from datetime import datetime
import csv
import time
import pyodbc   #SQL Server

# Definiciones

db = 'CDHBS'

ruta = '/home/dba/Documentos/personal/laboratorio/python/reconversion/gp/'
diccionariocsv = ruta + 'diccionarioHigea.csv'
updatescsv = ruta + 'updatesHigea.csv'

connection = pyodbc.connect("Driver={ODBC Driver 17 for SQL Server};"
            "Server=54.81.168.58\SERVERGP,1433;"
            "Database=CDHBS;"
            "uid=reconversion_user;"
            "pwd=12345678;")

#Se sugiere ejecutar el store procedure desde el servidor
#execute_storeprocedure = 'DECLARE @resultado INT; \
#                          EXECUTE ' + db + '..TablasNoVaciasV2 @resultado OUTPUT;\
#                          SELECT @resultado AS Resultado;'

#formula = 'ROUND({}/1000000,5)'
# CAST(ROUND(2325456.4566/1000000.0, 5) AS NUMERIC(19,2))
formula = 'CAST(ROUND({}/1000000.0, 5) AS NUMERIC(19,2))'
scriptsSQL = []

#select_diccionario = 'SELECT * FROM tempdb..Diccionario;'
select_distinct_diccionario = 'SELECT DISTINCT nombretabla FROM tempdb..CDHDiccionario ORDER BY 1;'
select_campos_tablas = 'SELECT nombrecampo FROM tempdb..CDHDiccionario WHERE nombretabla = \'{}\' AND espk != 1 ORDER BY 1;'

def leer_tabla_diccionario (cursor): 
    #Ejecutar store procedure para crear la tabla Diccionario con los campos nombretabla, nombrecampo, espk
    #cursor.execute(execute_storeprocedure)
    #time.sleep(360)
    #input('Teclee cualquier tecla para continuar ...')
    cursor.execute(select_distinct_diccionario)
    data = cursor.fetchall()
    tablas = []

    # Extrar solo las tablas
    for t in range(len(data)):
        tablas.append(list(data[t]))

    # Extraer los campos por cada tabla
    camposxtablas = []
    for t in range(len(tablas)):
        registro = []
        cursor.execute(select_campos_tablas.format(tablas[t][0]))
        data = cursor.fetchall()
        #Tablas con uno o mas campos
        if len(data) > 0:
            registro.append(tablas[t][0])
            print('Extrayendo ................ +++ {} '.format(tablas[t][0]))
            for c in range(len(data)):
                registro.append(data[c][0])
            camposxtablas.append(registro)

    print('Creando archivos ...  ')        
    diccionario = open(diccionariocsv, "w")
    scriptsupdates = open(updatescsv, "w")
    for t in range(len(camposxtablas)):
        estructura = camposxtablas[t][0]
        sentenciaSQL = 'UPDATE ' + camposxtablas[t][0] + ' SET '
        for c in range(1,len(camposxtablas[t])):
            sentenciaSQL += camposxtablas[t][c] + ' = ' + formula.format(camposxtablas[t][c]) + ', '
            estructura += ',' + camposxtablas[t][c]
        scriptsSQL.append(sentenciaSQL[:-2] + ';')
        diccionario.write(estructura + '\n')
        scriptsupdates.write(sentenciaSQL[:-2] + ';' + '\n')
    diccionario.close()
    scriptsupdates.close()

    print('Iniciando ejecucion de updates ...  ')
    for i in range(len(scriptsSQL)):
        print(scriptsSQL[i])
        cursor.execute(scriptsSQL[i])
        connection.commit()
      
def iniciar():

    print('Iniciando proceso para reconvertir base de datos {}'.format(db))
    tiempo_inicial = datetime.now()
    try :
        cursor = connection.cursor()
        leer_tabla_diccionario(cursor)
    except pyodbc.Error as error :
        print ("Error mientras se conecta al Servidor SQL Server ... Error nro.: ", error.args[0])
    finally :
        #Cerrar conexion
        if (connection) :
            cursor.close()
            connection.close()
            tiempo_final = datetime.now()
            print('Proceso de reconversion finalizada, tiempo estimado de reconversion : ', tiempo_final - tiempo_inicial)


if __name__ == '__main__':
    iniciar()

#FUENTE
#https://www.easysoft.com/developer/languages/python/examples/CallSPWithInOutParams.html


