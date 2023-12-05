from google.cloud import storage
import pandas as pd
from logo_analysis import analyze_logo,graph_pie_logo,logo_bar_chart,logo_pie_3s
from text_analysis import analyze_text,wordcloud
from audio_analysis import analyze_audio_contexto
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
import re





def generar_informe( carpeta_en_bucket):
    bucket_name = 'videos_online'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'vertexai-403121-4e2613b93cf2.json'  
 

    # Crear una instancia del cliente de almacenamiento de Google Cloud
    client = storage.Client()

    # Obtener el bucket
    bucket = client.get_bucket(bucket_name)

    # Obtener una lista de blobs en el bucket con la ruta de la carpeta especificada
    blobs_list = list(bucket.list_blobs(prefix=carpeta_en_bucket))

    cliente_match = re.match(r'^2023\/([^\/]+)\/Videos\/', carpeta_en_bucket)
    cliente = cliente_match.group(1) if cliente_match else None

    styles = getSampleStyleSheet()
    title_style = styles['Title'].clone('title_custom')
    title_style.textColor = colors.black
    title_style.fontSize = 16
    title_style.alignment = 1  # Alineación al centro
    title_style.spaceAfter = 12  # Espacio después del título

    data, total_videos, total_videos_con_logo, total_apariciones_antes_3s = analyze_logo(blobs_list,carpeta_en_bucket,cliente)
    pie_chart_logo = graph_pie_logo(total_videos, total_videos_con_logo)
    logo_3s = logo_pie_3s(total_videos_con_logo, total_apariciones_antes_3s)
    logo_bar = logo_bar_chart(blobs_list,cliente)
    content_text, all_video_texts, all_text_combined = analyze_text(blobs_list)
    graph_text = wordcloud(all_text_combined)
    content_audio_contexto = analyze_audio_contexto(blobs_list)    

    # Crear el contenido para el PDF
    content = []

    report_title = f"<b>Informe General de Videos para {cliente}</b>"
    content.append(Paragraph(report_title, title_style))
    content.append(Spacer(1, 40))
    content.append(Paragraph("<b>Analisis de la influencia del logo</b>", title_style))
    content.append(Spacer(1, 40))
    content.extend(data)
    
    content.append(PageBreak())
    content.append(Paragraph("<b>Apartado visual Logos</b>", title_style))
    content.extend(pie_chart_logo)
    content.extend(logo_3s)
    content.extend(logo_bar)
    content.append(PageBreak())
    content.append(Paragraph("<b>Análisis de Sobreimpresos</b>", title_style))
    content.extend(content_text)
    content.extend(all_video_texts)
    content.extend(graph_text)
    content.append(PageBreak())
    content.append(Paragraph("<b>Análisis de Audio Contexto</b>", title_style))
    content.extend(content_audio_contexto)

    nombre_archivo = re.search(r'/([^/]+)\.\w+$', carpeta_en_bucket).group(1) 
    nombre_archivo_completo = nombre_archivo + "_informe.pdf"

   
    base_path = re.search(r'videos_online/(.*?)/[^/]+$', carpeta_en_bucket).group(1)
    base_path_completo = base_path + "/"


    doc = SimpleDocTemplate(nombre_archivo_completo, pagesize=letter)    
    doc.build(content)
    
  
    blob = bucket.blob(base_path_completo+nombre_archivo_completo)
    blob.upload_from_filename(nombre_archivo_completo)
    print(f"El informe se ha generado correctamente en: {base_path_completo}{nombre_archivo_completo}")

