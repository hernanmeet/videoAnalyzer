from google.cloud import speech_v1p1beta1 as speech
from google.cloud import storage
import os
import whisper_at as whisper
import pandas as pd
import re
from google.cloud import storage
from io import BytesIO



os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'vertexai-403121-4e2613b93cf2.json'

client = storage.Client()
export_bucket= client.bucket('videos_online')

def sonidos(archivo):
    print ("---------- Iniciando Lectura de Sonido Ambiente y Conversaciones ----------")
    print("Archivo: ", archivo)
    audio_tagging_time_resolution = 10
    model = whisper.load_model("large-v1")

    blob = export_bucket.blob(archivo[len('gs://videos_online/'):])
    #file_content = BytesIO(blob.download_as_bytes())
    blob.download_to_filename("video.mp4")



    result = model.transcribe("video.mp4", at_time_res=audio_tagging_time_resolution, fp16=False)
    # ASR Results
  
    dftext=pd.DataFrame({"text": [result]})
    nombre_archivo = re.search(r'/([^/]+)\.\w+$', archivo).group(1) 
    nombre_archivo_completo = nombre_archivo + "_texto_whisper_contexto.csv"

   
    base_path = re.search(r'videos_online/(.*?)/[^/]+$', archivo).group(1)
    base_path_completo = base_path + "/"
   
    dftext.to_csv(nombre_archivo_completo, index=False)
    blob =export_bucket.blob(base_path_completo+nombre_archivo_completo)
    blob.upload_from_filename(nombre_archivo_completo)

    # Audio Tagging Results
    audio_tag_result = whisper.parse_at_label(result, language='follow_asr', top_k=5, p_threshold=-1, include_class_list=list(range(527)))
    #print(audio_tag_result)
    print("-----------------------------------")
    print(result["text"])
    print("-----------------------------------")
    for resultado in audio_tag_result:
        print(resultado)
    print("-----------------------------------")
    df = pd.DataFrame(audio_tag_result)

    nombre_archivo = re.search(r'/([^/]+)\.\w+$', archivo).group(1) 
    nombre_archivo_completo = nombre_archivo + "_audio_contexto.csv"

   
    base_path = re.search(r'videos_online/(.*?)/[^/]+$', archivo).group(1)
    base_path_completo = base_path + "/"
   
    df.to_csv(nombre_archivo_completo, index=False)
    blob =export_bucket.blob(base_path_completo+nombre_archivo_completo)
    blob.upload_from_filename(nombre_archivo_completo)
    
    print ("------------ Fin de Lectura de Sonido Ambiente y Conversaciones ------------")

# if __name__ == "__main__":
#     import sys

#     # Si el script se ejecuta como el principal, toma el primer argumento de la línea de comandos como la URL del video
#     archivo = sys.argv[1]
#     print ("---------- Iniciando Lectura de Sonido Ambiente y Conversaciones ----------")
#     sonidos(archivo)
#     print ("------------ Fin de Lectura de Sonido Ambiente y Conversaciones ------------")