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



def detect_logos(
    video_uri: str, segments: Optional[Sequence[vi.VideoSegment]] = None
) -> vi.VideoAnnotationResults:
    video_client = vi.VideoIntelligenceServiceClient()
    features = [vi.Feature.LOGO_RECOGNITION]
    context = vi.VideoContext(segments=segments)
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


def print_detected_logos(results: vi.VideoAnnotationResults,video_uri):
    annotations = results.logo_recognition_annotations

    columnas = ['confidence', 't_inicio','t_fin','cant_frames', 'id_entidad','entidad']
    df = pd.DataFrame(columns=columnas)

    print(f" Detected logos: {len(annotations)} ".center(80, "-"))
    for annotation in annotations:
        entity = annotation.entity
        entity_id = entity.entity_id
        description = entity.description
        for track in annotation.tracks:
            confidence = track.confidence
            t1 = track.segment.start_time_offset.total_seconds()
            t2 = track.segment.end_time_offset.total_seconds()
            logo_frames = len(track.timestamped_objects)
            print(
                f"{confidence:4.0%}",
                f"{t1:>7.3f}",
                f"{t2:>7.3f}",
                f"{logo_frames:>3} fr.",
                f"{entity_id:<15}",
                f"{description}",
                sep=" | ",
            )
            datos_fila = {'confidence': [confidence], 't_inicio': [t1],'t_fin':[t2], 'cant_frames':[logo_frames],'id_entidad':[entity_id],'entidad':[description]}

            df = pd.concat([df,pd.DataFrame(datos_fila)])
    
    nombre_archivo = re.search(r'/([^/]+)\.\w+$', video_uri).group(1) 
    nombre_archivo_completo = nombre_archivo + "_logos.csv"

   
    base_path = re.search(r'videos_online/(.*?)/[^/]+$', video_uri).group(1)
    base_path_completo = base_path + "/"
   
    df.to_csv(nombre_archivo_completo, index=False)
    blob =export_bucket.blob(base_path_completo+nombre_archivo_completo)
    blob.upload_from_filename(nombre_archivo_completo)

def captar_logos(archivo):
    print ("---------- Iniciando Lectura de Logos ----------")
    print(archivo)
    results = detect_logos(archivo)
    print_detected_logos(results,archivo)
    print ("------------ Fin de Lectura de Logos ------------")

# if __name__ == "__main__":
#     import sys

#     # Si el script se ejecuta como el principal, toma el primer argumento de la línea de comandos como la URL del video
#     archivo = sys.argv[1]
#     print ("---------- Iniciando Lectura de Logos ----------")
#     captar_logos(archivo)
#     print ("------------ Fin de Lectura de Logos ------------")