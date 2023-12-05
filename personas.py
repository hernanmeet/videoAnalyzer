from google.cloud import videointelligence_v1 as videointelligence
from datetime import timedelta
from typing import Optional, Sequence, cast
import pandas as pd
import re
from google.cloud import storage
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'vertexai-403121-4e2613b93cf2.json'

client = storage.Client()
export_bucket= client.bucket('videos_online')

def detect_person(gcs_uri):
    """Detects people in a video."""

    client = videointelligence.VideoIntelligenceServiceClient()

    # Configure the request
    config = videointelligence.types.PersonDetectionConfig(
        include_bounding_boxes=True,
        include_attributes=True,
        include_pose_landmarks=True,
    )
    context = videointelligence.types.VideoContext(person_detection_config=config)

    # Start the asynchronous request
    operation = client.annotate_video(
        request={
            "features": [videointelligence.Feature.PERSON_DETECTION],
            "input_uri": gcs_uri,
            "video_context": context,
        }
    )

    print("\nProcessing video for person detection annotations.")
    result = operation.result(timeout=300)

    print("\nFinished processing.\n")

    # Retrieve the first result, because a single video was processed.
    annotation_result = result.annotation_results[0]

    columnas = ['confidence', 'name','value']
    dfAtributos = pd.DataFrame(columns=columnas)

    columnas = ['confidence', 'name','x','y']
    dfLandmark = pd.DataFrame(columns=columnas)

    for annotation in annotation_result.person_detection_annotations:
        print("Person detected:")
        for track in annotation.tracks:
            print(
                "Segment: {}s to {}s".format(
                    track.segment.start_time_offset.seconds
                    + track.segment.start_time_offset.microseconds / 1e6,
                    track.segment.end_time_offset.seconds
                    + track.segment.end_time_offset.microseconds / 1e6,
                )
            )

            # Each segment includes timestamped objects that include
            # characteristics - -e.g.clothes, posture of the person detected.
            # Grab the first timestamped object
            timestamped_object = track.timestamped_objects[0]
            box = timestamped_object.normalized_bounding_box
            print("Bounding box:")
            print("\tleft  : {}".format(box.left))
            print("\ttop   : {}".format(box.top))
            print("\tright : {}".format(box.right))
            print("\tbottom: {}".format(box.bottom))

            # Attributes include unique pieces of clothing,
            # poses, or hair color.
            print("Attributes:")
            for attribute in timestamped_object.attributes:
                print(
                    "\t{}:{} {}".format(
                        attribute.name, attribute.value, attribute.confidence
                    )
                )

                datos_fila = {'confidence': [attribute.confidence], 'name': [attribute.name],'value':[attribute.value]}
                dfAtributos = pd.concat([dfAtributos,pd.DataFrame(datos_fila)])

            # Landmarks in person detection include body parts such as
            # left_shoulder, right_ear, and right_ankle
            print("Landmarks:")
            for landmark in timestamped_object.landmarks:
                print(
                    "\t{}: {} (x={}, y={})".format(
                        landmark.name,
                       landmark.confidence,
                        landmark.point.x,  # Normalized vertex
                        landmark.point.y,  # Normalized vertex
                    )
                )
                datos_fila = {'confidence': [landmark.confidence], 'name': [landmark.name],'x':[landmark.point.x],'y':[landmark.point.y]}
                dfLandmark = pd.concat([dfLandmark,pd.DataFrame(datos_fila)])

    print(dfAtributos)
    nombre_archivo = re.search(r'/([^/]+)\.\w+$', gcs_uri).group(1) 
    nombre_archivo_completo = nombre_archivo + "_personas_atributos.csv"

   
    base_path = re.search(r'videos_online/(.*?)/[^/]+$', gcs_uri).group(1)
    base_path_completo = base_path + "/"

  
    dfAtributos.to_csv(nombre_archivo_completo, index=False)
    blob =export_bucket.blob(base_path_completo+nombre_archivo_completo)
    blob.upload_from_filename(nombre_archivo_completo)
    print("-------------")
    print(dfLandmark)
    nombre_archivo = re.search(r'/([^/]+)\.\w+$', gcs_uri).group(1) 
    nombre_archivo_completo = nombre_archivo + "_persons_landmark.csv"

   
    base_path = re.search(r'videos_online/(.*?)/[^/]+$', gcs_uri).group(1)
    base_path_completo = base_path + "/"

  
    dfLandmark.to_csv(nombre_archivo_completo, index=False)
    blob =export_bucket.blob(base_path_completo+nombre_archivo_completo)
    blob.upload_from_filename(nombre_archivo_completo)

    
    
def count_people(gcs_uri):
    """Detects people in a video."""

    client = videointelligence.VideoIntelligenceServiceClient()

    # Configure the request
    config = videointelligence.types.PersonDetectionConfig(
        include_bounding_boxes=True,
        include_attributes=True,
        include_pose_landmarks=True,
    )
    context = videointelligence.types.VideoContext(person_detection_config=config)

    # Start the asynchronous request
    operation = client.annotate_video(
        request={
            "features": [videointelligence.Feature.PERSON_DETECTION],
            "input_uri": gcs_uri,
            "video_context": context,
        }
    )

    print("\nProcessing video for person detection annotations.")
    result = operation.result(timeout=300)

    print("\nFinished processing.\n")

    # Retrieve the first result, because a single video was processed.
    annotation_result = result.annotation_results[0]
    person_count=0
    for annotation in annotation_result.person_detection_annotations:
        print("Person detected:")
        person_count=person_count+1
    print("---------- Cantidad de Personas ------")
    print("personas detectadas: ", person_count)

def detect_shot_changes(video_uri: str) -> videointelligence.VideoAnnotationResults:
    video_client = videointelligence.VideoIntelligenceServiceClient()
    features = [videointelligence.Feature.SHOT_CHANGE_DETECTION]
    request = videointelligence.AnnotateVideoRequest(input_uri=video_uri, features=features)

    print(f'Processing video: "{video_uri}"...')
    operation = video_client.annotate_video(request)

    # Wait for operation to complete
    response = cast(videointelligence.AnnotateVideoResponse, operation.result())
    # A single video is processed
    results = response.annotation_results[0]

    return results

def print_video_shots(results: videointelligence.VideoAnnotationResults):
    shots = results.shot_annotations
    print("Cantidad de escenas: ", len(shots))
    print(f" Video shots: {len(shots)} ".center(40, "-"))
    for i, shot in enumerate(shots):
        t1 = shot.start_time_offset.total_seconds()
        t2 = shot.end_time_offset.total_seconds()
        print(f"{i+1:>3} | {t1:7.3f} | {t2:7.3f}")

def captar_personas(archivo):
    print ("---------- Iniciando Lectura de Personas ----------")
    detect_person(archivo)
    count_people(archivo)
    results=detect_shot_changes(archivo)
    print_video_shots(results)
    print ("------------ Fin de Lectura de Personas ------------")

# if __name__ == "__main__":
#     import sys

#     # Si el script se ejecuta como el principal, toma el primer argumento de la línea de comandos como la URL del video
#     archivo = sys.argv[1]
#     print ("---------- Iniciando Lectura de Personas ----------")
#     captar_personas(archivo)
#     print ("------------ Fin de Lectura de Personas ------------")