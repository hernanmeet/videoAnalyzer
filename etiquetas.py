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

def detect_labels(
    video_uri: str,
    mode: vi.LabelDetectionMode,
    segments: Optional[Sequence[vi.VideoSegment]] = None,
) -> vi.VideoAnnotationResults:
    video_client = vi.VideoIntelligenceServiceClient()
    features = [vi.Feature.LABEL_DETECTION]
    config = vi.LabelDetectionConfig(label_detection_mode=mode)
    context = vi.VideoContext(segments=segments, label_detection_config=config)
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

def print_video_labels(results: vi.VideoAnnotationResults, video_uri):
    labels = sorted_by_first_segment_confidence(results.segment_label_annotations)

    columnas = ['confidence', 't_inicio', 't_fin', 'label']
    frames = []

    print(f" Video labels: {len(labels)} ".center(80, "-"))
    for label in labels:
        categories = category_entities_to_str(label.category_entities)
        for segment in label.segments:
            confidence = segment.confidence
            t1 = segment.segment.start_time_offset.total_seconds()
            t2 = segment.segment.end_time_offset.total_seconds()
            print(
                f"{confidence:4.0%}",
                f"{t1:7.3f}",
                f"{t2:7.3f}",
                f"{label.entity.description}{categories}",
                sep=" | ",
            )
            datos_fila = {'confidence': confidence, 't_inicio': t1, 't_fin': t2,
                          'label': [label.entity.description + ' ' + categories]}

            frames.append(pd.DataFrame([datos_fila]))

    if frames:
        df = pd.concat(frames, ignore_index=True)
        nombre_archivo = re.search(r'/([^/]+)\.\w+$', video_uri).group(1)
        nombre_archivo_completo = nombre_archivo + "_etiquetas.csv"

        base_path = re.search(r'videos_online/(.*?)/[^/]+$', video_uri).group(1)
        base_path_completo = base_path + "/"

        df.to_csv(nombre_archivo_completo, index=False)
        blob = export_bucket.blob(base_path_completo + nombre_archivo_completo)
        blob.upload_from_filename(nombre_archivo_completo)
        print("Archivo de etiquetas creado y subido correctamente.")
    else:
        print("No hay etiquetas para grabar.")
        

def sorted_by_first_segment_confidence(
    labels: Sequence[vi.LabelAnnotation],
) -> Sequence[vi.LabelAnnotation]:
    def first_segment_confidence(label: vi.LabelAnnotation) -> float:
        return label.segments[0].confidence

    return sorted(labels, key=first_segment_confidence, reverse=True)


def category_entities_to_str(category_entities: Sequence[vi.Entity]) -> str:
    if not category_entities:
        return ""
    entities = ", ".join([e.description for e in category_entities])
    return f" ({entities})"

def captar_etiquetas(archivo):
    print ("---------- Iniciando Lectura de Etiquetas ----------")
    print("Nombre del archivo: ", archivo)
    mode = vi.LabelDetectionMode.SHOT_MODE
    results = detect_labels(archivo, mode)
    print_video_labels(results,archivo)
    print ("------------ Fin de Lectura de Etiquetas ------------")

# if __name__ == "__main__":
#     import sys

#     # Si el script se ejecuta como el principal, toma el primer argumento de la línea de comandos como la URL del video
#     archivo = sys.argv[1]
#     print ("---------- Iniciando Lectura de Etiquetas ----------")
#     captar_etiquetas(archivo)
#     print ("------------ Fin de Lectura de Etiquetas ------------")