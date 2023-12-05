import os 
import pyshorteners
import pandas as pd
from reportlab.lib import colors
from reportlab.platypus import Table
from google.cloud import storage



def extract_info_from_mp4(blob):
    """
    Extrae información de la tanda y el nombre del archivo MP4 desde el nombre del blob.
    """
    mp4_path = os.path.splitext(blob.name)[0]  # Obtener la ruta del archivo MP4 sin la extensión
    parts = mp4_path.split('/')
    
    # Tomar las últimas dos partes de la ruta para obtener la tanda y el nombre del archivo MP4
    tanda_info = parts[-2]
    
    
    video_id =blob.name.split('/')[-1]
    if "logo" in video_id.lower():
        video_id = video_id.split('_logo')[0]
    return tanda_info, video_id




def link_mp4(blobs_list, carpeta_en_bucket):
    df_general = pd.DataFrame(columns=['Nombre Archivo', 'Link Archivo'])
    content_general = []
    
    for blob in blobs_list:
        tanda_info, video_id = extract_info_from_mp4(blob)
    
        if 'logo' in blob.name.lower() and blob.name.lower().endswith('.csv'):
            nombre_archivo = blob.name.split('/')[-1].split('.')[0]           
          
                        
            mp4_link = f"https://storage.cloud.google.com/videos_online/{carpeta_en_bucket}{video_id}.mp4"
            s = pyshorteners.Shortener()
            short_mp4_link = s.tinyurl.short(mp4_link)
            
            # Crear un DataFrame para el archivo actual
            df_archivo = pd.DataFrame({
                'Nombre Archivo': [nombre_archivo],
                'Link Archivo': [short_mp4_link],
            })
            
            # Concatenar el DataFrame actual al DataFrame general
            df_general = pd.concat([df_general, df_archivo], ignore_index=True)

    table_style = [('GRID', (0, 0), (-1, -1), 1, colors.black),
                   ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                   ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                   ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                   ('SPACEAFTER', (0, 0), (-1, -1), 24)]

    data = [df_general.columns.tolist()] + df_general.values.tolist()
    table = Table(data)
    table.setStyle(table_style)

    content_general.append(table)
    return content_general


def make_video_blob_public(bucket_name, blob_name):
    """Hace que un objeto de tipo video/mp4 en un bucket sea público."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    # Verifica si el objeto es un archivo de tipo video/mp4
    if blob.content_type == 'video/mp4':
        # Configura la ACL para hacer el objeto público
        blob.acl.all().grant_read()  # Permite a todos los usuarios leer el objeto
        blob.acl.save()
        print(f"El objeto {blob_name} en el bucket {bucket_name} ahora es público.")
