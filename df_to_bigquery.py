from google.cloud import storage
import pandas as pd
from logo_analysis import df_logo,create_apariciones_table
from text_analysis import text_to_df
from audio_analysis import audio_to_df
import os
from google.cloud import bigquery
from google.oauth2 import service_account
from pandas_gbq import to_gbq
import re

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'vertexai-403121-4e2613b93cf2.json'
credentials = service_account.Credentials.from_service_account_file('vertexai-403121-4e2613b93cf2.json')

def df_to_bigquery(carpeta_en_bucket):


    # Dividir la cadena por "/"
    parts = carpeta_en_bucket.split("/")
    # Seleccionar las partes que deseas a partir de la tercera posición en adelante
    carpeta_en_bucket = "/".join(parts[3:-1])+"/"
    print( "Carpeta en Bucket: ",carpeta_en_bucket)

    client = bigquery.Client()
    project_id = client.project

    client_storage = storage.Client()
    bucket_name =  'videos_online'

    bucket = client_storage.get_bucket(bucket_name)
    # Obtener una lista de blobs en el bucket con la ruta de la carpeta especificada
    blobs_list = list(bucket.list_blobs(prefix=carpeta_en_bucket))
    
    cliente_match = match = re.search(r'\d+/(.*?)/Videos', carpeta_en_bucket)
    cliente = cliente_match.group(1) if cliente_match else None

    print ("Cliente: ",cliente)
    

    data, informe_texto = df_logo(blobs_list,carpeta_en_bucket,cliente)
    apariciones = create_apariciones_table(blobs_list, carpeta_en_bucket, cliente)
    df_texto, df_general,hola= text_to_df(blobs_list,cliente)
    content_audio_contexto = audio_to_df(blobs_list,cliente)

    data.rename(columns={
    'Nombre Archivo': 'Nombre_Archivo',
    'Aparece el logo': 'Aparece_el_logo',
    'Aparece antes de los 3s': 'Aparece_antes_de_los_3s',
    'Primera aparicion': 'Primera_aparicion',
    'Contador de apariciones': 'Contador_de_apariciones',
    'Link': 'Link',
    'Cliente': 'Cliente',
    'timestamp': 'timestamp'
    }, inplace=True)

    informe_texto.rename(columns={
        'total Videos': 'total_Videos',
        'total videos con logo': 'total_videos_con_logo',    
        'total apariciones':'total_apariciones',
        'Cliente': 'Cliente',
        'timestamp': 'timestamp'
    }, inplace=True)

    df_texto.rename(columns={
        'Video': 'Video',
        'Texto': 'Texto',
        'Cantidad Total de Palabras':'Cantidad_Total_Palabras',    
        'Cliente': 'Cliente',
        'timestamp': 'timestamp'
    }, inplace=True)

    df_general.rename(columns={
        'Video': 'Video',
        'Texto Combinado': 'Texto_Combinado',    
        'Cliente': 'Cliente',
        'timestamp': 'timestamp'
    }, inplace=True)

    content_audio_contexto.rename(columns={
        'Video': 'Video',
        'Tiempo Inicio': 'Tiempo_Inicio',
        'Tiempo Fin': 'Tiempo_Fin',
        'Tag Name': 'Tag_Name',
        'Tag Number': 'Tag_Number',    
        'Cliente': 'Client',
        'timestamp': 'timestamp'
    }, inplace=True)

    # data['Contador_de_apariciones'] = pd.to_numeric(data['Contador_de_apariciones'], errors='coerce', downcast='integer')
    # data['Primera_aparicion'] = pd.to_datetime(data['Primera_aparicion'], format='%M:%S').dt.time

    # Verifica si el DataFrame tiene datos antes de realizar operaciones adicionales
    if not data.empty:
        data['Contador_de_apariciones'] = pd.to_numeric(data['Contador_de_apariciones'], errors='coerce', downcast='integer')
        data['Primera_aparicion'] = pd.to_datetime(data['Primera_aparicion'], format='%M:%S').dt.time
    else:
        print("El DataFrame 'data' está vacío. Verifica la obtención de datos antes de realizar conversiones.")

    #apariciones['Tiempo_aparicion'] = pd.to_datetime(apariciones['Tiempo_aparicion'], format='%M:%S').dt.time
    # Verifica si el DataFrame tiene datos antes de realizar operaciones adicionales
    if not apariciones.empty:
        apariciones['Tiempo_aparicion'] = pd.to_datetime(apariciones['Tiempo_aparicion'], format='%M:%S').dt.time
    else:
        print("El DataFrame 'apariciones' está vacío. Verifica la función create_apariciones_table.")




    table_name_data = 'data_logo'
    dataset_name = 'data'


    to_gbq(apariciones, destination_table=f'{project_id}.data.logo_apariciones', if_exists='append', credentials=credentials, project_id=project_id)
    to_gbq(informe_texto, destination_table=f'{project_id}.data.data_logo_general', if_exists='append', credentials=credentials, project_id=project_id)
    to_gbq(df_texto, destination_table=f'{project_id}.data.data_texto', if_exists='append', credentials=credentials, project_id=project_id)
    to_gbq(df_general, destination_table=f'{project_id}.data.data_texto_general', if_exists='append', credentials=credentials, project_id=project_id)
    to_gbq(content_audio_contexto, destination_table=f'{project_id}.data.data_audio_contexto', if_exists='append', credentials=credentials, project_id=project_id)
    to_gbq(data, f'{project_id}.{dataset_name}.{table_name_data}', if_exists='append', credentials=credentials)


#df_to_bigquery('2023/Didi/Videos/Caito')





