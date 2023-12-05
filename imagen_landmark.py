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

def print_landmarks(response: vision.AnnotateImageResponse, archivo, min_score: float = 0.5):
    print("=" * 80)

    columnas = ['landmarkDescription', 'vertices','latitude','longitude']
    df = pd.DataFrame(columns=columnas)

    for landmark in response.landmark_annotations:
        if landmark.score < min_score:
            continue
        vertices = [f"({v.x},{v.y})" for v in landmark.bounding_poly.vertices]
        lat_lng = landmark.locations[0].lat_lng
        print(
            f"{landmark.description:18}",
            ",".join(vertices),
            f"{lat_lng.latitude:.5f}",
            f"{lat_lng.longitude:.5f}",
            sep=" | ",
        )
        datos_fila = {'landmarkDescription': [landmark.description], 'vertices': [vertices],'latitude': [lat_lng.latitude], 'longitude': [lat_lng.longitude]}
        df = pd.concat([df,pd.DataFrame(datos_fila)])
    
    
    nombre_archivo = re.search(r'/([^/]+)\.\w+$', archivo).group(1) 
    nombre_archivo_completo = nombre_archivo + "_imagen_landmark.csv"

   
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

def captar_imagen_landmark(archivo):
    image_uri = archivo
    features = [vision.Feature.Type.LANDMARK_DETECTION]

    response = analyze_image_from_uri(image_uri, features)
    print_landmarks(response,archivo)