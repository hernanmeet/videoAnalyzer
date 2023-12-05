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

def detect_text(
    video_uri: str,
    language_hints: Optional[Sequence[str]] = None,
    segments: Optional[Sequence[vi.VideoSegment]] = None,
) -> vi.VideoAnnotationResults:
    video_client = vi.VideoIntelligenceServiceClient()
    features = [vi.Feature.TEXT_DETECTION]
    config = vi.TextDetectionConfig(
        language_hints=language_hints,
    )
    context = vi.VideoContext(
        segments=segments,
        text_detection_config=config,
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


def print_video_text(results: vi.VideoAnnotationResults, video_uri, min_frames: int = 15):
    annotations = sorted_by_first_segment_end(results.text_annotations)

    columnas = ['confidence', 'text', 't_inicio', 'cantidad_segundos', 'frames']
    df = pd.DataFrame(columns=columnas)

    print(" Detected text ".center(80, "-"))
    for annotation in annotations:
        for text_segment in annotation.segments:
            frames = len(text_segment.frames)
            if frames < min_frames:
                continue
            text = annotation.text
            confidence = text_segment.confidence
            start = text_segment.segment.start_time_offset
            seconds = segment_seconds(text_segment.segment)
            print(f"  {confidence:4.0%} | {start} + {seconds:.1f}s | {frames} fr.")
            
            datos_fila = {'confidence': [confidence], 'text': [text], 't_inicio': [start],
                          'cantidad_segundos': [seconds], 'frames': [frames]}
            
            # Utilizo una lista para almacenar los DataFrames
            list_df = [df, pd.DataFrame(datos_fila)]
            df = pd.concat(list_df)

    # Verificar si el DataFrame tiene datos antes de guardarlo
    if not df.empty:
        nombre_archivo = re.search(r'/([^/]+)\.\w+$', video_uri).group(1)
        nombre_archivo_completo = nombre_archivo + "_texto_del_video.csv"

        base_path = re.search(r'videos_online/(.*?)/[^/]+$', video_uri).group(1)
        base_path_completo = base_path + "/"

        df.to_csv(nombre_archivo_completo, index=False)
        blob = export_bucket.blob(base_path_completo + nombre_archivo_completo)
        blob.upload_from_filename(nombre_archivo_completo)
        print("Archivo de texto del video creado y subido correctamente.")
    else:
        print("No hay texto del video para grabar.")



def sorted_by_first_segment_end(
    annotations: Sequence[vi.TextAnnotation],
) -> Sequence[vi.TextAnnotation]:
    def first_segment_end(annotation: vi.TextAnnotation) -> int:
        return annotation.segments[0].segment.end_time_offset.total_seconds()

    return sorted(annotations, key=first_segment_end)


def segment_seconds(segment: vi.VideoSegment) -> float:
    t1 = segment.start_time_offset.total_seconds()
    t2 = segment.end_time_offset.total_seconds()
    return t2 - t1


def captar_textos(archivo):
    print ("---------- Iniciando Lectura de Textos ----------")
    results = detect_text(archivo)
    print_video_text(results,archivo)
    print ("------------ Fin de Lectura de Textos ------------")

# if __name__ == "__main__":
#     import sys

#     # Si el script se ejecuta como el principal, toma el primer argumento de la línea de comandos como la URL del video
#     archivo = sys.argv[1]
#     print ("---------- Iniciando Lectura de Textos ----------")
#     captar_textos(archivo)
#     print ("------------ Fin de Lectura de Textos ------------")