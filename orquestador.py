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
import time
import redis



redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)


lista = []
ocupado=False
def procesar(archivo):
   global ocupado
   
   path_google = archivo.get('path_google')
   
   if (archivo.get('audio')=='true'):
      captar_audio(path_google)

   if (archivo.get('logos')=='true'):
      captar_logos(path_google)

   if (archivo.get('etiquetas')=='true'):
      captar_etiquetas(path_google)

   if (archivo.get('personas')=='true'):   
      captar_personas(path_google)
   
   if (archivo.get('textos')=='true'): 
      captar_textos(path_google)

   if (archivo.get('textospeech')=='true'): 
      sonidos(path_google)

   if (archivo.get('imagen_etiquetas')=='true'):
      captar_imagen_etiquetas(path_google)

   if (archivo.get('imagen_landmark')=='true'):
      captar_imagen_landmark(path_google)
   
   if (archivo.get('imagen_caras')=='true'):
      captar_imagen_caras(path_google)
   
   if (archivo.get('imagen_textos')=='true'):
      captar_imagen_textos(path_google)
   
   generar_informe(path_google)
   
   print("---------- FIN DEL ANALISIS -----------")
   ocupado=False

print ("iniciando programa")
while True:
    estado = redis_client.get('TERMINO').decode('utf-8')
    #print("Estado: ", redis_client.get('SE_TERMINO').decode('utf-8') )
    time.sleep(1)
    if (estado=='True'):
       print("---------------- Iniciando Analisis -----------------")
       
       #datos = ({'path_google':redis_client.get('PATH_GOOGLE').decode('utf-8'),'path_local':redis_client.get('PATH_LOCAL').decode('utf-8')})
       datos = ({
                  'path_google':redis_client.get('PATH_GOOGLE').decode('utf-8'),
                  'etiquetas':redis_client.get('ETIQUETAS').decode('utf-8'),
                  'logos':redis_client.get('LOGOS').decode('utf-8'),
                  'personas':redis_client.get('PERSONAS').decode('utf-8'),
                  'textos':redis_client.get('TEXTOS').decode('utf-8'),
                  'audio':redis_client.get('AUDIO').decode('utf-8'),
                  'textospeech':redis_client.get('TEXTOSPEECH').decode('utf-8'),
                  'imagen_etiquetas':redis_client.get('IMAGEN_ETIQUETAS').decode('utf-8'),
                  'imagen_landmark':redis_client.get('IMAGEN_LANDMARK').decode('utf-8'),
                  'imagen_caras':redis_client.get('IMAGEN_CARAS').decode('utf-8'),
                  'imagen_textos':redis_client.get('IMAGEN_TEXTOS').decode('utf-8'),
 

                 
                 })
       lista.append(datos)
       redis_client.set('TERMINO', 'False')
    
    if (len(lista)>0 and not ocupado):
        finalizado=True
        #mi_hilo = threading.Thread(target= procesar(lista[0])
        mi_hilo = threading.Thread(target=procesar, args=(lista[0],))
        mi_hilo.start() 
        lista.pop(0)
