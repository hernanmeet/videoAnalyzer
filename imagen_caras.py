from datetime import timedelta
from typing import Optional, Sequence, cast
import pandas as pd
from google.cloud import videointelligence_v1 as vi
import re
from google.cloud import storage
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'vertexai-403121-4e2613b93cf2.json'

client = storage.Client()
export_bucket= client.bucket('videos_online')

from typing import Sequence

from google.cloud import vision


def print_faces(response: vision.AnnotateImageResponse, archivo):
    print("=" * 80)
    
    columnas = ['face_number','joy','exposed', 'blurred', 'anger', 'headwear', 'sorrow', 'surprise']
    df = pd.DataFrame(columns=columnas)

    for face_number, face in enumerate(response.face_annotations, 1):
        vertices = ",".join(f"({v.x},{v.y})" for v in face.bounding_poly.vertices)
        print(f"# Face {face_number} @ {vertices}")
        print(f"Joy:     {face.joy_likelihood.name}")
        print(f"Exposed: {face.under_exposed_likelihood.name}")
        print(f"Blurred: {face.blurred_likelihood.name}")
        print(f"Anger: {face.anger_likelihood.name}")
        print(f"Headwear: {face.headwear_likelihood.name}")
        print(f"Sorrow: {face.sorrow_likelihood.name}")
        print(f"Surprise: {face.surprise_likelihood.name}")
        print("-" * 80)
        datos_fila = {'face_number': [face_number], 'joy': [face.joy_likelihood.name],'exposed': [face.under_exposed_likelihood.name], 'blurred': [face.blurred_likelihood.name],'anger': [face.anger_likelihood.name],'headwear': [face.headwear_likelihood.name],'sorrow': [face.sorrow_likelihood.name],'surprise': [face.surprise_likelihood.name]}
        df = pd.concat([df,pd.DataFrame(datos_fila)])
    
    nombre_archivo = re.search(r'/([^/]+)\.\w+$', archivo).group(1) 
    nombre_archivo_completo = nombre_archivo + "_imagen_caras.csv"

   
    base_path = re.search(r'videos_online/(.*?)/[^/]+$', archivo).group(1)
    base_path_completo = base_path + "/"
   
    df.to_csv(nombre_archivo_completo, index=False)
    blob =export_bucket.blob(base_path_completo+nombre_archivo_completo)
    blob.upload_from_filename(nombre_archivo_completo)


def analyze_image_from_uri(
    image_uri: str,
    feature_types: Sequence,
) -> vision.AnnotateImageResponse:
    client = vision.ImageAnnotatorClient()

    image = vision.Image()
    image.source.image_uri = image_uri
    features = [vision.Feature(type_=feature_type) for feature_type in feature_types]
    request = vision.AnnotateImageRequest(image=image, features=features)

    response = client.annotate_image(request=request)

    return response

def captar_imagen_caras(archivo):
    image_uri = archivo
    features = [vision.Feature.Type.FACE_DETECTION]

    response = analyze_image_from_uri(image_uri, features)
    print_faces(response, archivo)