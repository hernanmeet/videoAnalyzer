import pandas as pd
from io import BytesIO
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
import ast

def analyze_audio_contexto(blobs_list):
    content_audio_contexto = []

    # Inicializar variables para el análisis de audio
    for blob in blobs_list:
        # Verificar si el nombre del archivo contiene la palabra 'audio_contexto'
        if 'audio_contexto' in blob.name.lower() and blob.name.lower().endswith('.csv'):
            # Descargar el contenido del blob como bytes
            contenido_csv_bytes = blob.download_as_bytes()

            # Leer el contenido como DataFrame de pandas
            df_audio_contexto = pd.read_csv(BytesIO(contenido_csv_bytes))

            # Obtener el nombre del archivo sin la extensión
            nombre_archivo = blob.name.split('/')[-1].split('.')[0]

            # Crear el informe en formato de texto para cada video con audio_contexto
            informe_audio_contexto = f"<b>Análisis de Audio Contexto para el Video: {nombre_archivo}</b><br/><br/>"

            # Agregar información del audio_contexto al informe
            for index, row in df_audio_contexto.iterrows():
                tiempo_inicio = ast.literal_eval(row['time'])['start']
                tiempo_fin = ast.literal_eval(row['time'])['end']
                audio_tags = ast.literal_eval(row['audio tags'])

                informe_audio_contexto += f"Segmento de tiempo: {tiempo_inicio} a {tiempo_fin} segundos<br/>"
                informe_audio_contexto += f"Etiquetas de audio: {audio_tags}<br/><br/>"

            # Agregar el informe de audio_contexto al contenido específico de audio_contexto
            content_audio_contexto.append(Paragraph(informe_audio_contexto, getSampleStyleSheet()['Normal']))

    # Retornar el contenido generado para audio_contexto
    return content_audio_contexto


def audio_to_df(blobs_list,cliente):
    audio_contexto_data = {'Video': [], 'Tiempo Inicio': [], 'Tiempo Fin': [], 'Tag Name': [], 'Tag Number': [],'Cliente':[], 'Timestamp': []}

    for blob in blobs_list:
        if 'audio_contexto' in blob.name.lower() and blob.name.lower().endswith('.csv'):
            contenido_csv_bytes = blob.download_as_bytes()
            df_audio_contexto = pd.read_csv(BytesIO(contenido_csv_bytes))
            nombre_archivo = blob.name.split('/')[-1].split('.')[0]

            for index, row in df_audio_contexto.iterrows():
                tiempo_inicio = ast.literal_eval(row['time'])['start']
                tiempo_fin = ast.literal_eval(row['time'])['end']
                audio_tags = ast.literal_eval(row['audio tags'])
                timestamp = blob.time_created  # Use blob timestamp as the timestamp

                for tag in audio_tags:
                    tag_name, tag_number = tag
                    # Agregar información al diccionario
                    audio_contexto_data['Video'].append(nombre_archivo)
                    audio_contexto_data['Tiempo Inicio'].append(tiempo_inicio)
                    audio_contexto_data['Tiempo Fin'].append(tiempo_fin)
                    audio_contexto_data['Tag Name'].append(tag_name)
                    audio_contexto_data['Tag Number'].append(tag_number)
                    audio_contexto_data['Timestamp'].append(timestamp)
                    audio_contexto_data['Cliente'].append(cliente)

    # Crear DataFrame para el análisis de audio_contexto
    df_audio_contexto = pd.DataFrame(audio_contexto_data)

    return df_audio_contexto