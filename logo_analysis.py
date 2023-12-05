import pandas as pd
from io import BytesIO
from reportlab.platypus import Table
from reportlab.lib import colors
from reportlab.platypus import  Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
#import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.graphics.shapes import Drawing,String
from reportlab.graphics.charts.piecharts import Pie
from link import link_mp4,extract_info_from_mp4
import pyshorteners
import re

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def analyze_logo(blobs_list,carpeta_en_bucket,cliente):

    total_videos_con_logo = 0
    total_apariciones_antes_3s = 0
    content_general = []
    

    table_style = [
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Límites y color de la cuadrícula
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Fondo de la primera fila
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Color del texto en la primera fila
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('SPACEAFTER', (0, 0), (-1, -1), 24),
        ('FONTSIZE', (0, 0), (-1, -1), 8),  
    ]

    # Inicializar df_general como DataFrame vacío
    df_general = pd.DataFrame(columns=['Nombre Archivo', 'Aparece el logo', 'Aparece antes de los 3s', 'Primera aparicion', 'Contador de apariciones','Link'])
    for blob in blobs_list:
        tanda_info, video_id = extract_info_from_mp4(blob)
        if 'logo' in blob.name.lower() and blob.name.lower().endswith('.csv'):
            contenido_csv_bytes = blob.download_as_bytes()
            df = pd.read_csv(BytesIO(contenido_csv_bytes))
            mercado_libre_data = df[df['entidad'] == cliente]

            aparece_logo = 'No'
            aparece_antes_3s = 'No'
            tiempo_aparicion = None
            contador_apariciones = len(mercado_libre_data)

            if contador_apariciones > 0:
                aparece_logo = 'Sí'
                tiempo_aparicion_segundos = mercado_libre_data.iloc[0]['t_inicio']
                tiempo_aparicion = f"{int(tiempo_aparicion_segundos // 60)}:{int(tiempo_aparicion_segundos % 60):02d}"
                
                # Convertir tiempo_aparicion a segundos para la comparación
                tiempo_aparicion_en_segundos = tiempo_aparicion_segundos
                if tiempo_aparicion_en_segundos < 3:
                    aparece_antes_3s = 'Sí'
                    total_apariciones_antes_3s += 1

                total_videos_con_logo += 1

            nombre_archivo = blob.name.split('/')[-1].split('.')[0]
            mp4_link = f"https://storage.cloud.google.com/videos_online/{carpeta_en_bucket}{video_id}.mp4"
            s = pyshorteners.Shortener()
            mp4_link = s.tinyurl.short(mp4_link)

            # Crear un DataFrame para el archivo actual
            df_archivo = pd.DataFrame({
                'Nombre Archivo': [nombre_archivo],
                'Aparece el logo': [aparece_logo],
                'Aparece antes de los 3s': [aparece_antes_3s],
                'Primera aparicion': [tiempo_aparicion],
                'Contador de apariciones': [contador_apariciones],
                'Link':[mp4_link],
            })

            # Concatenar el DataFrame actual al DataFrame general
            df_general = pd.concat([df_general, df_archivo], ignore_index=True)

            # Crear el informe en formato de texto para cada video
            informe_texto = f"<b>Reporte de Videos para MercadoLibre - {nombre_archivo}</b><br/><br/>"
            informe_texto += f"En el video {nombre_archivo}: el logo {aparece_logo} aparece, con un total de {contador_apariciones} veces.<br/>"
            informe_texto += f"Aparece por primera vez a los {tiempo_aparicion} segundos.<br/>"
            informe_texto += f"Aparece antes de los 3 segundos: {aparece_antes_3s}"

    data = [df_general.columns.tolist()] + df_general.values.tolist()
    table = Table(data)
    table.setStyle(table_style)




    blobs_list_logo = [blob for blob in blobs_list if 'logo' in blob.name.lower()]
    total_videos = len(blobs_list_logo)
    data_total = [
        ["Videos analizados", total_videos],
        ["En cuántos videos aparece el logo", total_videos_con_logo],
        ["Total de apariciones antes de los 3 segundos", total_apariciones_antes_3s]
    ]
    tabla_informe_general = Table(data_total, style=table_style)

    # Agregar la tabla al contenido general
    content_general.append(tabla_informe_general)
    content_general.append(Spacer(1, 40)) 
    content_general.append(table)
    content_general.append(Spacer(1, 40)) 
    return content_general,total_videos,total_videos_con_logo,total_apariciones_antes_3s

def graph_pie_logo(total_videos,total_videos_con_logo):
    content_general = []
    try:
        plt.figure(figsize=(6, 6))
        plt.pie([total_videos_con_logo, total_videos - total_videos_con_logo],
                labels=['Con Logo', 'Sin Logo'],
                autopct='%1.1f%%',
                startangle=90,
                colors=['skyblue', 'lightcoral'])
        
        plt.title('Distribución de Videos con y sin Logo')
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        image_buffer = BytesIO()
        plt.savefig(image_buffer, format='png')
        content_general.append(Spacer(1, 24))
        content_general.append(Image(image_buffer, width=300, height=300))
        plt.close()

    except Exception as e:
        # Handle exceptions, print or log the error
        print(f"Error: {e}")
    return content_general


def logo_pie_3s(total_videos_con_logo,total_apariciones_antes_3s):
    content_general = []
    try:
        plt.figure(figsize=(6, 6))
        plt.pie([total_apariciones_antes_3s, total_videos_con_logo - total_apariciones_antes_3s],
                labels=['Antes de 3s', 'Después de 3s'],
                autopct='%1.1f%%',
                startangle=90,
                colors=['lightgreen', 'lightcoral'])
        plt.title('Distribución de Apariciones antes de 3s de los videos que tienen logo')
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        image_buffer = BytesIO()
        plt.savefig(image_buffer, format='png')
        content_general.append(Spacer(1, 12))
        content_general.append(Image(image_buffer, width=300, height=300))
        plt.close()
    except Exception as e:
        # Handle exceptions, print or log the error
        print(f"Error: {e}")
    return content_general

def logo_bar_chart(blobs_list,cliente):
    data_por_video = []
    content_general = []
    for blob in blobs_list:
        # Verificar si el nombre del archivo contiene la palabra 'logo' y es un archivo CSV
        if 'logo' in blob.name.lower() and blob.name.lower().endswith('.csv'):
            # Descargar el contenido del blob como bytes
            contenido_csv_bytes = blob.download_as_bytes()

            # Leer el contenido como DataFrame de pandas
            df = pd.read_csv(BytesIO(contenido_csv_bytes))

            # Filtrar por entidad 'MercadoLibre'
            mercado_libre_data = df[df['entidad'] == cliente]

            # Obtener el nombre del archivo sin la extensión
            nombre_archivo = blob.name.split('/')[-1].split('.')[0]

            # Obtener la cantidad de apariciones antes y después de los 3 segundos
            antes_3s = len(mercado_libre_data[mercado_libre_data['t_inicio'] < 3])
            despues_3s = len(mercado_libre_data[mercado_libre_data['t_inicio'] >= 3])

            # Agregar datos a la lista
            data_por_video.append({
                'Video': nombre_archivo,
                'Antes de 3s': antes_3s,
                'Después de 3s': despues_3s
            })

    df_por_video = pd.DataFrame(data_por_video)
    try:
        plt.figure(figsize=(10, 6))
        df_por_video.set_index('Video').plot(kind='bar', stacked=True, colormap='coolwarm')

        plt.xlabel('Videos')
        plt.ylabel('Cantidad de Apariciones')
        plt.title('Apariciones antes y después de 3 segundos')
        plt.legend(title='Tiempo')
        plt.tight_layout()

        image_buffer = BytesIO()
        plt.savefig(image_buffer, format='png')
        content_general.append(Image(image_buffer, width=400, height=300))
        plt.close()
    except Exception as e:
        # Handle exceptions, print or log the error
        print(f"Error: {e}")
    return content_general


def df_logo(blobs_list, carpeta_en_bucket,cliente):
    total_videos_con_logo = 0
    total_apariciones_antes_3s = 0
    match = re.search(r'Videos/(.+?)/', carpeta_en_bucket)

    if match:
        Tanda= match.group(1)
    else:
        Tanda= 'Videos/'
    # Inicializar df_general como DataFrame vacío
    df_general = pd.DataFrame(columns=['Nombre Archivo', 'Aparece el logo', 'Aparece antes de los 3s', 'Primera aparicion', 'Contador de apariciones', 'Link','Tanda'])

    for blob in blobs_list:
        tanda_info, video_id = extract_info_from_mp4(blob)
        if 'logo' in blob.name.lower() and blob.name.lower().endswith('.csv'):
            contenido_csv_bytes = blob.download_as_bytes()
            df = pd.read_csv(BytesIO(contenido_csv_bytes))
            mercado_libre_data = df[df['entidad'] == cliente]

            aparece_logo = 'No'
            aparece_antes_3s = 'No'
            tiempo_aparicion = None
            contador_apariciones = len(mercado_libre_data)

            if contador_apariciones > 0:
                aparece_logo = 'Sí'
                tiempo_aparicion_segundos = mercado_libre_data.iloc[0]['t_inicio']
                tiempo_aparicion = f"{int(tiempo_aparicion_segundos // 60)}:{int(tiempo_aparicion_segundos % 60):02d}"

                # Convertir tiempo_aparicion a segundos para la comparación
                tiempo_aparicion_en_segundos = tiempo_aparicion_segundos
                if tiempo_aparicion_en_segundos < 3:
                    aparece_antes_3s = 'Sí'
                    total_apariciones_antes_3s += 1

                total_videos_con_logo += 1

            nombre_archivo = blob.name.split('/')[-1].split('.')[0]
            mp4_link = f"https://storage.cloud.google.com/videos_online/{carpeta_en_bucket}{video_id}.mp4"
            s = pyshorteners.Shortener()
            short_mp4_link = s.tinyurl.short(mp4_link)

            # Crear un DataFrame para el archivo actual
            df_archivo = pd.DataFrame({
                'Nombre Archivo': [nombre_archivo],
                'Aparece el logo': [aparece_logo],
                'Aparece antes de los 3s': [aparece_antes_3s],
                'Primera aparicion': [tiempo_aparicion],
                'Contador de apariciones': [contador_apariciones],
                'Cliente':[cliente],
                'Link': [short_mp4_link],
                'Tanda':[Tanda],
                'timestamp': [pd.Timestamp.now()]
            })

            # Concatenar el DataFrame actual al DataFrame general
            df_general = pd.concat([df_general, df_archivo], ignore_index=True)

    blobs_list_logo = [blob for blob in blobs_list if 'logo' in blob.name.lower()]
    total_videos = len(blobs_list_logo)

    # Crear el informe en formato de texto para cada video
    informe_texto = pd.DataFrame({
        'total_Videos': [total_videos],
        'total_videos_con_logo': [total_videos_con_logo],
        'total_apariciones': [total_apariciones_antes_3s],
        'Cliente' : [cliente],
        'Tanda': [Tanda],
        'timestamp': [pd.Timestamp.now()]
    })

    return df_general, informe_texto


def create_apariciones_table(blobs_list, carpeta_en_bucket, cliente):
    data_apariciones = []
    match = re.search(r'Videos/(.+?)/', carpeta_en_bucket)

    if match:
        Tanda = match.group(1)
    else:
        Tanda = 'Videos/'

    for blob in blobs_list:
        tanda_info, video_id = extract_info_from_mp4(blob)
        if 'logo' in blob.name.lower() and blob.name.lower().endswith('.csv'):
            contenido_csv_bytes = blob.download_as_bytes()
            df = pd.read_csv(BytesIO(contenido_csv_bytes))
            mercado_libre_data = df[df['entidad'] == cliente]

            for index, row in mercado_libre_data.iterrows():
                tiempo_aparicion_segundos = row['t_inicio']
                tiempo_aparicion = f"{int(tiempo_aparicion_segundos // 60)}:{int(tiempo_aparicion_segundos % 60):02d}"

                aparece_antes_3s = 'Sí' if tiempo_aparicion_segundos < 3 else 'No'

                nombre_archivo = blob.name.split('/')[-1].split('.')[0]
                mp4_link = f"https://storage.cloud.google.com/videos_online/{carpeta_en_bucket}{video_id}.mp4"
                s = pyshorteners.Shortener()
                short_mp4_link = s.tinyurl.short(mp4_link)

                data_apariciones.append({
                    'Video': nombre_archivo,
                    'Cliente': cliente,
                    'Aparece_el_logo': 'Sí',
                    'Aparece_antes_de_los_3s': aparece_antes_3s,
                    'Tiempo_aparicion': tiempo_aparicion,
                    'Link': short_mp4_link,
                    'Tanda': Tanda,
                    'timestamp': pd.Timestamp.now()
                })

    df_apariciones = pd.DataFrame(data_apariciones)

    return df_apariciones
