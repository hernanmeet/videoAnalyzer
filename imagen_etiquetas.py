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


def print_labels(response: vision.AnnotateImageResponse, archivo):
    print("=" * 80)

    columnas = ['confidence', 'label']
    df = pd.DataFrame(columns=columnas)

    for label in response.label_annotations:
        print(
            f"{label.score:4.0%}",
            f"{label.description:5}",
            sep=" | ",
        )

        datos_fila = {'confidence': [label.score], 'label': [label.description]}
        df = pd.concat([df,pd.DataFrame(datos_fila)])
    
    nombre_archivo = re.search(r'/([^/]+)\.\w+$', archivo).group(1) 
    nombre_archivo_completo = nombre_archivo + "_imagen_etiquetas.csv"

   
    base_path = re.search(r'videos_online/(.*?)/[^/]+$', archivo).group(1)
    base_path_completo = base_path + "/"
   
    df.to_csv(nombre_archivo_completo, index=False)
    blob =export_bucket.blob(base_path_completo+nombre_archivo_completo)
    blob.upload_from_filename(nombre_archivo_completo)


def captar_imagen_etiquetas(archivo):
    image_uri = archivo
    features = [vision.Feature.Type.LABEL_DETECTION]

    response = analyze_image_from_uri(image_uri, features)
    print_labels(response, archivo)