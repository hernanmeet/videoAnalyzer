from datetime import timedelta
from typing import Optional, Sequence, cast
import pandas as pd
import re
from google.cloud import videointelligence_v1 as vi
from google.cloud import storage
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'vertexai-403121-4e2613b93cf2.json'

client = storage.Client()
export_bucket= client.bucket('videos_online')


def transcribe_speech(
    video_uri: str,
    language_code: str,
    segments: Optional[Sequence[vi.VideoSegment]] = None,
) -> vi.VideoAnnotationResults:
    video_client = vi.VideoIntelligenceServiceClient()
    features = [vi.Feature.SPEECH_TRANSCRIPTION]
    config = vi.SpeechTranscriptionConfig(
        language_code=language_code,
        enable_automatic_punctuation=True,
    )
    context = vi.VideoContext(
        segments=segments,
        speech_transcription_config=config,
    )
    request = vi.AnnotateVideoRequest(
        input_uri=video_uri,
        features=features,
        video_context=context,
    )

    print(f'Processing video "{video_uri}"...')
    operation = video_client.annotate_video(request)

    # Wait for operation to complete
    response = cast(vi.AnnotateVideoResponse, operation.result())
    # A single video is processed
    results = response.annotation_results[0]

    return results


def print_video_speech(results: vi.VideoAnnotationResults, video_uri, min_confidence: float = 0.8):
    def keep_transcription(transcription: vi.SpeechTranscription) -> bool:
        return min_confidence <= transcription.alternatives[0].confidence

    transcriptions = results.speech_transcriptions
    
    transcriptions = [t for t in transcriptions if keep_transcription(t)]

    columnas = ['confidence', 'transcript']
    df = pd.DataFrame(columns=columnas)

    print(f" Speech transcriptions: {len(transcriptions)} ".center(80, "-"))
    for transcription in transcriptions:
        first_alternative = transcription.alternatives[0]
        confidence = first_alternative.confidence
        transcript = first_alternative.transcript
        print(f" {confidence:4.0%} | {transcript.strip()}")
        
        # Crear un diccionario con los datos de la iteración actual
        datos_fila = {'confidence': [confidence], 'transcript': [transcript.strip()]}

        # Agregar una nueva fila al DataFrame
        # Utilizar una lista para almacenar los DataFrames
        if (df.empty):
            df= pd.DataFrame(datos_fila).copy()
        else:
            list_df = [df, pd.DataFrame(datos_fila)]
            df = pd.concat(list_df)
    # Verificar si el DataFrame tiene datos antes de guardarlo
    if not df.empty:
        nombre_archivo = re.search(r'/([^/]+)\.\w+$', video_uri).group(1) 
        nombre_archivo_completo = nombre_archivo + "_audio_en_una_linea.csv"

        base_path = re.search(r'videos_online/(.*?)/[^/]+$', video_uri).group(1)
        base_path_completo = base_path + "/"

        df.to_csv(nombre_archivo_completo, index=False)
        blob = export_bucket.blob(base_path_completo + nombre_archivo_completo)
        blob.upload_from_filename(nombre_archivo_completo)
        print("Archivo de audio en una línea creado y subido correctamente.")
    else:
        print("No hay transcripciones de audio para grabar.")


def print_word_timestamps(
    results: vi.VideoAnnotationResults,
    video_uri,
    min_confidence: float = 0.8,
):
    def keep_transcription(transcription: vi.SpeechTranscription) -> bool:
        return min_confidence <= transcription.alternatives[0].confidence

    transcriptions = results.speech_transcriptions
    transcriptions = [t for t in transcriptions if keep_transcription(t)]

    columnas = ['confidence', 't_inicio', 't_fin', 'palabra']
    df = pd.DataFrame(columns=columnas)

    print(" Word timestamps ".center(80, "-"))
    for transcription in transcriptions:
        first_alternative = transcription.alternatives[0]
        confidence = first_alternative.confidence
        for word_info in first_alternative.words:
            t1 = word_info.start_time.total_seconds()
            t2 = word_info.end_time.total_seconds()
            word = word_info.word
            print(f"{confidence:4.0%} | {t1:7.3f} | {t2:7.3f} | {word}")

            datos_fila = {'confidence': [confidence], 't_inicio': [t1], 't_fin': [t2], 'palabra': [word]}

            # Utilizar una lista para almacenar los DataFrames
            if (df.empty):
                df= pd.DataFrame(datos_fila).copy()
            else:
                list_df = [df, pd.DataFrame(datos_fila)]
                df = pd.concat(list_df)

    # Verificar si el DataFrame tiene datos antes de guardarlo
    if not df.empty:
        nombre_archivo = re.search(r'/([^/]+)\.\w+$', video_uri).group(1)
        nombre_archivo_completo = nombre_archivo + "_audio_con_timestamp.csv"

        base_path = re.search(r'videos_online/(.*?)/[^/]+$', video_uri).group(1)
        base_path_completo = base_path + "/"

        df.to_csv(nombre_archivo_completo, index=False)
        blob = export_bucket.blob(base_path_completo + nombre_archivo_completo)
        blob.upload_from_filename(nombre_archivo_completo)
        print("Archivo de audio con timestamp creado y subido correctamente.")
    else:
        print("No hay datos de palabras con timestamp para grabar.")

#-----------------




def captar_audio(archivo):
    print ("---------- Iniciando Lectura de Conversaciones ----------")
    print("Archivo: ", archivo)
    language_code = "es-AR"
    results = transcribe_speech(archivo, language_code)
    print("--- Grabando audio de una sola linea ----")
    print_video_speech(results,archivo)
    print("--- Grabando audio timestamp")
    print_word_timestamps(results,archivo)
    print ("------------ Fin de Lectura de Conversaciones ------------")

# if __name__ == "__main__":
#     import sys

#     # Si el script se ejecuta como el principal, toma el primer argumento de la línea de comandos como la URL del video
#     archivo = sys.argv[1]
#     print ("---------- Iniciando Lectura de Conversaciones ----------")
#     captar_audio(archivo)
#     print ("------------ Fin de Lectura de Conversaciones ------------")