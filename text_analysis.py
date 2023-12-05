import pandas as pd
from io import BytesIO
import nltk
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
from nltk.corpus import stopwords
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from html import escape

try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('tokenizers/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

def analyze_text(blobs_list):
    all_video_texts = []
    content_text = []  # Lista para almacenar el contenido del análisis de texto

    for blob in blobs_list:
        try:
            if 'texto_del' in blob.name.lower() and blob.name.lower().endswith('.csv'):
                contenido_csv_bytes = blob.download_as_bytes()
                df_texto = pd.read_csv(BytesIO(contenido_csv_bytes))
                video_name = blob.name.split('/')[-1].split('.')[0]

                # Agregar análisis de texto individual al contenido
                content_text.append(Paragraph(f"<b>Análisis de Sobre impresos para el Video: {video_name}</b>", getSampleStyleSheet()['Heading2']))

                video_text = ' '.join(df_texto['text'].dropna().astype(str).tolist())
                all_video_texts.append(video_text)

                video_tokens = word_tokenize(video_text)
                stop_words = set(stopwords.words('spanish'))
                filtered_video_tokens = [word.lower() for word in video_tokens if word.isalnum() and word.lower() not in stop_words]

                content_text.append(Paragraph(f"<b>Sobre impreso Combinado del Video:</b><br/>{video_text}", getSampleStyleSheet()['Normal']))
                content_text.append(Spacer(1, 12))

                content_text.append(Paragraph(f"<b>Cantidad Total de Palabras antes de Filtrar:</b> {len(video_tokens)}", getSampleStyleSheet()['Normal']))
                content_text.append(Paragraph(f"<b>Cantidad Total de Palabras después de Filtrar:</b> {len(filtered_video_tokens)}", getSampleStyleSheet()['Normal']))
                content_text.append(Spacer(1, 12))

                content_text.append(Paragraph("<b>Palabras Más Comunes en el Video:</b>", getSampleStyleSheet()['Normal']))
                fdist_video = FreqDist(filtered_video_tokens)
                common_words_video = fdist_video.most_common(10)

                for word, frequency in common_words_video:
                    content_text.append(Paragraph(f"{word}: {frequency} veces", getSampleStyleSheet()['Normal']))
                content_text.append(Spacer(1, 24))
        except Exception as e:
            # Handle exceptions (e.g., print an error message)
            print(f"Error processing {blob.name}: {str(e)}")

    # Unir todos los textos de los videos en un solo string
    all_text_combined = ' '.join(all_video_texts)
    content_general = []
    # Tokenizar el texto combinado
    all_tokens = word_tokenize(all_text_combined)

    # Filtrar stopwords y puntuación
    stop_words_all = set(stopwords.words('spanish'))  # Puedes cambiar a 'english' si es necesario
    filtered_tokens_all = [word.lower() for word in all_tokens if word.isalnum() and word.lower() not in stop_words_all]

    # Calcular la frecuencia de las palabras para el texto combinado
    fdist_all = FreqDist(filtered_tokens_all)

    # Obtener las palabras más comunes del texto combinado
    common_words_all = fdist_all.most_common(10)  # Puedes ajustar el número según tus necesidades

    # Agregar el texto combinado al contenido general
    content_general.append(PageBreak())
    content_general.append(Paragraph("<b> Combinacion de sobreimpresos de Todos los Videos:</b>", getSampleStyleSheet()['Heading2']))
    content_general.append(Paragraph(f"{escape(all_text_combined)}", getSampleStyleSheet()['Normal']))
    content_general.append(Spacer(1, 12))

    # Agregar la cantidad total de palabras antes y después del filtrado para el texto combinado
    content_general.append(Paragraph(f"<b>Cantidad Total de Palabras antes de Filtrar (Texto Combinado):</b> {len(all_tokens)}", getSampleStyleSheet()['Normal']))
    content_general.append(Paragraph(f"<b>Cantidad Total de Palabras después de Filtrar (Texto Combinado):</b> {len(filtered_tokens_all)}", getSampleStyleSheet()['Normal']))
    content_general.append(Spacer(1, 12))

    # Agregar las palabras más comunes del texto combinado
    content_general.append(Paragraph("<b>Palabras Más Comunes en el Texto Combinado:</b>", getSampleStyleSheet()['Normal']))
    for word, frequency in common_words_all:
        content_general.append(Paragraph(f"{word}: {frequency} veces", getSampleStyleSheet()['Normal']))
    content_general.append(Spacer(1, 24))

    return content_text, content_general,all_text_combined

def wordcloud(all_text_combined):
    content_general = []
    try:
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_text_combined)

        # Mostrar la nube de palabras
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('Nube de Palabras')
        wordcloud_image_buffer = BytesIO()
        plt.savefig(wordcloud_image_buffer, format='png')
        content_general.append(Image(wordcloud_image_buffer, width=500, height=250))
        plt.close()

    except Exception as e:
        # Handle exceptions, print or log the error
        print(f"Error: {e}")

    return content_general
    


def text_to_df(blobs_list, cliente):
    all_video_texts = []

    # Inicializar df_texto_dict como un diccionario
    df_texto_dict = {'Video': [], 'Texto': [], 'Cantidad Total de Palabras': [], 'Cliente': [], 'Timestamp': []}

    for blob in blobs_list:
        try:
            if 'texto_del' in blob.name.lower() and blob.name.lower().endswith('.csv'):
                contenido_csv_bytes = blob.download_as_bytes()
                df_texto = pd.read_csv(BytesIO(contenido_csv_bytes))
                video_name = blob.name.split('/')[-1].split('.')[0]

                video_text = ' '.join(df_texto['text'].dropna().astype(str).tolist())
                all_video_texts.append(video_text)

                video_tokens = word_tokenize(video_text)
                stop_words = set(stopwords.words('spanish'))
                filtered_video_tokens = [word.lower() for word in video_tokens if word.isalnum() and word.lower() not in stop_words]

                # Agregar información al diccionario
                df_texto_dict['Video'].append(video_name)
                df_texto_dict['Texto'].append(video_text)
                df_texto_dict['Cantidad Total de Palabras'].append(len(video_tokens))
                df_texto_dict['Timestamp'].append(blob.time_created)
                df_texto_dict['Cliente'].append(cliente)

        except Exception as e:
            # Handle exceptions (e.g., print an error message)
            print(f"Error processing {blob.name}: {str(e)}")

    # Crear DataFrame para el análisis de texto
    df_texto = pd.DataFrame(df_texto_dict)

    # Unir todos los textos de los videos en un solo string
    all_text_combined = ' '.join(all_video_texts)


    # Crear DataFrame para el análisis general del texto
    df_general = pd.DataFrame({
        'Video': df_texto_dict['Video'],
        'Texto Combinado': [all_text_combined] * len(df_texto_dict['Video']),
        'Cliente': df_texto_dict['Cliente'],
        'Timestamp': df_texto_dict['Timestamp']
    })

    return df_texto, df_general, all_text_combined