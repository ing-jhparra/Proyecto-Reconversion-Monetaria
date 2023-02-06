#!/usr/bin/python3
import pandas as pd
from datetime import datetime

import psycopg2 #Postgres

#Definiciones
driver = 'psql'
usuario = 'reconversion_user'
credenciales = '12345678'
server = '34.206.176.180'
puerto = '5432'
dbname = db = 'sanos'


formula = 'ROUND({}/1000000,2)'
scriptsSQL = []

ruta = '/home/dba/Documentos/personal/laboratorio/python/reconversion/sanos/'
diccionariocsv = ruta + 'diccionariosanos.csv'
updatescsv = ruta + 'updatessanos.csv'

select_distinct_diccionario = 'SELECT DISTINCT nombretabla,esquema FROM sanos_diccionario ORDER BY 2,1;'
select_campos_tablas = 'SELECT nombrecampo FROM sanos_diccionario WHERE nombretabla = \'{}\' ORDER BY 1;'

connection = psycopg2.connect(user = usuario, password = credenciales, host = server, port = puerto, database = dbname)

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
        tablas.append(list(data[t])[1]+'.'+list(data[t])[0])
        
    # Extraer los campos por cada tabla
    camposxtablas = []
    for t in range(len(tablas)):
        registro = []
        cursor.execute(select_campos_tablas.format(tablas[t].split('.')[1]))
        data = cursor.fetchall()
        #Tablas con uno o mas campos
        if len(data) > 0:
              registro.append(tablas[t])
              print('Extrayendo ................ +++ {} '.format(tablas[t]))
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
    tiempo_inicial = datetime.now()
    try :
        cursor = connection.cursor()
        leer_tabla_diccionario (cursor)
    except (Exception, psycopg2.Error) as error :
        print ("Error mientras se conecta al Servidor PostgreSQL Server ... Error nro.: ", error.args[0])
    finally:
        #Cerrar conexion
        if(connection):
            cursor.close()
            connection.close()
            tiempo_final = datetime.now()
            print('Proceso de reconversion finalizada, tiempo estimado de reconversion : ', tiempo_final - tiempo_inicial)

if __name__ == '__main__':
    iniciar()
