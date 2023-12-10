import asyncio
import threading
from audio import captar_audio
from logos import captar_logos
from etiquetas import captar_etiquetas
from personas import captar_personas
from textos import captar_textos
from textospeech import sonidos
from imagen_etiquetas import captar_imagen_etiquetas
from imagen_landmark import captar_imagen_landmark
from imagen_caras import captar_imagen_caras
from imagen_textos import captar_imagen_textos
from Report_generator import generar_informe
from df_to_bigquery import df_to_bigquery
import time
import redis

redis_client = redis.StrictRedis(host='redis', port=6379, db=0)

lista = []
ocupado = False

async def procesar(archivo):
    global ocupado

    path_google = archivo.get('path_google')

    if archivo.get('audio') == 'true':
        captar_audio(path_google)

    if archivo.get('logos') == 'true':
        captar_logos(path_google)

    if archivo.get('etiquetas') == 'true':
        captar_etiquetas(path_google)

    if archivo.get('personas') == 'true':
        captar_personas(path_google)

    if archivo.get('textos') == 'true':
        captar_textos(path_google)

    if archivo.get('textospeech') == 'true':
        sonidos(path_google)

    if archivo.get('imagen_etiquetas') == 'true':
        captar_imagen_etiquetas(path_google)

    if archivo.get('imagen_landmark') == 'true':
        captar_imagen_landmark(path_google)

    if archivo.get('imagen_caras') == 'true':
        captar_imagen_caras(path_google)

    if archivo.get('imagen_textos') == 'true':
        captar_imagen_textos(path_google)

    generar_informe(path_google)
    df_to_bigquery(path_google)

    print("---------- FIN DEL ANALISIS -----------")
    ocupado = False

async def procesar_archivos():
    global lista, ocupado
    print("Aplicación iniciada")
    
    while True:
        try:
            estado = redis_client.get('TERMINO').decode('utf-8')
            time.sleep(1)

            if estado == 'True':
                print("---------------- Iniciando Analisis -----------------")
                datos = {
                    'path_google': redis_client.get('PATH_GOOGLE').decode('utf-8'),
                    'etiquetas': redis_client.get('ETIQUETAS').decode('utf-8'),
                    'logos': redis_client.get('LOGOS').decode('utf-8'),
                    'personas': redis_client.get('PERSONAS').decode('utf-8'),
                    'textos': redis_client.get('TEXTOS').decode('utf-8'),
                    'audio': redis_client.get('AUDIO').decode('utf-8'),
                    'textospeech': redis_client.get('TEXTOSPEECH').decode('utf-8'),
                    'imagen_etiquetas': redis_client.get('IMAGEN_ETIQUETAS').decode('utf-8'),
                    'imagen_landmark': redis_client.get('IMAGEN_LANDMARK').decode('utf-8'),
                    'imagen_caras': redis_client.get('IMAGEN_CARAS').decode('utf-8'),
                    'imagen_textos': redis_client.get('IMAGEN_TEXTOS').decode('utf-8'),
                }

                lista.append(datos)
                redis_client.set('TERMINO', 'False')

            if lista and not ocupado:
                ocupado = True
                await asyncio.gather(procesar(lista[0]))
                lista.pop(0)

        except Exception as e:
            # Maneja la excepción aquí, por ejemplo, imprime un mensaje
            print(f"Error al interactuar con Redis: {e}")
            # Puedes agregar un tiempo de espera antes de intentar nuevamente
            time.sleep(5)

if __name__ == "__main__":
    asyncio.run(procesar_archivos())
